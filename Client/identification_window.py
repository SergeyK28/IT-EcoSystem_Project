# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QDate, QTimer
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette, QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QCheckBox, QCalendarWidget, QFrame, QMessageBox, QDialog, QSlider

from Server.db import register_user


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


class ModernDateInputWidget(QWidget):
    """Современный виджет ввода даты с календарем"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Контейнер для поля ввода и кнопки
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)

        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        # Поле ввода даты
        self.Data = ModernLineEdit()
        self.Data.setPlaceholderText("дд.мм.гггг")
        self.Data.setMaxLength(10)
        self.Data.textEdited.connect(self.auto_format_date)

        # Кнопка календаря
        self.btn_calendar = QPushButton("📅")
        self.btn_calendar.setFixedSize(50, 50)
        self.btn_calendar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 20px;
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
        self.btn_calendar.clicked.connect(self.toggle_calendar)

        input_layout.addWidget(self.Data)
        input_layout.addWidget(self.btn_calendar)

        # Календарь
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #2d2d2d;
                border-radius: 15px;
                color: white;
            }
            QCalendarWidget QWidget {
                background-color: #2d2d2d;
                color: white;
            }
            QCalendarWidget QMenu {
                background-color: #2d2d2d;
                color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #4CAF50;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #4CAF50;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
            QCalendarWidget QToolButton {
                background-color: transparent;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #45a049;
            }
        """)

        # Тень для календаря
        calendar_shadow = QGraphicsDropShadowEffect()
        calendar_shadow.setBlurRadius(20)
        calendar_shadow.setColor(QColor(0, 0, 0, 100))
        calendar_shadow.setOffset(0, 5)
        self.calendar.setGraphicsEffect(calendar_shadow)

        self.calendar.hide()
        self.calendar.clicked.connect(self.set_date_from_calendar)

        layout.addWidget(input_container)
        layout.addWidget(self.calendar)
        self.setLayout(layout)

    def auto_format_date(self, text):
        if not text:
            return

        # Очищаем от не-цифр
        digits = ''.join(filter(str.isdigit, text))

        # Форматируем
        if len(digits) > 2:
            day = digits[:2]
            if len(digits) > 4:
                month = digits[2:4]
                year = digits[4:8]
                formatted = f"{day}.{month}.{year}"
            else:
                month = digits[2:4] if len(digits) > 2 else ""
                formatted = f"{day}.{month}" if month else day
        else:
            formatted = digits

        self.Data.setText(formatted)
        self.Data.setCursorPosition(len(formatted))

        # Проверка корректности при полном вводе
        if len(formatted) == 10 and self.is_valid_date(formatted):
            self.focusNextChild()

    def is_valid_date(self, date_str):
        try:
            day, month, year = map(int, date_str.split('.'))
            return QDate.isValid(year, month, day)
        except:
            return False

    def toggle_calendar(self):
        if self.calendar.isHidden():
            self.calendar.show()
            # Анимация появления
            anim = QPropertyAnimation(self.calendar, b"windowOpacity")
            anim.setDuration(200)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
        else:
            self.calendar.hide()

    def set_date_from_calendar(self, date):
        self.Data.setText(date.toString("dd.MM.yyyy"))
        self.calendar.hide()


