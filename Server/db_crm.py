# -*- coding: utf-8 -*-
import mysql.connector
from PyQt5.QtWidgets import QMessageBox
from mysql.connector import Error, pooling
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import os
from dotenv import load_dotenv
from pathlib import Path

# Находим корневую директорию проекта
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env'

# Загружаем .env с принудительной перезаписью
load_dotenv(ENV_PATH, override=True)


class Config:
    # База данных - берем напрямую из os.environ
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME', 'SQL_IT_EcoSyttem_BD')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))

    @classmethod
    def validate(cls):
        """Проверяет, что все необходимые параметры заданы"""
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


class DatabaseConnectionPool:
    _instance = None
    _connection_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
            cls._instance._init_pool()
        return cls._instance

    def _init_pool(self):
        """Инициализирует пул соединений"""
        try:
            # Проверяем конфигурацию перед созданием пула
            Config.validate()

            self._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="crm_pool",
                pool_size=5,
                pool_reset_session=True,
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT,
                charset='utf8mb4',
                autocommit=False
            )
            print("✅ Пул соединений с БД инициализирован")
        except Exception as e:
            print(f"❌ Ошибка инициализации пула соединений: {e}")
            self._connection_pool = None

    def get_connection(self):
        """Получает соединение из пула"""
        if self._connection_pool:
            try:
                return self._connection_pool.get_connection()
            except Error as e:
                print(f"Ошибка получения соединения из пула: {e}")
        return None

# Создаем глобальный экземпляр пула соединений
db_pool = DatabaseConnectionPool()

def get_crm_connection():
    """Получает соединение с базой данных"""
    return db_pool.get_connection()

def get_order_id_by_number(order_number: str) -> Optional[int]:
    """
    Получает ID заказа по его номеру

    Args:
        order_number: Номер заказа (например: ORD-20260205-0004)

    Returns:
        ID заказа или None если не найден
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Ищем ID заказа по номеру
        cursor.execute("SELECT OrderID FROM Orders WHERE OrderNumber = %s", (order_number,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # Если не нашли, пробуем извлечь ID из номера
        if order_number and order_number.startswith('ORD-'):
            parts = order_number.split('-')
            if len(parts) >= 3:
                try:
                    return int(parts[2].lstrip('0'))  # Убираем ведущие нули
                except ValueError:
                    pass

        return None

    except Error as e:
        print(f"Ошибка получения ID заказа: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_order_for_edit_form(order_id: int) -> Dict[str, Any]:
    """
    Получает полные данные заказа для формы редактирования

    Args:
        order_id: ID заказа

    Returns:
        Словарь с данными заказа
    """
    connection = get_crm_connection()
    if connection is None:
        return {}

    cursor = connection.cursor(dictionary=True)

    try:
        # Основной запрос для получения данных заказа
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

            -- Менеджер
            m.EmployeeID as ManagerID,
            m.FirstName as ManagerFirstName,
            m.LastName as ManagerLastName,
            CONCAT(m.FirstName, ' ', m.LastName) as ManagerFullName,
            m.PhoneNumber as ManagerPhone,
            m.Email as ManagerEmail,

            -- Исполнитель
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

            -- Предоплата и платежи
            (SELECT COALESCE(SUM(Amount), 0) FROM Payments 
             WHERE OrderID = o.OrderID AND PaymentType = 'Предоплата') as PrepaymentTotal,

            (SELECT COALESCE(SUM(Amount), 0) FROM Payments WHERE OrderID = o.OrderID) as AllPaymentsTotal,

            -- Статистика
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
            # Загружаем детали (запчасти)
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

            # Загружаем услуги
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

            # Загружаем комментарии
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

            # Загружаем историю статусов
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
    Обновляет заказ из формы редактирования

    Args:
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
        # 1. Обновляем основную информацию заказа
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

        # Преобразуем даты
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

        # 2. Обновляем детали (запчасти)
        # Удаляем старые детали, которые не входят в новый список
        existing_details = []
        for detail in details_data:
            if detail.get('order_detail_id'):
                existing_details.append(detail['order_detail_id'])

        if existing_details:
            cursor.execute("""
                DELETE FROM OrderDetails 
                WHERE OrderID = %s AND OrderDetailID NOT IN (%s)
            """ % (order_id, ','.join(map(str, existing_details))))
        else:
            cursor.execute("DELETE FROM OrderDetails WHERE OrderID = %s", (order_id,))

        # Добавляем/обновляем детали
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

                # Обновляем количество на складе
                cursor.execute("""
                    UPDATE DetailStock 
                    SET CountInStock = CountInStock - %s
                    WHERE StockID = %s
                """, (detail.get('quantity', 1), detail.get('stock_id')))

        # 3. Обновляем услуги
        # Удаляем старые услуги, которые не входят в новый список
        existing_services = []
        for service in services_data:
            if service.get('order_service_id'):
                existing_services.append(service['order_service_id'])

        if existing_services:
            cursor.execute("""
                DELETE FROM OrderServices 
                WHERE OrderID = %s AND OrderServiceID NOT IN (%s)
            """ % (order_id, ','.join(map(str, existing_services))))
        else:
            cursor.execute("DELETE FROM OrderServices WHERE OrderID = %s", (order_id,))

        # Добавляем/обновляем услуги
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

        # 4. Добавляем комментарий об обновлении
        if order_data.get('update_comment'):
            cursor.execute("""
                INSERT INTO OrderComments (OrderID, EmployeeID, CommentText, IsInternal)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                order_data.get('updated_by', 1),
                f"Заказ обновлен: {order_data.get('update_comment')}",
                True
            ))

        # 5. Записываем изменение статуса в историю
        cursor.execute("""
            SELECT Status FROM Orders WHERE OrderID = %s
        """, (order_id,))
        old_status_result = cursor.fetchone()

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

        connection.commit()
        return True

    except Error as e:
        print(f"Ошибка обновления заказа: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()


def get_all_appeal_reasons() -> List[Dict[str, Any]]:
    """Получает все причины обращения"""
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
    """Получает всех сотрудников"""
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
    """Получает все типы услуг"""
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ServiceTypeID, ServiceDescription, BasePrice, Category, EstimatedTime
            FROM ServiceTypes 
            WHERE IsActive = TRUE 
            ORDER BY ServiceDescription
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


def get_all_stock_items() -> List[Dict[str, Any]]:
    """Получает все товары со склада"""
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


def get_orders_for_crm_table(filter_status: str = None, search_text: str = None) -> List[Dict[str, Any]]:
    """
    Получает список заказов для таблицы CRM

    Args:
        filter_status: Фильтр по статусу
        search_text: Текст для поиска

    Returns:
        Список заказов
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
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
        WHERE 1=1
        """

        params = []

        if filter_status and filter_status != "Все":
            query += " AND o.Status = %s"
            params.append(filter_status)

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
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern] * 8)

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


