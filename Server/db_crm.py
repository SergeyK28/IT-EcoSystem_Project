# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error
from datetime import datetime


def get_crm_connection():
    """Создает соединение с базой данных для CRM"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="sk28",
            password="Yes12345Yes.",
            database="SQL_IT_EcoSyttem_BD",
            charset='utf8mb4'
        )
        return connection
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def get_orders_for_crm_table(filter_status=None, search_text=None):
    """
    Получает список заказов для таблицы CRM

    Args:
        filter_status: Фильтр по статусу (опционально)
        search_text: Текст для поиска (опционально)

    Returns:
        Список словарей с данными заказов для таблицы CRM
    """
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        # Основной запрос для получения данных заказов для таблицы CRM
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

        # Добавляем фильтр по статусу
        if filter_status and filter_status != "Все":
            query += " AND o.Status = %s"
            params.append(filter_status)

        # Добавляем поиск по тексту
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
        orders = cursor.fetchall()

        return orders

    except Error as e:
        print(f"Ошибка получения заказов для CRM таблицы: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_order_statuses():
    """Получает список всех возможных статусов заказов"""
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor()

    try:
        # Получаем значения ENUM из базы данных
        cursor.execute("""
            SELECT COLUMN_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'Orders' 
            AND COLUMN_NAME = 'Status'
        """)

        result = cursor.fetchone()
        if result:
            # Извлекаем значения из ENUM('value1','value2',...)
            enum_str = result[0]
            statuses = enum_str.replace("enum('", "").replace("')", "").replace("'", "").split(',')
            return statuses

        return []

    except Error as e:
        print(f"Ошибка получения статусов: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_employees():
    """Получает список сотрудников для выпадающих списков"""
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT EmployeeID, CONCAT(FirstName, ' ', LastName) as FullName 
            FROM ListEmployee 
            ORDER BY LastName, FirstName
        """)

        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения сотрудников: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_appeal_reasons():
    """Получает список причин обращения"""
    connection = get_crm_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ReasonID, ReasonName 
            FROM AppealReasons 
            ORDER BY ReasonName
        """)

        return cursor.fetchall()

    except Error as e:
        print(f"Ошибка получения причин обращения: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_device_types():
    """Получает список типов устройств (можно расширить)"""
    return [
        "Смартфон", "Ноутбук", "Планшет", "Телевизор",
        "Игровая приставка", "Фотоаппарат", "Пылесос",
        "Кофемашина", "Стиральная машина", "Холодильник"
    ]


def update_order_status(order_id, new_status):
    """Обновляет статус заказа"""
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE Orders 
            SET Status = %s 
            WHERE OrderID = %s
        """, (new_status, order_id))

        connection.commit()
        return cursor.rowcount > 0

    except Error as e:
        print(f"Ошибка обновления статуса: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def create_new_order(order_data):
    """
    Создает новый заказ в системе

    Args:
        order_data: словарь с данными заказа

    Returns:
        ID нового заказа или None при ошибке
    """
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor()

    try:
        # Основной запрос на создание заказа
        query = """
        INSERT INTO Orders (
            ClientID, OrderType, Status, ManagerID, ExecutorID,
            AppealReasonID, DeviceType, DeviceBrand, DeviceModel,
            DeviceAppearance, DeviceIMEI_SN
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        params = (
            order_data.get('client_id'),
            order_data.get('order_type', 'Платный'),
            order_data.get('status', 'Новая'),
            order_data.get('manager_id'),
            order_data.get('executor_id'),
            order_data.get('appeal_reason_id'),
            order_data.get('device_type'),
            order_data.get('device_brand'),
            order_data.get('device_model'),
            order_data.get('device_appearance'),
            order_data.get('device_imei_sn')
        )

        cursor.execute(query, params)
        connection.commit()

        return cursor.lastrowid

    except Error as e:
        print(f"Ошибка создания заказа: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()


def get_client_by_phone(phone_number):
    """Находит клиента по номеру телефона"""
    connection = get_crm_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ID, FirstName, LastName, Email, Birthdate
            FROM Client 
            WHERE PhoneNumber LIKE %s
            LIMIT 1
        """, (f"%{phone_number}%",))

        return cursor.fetchone()

    except Error as e:
        print(f"Ошибка поиска клиента: {e}")
        return None
    finally:
        cursor.close()
        connection.close()


def add_service_to_order(order_id, service_data):
    """Добавляет услугу к заказу"""
    connection = get_crm_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        query = """
        INSERT INTO ServicesProvided (
            OrderID, EmployeeID, ServiceTypeID, ServiceType
        ) VALUES (%s, %s, %s, %s)
        """

        params = (
            order_id,
            service_data.get('employee_id'),
            service_data.get('service_type_id'),
            service_data.get('service_type')
        )

        cursor.execute(query, params)
        connection.commit()

        return True

    except Error as e:
        print(f"Ошибка добавления услуги: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()


def get_order_statistics():
    """Получает статистику по заказам для дашборда"""
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
        cursor.close()
        connection.close()


def get_all_orders():
    """Получает все заказы (для совместимости)"""
    return get_orders_for_crm_table()


def search_orders(search_text):
    """Ищет заказы по тексту"""
    return get_orders_for_crm_table(search_text=search_text)