# -*- coding: utf-8 -*-
import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from mysql.connector import Error

# Находим корневую директорию проекта
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env'

# Загружаем .env с принудительной перезаписью
load_dotenv(ENV_PATH, override=True)

# Для отладки - проверим, загрузились ли переменные
print(f"Загрузка .env из: {ENV_PATH}")
print(f"DB_USER из os.environ: {os.environ.get('DB_USER')}")
print(f"DB_PASSWORD установлен: {'Да' if os.environ.get('DB_PASSWORD') else 'Нет'}")


def get_connection():
    """Получает соединение с БД"""
    try:
        # Берем переменные напрямую из окружения
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME', 'SQL_IT_EcoSyttem_BD'),
            'port': int(os.getenv('DB_PORT', 3306))
        }

        # Проверяем, что все необходимые параметры заданы
        if not config['user'] or not config['password']:
            raise ValueError("DB_USER или DB_PASSWORD не заданы в .env файле")

        # Закомментируйте эти строки или удалите
        # print("Параметры подключения:")
        # print(f"  host: {config['host']}")
        # print(f"  user: {config['user']}")
        # print(f"  database: {config['database']}")
        # print(f"  password: {'*' * len(config['password'])}")

        conn = mysql.connector.connect(**config)
        # print("✅ Подключение успешно!")  # Тоже можно закомментировать
        return conn

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        raise


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(hashed, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed.encode('utf-8'))


