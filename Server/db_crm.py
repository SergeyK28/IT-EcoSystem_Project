# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных CRM системы IT-EcoSystem.
Содержит все функции для взаимодействия с MySQL базой данных:
- Управление заказами
- Управление клиентами
- Управление складом
- Управление платежами
- Управление сотрудниками
- Работа с корзиной
"""

import mysql.connector
from mysql.connector import Error, pooling
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import os
from dotenv import load_dotenv
from pathlib import Path

# ==================== НАСТРОЙКА ПУТЕЙ И КОНФИГУРАЦИИ ====================

# Находим корневую директорию проекта (поднимаемся на два уровня вверх от текущего файла)
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env'

# Загружаем переменные окружения из .env файла с принудительной перезаписью
# Это нужно для получения паролей и настроек подключения к БД
load_dotenv(ENV_PATH, override=True)


class Config:
    """
    Класс конфигурации для подключения к базе данных.
    Содержит параметры подключения, которые читаются из переменных окружения.
    """

    # Параметры подключения к БД с значениями по умолчанию
    DB_HOST = os.environ.get('DB_HOST', 'localhost')  # Хост БД (по умолчанию localhost)
    DB_USER = os.environ.get('DB_USER')  # Имя пользователя БД
    DB_PASSWORD = os.environ.get('DB_PASSWORD')  # Пароль пользователя
    DB_NAME = os.environ.get('DB_NAME', 'sql_it_ecosyttem_bd')  # Имя базы данных
    DB_PORT = int(os.environ.get('DB_PORT', 3306))  # Порт подключения

    @classmethod
    def validate(cls):
        """
        Проверяет, что все необходимые параметры для подключения заданы.
        Возвращает True если все в порядке, иначе выбрасывает исключение.
        """
        if not cls.DB_USER:
            raise ValueError("DB_USER не задан в .env файле")
        if not cls.DB_PASSWORD:
            raise ValueError("DB_PASSWORD не задан в .env файле")
        return True


# Валидируем конфигурацию при загрузке модуля
try:
    Config.validate()
    print("✅ Конфигурация БД загружена успешно")
except ValueError as e:
    print(f"❌ Ошибка конфигурации: {e}")


# ==================== ПУЛ СОЕДИНЕНИЙ С БАЗОЙ ДАННЫХ ====================

class DatabaseConnectionPool:
    """
    Класс для управления пулом соединений с базой данных (Singleton паттерн).
    Пул соединений позволяет эффективно использовать соединения, не создавая
    новое соединение для каждого запроса.
    """

    _instance = None  # Единственный экземпляр класса (Singleton)
    _connection_pool = None  # Пул соединений

    def __new__(cls):
        """
        Магический метод для создания Singleton.
        Гарантирует, что будет создан только один экземпляр класса.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
            cls._instance._init_pool()  # Инициализируем пул при создании
        return cls._instance

    def _init_pool(self):
        """
        Инициализирует пул соединений с MySQL.
        Создает пул из 5 соединений, которые будут переиспользоваться.
        """
        try:
            # Проверяем конфигурацию перед созданием пула
            Config.validate()

            # Создаем пул соединений
            self._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="crm_pool",  # Имя пула
                pool_size=5,  # Количество соединений в пуле
                pool_reset_session=True,  # Сбрасывать сессию при возврате в пул
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT,
                charset='utf8mb4',  # Поддержка Unicode (включая эмодзи)
                autocommit=False  # Отключаем автокоммит для транзакций
            )
            print("✅ Пул соединений с БД инициализирован")
        except Exception as e:
            print(f"❌ Ошибка инициализации пула соединений: {e}")
            self._connection_pool = None

    def get_connection(self):
        """
        Получает соединение из пула.
        Если пул не инициализирован или произошла ошибка, возвращает None.
        """
        if self._connection_pool:
            try:
                return self._connection_pool.get_connection()
            except Error as e:
                print(f"Ошибка получения соединения из пула: {e}")
        return None


# Создаем глобальный экземпляр пула соединений
# Этот объект будет использоваться всеми функциями для получения соединений
db_pool = DatabaseConnectionPool()


def get_crm_connection():
    """
    Вспомогательная функция для получения соединения с базой данных.
    Использует пул соединений для эффективного управления ресурсами.

    Returns:
        connection: Объект соединения с БД или None в случае ошибки
    """
    return db_pool.get_connection()


# ==================== РАБОТА С ЗАКАЗАМИ (ORDERS) ====================

