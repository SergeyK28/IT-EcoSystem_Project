# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush
from PyQt5.QtWidgets import QDialog, QMessageBox, QGraphicsDropShadowEffect
import sys
import os
import bcrypt
from datetime import datetime, timedelta

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server import db_crm


class EmployeeLoginDialog(QDialog):
    """Диалог авторизации для сотрудников (стилизованный под authorization_window)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.employee_data = None
        self.login_attempts = 0
        self.max_attempts = 5
        self.setup_ui()
        self.setModal(True)

    def setup_ui(self):
        self.setObjectName("EmployeeLoginDialog")
        self.setWindowTitle("IT-EcoSystem CRM - Вход для сотрудников")
        self.setFixedSize(550, 450)

        # Основной стиль как в authorization_window
        self.setStyleSheet("""
            QDialog {
                background-color: rgb(47, 47, 47);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QLineEdit {
                background-color: rgb(60, 60, 60);
                color: rgb(255, 255, 255);
                padding: 8px;
                border: 1px solid rgb(103, 155, 118);
                border-radius: 4px;
                font-size: 12pt;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid rgb(103, 155, 118);
            }
            QLineEdit::placeholder {
                color: rgb(150, 150, 150);
            }
            QPushButton {
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12pt;
                min-height: 30px;
            }
            QPushButton#loginBtn {
                background-color: rgb(103, 155, 118);
                color: rgb(255, 255, 255);
            }
            QPushButton#loginBtn:hover {
                background-color: rgb(123, 175, 138);
            }
            QPushButton#loginBtn:pressed {
                background-color: rgb(83, 135, 98);
            }
            QPushButton#cancelBtn {
                background-color: rgb(119, 118, 123);
                color: rgb(255, 255, 255);
            }
            QPushButton#cancelBtn:hover {
                background-color: rgb(139, 138, 143);
            }
            QPushButton#cancelBtn:pressed {
                background-color: rgb(99, 98, 103);
            }
            QPushButton#showPasswordBtn {
                background-color: rgb(60, 60, 60);
                border: 1px solid rgb(103, 155, 118);
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                min-width: 30px;
            }
            QPushButton#showPasswordBtn:hover {
                background-color: rgb(80, 80, 80);
            }
            QPushButton#showPasswordBtn:checked {
                background-color: rgb(103, 155, 118);
            }
        """)

        # Основной layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(15)

        # Заголовок
        title_label = QtWidgets.QLabel("CRM ДЛЯ СОТРУДНИКОВ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: rgb(103, 155, 118);
            padding: 10px;
            border-bottom: 2px solid rgb(103, 155, 118);
        """)
        main_layout.addWidget(title_label)

        # Иконка
        icon_label = QtWidgets.QLabel("IT-EcoSystem CRM")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            font-size: 40px;
            color: rgb(103, 155, 118);
            padding: 8px;
        """)
        main_layout.addWidget(icon_label)

        # Email
        email_label = QtWidgets.QLabel("Email сотрудника:")
        email_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        main_layout.addWidget(email_label)

        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Введите рабочий email")
        main_layout.addWidget(self.email_input)

        # Пароль
        password_label = QtWidgets.QLabel("Пароль:")
        password_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        main_layout.addWidget(password_label)

        # Контейнер для поля пароля и кнопки показа
        password_container = QtWidgets.QHBoxLayout()
        password_container.setSpacing(5)

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        password_container.addWidget(self.password_input)

        self.show_password_btn = QtWidgets.QPushButton("👁️")
        self.show_password_btn.setObjectName("showPasswordBtn")
        self.show_password_btn.setFixedSize(40, 40)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.setCursor(Qt.PointingHandCursor)
        self.show_password_btn.toggled.connect(self.toggle_password_visibility)
        password_container.addWidget(self.show_password_btn)

        main_layout.addLayout(password_container)

        # Информация о попытках
        self.attempts_label = QtWidgets.QLabel("")
        self.attempts_label.setStyleSheet("color: rgb(255, 100, 100); font-size: 9pt;")
        self.attempts_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.attempts_label)

        # Добавляем растяжку
        main_layout.addStretch()

        # Кнопки
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(15)

        self.login_btn = QtWidgets.QPushButton("Войти в CRM")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.attempt_login)
        button_layout.addWidget(self.login_btn)

        self.cancel_btn = QtWidgets.QPushButton("Отмена")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

        # Подключаем Enter
        self.email_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.attempt_login)

        # Добавляем тень для окна (опционально)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        self.shadow.setOffset(0, 5)
        self.setGraphicsEffect(self.shadow)

    def toggle_password_visibility(self, checked):
        """Переключение видимости пароля"""
        if checked:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.show_password_btn.setText("🔒")
        else:
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
            self.show_password_btn.setText("👁️")

    def attempt_login(self):
        """Попытка входа"""
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        # Проверяем блокировку
        if self.check_if_locked(email):
            QMessageBox.critical(self, "Аккаунт заблокирован",
                                 "Слишком много неудачных попыток. Аккаунт заблокирован на 30 минут.")
            return

        # Проверяем учетные данные
        employee = self.verify_employee(email, password)

        if employee:
            # Успешный вход
            self.employee_data = employee
            self.update_last_login(employee['EmployeeID'])
            self.accept()
        else:
            # Неудачная попытка
            self.handle_failed_attempt(email)

    def verify_employee(self, email, password):
        """Проверка учетных данных сотрудника"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
                return None

            cursor = connection.cursor(dictionary=True)

            # Ищем сотрудника по email
            cursor.execute("""
                SELECT EmployeeID, FirstName, LastName, Email, Position, Role,
                       PasswordHash, IsActive
                FROM ListEmployee 
                WHERE Email = %s AND IsActive = TRUE
            """, (email,))

            employee = cursor.fetchone()
            cursor.close()
            connection.close()

            if not employee:
                return None

            # Проверяем пароль
            stored_hash = employee.get('PasswordHash')
            if not stored_hash:
                return None

            # Используем bcrypt для проверки пароля
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                # Убираем хеш из возвращаемых данных
                employee.pop('PasswordHash', None)
                return employee

            return None

        except Exception as e:
            print(f"Ошибка проверки сотрудника: {e}")
            return None

    def check_if_locked(self, email):
        """Проверяет, заблокирован ли аккаунт"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return False

            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT LockedUntil FROM ListEmployee 
                WHERE Email = %s AND IsActive = TRUE
            """, (email,))

            result = cursor.fetchone()
            cursor.close()
            connection.close()

            if result and result['LockedUntil']:
                if result['LockedUntil'] > datetime.now():
                    return True
            return False

        except Exception as e:
            print(f"Ошибка проверки блокировки: {e}")
            return False

    def handle_failed_attempt(self, email):
        """Обработка неудачной попытки входа"""
        self.login_attempts += 1
        remaining = self.max_attempts - self.login_attempts

        if remaining <= 0:
            self.lock_account(email)
            self.attempts_label.setText("❌ Аккаунт заблокирован на 30 минут")
            self.login_btn.setEnabled(False)

            # Таймер для разблокировки
            QTimer.singleShot(1800000, self.unlock_account)  # 30 минут
        else:
            self.attempts_label.setText(f"⚠️ Осталось попыток: {remaining}")
            QMessageBox.warning(self, "Ошибка входа",
                                f"Неверный email или пароль!\nОсталось попыток: {remaining}")

    def lock_account(self, email):
        """Блокирует аккаунт"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor()
            locked_until = datetime.now() + timedelta(minutes=30)
            cursor.execute("""
                UPDATE ListEmployee 
                SET LockedUntil = %s, LoginAttempts = 0
                WHERE Email = %s
            """, (locked_until, email))
            connection.commit()
            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Ошибка блокировки аккаунта: {e}")

    def unlock_account(self):
        """Разблокирует аккаунт"""
        self.login_attempts = 0
        self.attempts_label.setText("")
        self.login_btn.setEnabled(True)
        QMessageBox.information(self, "Аккаунт разблокирован",
                                "Аккаунт разблокирован. Можете повторить попытку входа.")

    def update_last_login(self, employee_id):
        """Обновляет дату последнего входа"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor()
            cursor.execute("""
                UPDATE ListEmployee 
                SET LastLogin = NOW(), LoginAttempts = 0, LockedUntil = NULL
                WHERE EmployeeID = %s
            """, (employee_id,))
            connection.commit()
            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Ошибка обновления last_login: {e}")

    def get_employee_data(self):
        """Возвращает данные авторизованного сотрудника"""
        return self.employee_data

    def mousePressEvent(self, event):
        """Для перетаскивания окна (опционально)"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Для перетаскивания окна (опционально)"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()