def search_clients(search_term: str) -> List[Dict[str, Any]]:
    """Ищет клиентов по имени, телефону или email"""
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
            LIMIT 20
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

def add_payment_to_order(order_id: int, payment_data: Dict[str, Any]) -> bool:
    """Добавляет платеж к заказу"""
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


def get_order_statistics() -> Dict[str, Any]:
    """Получает статистику по заказам"""
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

        # Заказы по типам
        cursor.execute("""
            SELECT OrderType, COUNT(*) as count 
            FROM Orders 
            GROUP BY OrderType
        """)
        stats['by_type'] = {row['OrderType']: row['count'] for row in cursor.fetchall()}

        # Заказы за последние 7 дней
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


def test_connection() -> bool:
    """Тестирует соединение с базой данных"""
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


if __name__ == "__main__":
    # Тестирование модуля
    print("Тестирование модуля db_crm.py")
    print(f"Соединение с БД: {'OK' if test_connection() else 'FAILED'}")

    # Тестируем получение ID заказа
    test_order_id = get_order_id_by_number("ORD-20260205-0004")
    print(f"ID заказа ORD-20260205-0004: {test_order_id}")

    if test_order_id:
        # Тестируем получение данных заказа
        order_data = get_order_for_edit_form(test_order_id)
        print(f"Данные заказа #{test_order_id}: {'получены' if order_data else 'не получены'}")

    # Тестируем получение списков
    print(f"Причин обращения: {len(get_all_appeal_reasons())}")
    print(f"Сотрудников: {len(get_all_employees())}")
    print(f"Типов услуг: {len(get_all_service_types())}")
    print(f"Товаров на складе: {len(get_all_stock_items())}")


def create_new_client(client_data: Dict[str, Any]) -> Optional[int]:
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Генерируем логин из email
        email = client_data.get('email', '')
        first_name = client_data.get('first_name', '')
        last_name = client_data.get('last_name', '')

        if email:
            login = email.split('@')[0]
        elif first_name and last_name:
            login = f"{first_name.lower()}.{last_name.lower()}"
        else:
            import random
            login = f"client{random.randint(10000, 99999)}"

        # Проверяем уникальность логина
        cursor.execute("SELECT COUNT(*) FROM Client WHERE Login = %s", (login,))
        count = cursor.fetchone()[0]
        if count > 0:
            # Добавляем цифры если логин уже существует
            import random
            login = f"{login}{random.randint(100, 999)}"

        # Вариант 1: Используем bcrypt (рекомендуется)
        try:
            import bcrypt
            # Генерируем соль и хеш пароля
            temp_password = "TempPass123!"
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), salt)

            # Преобразуем bytes в строку для хранения
            password_hash_str = password_hash.decode('utf-8')

        except ImportError:
            # Вариант 2: Используем SHA256 и обрезаем до 60 символов
            import hashlib
            import secrets
            temp_password = secrets.token_urlsafe(8)
            # Создаем хеш и обрезаем до 60 символов
            full_hash = hashlib.sha256(temp_password.encode()).hexdigest()
            password_hash_str = full_hash[:60]  # Обрезаем до 60 символов

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


