# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette, QPixmap, QPainter, QPen, QPainterPath
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLabel, QPushButton, QFrame, \
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QSpacerItem, QSizePolicy

from Settig_profils.Setting_Date import Ui_Setting_Date
from Settig_profils.Setting_Email import Ui_Setting_Email
from Settig_profils.Setting_Login import Ui_Setting_Login
from Settig_profils.Setting_Nomber import Ui_Setting_Nomber
from Settig_profils.Setting_Passwork import Ui_Setting_Password
from Settig_profils.Setting_Name_Surnamel import Ui_Setting_Name_Surnamel
from Server.db import update_name_surname_in_db, update_birthdate_in_db


class ModernSettingButton(QPushButton):
    """Современная кнопка настроек в стиле главного окна"""

    def __init__(self, text="", icon="", description="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(70)
        self.setCursor(Qt.PointingHandCursor)

        # Основной стиль кнопки
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 2px solid #3a3a3a;
                border-radius: 15px;
                text-align: left;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #353535;
                border: 2px solid #4CAF50;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)

        # Тень для кнопки
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # Создаем layout для кнопки
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Иконка
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: rgba(76, 175, 80, 0.15);
                color: #4CAF50;
                font-size: 24px;
                padding: 8px;
                border-radius: 12px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
                qproperty-alignment: AlignCenter;
            }
        """)

        # Текстовый контейнер
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)

        # Заголовок
        self.title_label = QLabel(text)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 600;
                background: transparent;
            }
        """)

        # Описание
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 12px;
                background: transparent;
            }
        """)

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.desc_label)

        # Стрелка
        self.arrow_label = QLabel("→")
        self.arrow_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 24px;
                background: transparent;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.icon_label)
        layout.addWidget(text_container, 1)
        layout.addWidget(self.arrow_label)


class SettingDateDialog(QDialog):
    """Современный диалог изменения даты рождения"""

    def __init__(self, current_user_id, parent=None):
        super(SettingDateDialog, self).__init__(parent)
        self.current_user_id = current_user_id
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(400, 500)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 400, 500)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 25px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        header_layout = QHBoxLayout()

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        title_label = QLabel("📅 Изменить дату рождения")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: 600;
            }
        """)

        header_layout.addWidget(self.btn_close)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Текущая дата
        current_date_label = QLabel("Текущая дата рождения:")
        current_date_label.setStyleSheet("color: #808080; font-size: 13px;")
        layout.addWidget(current_date_label)

        self.current_date = QLabel("—")
        self.current_date.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: 600;
                padding: 10px;
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3a3a3a;
            }
        """)
        layout.addWidget(self.current_date)

        # Поле ввода
        input_label = QLabel("Новая дата рождения:")
        input_label.setStyleSheet("color: #808080; font-size: 13px; margin-top: 10px;")
        layout.addWidget(input_label)

        self.date_input = QtWidgets.QLineEdit()
        self.date_input.setPlaceholderText("дд.мм.гггг")
        self.date_input.setMinimumHeight(45)
        self.date_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        layout.addWidget(self.date_input)

        # Календарь
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
            }
            QCalendarWidget QWidget {
                background-color: #2d2d2d;
                color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #4CAF50;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #4CAF50;
                border-radius: 10px 10px 0 0;
            }
        """)
        self.calendar.clicked.connect(self.update_date_from_calendar)
        layout.addWidget(self.calendar)

        # Кнопка сохранения
        self.btn_save = QPushButton("💾 Сохранить изменения")
        self.btn_save.setMinimumHeight(50)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
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
        self.btn_save.clicked.connect(self.save_changes)
        layout.addWidget(self.btn_save)

        layout.addStretch()

    def update_date_from_calendar(self, date):
        self.date_input.setText(date.toString("dd.MM.yyyy"))

    def save_changes(self):
        new_date = self.date_input.text().strip()
        if not new_date:
            QMessageBox.warning(self, "Ошибка", "Введите дату рождения!")
            return

        # Валидация даты
        try:
            from datetime import datetime
            date_obj = datetime.strptime(new_date, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат даты! Используйте дд.мм.гггг")
            return

        success = update_birthdate_in_db(self.current_user_id, formatted_date)
        if success:
            QMessageBox.information(self, "Успех", "✅ Дата рождения успешно обновлена!")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "❌ Не удалось обновить дату рождения")


