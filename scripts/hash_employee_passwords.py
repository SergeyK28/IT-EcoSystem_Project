#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bcrypt
import mysql.connector
import sys
import os
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server.config import Config


def hash_password(password):
    """Хеширует пароль с помощью bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def add_real_employee():
    """Добавляет настоящего сотрудника"""
    print("\n=== ДОБАВЛЕНИЕ НАСТОЯЩЕГО СОТРУДНИКА ===\n")

    # Ввод данных сотрудника
    first_name = input("Имя: ").strip()
    last_name = input("Фамилия: ").strip()
    email = input("Email: ").strip()
    password = input("Пароль: ").strip()
    position = input("Должность: ").strip()
    role = input("Роль (admin/manager/technician): ").strip().lower()

    if role not in ['admin', 'manager', 'technician']:
        role = 'technician'  # По умолчанию

    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )

        cursor = connection.cursor()

        # Проверяем, существует ли уже такой email
        cursor.execute("SELECT EmployeeID FROM ListEmployee WHERE Email = %s", (email,))
        existing = cursor.fetchone()

        if existing:
            print(f"❌ Сотрудник с email {email} уже существует!")
            return False

        # Создаем нового сотрудника
        hashed = hash_password(password)
        cursor.execute("""
            INSERT INTO ListEmployee 
            (FirstName, LastName, Email, PasswordHash, Position, Role, IsActive)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, (first_name, last_name, email, hashed, position, role))

        employee_id = cursor.lastrowid
        connection.commit()

        print(f"\n✅ Сотрудник успешно добавлен!")
        print(f"ID сотрудника: {employee_id}")
        print(f"Email: {email}")
        print(f"Должность: {position}")
        print(f"Роль: {role}")

        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def list_employees():
    """Показывает список всех сотрудников"""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT EmployeeID, FirstName, LastName, Email, Position, Role, IsActive
            FROM ListEmployee
            ORDER BY EmployeeID
        """)

        employees = cursor.fetchall()

        print("\n=== СПИСОК СОТРУДНИКОВ ===\n")
        for emp in employees:
            status = "✅ Активен" if emp['IsActive'] else "❌ Неактивен"
            print(f"ID: {emp['EmployeeID']}")
            print(f"Имя: {emp['FirstName']} {emp['LastName']}")
            print(f"Email: {emp['Email']}")
            print(f"Должность: {emp['Position']}")
            print(f"Роль: {emp['Role']}")
            print(f"Статус: {status}")
            print("-" * 40)

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def remove_test_employees():
    """Удаляет тестовых сотрудников"""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )

        cursor = connection.cursor()

        # Список тестовых email'ов для удаления
        test_emails = [
            'admin@it-ecosystem.ru',
            'ivan.petrov@it-ecosystem.ru',
            'petr.sidorov@it-ecosystem.ru'
        ]

        for email in test_emails:
            cursor.execute("DELETE FROM ListEmployee WHERE Email = %s", (email,))
            if cursor.rowcount > 0:
                print(f"✅ Удален тестовый сотрудник: {email}")

        connection.commit()

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def update_employee_password():
    """Обновляет пароль сотрудника"""
    try:
        emp_id = input("ID сотрудника: ").strip()
        new_password = input("Новый пароль: ").strip()

        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )

        cursor = connection.cursor()
        hashed = hash_password(new_password)

        cursor.execute("""
            UPDATE ListEmployee 
            SET PasswordHash = %s 
            WHERE EmployeeID = %s
        """, (hashed, emp_id))

        connection.commit()
        print(f"✅ Пароль для сотрудника ID {emp_id} обновлен")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    while True:
        print("\n" + "=" * 50)
        print("УПРАВЛЕНИЕ СОТРУДНИКАМИ")
        print("=" * 50)
        print("1. Добавить настоящего сотрудника")
        print("2. Показать список сотрудников")
        print("3. Удалить тестовых сотрудников")
        print("4. Обновить пароль сотрудника")
        print("5. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            add_real_employee()
        elif choice == "2":
            list_employees()
        elif choice == "3":
            confirm = input("Вы уверены, что хотите удалить всех тестовых сотрудников? (да/нет): ")
            if confirm.lower() == 'да':
                remove_test_employees()
        elif choice == "4":
            update_employee_password()
        elif choice == "5":
            print("До свидания!")
            break
        else:
            print("❌ Неверный выбор")