def create_new_order(order_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает новый заказ в базе данных

    Args:
        order_data: Словарь с данными нового заказа

    Returns:
        ID созданного заказа или None при ошибке
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Генерируем номер заказа
        import random
        import time
        order_number = f"ORD-{time.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        # Запрос на создание нового заказа
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
        if estimated_completion:
            # Если дата передана как строка, конвертируем
            if isinstance(estimated_completion, str):
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

        new_order_id = cursor.lastrowid

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

        # Возвращаем номер заказа для удобства
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

def get_all_service_types_for_order() -> List[Dict[str, Any]]:
    """Получает все типы услуг для добавления в заказ"""
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


def get_all_stock_items_for_order() -> List[Dict[str, Any]]:
    """Получает все товары со склада для добавления в заказ"""
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


def create_new_order_with_services_parts(order_data: Dict[str, Any]) -> Optional[int]:
    """
    Создает новый заказ с услугами и запчастями

    Args:
        order_data: Словарь с данными нового заказа, включая services_list и parts_list

    Returns:
        ID созданного заказа или None при ошибке
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Генерируем номер заказа
        import random
        import time
        from datetime import datetime

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
            # Извлекаем номер из последнего заказа
            last_number = int(last_order[0].split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        order_number = f"ORD-{current_date}-{new_number:04d}"

        # Запрос на создание нового заказа
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

        # Добавляем услуги
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

        # Добавляем запчасти
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

            # Обновляем количество на складе
            cursor.execute("""
                UPDATE DetailStock 
                SET CountInStock = CountInStock - %s
                WHERE StockID = %s
            """, (part.get('quantity', 1), part.get('stock_id')))

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
        print(f"Ошибка создания заказа с услугами и запчастями: {e}")
        connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()

def add_to_cart_db(user_id: int, cart_item: Dict[str, Any]) -> bool:
    """
    Добавляет товар в корзину в базе данных

    Args:
        user_id: ID пользователя
        cart_item: Данные товара

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
    Получает корзину пользователя из базы данных

    Args:
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
        # Простой запрос без форматирования даты
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
        print(f"SQL запрос: {query}")

        cursor.execute(query, (user_id,))

        results = cursor.fetchall()

        # Форматируем дату в Python
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
    Очищает корзину пользователя (мягкое удаление - меняет статус)

    Args:
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
    Удаляет конкретный товар из корзины

    Args:
        cart_id: ID записи в корзине
        user_id: ID пользователя (для проверки)

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
    Перемещает товары из корзины в заказ (при оформлении)

    Args:
        user_id: ID пользователя

    Returns:
        True если успешно, False если ошибка
    """
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        # Меняем статус товаров в корзине на 'ordered'
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
    Получает статистику по корзине

    Args:
        user_id: ID пользователя (если None - общая статистика)

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
            # Общая статистика
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

        # Топ популярных устройств
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

def get_client_orders(client_id: int) -> List[Dict[str, Any]]:
    """
    Получает список заказов для конкретного клиента

    Args:
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

def open_customers(self):
    """Открывает окно управления клиентами"""
    try:
        from Handlers.employee_customers import CustomersDialog
        customers_dialog = CustomersDialog(self.PB_Customers)
        customers_dialog.exec_()
    except ImportError as e:
        print(f"Ошибка импорта модуля клиентов: {e}")
        QMessageBox.warning(self.PB_Customers, "Функция недоступна",
                           "Модуль управления клиентами временно недоступен")
    except Exception as e:
        print(f"Ошибка открытия окна клиентов: {e}")
        QMessageBox.critical(self.PB_Customers, "Ошибка",
                           f"Не удалось открыть окно клиентов: {e}")

def get_all_shops(only_active: bool = True, category: str = None, search: str = None) -> List[Dict[str, Any]]:
    """
    Получает список всех магазинов

    Args:
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
    Получает магазин по ID

    Args:
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
    Создает новый магазин

    Args:
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
    Обновляет данные магазина

    Args:
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
    Удаляет магазин

    Args:
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
            cursor.execute("DELETE FROM Shops WHERE ShopID = %s", (shop_id,))
        else:
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
    Получает список уникальных категорий магазинов

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


def import_shops_from_json(json_data: List[Dict[str, Any]], created_by: int = None) -> Tuple[int, int]:
    """
    Импортирует магазины из JSON в БД

    Args:
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


def get_shop_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Ищет магазин по названию

    Args:
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