def get_order_id_by_number(order_number: str) -> Optional[int]:
    """
    Получает ID заказа по его номеру.

    Аргументы:
        order_number: Номер заказа (например: ORD-20260205-0004)

    Returns:
        ID заказа или None если не найден

    Пример:
        order_id = get_order_id_by_number("ORD-20260205-0004")
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Ищем ID заказа по номеру в таблице Orders
        cursor.execute("SELECT OrderID FROM Orders WHERE OrderNumber = %s", (order_number,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # Если не нашли по номеру, пробуем извлечь ID из самого номера
        # Формат номера: ORD-YYYYMMDD-XXXX, где XXXX - это ID заказа
        if order_number and order_number.startswith('ORD-'):
            parts = order_number.split('-')
            if len(parts) >= 3:
                try:
                    # Убираем ведущие нули и преобразуем в число
                    return int(parts[2].lstrip('0'))
                except ValueError:
                    pass

        return None

    except Error as e:
        print(f"Ошибка получения ID заказа: {e}")
        return None
    finally:
        # Всегда закрываем курсор и соединение
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_order_for_edit_form(order_id: int) -> Dict[str, Any]:
    """
    Получает полные данные заказа для формы редактирования.
    Загружает основную информацию, клиента, сотрудников, детали, услуги,
    комментарии и историю статусов.

    Аргументы:
        order_id: ID заказа

    Returns:
        Словарь с данными заказа или пустой словарь если не найден
    """
    connection = get_crm_connection()
    if connection is None:
        return {}

    cursor = connection.cursor(dictionary=True)  # dictionary=True возвращает результаты как словари

    try:
        # ========== ОСНОВНОЙ ЗАПРОС ==========
        # Получаем основную информацию о заказе с JOIN для связанных таблиц
        query = """
        SELECT 
            o.OrderID,
            o.OrderNumber,
            o.OrderDate,
            o.OrderType,
            o.Status,
            o.Priority,
            o.DeviceType,
            o.DeviceBrand,
            o.DeviceModel,
            o.DeviceIMEI_SN,
            o.DeviceAppearance,
            o.DevicePurchaseDate,
            o.DeviceWarrantyUntil,
            o.ProblemDescription,
            o.Diagnosis,
            o.Recommendation,
            o.Prepayment,
            o.TotalAmount,
            o.Discount,
            o.FinalAmount,
            o.IsPaid,
            o.EstimatedCompletion,
            o.Notes,
            o.CompletionDate,

            -- Данные клиента
            c.ID as ClientID,
            c.FirstName as ClientFirstName,
            c.LastName as ClientLastName,
            c.Birthdate as ClientBirthdate,
            c.PhoneNumber as ClientPhone,
            c.Email as ClientEmail,
            c.AvatarPath as ClientAvatar,
            CONCAT(c.FirstName, ' ', c.LastName) as ClientFullName,

            -- Данные менеджера (сотрудник, принявший заказ)
            m.EmployeeID as ManagerID,
            m.FirstName as ManagerFirstName,
            m.LastName as ManagerLastName,
            CONCAT(m.FirstName, ' ', m.LastName) as ManagerFullName,
            m.PhoneNumber as ManagerPhone,
            m.Email as ManagerEmail,

            -- Данные исполнителя (сотрудник, выполняющий работу)
            e.EmployeeID as ExecutorID,
            e.FirstName as ExecutorFirstName,
            e.LastName as ExecutorLastName,
            CONCAT(e.FirstName, ' ', e.LastName) as ExecutorFullName,
            e.PhoneNumber as ExecutorPhone,
            e.Email as ExecutorEmail,

            -- Причина обращения
            ar.ReasonID as AppealReasonID,
            ar.ReasonName as AppealReasonName,
            ar.Description as AppealReasonDescription,

            -- Информация о платежах (подзапросы)
            (SELECT COALESCE(SUM(Amount), 0) FROM Payments 
             WHERE OrderID = o.OrderID AND PaymentType = 'Предоплата') as PrepaymentTotal,

            (SELECT COALESCE(SUM(Amount), 0) FROM Payments WHERE OrderID = o.OrderID) as AllPaymentsTotal,

            -- Статистика (количество связанных записей)
            (SELECT COUNT(*) FROM OrderServices WHERE OrderID = o.OrderID) as ServicesCount,
            (SELECT COUNT(*) FROM OrderDetails WHERE OrderID = o.OrderID) as DetailsCount,
            (SELECT COUNT(*) FROM OrderComments WHERE OrderID = o.OrderID) as CommentsCount

        FROM Orders o
        LEFT JOIN Client c ON o.ClientID = c.ID
        LEFT JOIN ListEmployee m ON o.ManagerID = m.EmployeeID
        LEFT JOIN ListEmployee e ON o.ExecutorID = e.EmployeeID
        LEFT JOIN AppealReasons ar ON o.AppealReasonID = ar.ReasonID
        WHERE o.OrderID = %s
        """

        cursor.execute(query, (order_id,))
        order_data = cursor.fetchone()

        if order_data:
            # ========== ЗАГРУЗКА ДЕТАЛЕЙ (ЗАПЧАСТЕЙ) ==========
            cursor.execute("""
                SELECT 
                    od.OrderDetailID,
                    od.StockID,
                    od.Quantity,
                    od.UnitPrice,
                    od.TotalPrice,
                    od.WarrantyDays,
                    od.Notes as DetailNotes,
                    ds.DetailName,
                    ds.DetailCode,
                    ds.Brand as PartBrand,
                    ds.Category as PartCategory,
                    ds.Description as PartDescription,
                    ds.CountInStock,
                    ds.Price as StockPrice
                FROM OrderDetails od
                JOIN DetailStock ds ON od.StockID = ds.StockID
                WHERE od.OrderID = %s
                ORDER BY od.OrderDetailID
            """, (order_id,))
            order_data['details_list'] = cursor.fetchall()

            # ========== ЗАГРУЗКА УСЛУГ ==========
            cursor.execute("""
                SELECT 
                    os.OrderServiceID,
                    os.ServiceTypeID,
                    os.EmployeeID,
                    os.Quantity,
                    os.UnitPrice,
                    os.TotalPrice,
                    os.StartDate,
                    os.EndDate,
                    os.Status as ServiceStatus,
                    os.Notes as ServiceNotes,
                    st.ServiceDescription,
                    st.Category as ServiceCategory,
                    st.BasePrice as ServiceBasePrice,
                    st.EstimatedTime,
                    CONCAT(emp.FirstName, ' ', emp.LastName) as EmployeeName
                FROM OrderServices os
                JOIN ServiceTypes st ON os.ServiceTypeID = st.ServiceTypeID
                LEFT JOIN ListEmployee emp ON os.EmployeeID = emp.EmployeeID
                WHERE os.OrderID = %s
                ORDER BY os.OrderServiceID
            """, (order_id,))
            order_data['services_list'] = cursor.fetchall()

            # ========== ЗАГРУЗКА КОММЕНТАРИЕВ ==========
            cursor.execute("""
                SELECT 
                    oc.CommentID,
                    oc.CommentDate,
                    oc.CommentText,
                    oc.IsInternal,
                    oc.AttachmentPath,
                    CONCAT(emp.FirstName, ' ', emp.LastName) as EmployeeName,
                    emp.EmployeeID
                FROM OrderComments oc
                LEFT JOIN ListEmployee emp ON oc.EmployeeID = emp.EmployeeID
                WHERE oc.OrderID = %s
                ORDER BY oc.CommentDate DESC
                LIMIT 20
            """, (order_id,))
            order_data['comments_list'] = cursor.fetchall()

            # ========== ЗАГРУЗКА ИСТОРИИ СТАТУСОВ ==========
            cursor.execute("""
                SELECT 
                    h.HistoryID,
                    h.OldStatus,
                    h.NewStatus,
                    h.ChangeDate,
                    h.ChangeReason,
                    CONCAT(emp.FirstName, ' ', emp.LastName) as ChangedByName,
                    emp.EmployeeID
                FROM OrderStatusHistory h
                LEFT JOIN ListEmployee emp ON h.ChangedBy = emp.EmployeeID
                WHERE h.OrderID = %s
                ORDER BY h.ChangeDate DESC
                LIMIT 20
            """, (order_id,))
            order_data['status_history'] = cursor.fetchall()

        return order_data if order_data else {}

    except Error as e:
        print(f"Ошибка получения данных заказа для редактирования: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def update_order_from_edit_form(order_id: int, order_data: Dict[str, Any],
                                details_data: List[Dict[str, Any]],
                                services_data: List[Dict[str, Any]]) -> bool:
    """
    Обновляет заказ из формы редактирования.
    Выполняет транзакцию: обновляет основную информацию, детали, услуги,
    добавляет комментарий и записывает изменение статуса в историю.

    Аргументы:
        order_id: ID заказа
        order_data: Данные заказа
        details_data: Данные деталей (запчастей)
        services_data: Данные услуг

    Returns:
        True если успешно, False если ошибка
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        # ========== ШАГ 1: Обновляем основную информацию заказа ==========
        update_order_query = """
        UPDATE Orders SET
            Status = %s,
            OrderType = %s,
            Priority = %s,
            DeviceType = %s,
            DeviceBrand = %s,
            DeviceModel = %s,
            DeviceIMEI_SN = %s,
            DeviceAppearance = %s,
            ProblemDescription = %s,
            Diagnosis = %s,
            Recommendation = %s,
            ManagerID = %s,
            ExecutorID = %s,
            AppealReasonID = %s,
            Prepayment = %s,
            Discount = %s,
            TotalAmount = %s,
            FinalAmount = %s,
            EstimatedCompletion = %s,
            Notes = %s
        WHERE OrderID = %s
        """

        # Преобразуем дату из строки в объект datetime если нужно
        estimated_completion = order_data.get('estimated_completion')
        if estimated_completion:
            try:
                if isinstance(estimated_completion, str):
                    estimated_completion = datetime.strptime(estimated_completion, '%Y-%m-%d %H:%M:%S')
            except:
                estimated_completion = None

        cursor.execute(update_order_query, (
            order_data.get('status'),
            order_data.get('order_type'),
            order_data.get('priority'),
            order_data.get('device_type'),
            order_data.get('device_brand'),
            order_data.get('device_model'),
            order_data.get('device_imei'),
            order_data.get('device_appearance'),
            order_data.get('problem_description'),
            order_data.get('diagnosis'),
            order_data.get('recommendation'),
            order_data.get('manager_id') or None,
            order_data.get('executor_id') or None,
            order_data.get('appeal_reason_id') or None,
            float(order_data.get('prepayment', 0)),
            float(order_data.get('discount', 0)),
            float(order_data.get('total_amount', 0)),
            float(order_data.get('final_amount', 0)),
            estimated_completion,
            order_data.get('notes'),
            order_id
        ))

        # ========== ШАГ 2: Обновляем детали (запчасти) ==========
        # Получаем список ID существующих деталей
        existing_details = []
        for detail in details_data:
            if detail.get('order_detail_id'):
                existing_details.append(detail['order_detail_id'])

        # Удаляем детали, которых нет в новом списке
        if existing_details:
            # Формируем строку с ID через запятую для SQL IN
            cursor.execute("""
                DELETE FROM OrderDetails 
                WHERE OrderID = %s AND OrderDetailID NOT IN (%s)
            """ % (order_id, ','.join(map(str, existing_details))))
        else:
            # Если нет ни одной детали, удаляем все
            cursor.execute("DELETE FROM OrderDetails WHERE OrderID = %s", (order_id,))

        # Добавляем/обновляем каждую деталь
        for detail in details_data:
            if detail.get('order_detail_id'):
                # Обновляем существующую запись
                cursor.execute("""
                    UPDATE OrderDetails SET
                        StockID = %s,
                        Quantity = %s,
                        UnitPrice = %s,
                        WarrantyDays = %s
                    WHERE OrderDetailID = %s
                """, (
                    detail.get('stock_id'),
                    detail.get('quantity', 1),
                    detail.get('unit_price', 0),
                    detail.get('warranty_days'),
                    detail.get('order_detail_id')
                ))
            else:
                # Добавляем новую запись
                cursor.execute("""
                    INSERT INTO OrderDetails (OrderID, StockID, Quantity, UnitPrice, WarrantyDays)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    order_id,
                    detail.get('stock_id'),
                    detail.get('quantity', 1),
                    detail.get('unit_price', 0),
                    detail.get('warranty_days')
                ))

                # Обновляем количество на складе (списываем использованные детали)
                cursor.execute("""
                    UPDATE DetailStock 
                    SET CountInStock = CountInStock - %s
                    WHERE StockID = %s
                """, (detail.get('quantity', 1), detail.get('stock_id')))

        # ========== ШАГ 3: Обновляем услуги ==========
        # Получаем список ID существующих услуг
        existing_services = []
        for service in services_data:
            if service.get('order_service_id'):
                existing_services.append(service['order_service_id'])

        # Удаляем услуги, которых нет в новом списке
        if existing_services:
            cursor.execute("""
                DELETE FROM OrderServices 
                WHERE OrderID = %s AND OrderServiceID NOT IN (%s)
            """ % (order_id, ','.join(map(str, existing_services))))
        else:
            cursor.execute("DELETE FROM OrderServices WHERE OrderID = %s", (order_id,))

        # Добавляем/обновляем каждую услугу
        for service in services_data:
            if service.get('order_service_id'):
                # Обновляем существующую запись
                cursor.execute("""
                    UPDATE OrderServices SET
                        ServiceTypeID = %s,
                        Quantity = %s,
                        UnitPrice = %s,
                        Status = %s
                    WHERE OrderServiceID = %s
                """, (
                    service.get('service_type_id'),
                    service.get('quantity', 1),
                    service.get('unit_price', 0),
                    service.get('status', 'Запланировано'),
                    service.get('order_service_id')
                ))
            else:
                # Добавляем новую запись
                cursor.execute("""
                    INSERT INTO OrderServices (OrderID, ServiceTypeID, Quantity, UnitPrice, Status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    order_id,
                    service.get('service_type_id'),
                    service.get('quantity', 1),
                    service.get('unit_price', 0),
                    service.get('status', 'Запланировано')
                ))

        # ========== ШАГ 4: Добавляем комментарий об обновлении ==========
        if order_data.get('update_comment'):
            cursor.execute("""
                INSERT INTO OrderComments (OrderID, EmployeeID, CommentText, IsInternal)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                order_data.get('updated_by', 1),
                f"Заказ обновлен: {order_data.get('update_comment')}",
                True  # True = внутренний комментарий
            ))

        # ========== ШАГ 5: Записываем изменение статуса в историю ==========
        # Получаем текущий статус для сравнения
        cursor.execute("""
            SELECT Status FROM Orders WHERE OrderID = %s
        """, (order_id,))
        old_status_result = cursor.fetchone()

        # Если статус изменился, добавляем запись в историю
        if old_status_result and old_status_result[0] != order_data.get('status'):
            cursor.execute("""
                INSERT INTO OrderStatusHistory (OrderID, OldStatus, NewStatus, ChangedBy, ChangeReason)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                order_id,
                old_status_result[0],
                order_data.get('status'),
                order_data.get('updated_by', 1),
                order_data.get('update_comment', 'Изменение через форму редактирования')
            ))

        # Подтверждаем транзакцию
        connection.commit()
        return True

    except Error as e:
        print(f"Ошибка обновления заказа: {e}")
        connection.rollback()  # Откатываем все изменения в случае ошибки
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_orders_for_crm_table(filter_status: str = None, search_text: str = None) -> List[Dict[str, Any]]:
    """
    Получает список заказов для отображения в таблице CRM.
    Поддерживает фильтрацию по статусу и поиск по тексту.

    Аргументы:
        filter_status: Фильтр по статусу (например: "Новая", "В работе")
        search_text: Текст для поиска по номеру, клиенту, устройству и т.д.

    Returns:
        Список заказов в формате, готовом для отображения в таблице
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        # Основной запрос с LEFT JOIN для получения связанных данных
        query = """
        SELECT 
            o.OrderID,
            o.OrderNumber as `Заказы`,
            o.Status as `Статус`,
            CONCAT(c.FirstName, ' ', c.LastName) as `Клиент`,
            CONCAT(m.FirstName, ' ', m.LastName) as `Менеджер`,
            CONCAT(e.FirstName, ' ', e.LastName) as `Исполнитель`,
            ar.ReasonName as `Причины обращения`,
            o.DeviceBrand as `Бренд`,
            o.DeviceModel as `Модель`,
            o.DeviceType as `Тип устройства`,
            o.DeviceAppearance as `Внешний вид`
        FROM Orders o
        LEFT JOIN Client c ON o.ClientID = c.ID
        LEFT JOIN ListEmployee m ON o.ManagerID = m.EmployeeID
        LEFT JOIN ListEmployee e ON o.ExecutorID = e.EmployeeID
        LEFT JOIN AppealReasons ar ON o.AppealReasonID = ar.ReasonID
        WHERE 1=1  -- Это условие всегда истинно, нужно для удобного добавления WHERE
        """

        params = []

        # Добавляем фильтр по статусу если указан
        if filter_status and filter_status != "Все":
            query += " AND o.Status = %s"
            params.append(filter_status)

        # Добавляем поиск по тексту если указан
        if search_text:
            query += """
            AND (
                o.OrderNumber LIKE %s 
                OR CONCAT(c.FirstName, ' ', c.LastName) LIKE %s
                OR o.DeviceBrand LIKE %s
                OR o.DeviceModel LIKE %s
                OR ar.ReasonName LIKE %s
                OR o.Status LIKE %s
                OR o.DeviceType LIKE %s
                OR o.DeviceAppearance LIKE %s
            )
            """
            search_pattern = f"%{search_text}%"  # Добавляем % для поиска по части слова
            params.extend([search_pattern] * 8)  # 8 раз добавляем один и тот же паттерн

        # Сортируем по дате создания (новые сверху)
        query += " ORDER BY o.OrderDate DESC"

        cursor.execute(query, params)
        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения заказов для CRM таблицы: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def create_new_order(order_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает новый заказ в базе данных.

    Аргументы:
        order_data: Словарь с данными нового заказа

    Returns:
        ID созданного заказа или None при ошибке
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Генерируем уникальный номер заказа
        import random
        import time
        # Формат: ORD-ГГГГММДД-СЛУЧАЙНОЕ_ЧИСЛО
        order_number = f"ORD-{time.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        # SQL запрос на вставку нового заказа
        query = """
        INSERT INTO Orders (
            OrderNumber, OrderDate, Status, OrderType, Priority,
            DeviceType, DeviceBrand, DeviceModel, DeviceIMEI_SN,
            DeviceAppearance, ProblemDescription,
            ClientID, ManagerID, ExecutorID, AppealReasonID,
            Prepayment, Discount, TotalAmount, FinalAmount,
            EstimatedCompletion, Notes
        ) VALUES (
            %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        # Подготавливаем дату завершения
        estimated_completion = order_data.get('estimated_completion')
        if estimated_completion and isinstance(estimated_completion, str):
            try:
                from datetime import datetime
                estimated_completion = datetime.strptime(estimated_completion, '%Y-%m-%d %H:%M:%S')
            except:
                estimated_completion = None

        cursor.execute(query, (
            order_number,
            order_data.get('status', 'Новая'),
            order_data.get('order_type', 'Платный'),
            order_data.get('priority', 'Средний'),
            order_data.get('device_type', ''),
            order_data.get('device_brand', ''),
            order_data.get('device_model', ''),
            order_data.get('device_imei', ''),
            order_data.get('device_appearance', ''),
            order_data.get('problem_description', ''),
            order_data.get('client_id'),
            order_data.get('manager_id') or None,
            order_data.get('executor_id') or None,
            order_data.get('appeal_reason_id') or None,
            float(order_data.get('prepayment', 0)),
            float(order_data.get('discount', 0)),
            float(order_data.get('total_amount', 0)),
            float(order_data.get('final_amount', 0)),
            estimated_completion,
            order_data.get('notes', '')
        ))

        new_order_id = cursor.lastrowid  # Получаем ID только что созданной записи

        # Добавляем комментарий о создании заказа
        if order_data.get('created_by'):
            cursor.execute("""
                INSERT INTO OrderComments (OrderID, EmployeeID, CommentText, IsInternal)
                VALUES (%s, %s, %s, %s)
            """, (new_order_id, order_data.get('created_by'), 'Заказ создан в системе', True))

        # Записываем в историю статусов
        cursor.execute("""
            INSERT INTO OrderStatusHistory (OrderID, OldStatus, NewStatus, ChangedBy, ChangeReason)
            VALUES (%s, NULL, %s, %s, %s)
        """, (new_order_id, order_data.get('status', 'Новая'),
              order_data.get('created_by'), 'Создание нового заказа'))

        connection.commit()
        return new_order_id

    except Error as e:
        print(f"Ошибка создания заказа: {e}")
        connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def create_new_order_with_services_parts(order_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает новый заказ с услугами и запчастями за одну транзакцию.

    Аргументы:
        order_data: Словарь с данными нового заказа, включая services_list и parts_list

    Returns:
        ID созданного заказа или None при ошибке
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        import random
        import time
        from datetime import datetime

        # ========== ГЕНЕРАЦИЯ НОМЕРА ЗАКАЗА ==========
        # Получаем текущую дату в формате YYYYMMDD
        current_date = time.strftime('%Y%m%d')

        # Получаем последний номер заказа за сегодня
        cursor.execute("""
            SELECT OrderNumber FROM Orders 
            WHERE OrderNumber LIKE %s 
            ORDER BY OrderNumber DESC 
            LIMIT 1
        """, (f'ORD-{current_date}-%',))

        last_order = cursor.fetchone()
        if last_order:
            # Извлекаем номер из последнего заказа и увеличиваем на 1
            last_number = int(last_order[0].split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        # Формируем номер с ведущими нулями (например: ORD-20260205-0004)
        order_number = f"ORD-{current_date}-{new_number:04d}"

        # ========== СОЗДАНИЕ ЗАКАЗА ==========
        query = """
        INSERT INTO Orders (
            OrderNumber, OrderDate, Status, OrderType, Priority,
            DeviceType, DeviceBrand, DeviceModel, DeviceIMEI_SN,
            DeviceAppearance, ProblemDescription,
            ClientID, ManagerID, ExecutorID, AppealReasonID,
            Prepayment, Discount, TotalAmount, FinalAmount,
            EstimatedCompletion, Notes
        ) VALUES (
            %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        estimated_completion = order_data.get('estimated_completion')

        cursor.execute(query, (
            order_number,
            order_data.get('status', 'Новая'),
            order_data.get('order_type', 'Платный'),
            order_data.get('priority', 'Средний'),
            order_data.get('device_type', ''),
            order_data.get('device_brand', ''),
            order_data.get('device_model', ''),
            order_data.get('device_imei', ''),
            order_data.get('device_appearance', ''),
            order_data.get('problem_description', ''),
            order_data.get('client_id'),
            order_data.get('manager_id') or None,
            order_data.get('executor_id') or None,
            order_data.get('appeal_reason_id') or None,
            float(order_data.get('prepayment', 0)),
            float(order_data.get('discount', 0)),
            float(order_data.get('total_amount', 0)),
            float(order_data.get('final_amount', 0)),
            estimated_completion,
            order_data.get('notes', '')
        ))

        new_order_id = cursor.lastrowid

        # ========== ДОБАВЛЕНИЕ УСЛУГ ==========
        services_list = order_data.get('services_list', [])
        for service in services_list:
            cursor.execute("""
                INSERT INTO OrderServices (OrderID, ServiceTypeID, Quantity, UnitPrice, Status)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                new_order_id,
                service.get('service_type_id'),
                service.get('quantity', 1),
                service.get('unit_price', 0),
                'Запланировано'
            ))

        # ========== ДОБАВЛЕНИЕ ЗАПЧАСТЕЙ ==========
        parts_list = order_data.get('parts_list', [])
        for part in parts_list:
            cursor.execute("""
                INSERT INTO OrderDetails (OrderID, StockID, Quantity, UnitPrice, WarrantyDays)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                new_order_id,
                part.get('stock_id'),
                part.get('quantity', 1),
                part.get('unit_price', 0),
                part.get('warranty_days', 90)
            ))

            # Обновляем количество на складе (списываем использованные детали)
            cursor.execute("""
                UPDATE DetailStock 
                SET CountInStock = CountInStock - %s
                WHERE StockID = %s
            """, (part.get('quantity', 1), part.get('stock_id')))

        # ========== ДОБАВЛЕНИЕ КОММЕНТАРИЯ ==========
        if order_data.get('created_by'):
            cursor.execute("""
                INSERT INTO OrderComments (OrderID, EmployeeID, CommentText, IsInternal)
                VALUES (%s, %s, %s, %s)
            """, (new_order_id, order_data.get('created_by'), 'Заказ создан в системе', True))

        # ========== ЗАПИСЬ В ИСТОРИЮ СТАТУСОВ ==========
        cursor.execute("""
            INSERT INTO OrderStatusHistory (OrderID, OldStatus, NewStatus, ChangedBy, ChangeReason)
            VALUES (%s, NULL, %s, %s, %s)
        """, (new_order_id, order_data.get('status', 'Новая'),
              order_data.get('created_by'), 'Создание нового заказа'))

        connection.commit()
        return new_order_id

    except Error as e:
        print(f"Ошибка создания заказа с услугами и запчастями: {e}")
        connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_order_statistics() -> Dict[str, Any]:
    """
    Получает статистику по заказам для аналитики.

    Returns:
        Словарь со статистикой: общее количество, по статусам, по типам, за последние 7 дней
    """
    connection = get_crm_connection()
    if connection is None:
        return {}

    cursor = connection.cursor(dictionary=True)

    try:
        stats = {}

        # Общее количество заказов
        cursor.execute("SELECT COUNT(*) as total FROM Orders")
        stats['total_orders'] = cursor.fetchone()['total']

        # Заказы по статусам
        cursor.execute("""
            SELECT Status, COUNT(*) as count 
            FROM Orders 
            GROUP BY Status
        """)
        stats['by_status'] = {row['Status']: row['count'] for row in cursor.fetchall()}

        # Заказы по типам (Платный/Гарантийный)
        cursor.execute("""
            SELECT OrderType, COUNT(*) as count 
            FROM Orders 
            GROUP BY OrderType
        """)
        stats['by_type'] = {row['OrderType']: row['count'] for row in cursor.fetchall()}

        # Заказы за последние 7 дней (для графика)
        cursor.execute("""
            SELECT DATE(OrderDate) as date, COUNT(*) as count 
            FROM Orders 
            WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(OrderDate)
            ORDER BY date
        """)
        stats['last_7_days'] = cursor.fetchall()

        return stats

    except Error as e:
        print(f"Ошибка получения статистики: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


# ==================== РАБОТА С КЛИЕНТАМИ (CLIENTS) ====================

def search_clients(search_term: str) -> List[Dict[str, Any]]:
    """
    Ищет клиентов по имени, телефону или email.

    Аргументы:
        search_term: Текст для поиска

    Returns:
        Список найденных клиентов (максимум 20)
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT ID, FirstName, LastName, PhoneNumber, Email, Birthdate
            FROM Client 
            WHERE FirstName LIKE %s 
               OR LastName LIKE %s 
               OR PhoneNumber LIKE %s 
               OR Email LIKE %s
               OR CONCAT(FirstName, ' ', LastName) LIKE %s
            ORDER BY LastName, FirstName
            LIMIT 20  -- Ограничиваем количество результатов
        """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))

        return cursor.fetchall()
    except Error as e:
        print(f"Ошибка поиска клиентов: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def create_new_client(client_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает нового клиента в базе данных.
    Автоматически генерирует логин и временный пароль.

    Аргументы:
        client_data: Данные клиента

    Returns:
        ID созданного клиента или None при ошибке
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # ========== ГЕНЕРАЦИЯ ЛОГИНА ==========
        email = client_data.get('email', '')
        first_name = client_data.get('first_name', '')
        last_name = client_data.get('last_name', '')

        if email:
            # Берем часть email до @
            login = email.split('@')[0]
        elif first_name and last_name:
            # Создаем логин из имени и фамилии
            login = f"{first_name.lower()}.{last_name.lower()}"
        else:
            # Если ничего нет, генерируем случайный
            import random
            login = f"client{random.randint(10000, 99999)}"

        # Проверяем уникальность логина
        cursor.execute("SELECT COUNT(*) FROM Client WHERE Login = %s", (login,))
        count = cursor.fetchone()[0]
        if count > 0:
            # Добавляем цифры если логин уже существует
            import random
            login = f"{login}{random.randint(100, 999)}"

        # ========== ГЕНЕРАЦИЯ ПАРОЛЯ ==========
        # Пытаемся использовать bcrypt для хеширования (более безопасно)
        try:
            import bcrypt
            # Генерируем временный пароль
            temp_password = "TempPass123!"
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), salt)
            password_hash_str = password_hash.decode('utf-8')
        except ImportError:
            # Если bcrypt не установлен, используем SHA256
            import hashlib
            import secrets
            temp_password = secrets.token_urlsafe(8)
            full_hash = hashlib.sha256(temp_password.encode()).hexdigest()
            password_hash_str = full_hash[:60]  # Обрезаем до 60 символов

        # ========== СОЗДАНИЕ КЛИЕНТА ==========
        query = """
        INSERT INTO Client (
            Login, PasswordHash, FirstName, LastName, 
            PhoneNumber, Email, Birthdate, RegistrationDate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """

        cursor.execute(query, (
            login[:50],  # Ограничиваем длину логина
            password_hash_str,
            first_name,
            last_name,
            client_data.get('phone_number', ''),
            email,
            client_data.get('birthdate')
        ))

        new_client_id = cursor.lastrowid
        connection.commit()

        print(f"Создан клиент #{new_client_id}: {first_name} {last_name}, логин: {login}")
        return new_client_id

    except Error as e:
        print(f"Ошибка создания клиента: {e}")
        connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_client_orders(client_id: int) -> List[Dict[str, Any]]:
    """
    Получает список заказов для конкретного клиента.

    Аргументы:
        client_id: ID клиента

    Returns:
        Список заказов клиента
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                o.OrderID,
                o.OrderNumber,
                o.OrderDate,
                o.Status,
                o.OrderType,
                o.DeviceType,
                o.DeviceBrand,
                o.DeviceModel,
                o.ProblemDescription,
                o.TotalAmount,
                o.FinalAmount,
                o.IsPaid,
                o.Prepayment,
                o.Diagnosis,
                o.CompletionDate,
                o.EstimatedCompletion
            FROM Orders o
            WHERE o.ClientID = %s
            ORDER BY o.OrderDate DESC
        """, (client_id,))

        return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения заказов клиента: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


# ==================== РАБОТА СО СПРАВОЧНИКАМИ ====================

def get_all_appeal_reasons() -> List[Dict[str, Any]]:
    """
    Получает все причины обращения из справочника.

    Returns:
        Список причин обращения
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT ReasonID, ReasonName FROM AppealReasons ORDER BY ReasonName")
        return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения причин обращения: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_all_employees() -> List[Dict[str, Any]]:
    """
    Получает всех активных сотрудников.

    Returns:
        Список сотрудников
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT EmployeeID, FirstName, LastName, Position, Role, PhoneNumber, Email
            FROM ListEmployee 
            WHERE IsActive = TRUE 
            ORDER BY LastName, FirstName
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения сотрудников: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_all_service_types() -> List[Dict[str, Any]]:
    """
    Получает все активные типы услуг.

    Returns:
        Список услуг
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ServiceTypeID, ServiceDescription, BasePrice, Category, 
                   EstimatedTime, IsActive
            FROM ServiceTypes 
            ORDER BY Category, ServiceDescription
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения типов услуг: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_all_service_types_for_order() -> List[Dict[str, Any]]:
    """
    Получает все типы услуг для добавления в заказ.
    Аналогично get_all_service_types, но с другим порядком сортировки.

    Returns:
        Список услуг, сгруппированный по категориям
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ServiceTypeID, ServiceDescription, BasePrice, Category, EstimatedTime
            FROM ServiceTypes 
            WHERE IsActive = TRUE 
            ORDER BY Category, ServiceDescription
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения типов услуг для заказа: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_all_stock_items() -> List[Dict[str, Any]]:
    """
    Получает все активные товары со склада.

    Returns:
        Список товаров
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT StockID, DetailCode, DetailName, Brand, Category, 
                   CountInStock, Price, CostPrice, WarrantyDays, Description
            FROM DetailStock 
            WHERE IsActive = TRUE
            ORDER BY DetailName
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения товаров со склада: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_all_stock_items_for_order() -> List[Dict[str, Any]]:
    """
    Получает товары со склада для добавления в заказ.
    Возвращает только те товары, которые есть в наличии.

    Returns:
        Список товаров в наличии
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT StockID, DetailCode, DetailName, Brand, Category, 
                   CountInStock, Price, WarrantyDays
            FROM DetailStock 
            WHERE IsActive = TRUE AND CountInStock > 0
            ORDER BY Category, DetailName
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения товаров со склада для заказа: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def save_payment(self):
    """Сохраняет операцию"""
    # Проверяем сумму
    try:
        amount_text = self.amount_input.text().strip()
        if not amount_text:
            QMessageBox.warning(self, "Ошибка", "Введите сумму")
            return

        amount = float(amount_text.replace(',', '.'))
        if amount <= 0:
            QMessageBox.warning(self, "Ошибка", "Сумма должна быть больше 0")
            return
    except ValueError:
        QMessageBox.warning(self, "Ошибка", "Введите корректную сумму (например: 1000.00)")
        return

    employee_id = employee_session.get_employee_id() if employee_session.is_authenticated() else None

    # Обработка в зависимости от режима
    if self.current_mode == 'order':
        # Оплата заказа
        if not self.selected_order_id:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите заказ")
            return

        payment_data = {
            'amount': amount,
            'payment_method': self.method_combo.currentText(),
            'payment_type': 'Оплата',
            'receipt_number': self.receipt_input.text().strip() or None,
            'notes': self.notes_input.text().strip() or None,
            'employee_id': employee_id
        }

        success, message = db_crm.add_payment_with_validation(self.selected_order_id, payment_data)

    elif self.current_mode == 'income':
        # Доход
        category = self.category_combo.currentText()
        description = self.description_input.text().strip()

        if not category:
            QMessageBox.warning(self, "Ошибка", "Выберите статью дохода")
            return

        transaction_data = {
            'transaction_type': 'income',
            'amount': amount,
            'method': self.method_combo.currentText(),
            'category': category,
            'description': description,
            'receipt_number': self.receipt_input.text().strip() or None,
            'employee_id': employee_id
        }

        success, message = db_crm.add_income_expense(transaction_data)

    else:  # expense
        # Расход
        category = self.category_combo.currentText()
        description = self.description_input.text().strip()

        if not category:
            QMessageBox.warning(self, "Ошибка", "Выберите статью расхода")
            return

        transaction_data = {
            'transaction_type': 'expense',
            'amount': amount,
            'method': self.method_combo.currentText(),
            'category': category,
            'description': description,
            'receipt_number': self.receipt_input.text().strip() or None,
            'employee_id': employee_id
        }

        success, message = db_crm.add_income_expense(transaction_data)

    if success:
        QMessageBox.information(self, "Успех", message)
        self.accept()
    else:
        QMessageBox.critical(self, "Ошибка", message)


# ==================== КОНСТАНТЫ ДЛЯ СИСТЕМНЫХ ОПЕРАЦИЙ ====================

# ID системного заказа для доходов и расходов (нужно создать в БД один раз)
SYSTEM_ORDER_ID = 1  # Замените на реальный ID после создания


# Функция для получения системного заказа
def get_system_order_id() -> int:
    """
    Получает ID системного заказа для учета доходов/расходов.
    Если заказа нет, создает его.

    Returns:
        ID системного заказа
    """
    global SYSTEM_ORDER_ID

    connection = get_crm_connection()
    if connection is None:
        return 1

    cursor = connection.cursor(dictionary=True)

    try:
        # Проверяем существование системного заказа
        cursor.execute("""
            SELECT OrderID FROM Orders 
            WHERE OrderNumber = 'SYS-GENERAL-0001'
        """)
        result = cursor.fetchone()

        if result:
            SYSTEM_ORDER_ID = result['OrderID']
            return SYSTEM_ORDER_ID

        # Если заказа нет, создаем его
        # Сначала получаем первого клиента
        cursor.execute("SELECT ID FROM Client LIMIT 1")
        client_result = cursor.fetchone()
        client_id = client_result['ID'] if client_result else 1

        cursor.execute("""
            INSERT INTO Orders (
                OrderNumber, 
                OrderDate, 
                Status, 
                OrderType, 
                Priority,
                ClientID,
                ProblemDescription,
                Notes
            ) VALUES (
                'SYS-GENERAL-0001',
                NOW(),
                'Завершен',
                'Платный',
                'Низкий',
                %s,
                'Системные операции (доходы/расходы)',
                'Служебный заказ для учета доходов и расходов, не привязанных к конкретным заказам'
            )
        """, (client_id,))

        connection.commit()
        SYSTEM_ORDER_ID = cursor.lastrowid
        return SYSTEM_ORDER_ID

    except Error as e:
        print(f"Ошибка получения системного заказа: {e}")
        return 1
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def add_income_expense(transaction_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Добавляет запись о доходе или расходе (не привязанную к заказу).

    Аргументы:
        transaction_data: Данные транзакции
            - transaction_type: 'income' или 'expense'
            - amount: сумма
            - category: статья (например: 'Зарплата', 'Аренда', 'Реклама' и т.д.)
            - method: метод оплаты
            - description: описание
            - employee_id: ID сотрудника

    Returns:
        Кортеж (успех, сообщение)
    """
    connection = get_crm_connection()
    if connection is None:
        return False, "Нет подключения к базе данных"

    cursor = connection.cursor()

    try:
        # Получаем ID системного заказа
        system_order_id = get_system_order_id()

        # Для доходов и расходов используем:
        # - OrderID = ID системного заказа
        # - PaymentType = 'Оплата' для доходов, 'Возврат' для расходов
        #   Чтобы отличать, используем Notes для хранения типа и категории

        if transaction_data.get('transaction_type') == 'income':
            # Доход - используем PaymentType = 'Оплата'
            payment_type = 'Оплата'
            prefix = "ДОХОД"
            amount = abs(float(transaction_data.get('amount', 0)))  # Положительная сумма
        else:
            # Расход - используем PaymentType = 'Возврат' (как отрицательный платеж)
            payment_type = 'Возврат'
            prefix = "РАСХОД"
            amount = abs(float(transaction_data.get('amount', 0)))  # Положительная сумма

        category = transaction_data.get('category', '')
        description = transaction_data.get('description', '')

        # Формируем Notes с информацией о типе и категории
        notes = f"[{prefix}][{category}] {description}".strip()
        if transaction_data.get('receipt_number'):
            notes += f" (Чек: {transaction_data.get('receipt_number')})"

        query = """
        INSERT INTO Payments (
            OrderID, Amount, PaymentMethod, PaymentType, 
            ReceiptNumber, Notes, EmployeeID, PaymentDate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """

        cursor.execute(query, (
            system_order_id,  # Используем системный заказ
            amount,
            transaction_data.get('method', 'Наличные'),
            payment_type,
            transaction_data.get('receipt_number', ''),
            notes,
            transaction_data.get('employee_id')
        ))

        connection.commit()
        return True, f"{'Доход' if transaction_data.get('transaction_type') == 'income' else 'Расход'} успешно добавлен"

    except Error as e:
        print(f"Ошибка добавления дохода/расхода: {e}")
        connection.rollback()
        return False, f"Ошибка базы данных: {e}"
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_income_expense_categories() -> Dict[str, List[str]]:
    """
    Получает списки статей для доходов и расходов.

    Returns:
        Словарь с категориями: {'income': [...], 'expense': [...]}
    """
    # Статьи доходов
    income_categories = [
        "Выручка от ремонта",
        "Продажа запчастей",
        "Консультации",
        "Диагностика",
        "Абонентское обслуживание",
        "Другое"
    ]

    # Статьи расходов
    expense_categories = [
        "Зарплата",
        "Аренда",
        "Коммунальные услуги",
        "Закупка запчастей",
        "Реклама",
        "Налоги",
        "Канцелярия",
        "Оборудование",
        "Транспорт",
        "Другое"
    ]

    return {
        'income': income_categories,
        'expense': expense_categories
    }


def get_financial_summary_with_categories() -> Dict[str, Any]:
    """
    Получает расширенную финансовую сводку с разбивкой по категориям.
    """
    connection = get_crm_connection()
    if connection is None:
        return {}

    cursor = connection.cursor(dictionary=True)

    try:
        summary = {}

        # Получаем ID системного заказа
        system_order_id = get_system_order_id()

        # Общий баланс (сумма всех платежей с учетом знака)
        cursor.execute("""
            SELECT 
                COALESCE(SUM(
                    CASE 
                        WHEN PaymentType IN ('Оплата', 'Предоплата') THEN Amount
                        WHEN PaymentType = 'Возврат' THEN -Amount
                        ELSE 0
                    END
                ), 0) as total_balance
            FROM Payments
        """)
        result = cursor.fetchone()
        summary['total_balance'] = float(result['total_balance']) if result else 0

        # Доходы от заказов за последние 30 дней (не системный заказ)
        cursor.execute("""
            SELECT COALESCE(SUM(Amount), 0) as order_income
            FROM Payments
            WHERE PaymentType IN ('Оплата', 'Предоплата')
                AND OrderID != %s
                AND PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, (system_order_id,))
        result = cursor.fetchone()
        summary['order_income'] = float(result['order_income']) if result else 0

        # Доходы (не от заказов) за последние 30 дней
        cursor.execute("""
            SELECT COALESCE(SUM(Amount), 0) as other_income
            FROM Payments
            WHERE OrderID = %s
                AND Notes LIKE '[ДОХОД]%'
                AND PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, (system_order_id,))
        result = cursor.fetchone()
        summary['other_income'] = float(result['other_income']) if result else 0

        # Расходы за последние 30 дней
        cursor.execute("""
            SELECT COALESCE(SUM(Amount), 0) as expense
            FROM Payments
            WHERE OrderID = %s
                AND Notes LIKE '[РАСХОД]%'
                AND PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, (system_order_id,))
        result = cursor.fetchone()
        summary['expense'] = float(result['expense']) if result else 0

        # Итого
        summary['total_income'] = summary['order_income'] + summary['other_income']
        summary['net_profit'] = summary['total_income'] - summary['expense']

        # Доходы по категориям (за последние 30 дней)
        cursor.execute("""
            SELECT 
                SUBSTRING_INDEX(SUBSTRING_INDEX(Notes, '][', -1), ']', 1) as category,
                COALESCE(SUM(Amount), 0) as total
            FROM Payments
            WHERE OrderID = %s
                AND Notes LIKE '[ДОХОД]%'
                AND PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY category
            ORDER BY total DESC
        """, (system_order_id,))
        summary['income_by_category'] = cursor.fetchall()

        # Расходы по категориям (за последние 30 дней)
        cursor.execute("""
            SELECT 
                SUBSTRING_INDEX(SUBSTRING_INDEX(Notes, '][', -1), ']', 1) as category,
                COALESCE(SUM(Amount), 0) as total
            FROM Payments
            WHERE OrderID = %s
                AND Notes LIKE '[РАСХОД]%'
                AND PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY category
            ORDER BY total DESC
        """, (system_order_id,))
        summary['expense_by_category'] = cursor.fetchall()

        return summary

    except Error as e:
        print(f"Ошибка получения финансовой сводки: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_all_payments_with_details(
        start_date: str = None,
        end_date: str = None,
        payment_type: str = None,
        payment_method: str = None,
        search_text: str = None,
        limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Получает список платежей с детальной информацией для отображения в таблице.
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        # Получаем ID системного заказа
        system_order_id = get_system_order_id()

        query = """
        SELECT 
            p.PaymentID,
            p.PaymentDate,
            p.Amount,
            p.PaymentMethod,
            p.PaymentType,
            p.ReceiptNumber,
            p.Notes as PaymentNotes,
            CONCAT(e.FirstName, ' ', e.LastName) as EmployeeName,
            p.EmployeeID,
            o.OrderID,
            o.OrderNumber,
            o.OrderType,
            o.Status as OrderStatus,
            CONCAT(c.FirstName, ' ', c.LastName) as ClientName,
            c.PhoneNumber as ClientPhone,
            c.Email as ClientEmail,
            o.DeviceType,
            o.DeviceBrand,
            o.DeviceModel,
            o.FinalAmount as OrderTotal,
            -- Определяем тип операции для отображения
            CASE 
                WHEN p.OrderID = %s AND p.Notes LIKE '[ДОХОД]%' THEN 'Доход'
                WHEN p.OrderID = %s AND p.Notes LIKE '[РАСХОД]%' THEN 'Расход'
                ELSE p.PaymentType
            END as DisplayType,
            -- Извлекаем категорию для доходов/расходов
            CASE 
                WHEN p.OrderID = %s AND p.Notes LIKE '[ДОХОД]%' THEN 
                    SUBSTRING_INDEX(SUBSTRING_INDEX(p.Notes, '][', -1), ']', 1)
                WHEN p.OrderID = %s AND p.Notes LIKE '[РАСХОД]%' THEN 
                    SUBSTRING_INDEX(SUBSTRING_INDEX(p.Notes, '][', -1), ']', 1)
                ELSE NULL
            END as Category
        FROM Payments p
        LEFT JOIN Orders o ON p.OrderID = o.OrderID
        LEFT JOIN Client c ON o.ClientID = c.ID
        LEFT JOIN ListEmployee e ON p.EmployeeID = e.EmployeeID
        WHERE 1=1
        """

        params = [system_order_id, system_order_id, system_order_id, system_order_id]

        if start_date:
            query += " AND DATE(p.PaymentDate) >= %s"
            params.append(start_date)

        if end_date:
            query += " AND DATE(p.PaymentDate) <= %s"
            params.append(end_date)

        if payment_method:
            query += " AND p.PaymentMethod = %s"
            params.append(payment_method)

        # Фильтр по типу платежа
        if payment_type:
            if payment_type == 'Доход':
                query += " AND p.OrderID = %s AND p.Notes LIKE '[ДОХОД]%'"
                params.append(system_order_id)
            elif payment_type == 'Расход':
                query += " AND p.OrderID = %s AND p.Notes LIKE '[РАСХОД]%'"
                params.append(system_order_id)
            else:
                query += " AND p.PaymentType = %s"
                params.append(payment_type)

        if search_text:
            query += """
                AND (
                    o.OrderNumber LIKE %s 
                    OR CONCAT(c.FirstName, ' ', c.LastName) LIKE %s
                    OR p.ReceiptNumber LIKE %s
                    OR p.Notes LIKE %s
                )
            """
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

        query += " ORDER BY p.PaymentDate DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения платежей: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

# ==================== РАБОТА С ПЛАТЕЖАМИ (ПОЛНЫЙ ФУНКЦИОНАЛ) ====================

def get_all_payments_with_details(
        start_date: str = None,
        end_date: str = None,
        payment_type: str = None,
        payment_method: str = None,
        search_text: str = None,
        limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Получает список платежей с детальной информацией для отображения в таблице.

    Аргументы:
        start_date: Начальная дата (YYYY-MM-DD)
        end_date: Конечная дата (YYYY-MM-DD)
        payment_type: Тип платежа ('Предоплата', 'Оплата', 'Возврат')
        payment_method: Метод оплаты ('Наличные', 'Карта', 'Перевод', 'Онлайн')
        search_text: Текст для поиска
        limit: Максимальное количество записей

    Returns:
        Список платежей с деталями
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            p.PaymentID,
            p.PaymentDate,
            p.Amount,
            p.PaymentMethod,
            p.PaymentType,
            p.ReceiptNumber,
            p.Notes as PaymentNotes,
            CONCAT(e.FirstName, ' ', e.LastName) as EmployeeName,
            p.EmployeeID,
            o.OrderID,
            o.OrderNumber,
            o.OrderType,
            o.Status as OrderStatus,
            CONCAT(c.FirstName, ' ', c.LastName) as ClientName,
            c.PhoneNumber as ClientPhone,
            c.Email as ClientEmail,
            o.DeviceType,
            o.DeviceBrand,
            o.DeviceModel,
            o.FinalAmount as OrderTotal
        FROM Payments p
        LEFT JOIN Orders o ON p.OrderID = o.OrderID
        LEFT JOIN Client c ON o.ClientID = c.ID
        LEFT JOIN ListEmployee e ON p.EmployeeID = e.EmployeeID
        WHERE 1=1
        """

        params = []

        if start_date:
            query += " AND DATE(p.PaymentDate) >= %s"
            params.append(start_date)

        if end_date:
            query += " AND DATE(p.PaymentDate) <= %s"
            params.append(end_date)

        if payment_type:
            query += " AND p.PaymentType = %s"
            params.append(payment_type)

        if payment_method:
            query += " AND p.PaymentMethod = %s"
            params.append(payment_method)

        if search_text:
            query += """
                AND (
                    o.OrderNumber LIKE %s 
                    OR CONCAT(c.FirstName, ' ', c.LastName) LIKE %s
                    OR p.ReceiptNumber LIKE %s
                    OR p.Notes LIKE %s
                )
            """
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

        query += " ORDER BY p.PaymentDate DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения платежей: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_financial_summary() -> Dict[str, Any]:
    """
    Получает сводную финансовую информацию (баланс, приход, расход).

    Returns:
        Словарь с финансовыми показателями
    """
    connection = get_crm_connection()
    if connection is None:
        return {}

    cursor = connection.cursor(dictionary=True)

    try:
        summary = {}

        # Общий баланс (сумма всех платежей)
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN PaymentType != 'Возврат' THEN Amount ELSE -Amount END), 0) as total_balance
            FROM Payments
        """)
        result = cursor.fetchone()
        summary['total_balance'] = float(result['total_balance']) if result else 0

        # Приход за последние 30 дней
        cursor.execute("""
            SELECT COALESCE(SUM(Amount), 0) as total_income
            FROM Payments
            WHERE PaymentType IN ('Оплата', 'Предоплата')
                AND PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        result = cursor.fetchone()
        summary['income_30days'] = float(result['total_income']) if result else 0

        # Расход за последние 30 дней (возвраты)
        cursor.execute("""
            SELECT COALESCE(SUM(Amount), 0) as total_expense
            FROM Payments
            WHERE PaymentType = 'Возврат'
                AND PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        result = cursor.fetchone()
        summary['expense_30days'] = float(result['total_expense']) if result else 0

        # Итого за период
        summary['total_30days'] = summary['income_30days'] - summary['expense_30days']

        # Статистика по методам оплаты
        cursor.execute("""
            SELECT 
                PaymentMethod,
                COUNT(*) as count,
                COALESCE(SUM(Amount), 0) as total
            FROM Payments
            WHERE PaymentDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY PaymentMethod
            ORDER BY total DESC
        """)
        summary['by_method'] = cursor.fetchall()

        # Ежедневная статистика за последние 7 дней
        cursor.execute("""
            SELECT 
                DATE(PaymentDate) as date,
                COALESCE(SUM(CASE WHEN PaymentType != 'Возврат' THEN Amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN PaymentType = 'Возврат' THEN Amount ELSE 0 END), 0) as expense
            FROM Payments
            WHERE PaymentDate >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(PaymentDate)
            ORDER BY date
        """)
        summary['daily_stats'] = cursor.fetchall()

        return summary

    except Error as e:
        print(f"Ошибка получения финансовой сводки: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def add_payment_with_validation(order_id: int, payment_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Добавляет платеж с валидацией суммы и обновлением статуса оплаты заказа.

    Аргументы:
        order_id: ID заказа
        payment_data: Данные платежа

    Returns:
        Кортеж (успех, сообщение)
    """
    connection = get_crm_connection()
    if connection is None:
        return False, "Нет подключения к базе данных"

    cursor = connection.cursor(dictionary=True)

    try:
        # Получаем информацию о заказе
        cursor.execute("""
            SELECT FinalAmount, IsPaid, Prepayment, TotalAmount, Discount
            FROM Orders WHERE OrderID = %s
        """, (order_id,))
        order = cursor.fetchone()

        if not order:
            return False, "Заказ не найден"

        amount = float(payment_data.get('amount', 0))
        payment_type = payment_data.get('payment_type', 'Оплата')

        # Получаем сумму уже внесенных платежей
        cursor.execute("""
            SELECT COALESCE(SUM(Amount), 0) as total_paid
            FROM Payments
            WHERE OrderID = %s AND PaymentType != 'Возврат'
        """, (order_id,))
        paid_result = cursor.fetchone()
        total_paid = float(paid_result['total_paid']) if paid_result else 0

        final_amount = float(order['FinalAmount'])

        # Валидация суммы
        if payment_type == 'Оплата' or payment_type == 'Предоплата':
            if total_paid + amount > final_amount:
                return False, f"Сумма оплаты превышает остаток долга. Остаток: {final_amount - total_paid:.2f} ₽"

        # Добавляем платеж
        cursor.execute("""
            INSERT INTO Payments (OrderID, Amount, PaymentMethod, PaymentType, 
                                ReceiptNumber, Notes, EmployeeID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id,
            amount,
            payment_data.get('payment_method', 'Наличные'),
            payment_type,
            payment_data.get('receipt_number'),
            payment_data.get('notes'),
            payment_data.get('employee_id')
        ))

        # Обновляем статус оплаты заказа
        cursor.execute("""
            SELECT COALESCE(SUM(Amount), 0) as total_paid
            FROM Payments
            WHERE OrderID = %s AND PaymentType != 'Возврат'
        """, (order_id,))
        new_total_paid = float(cursor.fetchone()['total_paid'])

        is_paid = new_total_paid >= final_amount
        cursor.execute("""
            UPDATE Orders SET IsPaid = %s WHERE OrderID = %s
        """, (is_paid, order_id))

        connection.commit()
        return True, "Платеж успешно добавлен"

    except Error as e:
        print(f"Ошибка добавления платежа: {e}")
        connection.rollback()
        return False, f"Ошибка базы данных: {e}"
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_order_payment_history(order_id: int) -> List[Dict[str, Any]]:
    """
    Получает историю платежей для конкретного заказа.

    Аргументы:
        order_id: ID заказа

    Returns:
        Список платежей
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                p.PaymentID,
                p.PaymentDate,
                p.Amount,
                p.PaymentMethod,
                p.PaymentType,
                p.ReceiptNumber,
                p.Notes,
                CONCAT(e.FirstName, ' ', e.LastName) as EmployeeName
            FROM Payments p
            LEFT JOIN ListEmployee e ON p.EmployeeID = e.EmployeeID
            WHERE p.OrderID = %s
            ORDER BY p.PaymentDate DESC
        """, (order_id,))

        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения истории платежей: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

# ==================== РАБОТА С ПЛАТЕЖАМИ (PAYMENTS) ====================

def add_payment_to_order(order_id: int, payment_data: Dict[str, Any]) -> bool:
    """
    Добавляет платеж к заказу.

    Аргументы:
        order_id: ID заказа
        payment_data: Данные платежа

    Returns:
        True если успешно, False если ошибка
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO Payments (OrderID, Amount, PaymentMethod, PaymentType, 
                                ReceiptNumber, Notes, EmployeeID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id,
            float(payment_data.get('amount', 0)),
            payment_data.get('payment_method', 'Наличные'),
            payment_data.get('payment_type', 'Оплата'),
            payment_data.get('receipt_number'),
            payment_data.get('notes'),
            payment_data.get('employee_id') or None
        ))

        connection.commit()
        return True

    except Error as e:
        print(f"Ошибка добавления платежа: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


# ==================== РАБОТА СО СКЛАДОМ (WAREHOUSE) ====================

def get_all_warehouse_items(
        category: str = None,
        brand: str = None,
        low_stock_only: bool = False,
        search: str = None
) -> List[Dict[str, Any]]:
    """
    Получает список всех товаров на складе с возможностью фильтрации.

    Аргументы:
        category: Фильтр по категории
        brand: Фильтр по бренду
        low_stock_only: Только товары с низким запасом
        search: Поиск по названию, коду или описанию

    Returns:
        Список товаров на складе с дополнительными вычисляемыми полями
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        # Основной запрос с вычисляемыми полями
        query = """
        SELECT 
            StockID,
            DetailCode,
            DetailName,
            Description,
            Category,
            Brand,
            CompatibleModels,
            CountInStock,
            MinStockLevel,
            Price,
            CostPrice,
            Supplier,
            WarrantyDays,
            Location,
            LastRestockDate,
            IsActive,
            -- Вычисляем прибыль с каждого товара
            (Price - CostPrice) as ProfitPerUnit,
            -- Вычисляем общую стоимость запасов
            (CountInStock * CostPrice) as TotalCostValue,
            -- Вычисляем общую потенциальную выручку
            (CountInStock * Price) as TotalPotentialRevenue,
            -- Статус запаса (текстовое описание)
            CASE 
                WHEN CountInStock <= 0 THEN 'Нет в наличии'
                WHEN CountInStock <= MinStockLevel THEN 'Мало'
                WHEN CountInStock <= MinStockLevel * 2 THEN 'Достаточно'
                ELSE 'Много'
            END as StockStatus
        FROM DetailStock
        WHERE 1=1
        """

        params = []

        # Только активные товары
        query += " AND IsActive = TRUE"

        if category:
            query += " AND Category = %s"
            params.append(category)

        if brand:
            query += " AND Brand = %s"
            params.append(brand)

        if low_stock_only:
            query += " AND CountInStock <= MinStockLevel"

        if search:
            query += """ AND (
                DetailName LIKE %s 
                OR DetailCode LIKE %s 
                OR Description LIKE %s
                OR Brand LIKE %s
                OR Category LIKE %s
                OR Supplier LIKE %s
            )"""
            search_pattern = f"%{search}%"
            params.extend([search_pattern] * 6)

        query += " ORDER BY Category, Brand, DetailName"

        cursor.execute(query, params)
        items = cursor.fetchall()

        # Обрабатываем совместимые модели (если они хранятся как JSON или текст)
        for item in items:
            if item.get('CompatibleModels'):
                try:
                    # Пробуем распарсить как JSON
                    import json
                    item['CompatibleModelsList'] = json.loads(item['CompatibleModels'])
                except:
                    # Если не JSON, разбиваем по запятой
                    item['CompatibleModelsList'] = [m.strip() for m in item['CompatibleModels'].split(',')]

        return items

    except Error as e:
        print(f"Ошибка получения товаров со склада: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_warehouse_item_detail(stock_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает детальную информацию о конкретном товаре.
    Включает статистику использования в заказах.

    Аргументы:
        stock_id: ID товара на складе

    Returns:
        Детальная информация о товаре или None
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            ds.*,
            -- Статистика использования в заказах
            (SELECT COUNT(*) FROM OrderDetails od 
             WHERE od.StockID = ds.StockID) as TimesOrdered,
            (SELECT SUM(Quantity) FROM OrderDetails od 
             WHERE od.StockID = ds.StockID) as TotalSold,
            -- Средняя цена продажи
            (SELECT AVG(UnitPrice) FROM OrderDetails od 
             WHERE od.StockID = ds.StockID) as AvgSellingPrice,
            -- Последняя дата продажи
            (SELECT MAX(o.OrderDate) 
             FROM OrderDetails od
             JOIN Orders o ON od.OrderID = o.OrderID
             WHERE od.StockID = ds.StockID) as LastSoldDate,
            -- Количество заказов ожидающих эту деталь
            (SELECT COUNT(*) 
             FROM OrderDetails od
             JOIN Orders o ON od.OrderID = o.OrderID
             WHERE od.StockID = ds.StockID 
               AND o.Status IN ('Ждут запчасти', 'В работе')) as WaitingOrders
        FROM DetailStock ds
        WHERE ds.StockID = %s
        """

        cursor.execute(query, (stock_id,))
        return cursor.fetchone()

    except Error as e:
        print(f"Ошибка получения деталей товара: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def update_warehouse_item(stock_id: int, item_data: Dict[str, Any]) -> bool:
    """
    Обновляет информацию о товаре на складе.

    Аргументы:
        stock_id: ID товара
        item_data: Новые данные

    Returns:
        True если успешно
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
        UPDATE DetailStock SET
            DetailCode = %s,
            DetailName = %s,
            Description = %s,
            Category = %s,
            Brand = %s,
            CompatibleModels = %s,
            CountInStock = %s,
            MinStockLevel = %s,
            Price = %s,
            CostPrice = %s,
            Supplier = %s,
            WarrantyDays = %s,
            Location = %s,
            LastRestockDate = %s,
            IsActive = %s
        WHERE StockID = %s
        """

        cursor.execute(query, (
            item_data.get('detail_code'),
            item_data.get('detail_name'),
            item_data.get('description', ''),
            item_data.get('category'),
            item_data.get('brand'),
            item_data.get('compatible_models'),
            item_data.get('count_in_stock', 0),
            item_data.get('min_stock_level', 5),
            item_data.get('price', 0),
            item_data.get('cost_price', 0),
            item_data.get('supplier'),
            item_data.get('warranty_days', 90),
            item_data.get('location'),
            item_data.get('last_restock_date'),
            item_data.get('is_active', True),
            stock_id
        ))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка обновления товара: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def create_warehouse_item(item_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает новый товар на складе.

    Аргументы:
        item_data: Данные товара

    Returns:
        ID созданного товара или None
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Генерируем код детали, если не указан
        if not item_data.get('detail_code'):
            import random
            import time
            category_prefix = item_data.get('category', 'PRT')[:3].upper()
            timestamp = int(time.time()) % 10000
            random_num = random.randint(100, 999)
            detail_code = f"{category_prefix}-{timestamp}-{random_num}"
        else:
            detail_code = item_data.get('detail_code')

        query = """
        INSERT INTO DetailStock (
            DetailCode, DetailName, Description, Category, Brand,
            CompatibleModels, CountInStock, MinStockLevel, Price,
            CostPrice, Supplier, WarrantyDays, Location, LastRestockDate,
            IsActive
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            detail_code,
            item_data.get('detail_name'),
            item_data.get('description', ''),
            item_data.get('category'),
            item_data.get('brand'),
            item_data.get('compatible_models'),
            item_data.get('count_in_stock', 0),
            item_data.get('min_stock_level', 5),
            item_data.get('price', 0),
            item_data.get('cost_price', 0),
            item_data.get('supplier'),
            item_data.get('warranty_days', 90),
            item_data.get('location'),
            item_data.get('last_restock_date'),
            item_data.get('is_active', True)
        ))

        new_id = cursor.lastrowid
        connection.commit()
        return new_id

    except Error as e:
        print(f"Ошибка создания товара: {e}")
        connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_warehouse_categories() -> List[str]:
    """
    Получает список всех уникальных категорий на складе.

    Returns:
        Список категорий
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT DISTINCT Category 
            FROM DetailStock 
            WHERE IsActive = TRUE 
            ORDER BY Category
        """)
        return [row[0] for row in cursor.fetchall() if row[0]]
    except Error as e:
        print(f"Ошибка получения категорий: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_warehouse_brands() -> List[str]:
    """
    Получает список всех уникальных брендов на складе.

    Returns:
        Список брендов
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT DISTINCT Brand 
            FROM DetailStock 
            WHERE IsActive = TRUE AND Brand IS NOT NULL
            ORDER BY Brand
        """)
        return [row[0] for row in cursor.fetchall() if row[0]]
    except Error as e:
        print(f"Ошибка получения брендов: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_warehouse_statistics() -> Dict[str, Any]:
    """
    Получает статистику по складу.

    Returns:
        Словарь со статистикой: общие показатели, топ категорий, топ брендов
    """
    connection = get_crm_connection()
    if connection is None:
        return {}

    cursor = connection.cursor(dictionary=True)

    try:
        stats = {}

        # Общая статистика
        cursor.execute("""
            SELECT 
                COUNT(*) as total_items,
                COUNT(DISTINCT Category) as total_categories,
                COUNT(DISTINCT Brand) as total_brands,
                SUM(CountInStock) as total_units,
                SUM(CountInStock * CostPrice) as total_investment,
                SUM(CountInStock * Price) as total_potential_revenue,
                SUM(CountInStock * Price) - SUM(CountInStock * CostPrice) as total_potential_profit,
                AVG(Price - CostPrice) as avg_margin,
                SUM(CASE WHEN CountInStock <= MinStockLevel THEN 1 ELSE 0 END) as low_stock_count,
                SUM(CASE WHEN CountInStock = 0 THEN 1 ELSE 0 END) as out_of_stock_count
            FROM DetailStock
            WHERE IsActive = TRUE
        """)
        stats.update(cursor.fetchone())

        # Топ категорий по стоимости
        cursor.execute("""
            SELECT 
                Category,
                COUNT(*) as item_count,
                SUM(CountInStock) as total_units,
                SUM(CountInStock * Price) as total_value
            FROM DetailStock
            WHERE IsActive = TRUE
            GROUP BY Category
            ORDER BY total_value DESC
            LIMIT 5
        """)
        stats['top_categories'] = cursor.fetchall()

        # Топ брендов по количеству
        cursor.execute("""
            SELECT 
                Brand,
                COUNT(*) as item_count,
                SUM(CountInStock) as total_units
            FROM DetailStock
            WHERE IsActive = TRUE AND Brand IS NOT NULL
            GROUP BY Brand
            ORDER BY total_units DESC
            LIMIT 5
        """)
        stats['top_brands'] = cursor.fetchall()

        return stats

    except Error as e:
        print(f"Ошибка получения статистики склада: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def restock_item(stock_id: int, quantity: int, purchase_price: float = None) -> bool:
    """
    Пополняет запас товара на складе.

    Аргументы:
        stock_id: ID товара
        quantity: Количество для добавления
        purchase_price: Новая закупочная цена (если изменилась)

    Returns:
        True если успешно
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        if purchase_price:
            # Обновляем количество и цену
            cursor.execute("""
                UPDATE DetailStock 
                SET CountInStock = CountInStock + %s,
                    CostPrice = %s,
                    LastRestockDate = CURDATE()
                WHERE StockID = %s
            """, (quantity, purchase_price, stock_id))
        else:
            # Только количество
            cursor.execute("""
                UPDATE DetailStock 
                SET CountInStock = CountInStock + %s,
                    LastRestockDate = CURDATE()
                WHERE StockID = %s
            """, (quantity, stock_id))

        connection.commit()
        return True

    except Error as e:
        print(f"Ошибка пополнения запаса: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


# ==================== РАБОТА С КОРЗИНОЙ (CART) ====================

def add_to_cart_db(user_id: int, cart_item: Dict[str, Any]) -> bool:
    """
    Добавляет товар в корзину в базе данных.

    Аргументы:
        user_id: ID пользователя
        cart_item: Данные товара (устройство, цена и т.д.)

    Returns:
        True если успешно, False если ошибка
    """
    connection = get_crm_connection()
    if connection is None:
        print("Ошибка: не удалось получить соединение с БД")
        return False

    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO Cart (UserID, DeviceType, DeviceBrand, DeviceModel, Reason, Price, Status)
        VALUES (%s, %s, %s, %s, %s, %s, 'active')
        """

        values = (
            user_id,
            cart_item.get('device_type', ''),
            cart_item.get('device_brand', ''),
            cart_item.get('device_model', ''),
            cart_item.get('reason', ''),
            float(cart_item.get('price', 0))
        )

        print(f"Добавление в корзину: {values}")
        cursor.execute(query, values)

        connection.commit()
        print(f"Успешно добавлено, ID: {cursor.lastrowid}")
        return True

    except Error as e:
        print(f"Ошибка добавления в корзину: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_user_cart_from_db(user_id: int) -> List[Dict[str, Any]]:
    """
    Получает корзину пользователя из базы данных.

    Аргументы:
        user_id: ID пользователя

    Returns:
        Список товаров в корзине
    """
    connection = get_crm_connection()
    if connection is None:
        print("Ошибка: не удалось получить соединение с БД")
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            CartID,
            DeviceType,
            DeviceBrand,
            DeviceModel,
            Reason,
            Price,
            DateAdded
        FROM Cart 
        WHERE UserID = %s AND Status = 'active'
        ORDER BY DateAdded DESC
        """

        print(f"Запрос корзины для пользователя ID: {user_id}")
        cursor.execute(query, (user_id,))

        results = cursor.fetchall()

        # Форматируем дату для отображения
        for item in results:
            if item.get('DateAdded'):
                item['DateAdded'] = item['DateAdded'].strftime('%Y-%m-%d %H:%M:%S')

        print(f"Найдено записей: {len(results)}")
        return results

    except Error as e:
        print(f"Ошибка получения корзины: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def clear_user_cart_db(user_id: int) -> bool:
    """
    Очищает корзину пользователя (мягкое удаление - меняет статус на 'removed').

    Аргументы:
        user_id: ID пользователя

    Returns:
        True если успешно, False если ошибка
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Cart 
            SET Status = 'removed' 
            WHERE UserID = %s AND Status = 'active'
        """, (user_id,))

        connection.commit()
        return True

    except Error as e:
        print(f"Ошибка очистки корзины: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def remove_from_cart_db(cart_id: int, user_id: int) -> bool:
    """
    Удаляет конкретный товар из корзины.

    Аргументы:
        cart_id: ID записи в корзине
        user_id: ID пользователя (для проверки принадлежности)

    Returns:
        True если успешно, False если ошибка
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Cart 
            SET Status = 'removed' 
            WHERE CartID = %s AND UserID = %s AND Status = 'active'
        """, (cart_id, user_id))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка удаления из корзины: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def move_cart_to_order(user_id: int) -> bool:
    """
    Перемещает товары из корзины в заказ (при оформлении).
    Меняет статус товаров на 'ordered'.

    Аргументы:
        user_id: ID пользователя

    Returns:
        True если успешно, False если ошибка
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Cart 
            SET Status = 'ordered' 
            WHERE UserID = %s AND Status = 'active'
        """, (user_id,))

        connection.commit()
        return True

    except Error as e:
        print(f"Ошибка оформления заказа: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_cart_statistics(user_id: int = None) -> Dict[str, Any]:
    """
    Получает статистику по корзине.

    Аргументы:
        user_id: ID пользователя (если None - общая статистика по всем)

    Returns:
        Словарь со статистикой
    """
    connection = get_crm_connection()
    if connection is None:
        return {}

    cursor = connection.cursor(dictionary=True)

    try:
        stats = {}

        if user_id:
            # Статистика для конкретного пользователя
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_items,
                    SUM(Price) as total_sum,
                    MAX(Price) as max_price,
                    MIN(Price) as min_price,
                    AVG(Price) as avg_price
                FROM Cart 
                WHERE UserID = %s AND Status = 'active'
            """, (user_id,))
        else:
            # Общая статистика по всем пользователям
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_items,
                    SUM(Price) as total_sum,
                    COUNT(DISTINCT UserID) as total_users
                FROM Cart 
                WHERE Status = 'active'
            """)

        result = cursor.fetchone()
        if result:
            stats.update(result)

        # Топ популярных устройств (для общей статистики)
        if not user_id:
            cursor.execute("""
                SELECT 
                    DeviceBrand,
                    COUNT(*) as count
                FROM Cart 
                WHERE Status = 'active'
                GROUP BY DeviceBrand
                ORDER BY count DESC
                LIMIT 5
            """)
            stats['top_brands'] = cursor.fetchall()

        return stats

    except Error as e:
        print(f"Ошибка получения статистики корзины: {e}")
        return {}
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


# ==================== РАБОТА С МАГАЗИНАМИ (SHOPS) ====================

def get_all_shops(only_active: bool = True, category: str = None, search: str = None) -> List[Dict[str, Any]]:
    """
    Получает список всех магазинов с возможностью фильтрации.

    Аргументы:
        only_active: Только активные магазины
        category: Фильтр по категории
        search: Поиск по названию или описанию

    Returns:
        Список магазинов
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            s.ShopID as id,
            s.Name as name,
            s.Category as category,
            s.URL as url,
            s.Description as description,
            s.Logo as logo,
            s.IsActive as is_active,
            s.CreatedDate as created_date,
            s.UpdatedDate as updated_date,
            CONCAT(e.FirstName, ' ', e.LastName) as created_by_name
        FROM Shops s
        LEFT JOIN ListEmployee e ON s.CreatedBy = e.EmployeeID
        WHERE 1=1
        """

        params = []

        if only_active:
            query += " AND s.IsActive = TRUE"

        if category:
            query += " AND s.Category = %s"
            params.append(category)

        if search:
            query += """ AND (s.Name LIKE %s OR s.Description LIKE %s OR s.Category LIKE %s)"""
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        query += " ORDER BY s.Name"

        cursor.execute(query, params)
        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения магазинов: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_shop_by_id(shop_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает магазин по ID.

    Аргументы:
        shop_id: ID магазина

    Returns:
        Данные магазина или None
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                ShopID as id,
                Name as name,
                Category as category,
                URL as url,
                Description as description,
                Logo as logo,
                IsActive as is_active,
                CreatedDate as created_date,
                CreatedBy as created_by
            FROM Shops 
            WHERE ShopID = %s
        """, (shop_id,))

        return cursor.fetchone()

    except Error as e:
        print(f"Ошибка получения магазина: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def create_shop(shop_data: Dict[str, Any], created_by: int = None) -> Optional[int]:
    """
    Создает новый магазин.

    Аргументы:
        shop_data: Данные магазина
        created_by: ID сотрудника, создавшего запись

    Returns:
        ID созданного магазина или None
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO Shops (Name, Category, URL, Description, Logo, CreatedBy)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            shop_data.get('name'),
            shop_data.get('category'),
            shop_data.get('url'),
            shop_data.get('description', ''),
            shop_data.get('logo'),
            created_by
        ))

        new_shop_id = cursor.lastrowid
        connection.commit()
        return new_shop_id

    except Error as e:
        print(f"Ошибка создания магазина: {e}")
        connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def update_shop(shop_id: int, shop_data: Dict[str, Any]) -> bool:
    """
    Обновляет данные магазина.

    Аргументы:
        shop_id: ID магазина
        shop_data: Новые данные

    Returns:
        True если успешно
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
        UPDATE Shops SET
            Name = %s,
            Category = %s,
            URL = %s,
            Description = %s,
            Logo = %s
        WHERE ShopID = %s
        """

        cursor.execute(query, (
            shop_data.get('name'),
            shop_data.get('category'),
            shop_data.get('url'),
            shop_data.get('description', ''),
            shop_data.get('logo'),
            shop_id
        ))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка обновления магазина: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def delete_shop(shop_id: int, hard_delete: bool = False) -> bool:
    """
    Удаляет магазин.

    Аргументы:
        shop_id: ID магазина
        hard_delete: Полное удаление (иначе только деактивация)

    Returns:
        True если успешно
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        if hard_delete:
            # Полное удаление из БД
            cursor.execute("DELETE FROM Shops WHERE ShopID = %s", (shop_id,))
        else:
            # Мягкое удаление (только деактивация)
            cursor.execute("UPDATE Shops SET IsActive = FALSE WHERE ShopID = %s", (shop_id,))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка удаления магазина: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_shop_categories() -> List[str]:
    """
    Получает список уникальных категорий магазинов.

    Returns:
        Список категорий
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT DISTINCT Category 
            FROM Shops 
            WHERE IsActive = TRUE 
            ORDER BY Category
        """)

        return [row[0] for row in cursor.fetchall()]

    except Error as e:
        print(f"Ошибка получения категорий: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_shop_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Ищет магазин по точному названию.

    Аргументы:
        name: Название магазина

    Returns:
        Данные магазина или None
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ShopID as id, Name as name
            FROM Shops 
            WHERE Name = %s
            LIMIT 1
        """, (name,))

        return cursor.fetchone()

    except Error as e:
        print(f"Ошибка поиска магазина: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def import_shops_from_json(json_data: List[Dict[str, Any]], created_by: int = None) -> Tuple[int, int]:
    """
    Импортирует магазины из JSON в БД.

    Аргументы:
        json_data: Данные из JSON
        created_by: ID создателя

    Returns:
        Кортеж (добавлено, обновлено)
    """
    added = 0
    updated = 0

    for shop in json_data:
        # Проверяем, существует ли магазин с таким названием
        existing = get_shop_by_name(shop.get('name'))

        if existing:
            # Обновляем существующий
            if update_shop(existing['id'], shop):
                updated += 1
        else:
            # Добавляем новый
            if create_shop(shop, created_by):
                added += 1

    return added, updated


# ==================== ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ ====================

def test_connection() -> bool:
    """
    Тестирует соединение с базой данных.
    Простой запрос SELECT 1 для проверки работоспособности.

    Returns:
        True если соединение работает
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return True
    except Error as e:
        print(f"Ошибка тестирования соединения: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if connection.is_connected():
            connection.close()


# ==================== БЛОК ТЕСТИРОВАНИЯ ====================
# Этот код выполняется только если файл запущен напрямую

if __name__ == "__main__":
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ db_crm.py")
    print("=" * 50)

    # Тест соединения
    conn_ok = test_connection()
    print(f"Соединение с БД: {'✅ OK' if conn_ok else '❌ FAILED'}")

    if conn_ok:
        # Тест получения ID заказа (замените на реальный номер из вашей БД)
        test_order_id = get_order_id_by_number("ORD-20260205-0004")
        print(f"ID заказа ORD-20260205-0004: {test_order_id}")

        if test_order_id:
            # Тест получения данных заказа
            order_data = get_order_for_edit_form(test_order_id)
            print(f"Данные заказа #{test_order_id}: {'✅ получены' if order_data else '❌ не получены'}")

        # Тест получения справочников
        print(f"Причин обращения: {len(get_all_appeal_reasons())}")
        print(f"Сотрудников: {len(get_all_employees())}")
        print(f"Типов услуг: {len(get_all_service_types())}")
        print(f"Товаров на складе: {len(get_all_stock_items())}")

        # Тест статистики склада
        warehouse_stats = get_warehouse_statistics()
        print(f"Статистика склада: {warehouse_stats.get('total_items', 0)} товаров, "
              f"{warehouse_stats.get('total_categories', 0)} категорий")

    print("=" * 50)


# ==================== РАБОТА С УВЕДОМЛЕНИЯМИ (NOTIFICATIONS) ====================

def create_notification(employee_id: int, title: str, message: str,
                        notification_type: str = 'info',
                        link_to: str = None,
                        link_type: str = None,
                        link_id: int = None) -> bool:
    """
    Создает уведомление для сотрудника.

    Аргументы:
        employee_id: ID сотрудника
        title: Заголовок уведомления
        message: Текст уведомления
        notification_type: Тип ('info', 'success', 'warning', 'error', 'order', 'stock', 'payment')
        link_to: Полная ссылка для перехода
        link_type: Тип ссылки (например: 'order', 'stock_item')
        link_id: ID связанного объекта

    Returns:
        True если успешно
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO Notifications (EmployeeID, Title, Message, Type, LinkTo, LinkType, LinkID)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            employee_id,
            title[:255],  # Ограничиваем длину
            message,
            notification_type,
            link_to,
            link_type,
            link_id
        ))

        connection.commit()
        return True

    except Error as e:
        print(f"Ошибка создания уведомления: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_user_notifications(employee_id: int, limit: int = 50, include_read: bool = False) -> List[Dict[str, Any]]:
    """
    Получает уведомления для сотрудника.

    Аргументы:
        employee_id: ID сотрудника
        limit: Максимальное количество уведомлений
        include_read: Включать прочитанные

    Returns:
        Список уведомлений
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
        SELECT 
            NotificationID,
            Title,
            Message,
            Type,
            IsRead,
            LinkTo,
            LinkType,
            LinkID,
            DATE_FORMAT(CreatedAt, '%%d.%%m.%%Y %%H:%%i') as CreatedAtFormatted,
            CreatedAt
        FROM Notifications
        WHERE EmployeeID = %s
        """

        params = [employee_id]

        if not include_read:
            query += " AND IsRead = 0"

        query += " ORDER BY CreatedAt DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения уведомлений: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_unread_notifications_count(employee_id: int) -> int:
    """
    Получает количество непрочитанных уведомлений для сотрудника.

    Аргументы:
        employee_id: ID сотрудника

    Returns:
        Количество непрочитанных уведомлений
    """
    connection = get_crm_connection()
    if connection is None:
        return 0

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) FROM Notifications 
            WHERE EmployeeID = %s AND IsRead = 0
        """, (employee_id,))

        return cursor.fetchone()[0]

    except Error as e:
        print(f"Ошибка получения количества уведомлений: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def mark_notification_as_read(notification_id: int, employee_id: int) -> bool:
    """
    Отмечает уведомление как прочитанное.

    Аргументы:
        notification_id: ID уведомления
        employee_id: ID сотрудника (для проверки)

    Returns:
        True если успешно
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Notifications 
            SET IsRead = 1 
            WHERE NotificationID = %s AND EmployeeID = %s
        """, (notification_id, employee_id))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка отметки уведомления: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def mark_all_notifications_as_read(employee_id: int) -> int:
    """
    Отмечает все уведомления сотрудника как прочитанные.

    Аргументы:
        employee_id: ID сотрудника

    Returns:
        Количество отмеченных уведомлений
    """
    connection = get_crm_connection()
    if connection is None:
        return 0

    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Notifications 
            SET IsRead = 1 
            WHERE EmployeeID = %s AND IsRead = 0
        """, (employee_id,))

        connection.commit()
        return cursor.rowcount

    except Error as e:
        print(f"Ошибка отметки всех уведомлений: {e}")
        connection.rollback()
        return 0
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def delete_notification(notification_id: int, employee_id: int) -> bool:
    """
    Удаляет уведомление.

    Аргументы:
        notification_id: ID уведомления
        employee_id: ID сотрудника (для проверки)

    Returns:
        True если успешно
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM Notifications 
            WHERE NotificationID = %s AND EmployeeID = %s
        """, (notification_id, employee_id))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка удаления уведомления: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_notification_by_id(notification_id: int, employee_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает уведомление по ID.

    Аргументы:
        notification_id: ID уведомления
        employee_id: ID сотрудника (для проверки)

    Returns:
        Данные уведомления или None
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM Notifications 
            WHERE NotificationID = %s AND EmployeeID = %s
        """, (notification_id, employee_id))

        return cursor.fetchone()

    except Error as e:
        print(f"Ошибка получения уведомления: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def create_notification_for_all_admins(title: str, message: str,
                                       notification_type: str = 'info',
                                       link_to: str = None,
                                       link_type: str = None,
                                       link_id: int = None) -> int:
    """
    Создает уведомление для всех администраторов и менеджеров.

    Аргументы:
        title: Заголовок
        message: Текст
        notification_type: Тип
        link_to: Ссылка
        link_type: Тип ссылки
        link_id: ID объекта

    Returns:
        Количество созданных уведомлений
    """
    connection = get_crm_connection()
    if connection is None:
        return 0

    cursor = connection.cursor()

    try:
        # Получаем всех сотрудников с ролями admin и manager
        cursor.execute("""
            SELECT EmployeeID FROM ListEmployee 
            WHERE IsActive = TRUE AND Role IN ('admin', 'manager')
        """)

        admins = cursor.fetchall()
        created_count = 0

        for admin in admins:
            if create_notification(
                    admin[0], title, message, notification_type,
                    link_to, link_type, link_id
            ):
                created_count += 1

        return created_count

    except Error as e:
        print(f"Ошибка создания уведомлений для админов: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def create_system_notifications_for_low_stock() -> int:
    """
    Создает уведомления о низком запасе товаров для ответственных сотрудников.

    Returns:
        Количество созданных уведомлений
    """
    connection = get_crm_connection()
    if connection is None:
        return 0

    cursor = connection.cursor(dictionary=True)

    try:
        # Получаем товары с низким запасом
        cursor.execute("""
            SELECT StockID, DetailName, DetailCode, CountInStock, MinStockLevel
            FROM DetailStock 
            WHERE IsActive = TRUE AND CountInStock <= MinStockLevel
        """)

        low_stock_items = cursor.fetchall()

        if not low_stock_items:
            return 0

        # Создаем уведомления для всех менеджеров склада
        created_count = 0

        for item in low_stock_items:
            title = f"Низкий запас: {item['DetailName']}"
            message = f"Товар '{item['DetailName']}' (код: {item['DetailCode']}) имеет запас {item['CountInStock']} шт. (минимальный: {item['MinStockLevel']} шт.)"

            created = create_notification_for_all_admins(
                title,
                message,
                'stock',
                f"/warehouse?stock_id={item['StockID']}",
                'stock_item',
                item['StockID']
            )
            created_count += created

        return created_count

    except Error as e:
        print(f"Ошибка создания уведомлений о низком запасе: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

def get_employee_active_status(email: str) -> Optional[bool]:
    """
    Проверяет, активен ли сотрудник (IsActive = 1).
    Возвращает:
        True  – если сотрудник активен
        False – если сотрудник существует, но заблокирован
        None  – если сотрудник не найден
    """
    connection = get_crm_connection()
    if connection is None:
        return None
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT IsActive FROM ListEmployee WHERE Email = %s",
            (email,)
        )
        result = cursor.fetchone()
        if result:
            return result[0] == 1
        return None
    except Error as e:
        print(f"Ошибка проверки активности сотрудника: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()