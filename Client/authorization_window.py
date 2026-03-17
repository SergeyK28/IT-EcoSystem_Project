# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette, QPixmap, QIcon
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QCheckBox, QFrame, QMessageBox, QDialog

from identification_window import IdenDialog
from profil_window import Ui_profil
from Server.db import check_user, get_user_data_by_login, hash_password, get_connection
from session_manager import session
import random
import string


class PasswordLineEdit(QLineEdit):
    """Поле ввода пароля с кнопкой показа/скрытия"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(50)

        # Устанавливаем стили
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                padding: 0 50px 0 20px;
                font-size: 15px;
                font-weight: 400;
                selection-background-color: #4CAF50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #333333;
            }
            QLineEdit:hover:not(:focus) {
                background-color: #353535;
                border: 2px solid #454545;
            }
            QLineEdit::placeholder {
                color: #808080;
                font-style: italic;
            }
        """)

        # Добавляем тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # Создаем кнопку показа/скрытия пароля
        self.toggle_btn = QPushButton("👁", self)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #808080;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                color: #4CAF50;
            }
            QPushButton:pressed {
                color: #45a049;
            }
        """)

        # Подключаем кнопку
        self.toggle_btn.clicked.connect(self.toggle_visibility)

        # Устанавливаем режим пароля по умолчанию
        self.setEchoMode(QLineEdit.Password)
        self.password_visible = False

    def resizeEvent(self, event):
        """Переопределяем resizeEvent для позиционирования кнопки"""
        super().resizeEvent(event)
        # Размещаем кнопку справа
        btn_x = self.width() - self.toggle_btn.width() - 10
        btn_y = (self.height() - self.toggle_btn.height()) // 2
        self.toggle_btn.move(btn_x, btn_y)

    def toggle_visibility(self):
        """Переключение видимости пароля"""
        if self.password_visible:
            self.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("👁")
            self.password_visible = False
        else:
            self.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("👁‍🗨")
            self.password_visible = True


class ModernLineEdit(QLineEdit):
    """Современное поле ввода с анимацией"""

    def __init__(self, placeholder="", icon=None, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                padding: 0 20px;
                font-size: 15px;
                font-weight: 400;
                selection-background-color: #4CAF50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #333333;
            }
            QLineEdit:hover:not(:focus) {
                background-color: #353535;
                border: 2px solid #454545;
            }
            QLineEdit::placeholder {
                color: #808080;
                font-style: italic;
            }
        """)

        # Добавляем тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernButton(QPushButton):
    """Современная кнопка с анимацией"""

    def __init__(self, text="", primary=True, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(55)
        self.setCursor(Qt.PointingHandCursor)

        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #45a049, stop:1 #3d8b40);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3d8b40, stop:1 #357a38);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: #b0b0b0;
                    border: 2px solid #4a4a4a;
                    border-radius: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #454545;
                    color: white;
                    border: 2px solid #4CAF50;
                }
                QPushButton:pressed {
                    background-color: #353535;
                }
            """)


class ForgotPasswordDialog(QDialog):
    """Диалог для восстановления пароля с современным дизайном"""

    def __init__(self, parent=None):
        super(ForgotPasswordDialog, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.current_user_id = None
        self.verification_code = None
        self.setupUi()

    def setupUi(self):
        self.setObjectName("ForgotPasswordDialog")
        self.resize(450, 500)

        # Главный контейнер с тенью и фоном
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 450, 500)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 30px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Основная тень
        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(30)
        main_shadow.setColor(QColor(0, 0, 0, 150))
        main_shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(main_shadow)

        # Основной layout
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # ===== ЗАГОЛОВОК С КНОПКОЙ ЗАКРЫТИЯ =====
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Кнопка закрытия
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        self.btn_close.clicked.connect(self.reject)

        # Заголовок
        title_label = QLabel("🔐 Восстановление пароля")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        # Логотип/иконка
        logo_label = QLabel("🔄")
        logo_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 28px;
            }
        """)

        header_layout.addWidget(self.btn_close)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(logo_label)

        layout.addLayout(header_layout)

        # ===== ИНФОРМАЦИОННОЕ СООБЩЕНИЕ =====
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(76, 175, 80, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(76, 175, 80, 0.3);
                padding: 15px;
            }
        """)

        info_layout = QVBoxLayout(info_frame)

        info_text = QLabel("📧 Введите email или логин для получения кода подтверждения")
        info_text.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setWordWrap(True)

        info_layout.addWidget(info_text)
        layout.addWidget(info_frame)

        # ===== ПОЛЯ ВВОДА =====
        # Email/логин
        self.email_input = ModernLineEdit("Email или логин")
        layout.addWidget(self.email_input)

        # Код подтверждения (скрыт)
        self.code_input = ModernLineEdit("Код подтверждения")
        self.code_input.hide()
        layout.addWidget(self.code_input)

        # Новый пароль (скрыт) - используем PasswordLineEdit
        self.new_password_input = PasswordLineEdit("Новый пароль")
        self.new_password_input.hide()
        layout.addWidget(self.new_password_input)

        # Подтверждение пароля (скрыт) - используем PasswordLineEdit
        self.confirm_password_input = PasswordLineEdit("Подтвердите пароль")
        self.confirm_password_input.hide()
        layout.addWidget(self.confirm_password_input)

        # Индикатор сложности пароля (скрыт)
        self.password_strength_frame = QFrame()
        self.password_strength_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.password_strength_frame.hide()

        strength_layout = QVBoxLayout(self.password_strength_frame)

        strength_label = QLabel("Сложность пароля:")
        strength_label.setStyleSheet("color: #b0b0b0; font-size: 13px;")

        self.strength_bar = QFrame()
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 3px;
            }
        """)

        self.strength_indicator = QFrame(self.strength_bar)
        self.strength_indicator.setGeometry(0, 0, 0, 6)
        self.strength_indicator.setStyleSheet("""
            QFrame {
                background-color: #ff4444;
                border-radius: 3px;
            }
        """)

        self.strength_text = QLabel("Минимум 6 символов")
        self.strength_text.setStyleSheet("color: #ff4444; font-size: 12px;")
        self.strength_text.setAlignment(Qt.AlignRight)

        strength_layout.addWidget(strength_label)
        strength_layout.addWidget(self.strength_bar)
        strength_layout.addWidget(self.strength_text)

        layout.addWidget(self.password_strength_frame)

        # Растягивающийся элемент
        layout.addStretch()

        # ===== КНОПКИ =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.send_code_btn = ModernButton("📧 Отправить код", True)
        self.verify_code_btn = ModernButton("✓ Проверить код", True)
        self.verify_code_btn.hide()
        self.reset_password_btn = ModernButton("🔄 Сменить пароль", True)
        self.reset_password_btn.hide()
        self.cancel_btn = ModernButton("✕ Отмена", False)

        button_layout.addWidget(self.send_code_btn)
        button_layout.addWidget(self.verify_code_btn)
        button_layout.addWidget(self.reset_password_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # Подключение сигналов
        self.send_code_btn.clicked.connect(self.send_verification_code)
        self.verify_code_btn.clicked.connect(self.verify_code)
        self.reset_password_btn.clicked.connect(self.reset_password)
        self.cancel_btn.clicked.connect(self.reject)

        # Подключаем проверку пароля
        self.new_password_input.textChanged.connect(self.check_password_strength)

    def generate_verification_code(self):
        """Генерирует 6-значный код подтверждения"""
        return ''.join(random.choices(string.digits, k=6))

    def find_user_by_login_or_email(self, login_or_email):
        """Поиск пользователя по логину или email"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Сначала ищем по логину
            cursor.execute("SELECT ID, Login, Email FROM Client WHERE Login = %s", (login_or_email,))
            user = cursor.fetchone()

            # Если не нашли, ищем по email
            if not user:
                cursor.execute("SELECT ID, Login, Email FROM Client WHERE Email = %s", (login_or_email,))
                user = cursor.fetchone()

            return user
        finally:
            cursor.close()
            conn.close()

    def send_verification_code(self):
        """Отправляет код подтверждения на email пользователя"""
        login_or_email = self.email_input.text().strip()

        if not login_or_email:
            self.show_custom_message("Ошибка", "❌ Введите email или логин!", "error")
            return

        # Поиск пользователя
        user = self.find_user_by_login_or_email(login_or_email)

        if not user:
            self.show_custom_message("Ошибка", "❌ Пользователь с таким логином или email не найден!", "error")
            return

        # Сохраняем ID пользователя
        self.current_user_id = user['ID']

        # Генерируем код подтверждения
        self.verification_code = self.generate_verification_code()

        # Здесь должна быть отправка email
        self.show_custom_message("Код подтверждения",
                                 f"✅ Ваш код подтверждения: {self.verification_code}\n\n"
                                 f"(В реальном приложении код будет отправлен на {user['Email']})",
                                 "success")

        # Переключаем интерфейс на ввод кода
        self.email_input.setEnabled(False)
        self.send_code_btn.hide()

        self.code_input.show()
        self.verify_code_btn.show()
        self.cancel_btn.setText("← Назад")

    def verify_code(self):
        """Проверяет введенный код подтверждения"""
        entered_code = self.code_input.text().strip()

        if not entered_code:
            self.show_custom_message("Ошибка", "❌ Введите код подтверждения!", "error")
            return

        if entered_code == self.verification_code:
            # Код верный - показываем поля для нового пароля
            self.code_input.setEnabled(False)
            self.verify_code_btn.hide()

            self.new_password_input.show()
            self.confirm_password_input.show()
            self.password_strength_frame.show()
            self.reset_password_btn.show()
            self.cancel_btn.setText("✕ Отмена")
        else:
            self.show_custom_message("Ошибка", "❌ Неверный код подтверждения!", "error")

    def check_password_strength(self, password):
        """Проверка сложности пароля с визуальной индикацией"""
        strength = 0
        width = self.strength_bar.width()

        if len(password) >= 6:
            strength += 25
        if any(c.isupper() for c in password):
            strength += 25
        if any(c.islower() for c in password):
            strength += 25
        if any(c in "!@#$%^&*()_+-=[]{};:,.<>?" for c in password):
            strength += 25

        self.strength_indicator.setFixedWidth(int(width * (strength / 100)) if width > 0 else 0)

        if strength < 25:
            self.strength_indicator.setStyleSheet("background-color: #ff4444; border-radius: 3px;")
            self.strength_text.setText("⚠️ Слишком простой пароль")
            self.strength_text.setStyleSheet("color: #ff4444; font-size: 12px;")
        elif strength < 50:
            self.strength_indicator.setStyleSheet("background-color: #ffaa44; border-radius: 3px;")
            self.strength_text.setText("⚠️ Слабый пароль")
            self.strength_text.setStyleSheet("color: #ffaa44; font-size: 12px;")
        elif strength < 75:
            self.strength_indicator.setStyleSheet("background-color: #ffff44; border-radius: 3px;")
            self.strength_text.setText("✓ Средний пароль")
            self.strength_text.setStyleSheet("color: #ffff44; font-size: 12px;")
        else:
            self.strength_indicator.setStyleSheet("background-color: #44ff44; border-radius: 3px;")
            self.strength_text.setText("✅ Надежный пароль")
            self.strength_text.setStyleSheet("color: #44ff44; font-size: 12px;")

    def reset_password(self):
        """Сбрасывает пароль пользователя"""
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not new_password or not confirm_password:
            self.show_custom_message("Ошибка", "❌ Заполните все поля!", "error")
            return

        if new_password != confirm_password:
            self.show_custom_message("Ошибка", "❌ Пароли не совпадают!", "error")
            return

        if len(new_password) < 6:
            self.show_custom_message("Ошибка", "❌ Пароль должен содержать минимум 6 символов!", "error")
            return

        # Обновляем пароль в базе данных
        try:
            conn = get_connection()
            cursor = conn.cursor()

            hashed_password = hash_password(new_password)
            cursor.execute("UPDATE Client SET PasswordHash = %s WHERE ID = %s",
                           (hashed_password, self.current_user_id))
            conn.commit()

            self.show_custom_message("Успех", "✅ Пароль успешно изменен!", "success")

            # Закрываем диалог
            self.accept()

        except Exception as e:
            self.show_custom_message("Ошибка", f"❌ Не удалось изменить пароль: {str(e)}", "error")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def show_custom_message(self, title, text, msg_type="info"):
        """Кастомное сообщение"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 20px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        if msg_type == "error":
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Information)

        msg.exec_()