class SettingNameSurnameDialog(QDialog):
    """Современный диалог изменения имени и фамилии"""

    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(400, 400)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 400, 400)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 25px;
                border: 1px solid #3a3a3a;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        header_layout = QHBoxLayout()

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        title_label = QLabel("👤 Изменить имя и фамилию")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: 600;
            }
        """)

        header_layout.addWidget(self.btn_close)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Поле имени
        name_label = QLabel("Имя:")
        name_label.setStyleSheet("color: #808080; font-size: 13px;")
        layout.addWidget(name_label)

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Введите новое имя")
        self.name_input.setMinimumHeight(45)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(self.name_input)

        # Поле фамилии
        surname_label = QLabel("Фамилия:")
        surname_label.setStyleSheet("color: #808080; font-size: 13px; margin-top: 10px;")
        layout.addWidget(surname_label)

        self.surname_input = QtWidgets.QLineEdit()
        self.surname_input.setPlaceholderText("Введите новую фамилию")
        self.surname_input.setMinimumHeight(45)
        self.surname_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(self.surname_input)

        # Кнопка сохранения
        self.btn_save = QPushButton("💾 Сохранить изменения")
        self.btn_save.setMinimumHeight(50)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
        """)
        self.btn_save.clicked.connect(self.save_changes)
        layout.addWidget(self.btn_save)

        layout.addStretch()

    def save_changes(self):
        new_name = self.name_input.text().strip()
        new_surname = self.surname_input.text().strip()

        if not new_name or not new_surname:
            QMessageBox.warning(self, "Ошибка", "Заполните оба поля!")
            return

        success = update_name_surname_in_db(self.user_id, new_name, new_surname)
        if success:
            QMessageBox.information(self, "Успех", "✅ Имя и фамилия успешно обновлены!")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "❌ Не удалось обновить данные")