class IdenDialog(QDialog):
    def __init__(self, parent=None):
        super(IdenDialog, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setupUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName("IdenDialog")
        Dialog.resize(550, 850)  # Уменьшил высоту после удаления слайдера

        # Главный контейнер с тенью и фоном
        main_container = QFrame(Dialog)
        main_container.setGeometry(0, 0, 550, 850)
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

        # Скролл-область для контента
        scroll_area = QtWidgets.QScrollArea(main_container)
        scroll_area.setGeometry(0, 0, 550, 850)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #45a049;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(40, 40, 40, 40)
        scroll_layout.setSpacing(20)

        # ===== ЗАГОЛОВОК =====
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
        title_label = QLabel("📝 Регистрация")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        # Логотип/иконка
        logo_label = QLabel("✨")
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

        scroll_layout.addLayout(header_layout)

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

        info_text = QLabel("🔐 Заполните все поля для создания аккаунта")
        info_text.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        info_text.setAlignment(Qt.AlignCenter)

        info_layout.addWidget(info_text)
        scroll_layout.addWidget(info_frame)

        # ===== ПОЛЯ ВВОДА =====
        # Фамилия
        self.Surname = ModernLineEdit("Фамилия *", "👤")
        scroll_layout.addWidget(self.Surname)

        # Имя
        self.Name = ModernLineEdit("Имя *", "👤")
        scroll_layout.addWidget(self.Name)

        # Логин
        self.Login = ModernLineEdit("Логин *", "🔑")
        scroll_layout.addWidget(self.Login)

        # Дата рождения
        date_label = QLabel("Дата рождения")
        date_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: -15px;
            }
        """)
        scroll_layout.addWidget(date_label)

        self.DateInput = ModernDateInputWidget()
        scroll_layout.addWidget(self.DateInput)

        # Телефон
        self.Nomber = ModernLineEdit("Телефон (+7...) *", "📱")
        self.Nomber.setMaxLength(12)
        scroll_layout.addWidget(self.Nomber)

        # Email
        self.Email = ModernLineEdit("Email *", "📧")
        scroll_layout.addWidget(self.Email)

        # ===== ПАРОЛИ =====
        # Пароль
        self.Create_password = ModernLineEdit("Пароль *", "🔒")
        self.Create_password.setEchoMode(QLineEdit.Password)
        scroll_layout.addWidget(self.Create_password)

        # Подтверждение пароля
        self.Repeat_create_password = ModernLineEdit("Подтвердите пароль *", "🔒")
        self.Repeat_create_password.setEchoMode(QLineEdit.Password)
        scroll_layout.addWidget(self.Repeat_create_password)

        # ===== ИНДИКАТОР СЛОЖНОСТИ ПАРОЛЯ =====
        password_strength_frame = QFrame()
        password_strength_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        password_strength_layout = QVBoxLayout(password_strength_frame)

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

        password_strength_layout.addWidget(strength_label)
        password_strength_layout.addWidget(self.strength_bar)
        password_strength_layout.addWidget(self.strength_text)

        scroll_layout.addWidget(password_strength_frame)

        # Подключаем проверку пароля
        self.Create_password.textChanged.connect(self.check_password_strength)

        # ===== ЧЕКБОКС =====
        agreement_layout = QHBoxLayout()
        agreement_layout.setSpacing(15)

        self.User_agreement = QCheckBox()
        self.User_agreement.setStyleSheet("""
            QCheckBox {
                color: #b0b0b0;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid #4a4a4a;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #4CAF50;
                background-color: #353535;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                image: url(:/icons/check.png);
            }
        """)

        agreement_text = QLabel("Я принимаю условия")
        agreement_text.setStyleSheet("color: #b0b0b0; font-size: 13px;")

        agreement_link = QPushButton("пользовательского соглашения")
        agreement_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #4CAF50;
                font-size: 13px;
                font-weight: bold;
                text-decoration: underline;
                padding: 0;
            }
            QPushButton:hover {
                color: #45a049;
            }
        """)

        agreement_layout.addWidget(self.User_agreement)
        agreement_layout.addWidget(agreement_text)
        agreement_layout.addWidget(agreement_link)
        agreement_layout.addStretch()

        scroll_layout.addLayout(agreement_layout)

        # ===== КНОПКА РЕГИСТРАЦИИ =====
        self.Creat_account = QPushButton("📝 Зарегистрироваться")
        self.Creat_account.setMinimumHeight(55)
        self.Creat_account.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #357a38);
            }
            QPushButton:disabled {
                background: #3a3a3a;
                color: #808080;
            }
        """)
        self.Creat_account.setEnabled(False)
        self.Creat_account.clicked.connect(self.register)

        scroll_layout.addWidget(self.Creat_account)

        # ===== ССЫЛКА НА ВХОД =====
        login_layout = QHBoxLayout()
        login_layout.setSpacing(5)
        login_layout.setAlignment(Qt.AlignCenter)

        login_text = QLabel("Уже есть аккаунт?")
        login_text.setStyleSheet("color: #b0b0b0; font-size: 14px;")

        login_link = QPushButton("Войти")
        login_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #4CAF50;
                font-size: 14px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                color: #45a049;
                text-decoration: underline;
            }
        """)

        login_layout.addWidget(login_text)
        login_layout.addWidget(login_link)

        scroll_layout.addLayout(login_layout)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)

        # ===== ПОДКЛЮЧЕНИЕ СИГНАЛОВ =====
        self.User_agreement.stateChanged.connect(self.toggle_register_button)
        login_link.clicked.connect(self.close)

        # Переключение по Enter
        self.Surname.returnPressed.connect(self.Name.setFocus)
        self.Name.returnPressed.connect(self.Login.setFocus)
        self.Login.returnPressed.connect(self.DateInput.Data.setFocus)
        self.DateInput.Data.returnPressed.connect(self.Nomber.setFocus)
        self.Nomber.returnPressed.connect(self.Email.setFocus)
        self.Email.returnPressed.connect(self.Create_password.setFocus)
        self.Create_password.returnPressed.connect(self.Repeat_create_password.setFocus)
        self.Repeat_create_password.returnPressed.connect(self.Creat_account.click)

        # Валидация для телефона
        self.Nomber.textChanged.connect(self.format_phone)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

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

        self.strength_indicator.setFixedWidth(int(width * (strength / 100)))

        if strength < 25:
            self.strength_indicator.setStyleSheet("background-color: #ff4444; border-radius: 3px;")
            self.strength_text.setText("Слишком простой пароль")
            self.strength_text.setStyleSheet("color: #ff4444; font-size: 12px;")
        elif strength < 50:
            self.strength_indicator.setStyleSheet("background-color: #ffaa44; border-radius: 3px;")
            self.strength_text.setText("Слабый пароль")
            self.strength_text.setStyleSheet("color: #ffaa44; font-size: 12px;")
        elif strength < 75:
            self.strength_indicator.setStyleSheet("background-color: #ffff44; border-radius: 3px;")
            self.strength_text.setText("Средний пароль")
            self.strength_text.setStyleSheet("color: #ffff44; font-size: 12px;")
        else:
            self.strength_indicator.setStyleSheet("background-color: #44ff44; border-radius: 3px;")
            self.strength_text.setText("Надежный пароль")
            self.strength_text.setStyleSheet("color: #44ff44; font-size: 12px;")

    def format_phone(self, text):
        """Форматирование номера телефона"""
        if not text:
            return
        if not text.startswith('+'):
            if text[0].isdigit():
                self.Nomber.blockSignals(True)
                self.Nomber.setText('+' + text)
                self.Nomber.blockSignals(False)

    def toggle_register_button(self, state):
        self.Creat_account.setEnabled(state == Qt.Checked)
        if state == Qt.Checked:
            self.Creat_account.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 10px;
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

    def register(self):
        surname = self.Surname.text().strip()
        first_name = self.Name.text().strip()
        login = self.Login.text().strip()
        password = self.Create_password.text()
        repeat_password = self.Repeat_create_password.text()
        phone = self.Nomber.text().strip()
        email = self.Email.text().strip()

        # Валидация
        errors = []

        if not all([surname, first_name, login, password, repeat_password, phone, email]):
            errors.append("❌ Заполните все обязательные поля!")

        if len(password) < 6:
            errors.append("❌ Пароль должен содержать минимум 6 символов!")

        if password != repeat_password:
            errors.append("❌ Пароли не совпадают!")

        if not phone.startswith("+7") or len(phone) != 12 or not phone[2:].isdigit():
            errors.append("❌ Телефон должен начинаться с +7 и содержать 12 цифр!")

        if '@' not in email or '.' not in email:
            errors.append("❌ Введите корректный email адрес!")

        if errors:
            error_msg = "\n".join(errors)
            self.show_custom_message("Ошибка регистрации", error_msg, "error")
            return

        # Регистрация
        success = register_user(surname, first_name, login, password, email)

        if success:
            self.show_custom_message("Успех",
                                     "✅ Регистрация прошла успешно!",
                                     "success")
            self.close()
        else:
            self.show_custom_message("Ошибка", "❌ Пользователь с таким логином уже существует!", "error")

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
        elif msg_type == "success":
            msg.setIcon(QMessageBox.Information)
        else:
            msg.setIcon(QMessageBox.Information)

        msg.exec_()


def show_registration_dialog(parent=None):
    """Показать диалог регистрации"""
    dialog = IdenDialog(parent)
    result = dialog.exec_()
    return result


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

    dialog = IdenDialog()
    dialog.show()
    sys.exit(app.exec_())