class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super(AuthDialog, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setupUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName("AuthDialog")
        Dialog.resize(500, 600)

        # Сохраняем ссылку на диалог
        self.dialog = Dialog

        # Главный контейнер с тенью и фоном
        main_container = QFrame(Dialog)
        main_container.setGeometry(0, 0, 500, 600)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 30px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Основная тень
        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(30)
        main_shadow.setColor(QColor(0, 0, 0, 150))
        main_shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(main_shadow)

        # Основной layout
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # ===== ЗАГОЛОВОК С КНОПКОЙ ЗАКРЫТИЯ =====
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # Кнопка закрытия
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        # Заголовок
        title_label = QLabel("🔑 Вход в IT-EcoSystem")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        # Логотип/иконка
        logo_label = QLabel("🚀")
        logo_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 32px;
            }
        """)

        header_layout.addWidget(self.btn_close)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(logo_label)

        layout.addLayout(header_layout)

        # ===== ИНФОРМАЦИОННОЕ СООБЩЕНИЕ =====
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(76, 175, 80, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(76, 175, 80, 0.3);
                padding: 15px;
            }
        """)

        info_layout = QVBoxLayout(info_frame)

        info_text = QLabel("👋 Войдите в свой аккаунт для доступа к IT-EcoSystem")
        info_text.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setWordWrap(True)

        info_layout.addWidget(info_text)
        layout.addWidget(info_frame)

        # ===== ПОЛЯ ВВОДА =====
        # Логин/Email
        self.login = ModernLineEdit("Логин или Email")
        layout.addWidget(self.login)

        # Пароль с функцией показа/скрытия
        self.password = PasswordLineEdit("Пароль")
        layout.addWidget(self.password)

        # Кнопка "Забыли пароль?"
        self.forgot_password_btn = QPushButton("Забыли пароль?")
        self.forgot_password_btn.setStyleSheet("""
            QPushButton {
                color: #4CAF50;
                background-color: transparent;
                border: none;
                font-size: 14px;
                font-weight: 500;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #45a049;
            }
        """)
        self.forgot_password_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.forgot_password_btn, 0, Qt.AlignRight)

        # Растягивающийся элемент
        layout.addStretch()

        # ===== КНОПКИ =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.sign_up = ModernButton("🔓 Войти", True)
        self.sign_in = ModernButton("📝 Регистрация", False)

        button_layout.addWidget(self.sign_up)
        button_layout.addWidget(self.sign_in)

        layout.addLayout(button_layout)

        # Подключение сигналов
        self.sign_up.clicked.connect(self.open_profil_window)
        self.sign_in.clicked.connect(self.open_ide_window)
        self.forgot_password_btn.clicked.connect(self.open_forgot_password_dialog)

        # Переключение по Enter
        self.login.returnPressed.connect(self.password.setFocus)
        self.password.returnPressed.connect(self.sign_up.click)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def open_ide_window(self):
        """Открывает окно регистрации"""
        self.registration_dialog = IdenDialog(self)
        self.registration_dialog.show()

    def open_profil_window(self):
        """Открывает профиль после успешного входа"""
        login = self.login.text()
        password = self.password.text()

        # Всегда запоминаем пользователя (убрали чекбокс)
        remember_me = True

        if login and password:
            if check_user(login, password):
                user_data = get_user_data_by_login(login)

                # Выполняем вход через менеджер сессии с сохранением
                session.login(user_data["ID"],
                             user_data["FirstName"] + " " + user_data["LastName"],
                             remember_me)

                # Закрываем окно авторизации
                self.close()

                # Открываем профиль
                self.profile_dialog = QDialog()
                self.profile_ui = Ui_profil(user_data["ID"],
                                           user_data["FirstName"] + " " + user_data["LastName"])
                self.profile_ui.setupUi(self.profile_dialog)

                # Подключаем сигнал закрытия профиля для обновления кнопки
                if hasattr(session, '_main_window') and session._main_window:
                    self.profile_dialog.finished.connect(
                        lambda: session._main_window.update_login_button()
                    )

                self.profile_dialog.show()
            else:
                self.show_custom_message("Ошибка", "❌ Неверный логин или пароль!", "error")
        else:
            self.show_custom_message("Ошибка", "❌ Заполните все поля!", "error")

    def open_forgot_password_dialog(self):
        """Открывает диалог восстановления пароля"""
        self.forgot_dialog = ForgotPasswordDialog(self)
        self.forgot_dialog.exec_()

    def show_custom_message(self, title, text, msg_type="info"):
        """Кастомное сообщение"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 20px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        if msg_type == "error":
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Information)

        msg.exec_()


if __name__ == "__main__":
    import sys

    # Установка высокого DPI для современных экранов
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    # Установка глобального шрифта
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Применяем темную палитру глобально
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(76, 175, 80))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    dialog = AuthDialog()
    dialog.show()
    sys.exit(app.exec_())