# -*- coding: utf-8 -*-
import mysql.connector
import bcrypt

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="sk28",
        password="Yes12345Yes.",
        database="SQL_IT_EcoSyttem_BD"
    )

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