class Ui_Setting_Profil(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.dialog = None

    def setupUi(self, Setting_Profil):
        self.dialog = Setting_Profil
        Setting_Profil.setObjectName("Setting_Profil")
        Setting_Profil.resize(500, 700)
        Setting_Profil.setMinimumSize(450, 600)
        Setting_Profil.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        Setting_Profil.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        main_container = QFrame(Setting_Profil)
        main_container.setObjectName("main_container")
        main_container.setGeometry(0, 0, 500, 700)
        main_container.setStyleSheet("""
            QFrame#main_container {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 25px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(shadow)

        # Основной layout
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Скролл-область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
                border-radius: 25px;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
                margin: 20px 0px;
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
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignTop)

        # ===== ВЕРХНЯЯ ПАНЕЛЬ =====
        header_layout = QHBoxLayout()

        # Кнопка закрытия
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setCursor(Qt.PointingHandCursor)
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
        """)
        self.btn_close.clicked.connect(Setting_Profil.close)

        # Заголовок
        title_label = QLabel("⚙️ Настройки профиля")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: 600;
                margin-left: 10px;
            }
        """)

        # Аватарка маленькая
        self.avatar_preview = QLabel()
        self.avatar_preview.setFixedSize(50, 50)
        self.avatar_preview.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                border-radius: 15px;
                color: white;
                font-size: 20px;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.avatar_preview.setText("👤")

        header_layout.addWidget(self.btn_close)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.avatar_preview)

        content_layout.addLayout(header_layout)

        # ===== ИНФОРМАЦИОННЫЙ БЛОК =====
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(76, 175, 80, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(76, 175, 80, 0.3);
                padding: 15px;
            }
        """)

        info_layout = QHBoxLayout(info_frame)

        info_icon = QLabel("ℹ️")
        info_icon.setStyleSheet("font-size: 24px; background: none;")

        info_text = QLabel("Управляйте настройками вашего профиля.\n"
                           "Нажмите на любой пункт для изменения данных.")
        info_text.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
                background: none;
            }
        """)
        info_text.setWordWrap(True)

        info_layout.addWidget(info_icon)
        info_layout.addWidget(info_text, 1)

        content_layout.addWidget(info_frame)

        # ===== РАЗДЕЛ: ЛИЧНЫЕ ДАННЫЕ =====
        personal_section = QLabel("📋 Личные данные")
        personal_section.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: 600;
                margin-top: 10px;
            }
        """)
        content_layout.addWidget(personal_section)

        # Кнопка "Имя и Фамилия"
        self.btn_name_surname = ModernSettingButton(
            "Имя и Фамилия",
            "👤",
            "Изменить ваши имя и фамилию"
        )
        self.btn_name_surname.clicked.connect(self.open_name_surname)
        content_layout.addWidget(self.btn_name_surname)

        # Кнопка "Логин"
        self.btn_login = ModernSettingButton(
            "Логин",
            "🔑",
            "Изменить имя пользователя"
        )
        self.btn_login.clicked.connect(self.open_login)
        content_layout.addWidget(self.btn_login)

        # Кнопка "Дата рождения"
        self.btn_date = ModernSettingButton(
            "Дата рождения",
            "📅",
            "Изменить дату рождения"
        )
        self.btn_date.clicked.connect(self.open_date)
        content_layout.addWidget(self.btn_date)

        # ===== РАЗДЕЛИТЕЛЬ =====
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                max-height: 2px;
                min-height: 2px;
                margin: 10px 0;
            }
        """)
        content_layout.addWidget(separator1)

        # ===== РАЗДЕЛ: БЕЗОПАСНОСТЬ И КОНТАКТЫ =====
        security_section = QLabel("🔒 Безопасность и контакты")
        security_section.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: 600;
            }
        """)
        content_layout.addWidget(security_section)

        # Кнопка "Пароль"
        self.btn_password = ModernSettingButton(
            "Пароль",
            "🔒",
            "Изменить пароль"
        )
        self.btn_password.clicked.connect(self.open_password)
        content_layout.addWidget(self.btn_password)

        # Кнопка "Номер телефона"
        self.btn_phone = ModernSettingButton(
            "Номер телефона",
            "📱",
            "Изменить номер телефона"
        )
        self.btn_phone.clicked.connect(self.open_phone)
        content_layout.addWidget(self.btn_phone)

        # Кнопка "Email"
        self.btn_email = ModernSettingButton(
            "Email",
            "📧",
            "Изменить электронную почту"
        )
        self.btn_email.clicked.connect(self.open_email)
        content_layout.addWidget(self.btn_email)

        # ===== РАЗДЕЛИТЕЛЬ =====
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                max-height: 2px;
                min-height: 2px;
                margin: 10px 0;
            }
        """)
        content_layout.addWidget(separator2)

        # Растяжка
        content_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Подгоняем размер контейнера под окно
        Setting_Profil.resizeEvent = self.resize_event

        self.retranslateUi(Setting_Profil)
        QtCore.QMetaObject.connectSlotsByName(Setting_Profil)

    def resize_event(self, event):
        """Обработка изменения размера окна"""
        main_container = self.dialog.findChild(QFrame, "main_container")
        if main_container:
            main_container.setGeometry(0, 0, self.dialog.width(), self.dialog.height())

    def retranslateUi(self, Setting_Profil):
        _translate = QtCore.QCoreApplication.translate
        Setting_Profil.setWindowTitle(_translate("Setting_Profil", "IT-EcoSystem - Настройки"))

    def open_name_surname(self):
        dialog = SettingNameSurnameDialog(self.user_id, self.dialog)
        dialog.exec_()

    def open_login(self):
        # Здесь будет открытие диалога смены логина
        QMessageBox.information(self.dialog, "Информация", "Функция будет доступна в следующем обновлении")

    def open_date(self):
        dialog = SettingDateDialog(self.user_id, self.dialog)
        dialog.exec_()

    def open_password(self):
        # Здесь будет открытие диалога смены пароля
        QMessageBox.information(self.dialog, "Информация", "Функция будет доступна в следующем обновлении")

    def open_phone(self):
        # Здесь будет открытие диалога смены телефона
        QMessageBox.information(self.dialog, "Информация", "Функция будет доступна в следующем обновлении")

    def open_email(self):
        # Здесь будет открытие диалога смены email
        QMessageBox.information(self.dialog, "Информация", "Функция будет доступна в следующем обновлении")


if __name__ == "__main__":
    import sys

    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Применяем темную палитру
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
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    app.setPalette(palette)

    dialog = QtWidgets.QDialog()
    ui = Ui_Setting_Profil(1)  # Тестовый user_id
    ui.setupUi(dialog)
    dialog.show()

    sys.exit(app.exec_())