# Функция для регистрации нового пользователя
def register_user(first_name, last_name, login, password, email):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO Client (FirstName, LastName, Login, PasswordHash, Email)
            VALUES (%s, %s, %s, %s, %s)
        """, (first_name, last_name, login, hashed, email))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Ошибка регистрации: {err}")
        return False
    finally:
        cursor.close()
        conn.close()


# Функция для проверки логина и пароля пользователя
def check_user(login, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Client WHERE Login = %s", (login,))
        user = cursor.fetchone()
        if user is None or not check_password(user['PasswordHash'], password):
            return False
        return True
    finally:
        cursor.close()
        conn.close()


# Функция для изменения имени и фамилии пользователя
def update_name_surname_in_db(user_id, first_name, last_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE Client SET FirstName = %s, LastName = %s WHERE ID = %s;"
        cursor.execute(query, (first_name, last_name, user_id))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Ошибка обновления: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def update_birthdate_in_db(user_id, birthdate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE Client SET Birthdate = %s WHERE ID = %s;"
        cursor.execute(query, (birthdate, user_id))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Ошибка обновления даты рождения: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_user_id_by_login(login):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT ID FROM Client WHERE Login = %s", (login,))
        user = cursor.fetchone()
        if user:
            return user['ID']
        return None
    finally:
        cursor.close()
        conn.close()


def get_user_data_by_login(login):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT ID, FirstName, LastName FROM Client WHERE Login = %s", (login,))
        user = cursor.fetchone()
        if user:
            return user
        return None
    finally:
        cursor.close()
        conn.close()


def update_avatar_in_db(user_id, avatar_path):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE Client SET AvatarPath = %s WHERE ID = %s;"
        cursor.execute(query, (avatar_path, user_id))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Ошибка обновления аватара: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_avatar_path_by_user_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT AvatarPath FROM Client WHERE ID = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            return row["AvatarPath"]
        return None
    finally:
        cursor.close()
        conn.close()


def update_user_experience(user_id, experience_value):
    """Обновление уровня опыта пользователя"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET experience = %s WHERE id = %s",
            (experience_value, user_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка при обновлении опыта: {e}")
        return False


def get_user_experience(user_id):
    """Получение уровня опыта пользователя"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT experience FROM users WHERE id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0  # Возвращаем 0, если опыта нет
    except Exception as e:
        print(f"Ошибка при получении опыта: {e}")
        return 0


# ========== ФУНКЦИИ ПОИСКА ==========

def search_products_and_services(search_text: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Выполняет поиск товаров и услуг по тексту
    """
    conn = get_connection()
    if conn is None:
        return {'services': [], 'parts': [], 'categories': []}

    cursor = conn.cursor(dictionary=True)
    results = {'services': [], 'parts': [], 'categories': []}

    try:
        search_pattern = f"%{search_text}%"
        print(f"Поиск по тексту: '{search_text}'")  # Отладка

        # Поиск услуг
        cursor.execute("""
            SELECT 
                ServiceTypeID as id,
                ServiceDescription as name,
                BasePrice as price,
                Category as category,
                EstimatedTime as duration,
                'service' as type
            FROM ServiceTypes 
            WHERE IsActive = TRUE 
                AND (ServiceDescription LIKE %s 
                     OR Category LIKE %s)
            ORDER BY 
                CASE 
                    WHEN ServiceDescription LIKE %s THEN 1
                    ELSE 2
                END,
                ServiceDescription
            LIMIT 20
        """, (search_pattern, search_pattern, f"{search_text}%"))

        services = cursor.fetchall()
        results['services'] = services
        print(f"Найдено услуг: {len(services)}")  # Отладка

        # Поиск товаров на складе (запчасти)
        cursor.execute("""
            SELECT 
                StockID as id,
                DetailName as name,
                DetailCode as code,
                Price as price,
                Brand as brand,
                Category as category,
                CountInStock as stock,
                'part' as type
            FROM DetailStock 
            WHERE IsActive = TRUE 
                AND CountInStock > 0
                AND (DetailName LIKE %s 
                     OR DetailCode LIKE %s 
                     OR Brand LIKE %s 
                     OR Category LIKE %s)
            ORDER BY 
                CASE 
                    WHEN DetailName LIKE %s THEN 1
                    WHEN Brand LIKE %s THEN 2
                    ELSE 3
                END,
                DetailName
            LIMIT 20
        """, (search_pattern, search_pattern, search_pattern, search_pattern,
              f"{search_text}%", f"{search_text}%"))

        parts = cursor.fetchall()
        results['parts'] = parts
        print(f"Найдено товаров: {len(parts)}")  # Отладка

        # Поиск категорий
        cursor.execute("""
            SELECT DISTINCT Category as name, 'category' as type
            FROM ServiceTypes 
            WHERE IsActive = TRUE AND Category LIKE %s
            UNION
            SELECT DISTINCT Category, 'category'
            FROM DetailStock 
            WHERE IsActive = TRUE AND Category LIKE %s
            LIMIT 10
        """, (search_pattern, search_pattern))

        categories = cursor.fetchall()
        results['categories'] = categories
        print(f"Найдено категорий: {len(categories)}")  # Отладка

        print(f"Всего результатов: {len(services) + len(parts) + len(categories)}")  # Отладка
        return results

    except Error as e:
        print(f"Ошибка поиска: {e}")
        return {'services': [], 'parts': [], 'categories': []}
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_popular_searches(limit: int = 5) -> List[str]:
    """
    Получает популярные поисковые запросы
    """
    # Для начала вернем статические данные
    # Позже можно добавить таблицу SearchHistory
    popular = [
        "ремонт телефона",
        "замена экрана",
        "ноутбук",
        "аккумулятор",
        "диагностика"
    ]
    return popular[:limit]


def save_search_query(query: str, user_id: int = None) -> bool:
    """
    Сохраняет поисковый запрос в историю

    Args:
        query: Поисковый запрос
        user_id: ID пользователя (если авторизован)

    Returns:
        True если успешно
    """
    # Пока просто логируем, потом можно добавить таблицу
    print(f"Поисковый запрос от user_id={user_id}: {query}")
    return True


def get_search_history(user_id: int = None, limit: int = 10) -> List[str]:
    """
    Получает историю поисковых запросов
    """
    # Пока вернем пустой список
    return []


def add_to_favorites(user_id: int, item_type: str, item_id: int, item_name: str,
                     item_price: float, item_category: str = None, notes: str = None) -> bool:
    """
    Добавляет элемент в избранное пользователя

    Args:
        user_id: ID пользователя
        item_type: Тип элемента ('service' или 'part')
        item_id: ID элемента
        item_name: Название элемента
        item_price: Цена
        item_category: Категория
        notes: Заметки

    Returns:
        True если успешно добавлено, False если ошибка или уже в избранном
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Favorites (UserID, ItemType, ItemID, ItemName, ItemPrice, ItemCategory, Notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, item_type, item_id, item_name, item_price, item_category, notes))
        conn.commit()
        print(f"✅ Добавлено в избранное: {item_name}")
        return True
    except mysql.connector.IntegrityError:
        # Элемент уже в избранном
        print(f"ℹ️ Элемент уже в избранном: {item_name}")
        return False
    except mysql.connector.Error as err:
        print(f"❌ Ошибка добавления в избранное: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def remove_from_favorites(user_id: int, favorite_id: int) -> bool:
    """
    Удаляет элемент из избранного по ID записи
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM Favorites 
            WHERE FavoriteID = %s AND UserID = %s
        """, (favorite_id, user_id))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            print(f"✅ Удалено из избранного, ID: {favorite_id}")
        return success
    except mysql.connector.Error as err:
        print(f"❌ Ошибка удаления из избранного: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def remove_from_favorites_by_item(user_id: int, item_type: str, item_id: int) -> bool:
    """
    Удаляет элемент из избранного по типу и ID элемента
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM Favorites 
            WHERE UserID = %s AND ItemType = %s AND ItemID = %s
        """, (user_id, item_type, item_id))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            print(f"✅ Удалено из избранного: type={item_type}, id={item_id}")
        return success
    except mysql.connector.Error as err:
        print(f"❌ Ошибка удаления из избранного: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_user_favorites(user_id: int) -> List[Dict[str, Any]]:
    """
    Получает все избранные элементы пользователя
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                FavoriteID,
                ItemType,
                ItemID,
                ItemName,
                ItemPrice,
                ItemCategory,
                DATE_FORMAT(DateAdded, '%d.%m.%Y %H:%i') as DateAddedFormatted,
                Notes
            FROM Favorites 
            WHERE UserID = %s
            ORDER BY DateAdded DESC
        """, (user_id,))

        favorites = cursor.fetchall()
        print(f"📋 Найдено избранных элементов: {len(favorites)}")
        return favorites
    except mysql.connector.Error as err:
        print(f"❌ Ошибка получения избранного: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def is_in_favorites(user_id: int, item_type: str, item_id: int) -> bool:
    """
    Проверяет, находится ли элемент в избранном у пользователя
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) FROM Favorites 
            WHERE UserID = %s AND ItemType = %s AND ItemID = %s
        """, (user_id, item_type, item_id))

        count = cursor.fetchone()[0]
        return count > 0
    except mysql.connector.Error as err:
        print(f"❌ Ошибка проверки избранного: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_favorite_by_id(user_id: int, favorite_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает информацию о конкретном элементе избранного по ID
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM Favorites 
            WHERE FavoriteID = %s AND UserID = %s
        """, (favorite_id, user_id))

        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"❌ Ошибка получения элемента избранного: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def clear_all_favorites(user_id: int) -> bool:
    """
    Очищает всё избранное пользователя
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM Favorites WHERE UserID = %s
        """, (user_id,))
        conn.commit()
        count = cursor.rowcount
        print(f"✅ Очищено избранное: удалено {count} элементов")
        return True
    except mysql.connector.Error as err:
        print(f"❌ Ошибка очистки избранного: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_favorites_count(user_id: int) -> int:
    """
    Получает количество элементов в избранном пользователя
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) FROM Favorites WHERE UserID = %s
        """, (user_id,))

        count = cursor.fetchone()[0]
        return count
    except mysql.connector.Error as err:
        print(f"❌ Ошибка получения количества избранного: {err}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_favorites_by_category(user_id: int, category: str) -> List[Dict[str, Any]]:
    """
    Получает избранные элементы пользователя по категории
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM Favorites 
            WHERE UserID = %s AND ItemCategory = %s
            ORDER BY DateAdded DESC
        """, (user_id, category))

        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"❌ Ошибка получения избранного по категории: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_favorites_by_type(user_id: int, item_type: str) -> List[Dict[str, Any]]:
    """
    Получает избранные элементы пользователя по типу (service/part)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM Favorites 
            WHERE UserID = %s AND ItemType = %s
            ORDER BY DateAdded DESC
        """, (user_id, item_type))

        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"❌ Ошибка получения избранного по типу: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_user_statistics(user_id):
    """
    Получает статистику пользователя из базы данных
    Возвращает словарь со статистикой
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Получаем количество заказов пользователя
        cursor.execute("""
            SELECT COUNT(*) as orders_count 
            FROM Orders 
            WHERE ClientID = %s
        """, (user_id,))
        orders_result = cursor.fetchone()
        orders_count = orders_result['orders_count'] if orders_result else 0

        # Получаем дату регистрации для расчета дней
        cursor.execute("""
            SELECT RegistrationDate 
            FROM Client 
            WHERE ID = %s
        """, (user_id,))
        reg_result = cursor.fetchone()

        days_with_us = 0
        if reg_result and reg_result['RegistrationDate']:
            from datetime import datetime
            reg_date = reg_result['RegistrationDate']
            if isinstance(reg_date, datetime):
                days_with_us = (datetime.now() - reg_date).days
            else:
                # Если это строка, конвертируем
                try:
                    if isinstance(reg_date, str):
                        reg_date = datetime.strptime(reg_date, '%Y-%m-%d %H:%M:%S')
                        days_with_us = (datetime.now() - reg_date).days
                except:
                    days_with_us = 0

        # Получаем количество избранного (если есть таблица Favorites)
        favorites_count = 0
        try:
            # Проверяем существование таблицы Favorites
            cursor.execute("""
                SELECT COUNT(*) as table_exists
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() AND table_name = 'Favorites'
            """)
            table_check = cursor.fetchone()

            if table_check and table_check['table_exists'] > 0:
                cursor.execute("""
                    SELECT COUNT(*) as fav_count 
                    FROM Favorites 
                    WHERE UserID = %s
                """, (user_id,))
                fav_result = cursor.fetchone()
                favorites_count = fav_result['fav_count'] if fav_result else 0
        except Exception as e:
            print(f"Ошибка при проверке таблицы Favorites: {e}")
            favorites_count = 0

        # Получаем бонусные баллы (сумма всех оплаченных заказов * 0.05)
        cursor.execute("""
            SELECT COALESCE(SUM(FinalAmount), 0) as total_spent
            FROM Orders 
            WHERE ClientID = %s AND IsPaid = 1
        """, (user_id,))
        spent_result = cursor.fetchone()

        # Исправление: конвертируем Decimal в float или int
        if spent_result and spent_result['total_spent']:
            total_spent = float(spent_result['total_spent'])  # Конвертируем Decimal в float
            bonus_points = int(total_spent * 0.05)  # Теперь можно умножать
        else:
            bonus_points = 0

        return {
            'orders_count': orders_count,
            'favorites_count': favorites_count,
            'days_with_us': days_with_us,
            'bonus_points': bonus_points
        }

    except Exception as e:
        print(f"❌ Ошибка получения статистики пользователя: {e}")
        import traceback
        traceback.print_exc()
        return {
            'orders_count': 0,
            'favorites_count': 0,
            'days_with_us': 0,
            'bonus_points': 0
        }
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def get_user_info(user_id):
    """
    Получает полную информацию о пользователе
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ID, Login, FirstName, LastName, Email, PhoneNumber, 
                   RegistrationDate, AvatarPath, Birthdate
            FROM Client 
            WHERE ID = %s
        """, (user_id,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"❌ Ошибка получения информации пользователя: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def get_user_orders_count(user_id):
    """
    Получает количество заказов пользователя
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM Orders WHERE ClientID = %s
        """, (user_id,))
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"❌ Ошибка получения количества заказов: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def get_user_registration_date(user_id):
    """
    Получает дату регистрации пользователя
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT RegistrationDate FROM Client WHERE ID = %s
        """, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"❌ Ошибка получения даты регистрации: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def get_user_bonus_points(user_id):
    """
    Рассчитывает бонусные баллы пользователя (5% от суммы оплаченных заказов)
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(FinalAmount), 0) FROM Orders 
            WHERE ClientID = %s AND IsPaid = 1
        """, (user_id,))
        total_spent = cursor.fetchone()[0]
        return int(total_spent * 0.05)  # 5% бонусами
    except Exception as e:
        print(f"❌ Ошибка расчета бонусов: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def update_email_in_db(user_id, new_email):
    """Обновление email пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Проверяем, не занят ли email другим пользователем
        cursor.execute("SELECT ID FROM Client WHERE Email = %s AND ID != %s", (new_email, user_id))
        if cursor.fetchone():
            return False

        cursor.execute("UPDATE Client SET Email = %s WHERE ID = %s", (new_email, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Ошибка обновления email: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def update_phone_in_db(user_id, new_phone):
    """Обновление номера телефона пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Client SET PhoneNumber = %s WHERE ID = %s", (new_phone, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Ошибка обновления телефона: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def update_password_in_db(user_id, current_password, new_password):
    """Обновление пароля пользователя"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Получаем текущий хеш пароля
        cursor.execute("SELECT PasswordHash FROM Client WHERE ID = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return False

        # Проверяем текущий пароль
        if not check_password(user['PasswordHash'], current_password):
            return False

        # Хешируем новый пароль
        new_hash = hash_password(new_password)

        # Обновляем пароль
        cursor.execute("UPDATE Client SET PasswordHash = %s WHERE ID = %s", (new_hash, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        print(f"Ошибка обновления пароля: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ========== УВЕДОМЛЕНИЯ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========

def create_user_notification(user_id: int, title: str, message: str,
                             notification_type: str = 'info',
                             link_to: str = None, link_type: str = None,
                             link_id: int = None) -> bool:
    """
    Создает уведомление для пользователя
    """
    conn = get_connection()
    if conn is None:
        return False

    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO UserNotifications (UserID, Title, Message, Type, LinkTo, LinkType, LinkID)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, title[:255], message, notification_type,
                               link_to, link_type, link_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка создания уведомления: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_user_notifications(user_id: int, limit: int = 50, include_read: bool = False) -> List[Dict[str, Any]]:
    """
    Получает уведомления пользователя
    """
    conn = get_connection()
    if conn is None:
        return []

    cursor = conn.cursor(dictionary=True)

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
        FROM UserNotifications
        WHERE UserID = %s
        """
        params = [user_id]

        if not include_read:
            query += " AND IsRead = 0"

        query += " ORDER BY CreatedAt DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка получения уведомлений: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def get_unread_notifications_count(user_id: int) -> int:
    """
    Получает количество непрочитанных уведомлений пользователя
    """
    conn = get_connection()
    if conn is None:
        return 0

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*) FROM UserNotifications 
            WHERE UserID = %s AND IsRead = 0
        """, (user_id,))
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"Ошибка получения количества уведомлений: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def mark_notification_as_read(notification_id: int, user_id: int) -> bool:
    """
    Отмечает уведомление как прочитанное
    """
    conn = get_connection()
    if conn is None:
        return False

    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE UserNotifications 
            SET IsRead = 1 
            WHERE NotificationID = %s AND UserID = %s
        """, (notification_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Ошибка отметки уведомления: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def mark_all_notifications_as_read(user_id: int) -> int:
    """
    Отмечает все уведомления пользователя как прочитанные
    """
    conn = get_connection()
    if conn is None:
        return 0

    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE UserNotifications 
            SET IsRead = 1 
            WHERE UserID = %s AND IsRead = 0
        """, (user_id,))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Ошибка отметки всех уведомлений: {e}")
        conn.rollback()
        return 0
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()


def delete_notification(notification_id: int, user_id: int) -> bool:
    """
    Удаляет уведомление
    """
    conn = get_connection()
    if conn is None:
        return False

    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM UserNotifications 
            WHERE NotificationID = %s AND UserID = %s
        """, (notification_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Ошибка удаления уведомления: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn.is_connected():
            conn.close()

def get_user_active_status(login_or_email):
    """
    Проверяет, активен ли пользователь (IsActive = 1).
    Возвращает:
        True  – если пользователь активен
        False – если пользователь существует, но заблокирован
        None  – если пользователь не найден
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT IsActive FROM Client WHERE Login = %s OR Email = %s",
            (login_or_email, login_or_email)
        )
        user = cursor.fetchone()
        if user:
            return user['IsActive'] == 1
        return None
    finally:
        cursor.close()
        conn.close()