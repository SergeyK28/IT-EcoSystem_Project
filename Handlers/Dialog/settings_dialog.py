# -*- coding: utf-8 -*-
"""
Модуль настроек CRM системы.
Содержит диалоговое окно с настройками пользователя, интерфейса, уведомлений и БД.
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton,
                             QCheckBox, QComboBox, QSpinBox, QGroupBox, QFormLayout, QMessageBox, QFileDialog,
                             QColorDialog, QFontDialog, QSplitter, QListWidget,
                             QListWidgetItem, QStackedWidget)
import sys
import os

# Добавляем путь к корневой директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем сессию сотрудника
try:
    from Handlers.Employees.employee_session import employee_session
except ImportError:
    # Создаем заглушку, если модуль не найден
    class DummyEmployeeSession:
        def is_authenticated(self):
            return False

        def get_employee_data(self):
            return None

        def get_employee_id(self):
            return None

        def get_employee_name(self):
            return None


    employee_session = DummyEmployeeSession()


class SettingsDialog(QDialog):
    """Диалоговое окно настроек CRM"""

    # Сигналы для обновления интерфейса после сохранения настроек
    settings_saved = pyqtSignal()
    theme_changed = pyqtSignal(str)
    font_changed = pyqtSignal(QFont)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("IT-EcoSystem", "CRM")

        # Получаем данные текущего пользователя безопасно
        self.current_user = None
        try:
            if employee_session.is_authenticated():
                # Пытаемся получить данные разными способами
                if hasattr(employee_session, 'get_employee_data'):
                    self.current_user = employee_session.get_employee_data()
                elif hasattr(employee_session, '_employee_data'):
                    self.current_user = employee_session._employee_data
                else:
                    self.current_user = {}
        except Exception as e:
            print(f"Ошибка получения данных пользователя: {e}")
            self.current_user = {}

        self.setWindowTitle("Настройки CRM - IT-EcoSystem")
        self.setMinimumSize(900, 650)
        self.resize(950, 700)

        # Устанавливаем иконку
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "Pictures", "Screenshot from 2025-09-15 14-30-16.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Создаем разделитель для левой навигации и правого контента
        splitter = QSplitter(Qt.Horizontal)

        # ==================== ЛЕВАЯ ПАНЕЛЬ НАВИГАЦИИ ====================
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 8px;
                color: #d0d0d0;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
        """)

        # Добавляем пункты навигации
        nav_items = [
            ("👤 Профиль", "profile"),
            ("🎨 Внешний вид", "appearance"),
            ("🔔 Уведомления", "notifications"),
            ("📁 База данных", "database"),
            ("⚙️ Системные", "system"),
            ("ℹ️ О программе", "about")
        ]

        for text, data in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, data)
            self.nav_list.addItem(item)

        splitter.addWidget(self.nav_list)

        # ==================== ПРАВАЯ ПАНЕЛЬ ====================
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        # Создаем страницы настроек
        self.profile_page = self.create_profile_page()
        self.appearance_page = self.create_appearance_page()
        self.notifications_page = self.create_notifications_page()
        self.database_page = self.create_database_page()
        self.system_page = self.create_system_page()
        self.about_page = self.create_about_page()

        self.content_stack.addWidget(self.profile_page)
        self.content_stack.addWidget(self.appearance_page)
        self.content_stack.addWidget(self.notifications_page)
        self.content_stack.addWidget(self.database_page)
        self.content_stack.addWidget(self.system_page)
        self.content_stack.addWidget(self.about_page)

        splitter.addWidget(self.content_stack)
        splitter.setSizes([200, 700])

        main_layout.addWidget(splitter)

        # ==================== НИЖНЯЯ ПАНЕЛЬ С КНОПКАМИ ====================
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Кнопка сохранения
        self.save_btn = QPushButton("💾 Сохранить настройки")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 25px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)

        # Кнопка отмены
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 25px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

        # Подключаем навигацию
        self.nav_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        self.nav_list.setCurrentRow(0)

    def create_profile_page(self):
        """Создает страницу настроек профиля пользователя"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Настройки профиля")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding-bottom: 10px;")
        layout.addWidget(title)

        # Группа личной информации
        personal_group = QGroupBox("Личная информация")
        personal_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        personal_layout = QFormLayout(personal_group)
        personal_layout.setSpacing(15)
        personal_layout.setLabelAlignment(Qt.AlignRight)

        # ФИО
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя")
        self.name_edit.setMinimumHeight(35)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 8px 12px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        personal_layout.addRow("Имя:", self.name_edit)

        # Фамилия
        self.surname_edit = QLineEdit()
        self.surname_edit.setPlaceholderText("Введите фамилию")
        self.surname_edit.setMinimumHeight(35)
        self.surname_edit.setStyleSheet(self.name_edit.styleSheet())
        personal_layout.addRow("Фамилия:", self.surname_edit)

        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("email@example.com")
        self.email_edit.setMinimumHeight(35)
        self.email_edit.setStyleSheet(self.name_edit.styleSheet())
        personal_layout.addRow("Email:", self.email_edit)

        # Телефон
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+7 (999) 123-45-67")
        self.phone_edit.setMinimumHeight(35)
        self.phone_edit.setStyleSheet(self.name_edit.styleSheet())
        personal_layout.addRow("Телефон:", self.phone_edit)

        layout.addWidget(personal_group)

        # Группа изменения пароля
        password_group = QGroupBox("Смена пароля")
        password_group.setStyleSheet(personal_group.styleSheet())

        password_layout = QFormLayout(password_group)
        password_layout.setSpacing(15)
        password_layout.setLabelAlignment(Qt.AlignRight)

        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setPlaceholderText("Введите текущий пароль")
        self.old_password.setMinimumHeight(35)
        self.old_password.setStyleSheet(self.name_edit.styleSheet())
        password_layout.addRow("Текущий пароль:", self.old_password)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Введите новый пароль")
        self.new_password.setMinimumHeight(35)
        self.new_password.setStyleSheet(self.name_edit.styleSheet())
        password_layout.addRow("Новый пароль:", self.new_password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Подтвердите новый пароль")
        self.confirm_password.setMinimumHeight(35)
        self.confirm_password.setStyleSheet(self.name_edit.styleSheet())
        password_layout.addRow("Подтверждение:", self.confirm_password)

        layout.addWidget(password_group)

        # Группа настроек отображения
        display_group = QGroupBox("Настройки отображения")
        display_group.setStyleSheet(personal_group.styleSheet())

        display_layout = QVBoxLayout(display_group)

        self.show_tooltips = QCheckBox("Показывать подсказки")
        self.show_tooltips.setStyleSheet("color: #d0d0d0; padding: 5px;")
        display_layout.addWidget(self.show_tooltips)

        self.confirm_exit = QCheckBox("Подтверждать выход из программы")
        self.confirm_exit.setStyleSheet("color: #d0d0d0; padding: 5px;")
        display_layout.addWidget(self.confirm_exit)

        self.auto_save = QCheckBox("Автоматически сохранять изменения")
        self.auto_save.setStyleSheet("color: #d0d0d0; padding: 5px;")
        display_layout.addWidget(self.auto_save)

        layout.addWidget(display_group)

        layout.addStretch()
        return page

    def create_appearance_page(self):
        """Создает страницу настроек внешнего вида"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Настройки внешнего вида")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding-bottom: 10px;")
        layout.addWidget(title)

        # Группа темы оформления
        theme_group = QGroupBox("Тема оформления")
        theme_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)

        theme_layout = QVBoxLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темная (по умолчанию)", "Светлая", "Синяя", "Зеленая", "Оранжевая"])
        self.theme_combo.setMinimumHeight(35)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 8px 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: white;
                selection-background-color: #4CAF50;
            }
        """)
        theme_layout.addWidget(self.theme_combo)

        # Предпросмотр темы
        preview_label = QLabel("Предпросмотр:")
        preview_label.setStyleSheet("color: #b0b0b0; margin-top: 10px;")
        theme_layout.addWidget(preview_label)

        self.preview_frame = QWidget()
        self.preview_frame.setFixedHeight(80)
        self.preview_frame.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a1a, stop:1 #2a2a2a);
                border-radius: 8px;
                border: 1px solid #4a4a4a;
            }
        """)
        theme_layout.addWidget(self.preview_frame)

        layout.addWidget(theme_group)

        # Группа шрифтов
        font_group = QGroupBox("Шрифты")
        font_group.setStyleSheet(theme_group.styleSheet())

        font_layout = QVBoxLayout(font_group)

        # Кнопка выбора шрифта
        font_button_layout = QHBoxLayout()
        self.font_preview = QLineEdit()
        self.font_preview.setReadOnly(True)
        self.font_preview.setMinimumHeight(35)
        self.font_preview.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 8px 12px;
            }
        """)

        self.font_btn = QPushButton("Выбрать шрифт...")
        self.font_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.font_btn.clicked.connect(self.choose_font)

        font_button_layout.addWidget(self.font_preview)
        font_button_layout.addWidget(self.font_btn)
        font_layout.addLayout(font_button_layout)

        # Размер шрифта
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Размер шрифта:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setMinimumHeight(35)
        self.font_size_spin.setStyleSheet("""
            QSpinBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        size_layout.addWidget(self.font_size_spin)
        size_layout.addStretch()
        font_layout.addLayout(size_layout)

        layout.addWidget(font_group)

        # Группа цветов
        colors_group = QGroupBox("Цветовая схема")
        colors_group.setStyleSheet(theme_group.styleSheet())

        colors_layout = QFormLayout(colors_group)
        colors_layout.setSpacing(15)

        self.primary_color_btn = QPushButton("Выбрать цвет")
        self.primary_color_btn.setStyleSheet(self.font_btn.styleSheet())
        self.primary_color_btn.clicked.connect(lambda: self.choose_color("primary"))
        colors_layout.addRow("Основной цвет:", self.primary_color_btn)

        self.secondary_color_btn = QPushButton("Выбрать цвет")
        self.secondary_color_btn.setStyleSheet(self.font_btn.styleSheet())
        self.secondary_color_btn.clicked.connect(lambda: self.choose_color("secondary"))
        colors_layout.addRow("Вторичный цвет:", self.secondary_color_btn)

        layout.addWidget(colors_group)

        layout.addStretch()
        return page

    def create_notifications_page(self):
        """Создает страницу настроек уведомлений"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Настройки уведомлений")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding-bottom: 10px;")
        layout.addWidget(title)

        # Группа общих уведомлений
        general_group = QGroupBox("Общие уведомления")
        general_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)

        general_layout = QVBoxLayout(general_group)

        self.notify_new_orders = QCheckBox("Новые заказы")
        self.notify_new_orders.setStyleSheet("color: #d0d0d0; padding: 5px;")
        general_layout.addWidget(self.notify_new_orders)

        self.notify_status_change = QCheckBox("Изменение статуса заказа")
        self.notify_status_change.setStyleSheet("color: #d0d0d0; padding: 5px;")
        general_layout.addWidget(self.notify_status_change)

        self.notify_comments = QCheckBox("Новые комментарии к заказу")
        self.notify_comments.setStyleSheet("color: #d0d0d0; padding: 5px;")
        general_layout.addWidget(self.notify_comments)

        self.notify_deadlines = QCheckBox("Приближение срока выполнения")
        self.notify_deadlines.setStyleSheet("color: #d0d0d0; padding: 5px;")
        general_layout.addWidget(self.notify_deadlines)

        layout.addWidget(general_group)

        # Группа звуковых уведомлений
        sound_group = QGroupBox("Звуковые уведомления")
        sound_group.setStyleSheet(general_group.styleSheet())

        sound_layout = QVBoxLayout(sound_group)

        self.enable_sound = QCheckBox("Включить звуковые уведомления")
        self.enable_sound.setStyleSheet("color: #d0d0d0; padding: 5px;")
        sound_layout.addWidget(self.enable_sound)

        sound_file_layout = QHBoxLayout()
        self.sound_file_edit = QLineEdit()
        self.sound_file_edit.setPlaceholderText("Выберите звуковой файл...")
        self.sound_file_edit.setReadOnly(True)
        self.sound_file_edit.setMinimumHeight(35)
        self.sound_file_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 8px 12px;
            }
        """)

        self.choose_sound_btn = QPushButton("Обзор...")
        self.choose_sound_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        self.choose_sound_btn.clicked.connect(self.choose_sound_file)

        sound_file_layout.addWidget(self.sound_file_edit)
        sound_file_layout.addWidget(self.choose_sound_btn)
        sound_layout.addLayout(sound_file_layout)

        layout.addWidget(sound_group)

        # Группа уведомлений на почту
        email_group = QGroupBox("Уведомления на почту")
        email_group.setStyleSheet(general_group.styleSheet())

        email_layout = QVBoxLayout(email_group)

        self.enable_email = QCheckBox("Отправлять уведомления на почту")
        self.enable_email.setStyleSheet("color: #d0d0d0; padding: 5px;")
        email_layout.addWidget(self.enable_email)

        self.email_digest = QCheckBox("Ежедневный дайджест")
        self.email_digest.setStyleSheet("color: #d0d0d0; padding: 5px;")
        email_layout.addWidget(self.email_digest)

        layout.addWidget(email_group)

        layout.addStretch()
        return page

    def create_database_page(self):
        """Создает страницу настроек базы данных"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Настройки базы данных")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding-bottom: 10px;")
        layout.addWidget(title)

        # Группа подключения
        connection_group = QGroupBox("Параметры подключения")
        connection_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)

        conn_layout = QFormLayout(connection_group)
        conn_layout.setSpacing(15)

        self.db_host = QLineEdit()
        self.db_host.setPlaceholderText("localhost")
        self.db_host.setMinimumHeight(35)
        self.db_host.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 8px 12px;
            }
        """)
        conn_layout.addRow("Хост:", self.db_host)

        self.db_port = QSpinBox()
        self.db_port.setRange(1, 65535)
        self.db_port.setValue(3306)
        self.db_port.setMinimumHeight(35)
        self.db_port.setStyleSheet("""
            QSpinBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        conn_layout.addRow("Порт:", self.db_port)

        self.db_name = QLineEdit()
        self.db_name.setPlaceholderText("SQL_IT_EcoSyttem_BD")
        self.db_name.setMinimumHeight(35)
        self.db_name.setStyleSheet(self.db_host.styleSheet())
        conn_layout.addRow("База данных:", self.db_name)

        self.db_user = QLineEdit()
        self.db_user.setPlaceholderText("Имя пользователя")
        self.db_user.setMinimumHeight(35)
        self.db_user.setStyleSheet(self.db_host.styleSheet())
        conn_layout.addRow("Пользователь:", self.db_user)

        self.db_password = QLineEdit()
        self.db_password.setEchoMode(QLineEdit.Password)
        self.db_password.setPlaceholderText("Пароль")
        self.db_password.setMinimumHeight(35)
        self.db_password.setStyleSheet(self.db_host.styleSheet())
        conn_layout.addRow("Пароль:", self.db_password)

        # Кнопка тестирования
        test_btn = QPushButton("🔌 Тестировать подключение")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        test_btn.clicked.connect(self.test_db_connection)
        conn_layout.addRow(test_btn)

        layout.addWidget(connection_group)

        # Группа резервного копирования
        backup_group = QGroupBox("Резервное копирование")
        backup_group.setStyleSheet(connection_group.styleSheet())

        backup_layout = QVBoxLayout(backup_group)

        self.auto_backup = QCheckBox("Автоматическое резервное копирование")
        self.auto_backup.setStyleSheet("color: #d0d0d0; padding: 5px;")
        backup_layout.addWidget(self.auto_backup)

        backup_freq_layout = QHBoxLayout()
        backup_freq_layout.addWidget(QLabel("Частота:"))
        self.backup_freq = QComboBox()
        self.backup_freq.addItems(["Ежедневно", "Еженедельно", "Ежемесячно"])
        self.backup_freq.setMinimumHeight(35)
        backup_freq_layout.addWidget(self.backup_freq)
        backup_freq_layout.addStretch()
        backup_layout.addLayout(backup_freq_layout)

        backup_path_layout = QHBoxLayout()
        self.backup_path = QLineEdit()
        self.backup_path.setPlaceholderText("Путь для сохранения бэкапов...")
        self.backup_path.setMinimumHeight(35)
        self.backup_path.setStyleSheet(self.db_host.styleSheet())

        backup_path_btn = QPushButton("Обзор...")
        backup_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
        """)
        backup_path_btn.clicked.connect(self.choose_backup_path)

        backup_path_layout.addWidget(self.backup_path)
        backup_path_layout.addWidget(backup_path_btn)
        backup_layout.addLayout(backup_path_layout)

        # Кнопка создания бэкапа
        create_backup_btn = QPushButton("💾 Создать резервную копию сейчас")
        create_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        create_backup_btn.clicked.connect(self.create_backup)
        backup_layout.addWidget(create_backup_btn)

        layout.addWidget(backup_group)

        layout.addStretch()
        return page

    def create_system_page(self):
        """Создает страницу системных настроек"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Системные настройки")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding-bottom: 10px;")
        layout.addWidget(title)

        # Группа кэша
        cache_group = QGroupBox("Управление кэшем")
        cache_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)

        cache_layout = QVBoxLayout(cache_group)

        self.clear_cache_on_exit = QCheckBox("Очищать кэш при выходе")
        self.clear_cache_on_exit.setStyleSheet("color: #d0d0d0; padding: 5px;")
        cache_layout.addWidget(self.clear_cache_on_exit)

        clear_cache_btn = QPushButton("🗑️ Очистить кэш сейчас")
        clear_cache_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addWidget(clear_cache_btn)

        layout.addWidget(cache_group)

        # Группа логов
        logs_group = QGroupBox("Журналирование")
        logs_group.setStyleSheet(cache_group.styleSheet())

        logs_layout = QVBoxLayout(logs_group)

        self.enable_logging = QCheckBox("Включить ведение логов")
        self.enable_logging.setStyleSheet("color: #d0d0d0; padding: 5px;")
        logs_layout.addWidget(self.enable_logging)

        logs_level_layout = QHBoxLayout()
        logs_level_layout.addWidget(QLabel("Уровень логирования:"))
        self.logs_level = QComboBox()
        self.logs_level.addItems(["ERROR", "WARNING", "INFO", "DEBUG"])
        self.logs_level.setMinimumHeight(35)
        logs_level_layout.addWidget(self.logs_level)
        logs_level_layout.addStretch()
        logs_layout.addLayout(logs_level_layout)

        logs_path_layout = QHBoxLayout()
        self.logs_path = QLineEdit()
        self.logs_path.setPlaceholderText("Путь для сохранения логов...")
        self.logs_path.setMinimumHeight(35)
        logs_path_layout.addWidget(self.logs_path)

        logs_path_btn = QPushButton("Обзор...")
        logs_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
        """)
        logs_path_btn.clicked.connect(self.choose_logs_path)
        logs_path_layout.addWidget(logs_path_btn)
        logs_layout.addLayout(logs_path_layout)

        layout.addWidget(logs_group)

        # Группа сброса настроек
        reset_group = QGroupBox("Сброс настроек")
        reset_group.setStyleSheet(cache_group.styleSheet())

        reset_layout = QVBoxLayout(reset_group)

        reset_btn = QPushButton("🔄 Сбросить все настройки")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        reset_layout.addWidget(reset_btn)

        layout.addWidget(reset_group)

        layout.addStretch()
        return page

    def create_about_page(self):
        """Создает страницу информации о программе"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Логотип
        logo_label = QLabel("IT-EcoSystem\nCRM")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        layout.addWidget(logo_label)

        # Версия
        version_label = QLabel("Версия 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #b0b0b0; font-size: 14px;")
        layout.addWidget(version_label)

        # Описание
        desc_label = QLabel(
            "CRM система для управления сервисным центром IT-EcoSystem.\n"
            "Позволяет управлять заказами, клиентами, складом и финансами.\n\n"
            "© 2024 IT-EcoSystem. Все права защищены."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #d0d0d0; font-size: 12px; padding: 20px;")
        layout.addWidget(desc_label)

        # Информация о разработчике
        dev_label = QLabel(
            "Разработка: IT-EcoSystem Team\n"
            "Поддержка: support@it-ecosystem.ru\n"
            "Веб-сайт: www.it-ecosystem.ru"
        )
        dev_label.setAlignment(Qt.AlignCenter)
        dev_label.setStyleSheet("color: #808080; font-size: 11px;")
        layout.addWidget(dev_label)

        layout.addStretch()
        return page

    def load_settings(self):
        """Загружает сохраненные настройки"""
        # Получаем данные пользователя безопасно
        user_name = ''
        user_surname = ''
        user_email = ''
        user_phone = ''

        if self.current_user:
            user_name = self.current_user.get('FirstName', '') if isinstance(self.current_user, dict) else ''
            user_surname = self.current_user.get('LastName', '') if isinstance(self.current_user, dict) else ''
            user_email = self.current_user.get('Email', '') if isinstance(self.current_user, dict) else ''
            user_phone = self.current_user.get('PhoneNumber', '') if isinstance(self.current_user, dict) else ''

        # Профиль
        self.name_edit.setText(self.settings.value("profile/name", user_name))
        self.surname_edit.setText(self.settings.value("profile/surname", user_surname))
        self.email_edit.setText(self.settings.value("profile/email", user_email))
        self.phone_edit.setText(self.settings.value("profile/phone", user_phone))

        self.show_tooltips.setChecked(self.settings.value("profile/show_tooltips", True, type=bool))
        self.confirm_exit.setChecked(self.settings.value("profile/confirm_exit", True, type=bool))
        self.auto_save.setChecked(self.settings.value("profile/auto_save", True, type=bool))

        # Внешний вид
        theme_index = self.settings.value("appearance/theme", 0, type=int)
        self.theme_combo.setCurrentIndex(theme_index)

        font_family = self.settings.value("appearance/font_family", "Segoe UI")
        font_size = self.settings.value("appearance/font_size", 10, type=int)
        self.font_preview.setText(f"{font_family}, {font_size}pt")
        self.font_size_spin.setValue(font_size)

        # Уведомления
        self.notify_new_orders.setChecked(self.settings.value("notifications/new_orders", True, type=bool))
        self.notify_status_change.setChecked(self.settings.value("notifications/status_change", True, type=bool))
        self.notify_comments.setChecked(self.settings.value("notifications/comments", True, type=bool))
        self.notify_deadlines.setChecked(self.settings.value("notifications/deadlines", True, type=bool))

        self.enable_sound.setChecked(self.settings.value("notifications/enable_sound", False, type=bool))
        self.sound_file_edit.setText(self.settings.value("notifications/sound_file", ""))

        self.enable_email.setChecked(self.settings.value("notifications/enable_email", False, type=bool))
        self.email_digest.setChecked(self.settings.value("notifications/email_digest", False, type=bool))

        # База данных
        self.db_host.setText(self.settings.value("database/host", "localhost"))
        self.db_port.setValue(self.settings.value("database/port", 3306, type=int))
        self.db_name.setText(self.settings.value("database/name", "SQL_IT_EcoSyttem_BD"))
        self.db_user.setText(self.settings.value("database/user", ""))

        self.auto_backup.setChecked(self.settings.value("database/auto_backup", False, type=bool))
        self.backup_freq.setCurrentIndex(self.settings.value("database/backup_freq", 1, type=int))
        self.backup_path.setText(self.settings.value("database/backup_path", ""))

        # Системные
        self.clear_cache_on_exit.setChecked(self.settings.value("system/clear_cache_on_exit", False, type=bool))
        self.enable_logging.setChecked(self.settings.value("system/enable_logging", True, type=bool))
        self.logs_level.setCurrentText(self.settings.value("system/logs_level", "INFO"))
        self.logs_path.setText(self.settings.value("system/logs_path", ""))

    def save_settings(self):
        """Сохраняет все настройки"""
        # Профиль
        self.settings.setValue("profile/name", self.name_edit.text())
        self.settings.setValue("profile/surname", self.surname_edit.text())
        self.settings.setValue("profile/email", self.email_edit.text())
        self.settings.setValue("profile/phone", self.phone_edit.text())
        self.settings.setValue("profile/show_tooltips", self.show_tooltips.isChecked())
        self.settings.setValue("profile/confirm_exit", self.confirm_exit.isChecked())
        self.settings.setValue("profile/auto_save", self.auto_save.isChecked())

        # Внешний вид
        self.settings.setValue("appearance/theme", self.theme_combo.currentIndex())
        self.settings.setValue("appearance/font_size", self.font_size_spin.value())

        # Уведомления
        self.settings.setValue("notifications/new_orders", self.notify_new_orders.isChecked())
        self.settings.setValue("notifications/status_change", self.notify_status_change.isChecked())
        self.settings.setValue("notifications/comments", self.notify_comments.isChecked())
        self.settings.setValue("notifications/deadlines", self.notify_deadlines.isChecked())
        self.settings.setValue("notifications/enable_sound", self.enable_sound.isChecked())
        self.settings.setValue("notifications/sound_file", self.sound_file_edit.text())
        self.settings.setValue("notifications/enable_email", self.enable_email.isChecked())
        self.settings.setValue("notifications/email_digest", self.email_digest.isChecked())

        # База данных
        self.settings.setValue("database/host", self.db_host.text())
        self.settings.setValue("database/port", self.db_port.value())
        self.settings.setValue("database/name", self.db_name.text())
        self.settings.setValue("database/user", self.db_user.text())
        self.settings.setValue("database/auto_backup", self.auto_backup.isChecked())
        self.settings.setValue("database/backup_freq", self.backup_freq.currentIndex())
        self.settings.setValue("database/backup_path", self.backup_path.text())

        # Системные
        self.settings.setValue("system/clear_cache_on_exit", self.clear_cache_on_exit.isChecked())
        self.settings.setValue("system/enable_logging", self.enable_logging.isChecked())
        self.settings.setValue("system/logs_level", self.logs_level.currentText())
        self.settings.setValue("system/logs_path", self.logs_path.text())

        # Сохраняем пароль БД отдельно (зашифрованно)
        if self.db_password.text():
            self.settings.setValue("database/password", self.db_password.text())

        # Применяем настройки темы
        self.apply_theme()

        # Применяем настройки шрифта
        self.apply_font()

        # Эмитируем сигнал о сохранении
        self.settings_saved.emit()

        QMessageBox.information(self, "Успех", "Настройки успешно сохранены!")
        self.accept()

    def choose_font(self):
        """Выбор шрифта"""
        current_font = QFont(self.font_preview.text().split(',')[0] if ',' in self.font_preview.text() else "Segoe UI",
                             self.font_size_spin.value())
        font, ok = QFontDialog.getFont(current_font, self, "Выберите шрифт")
        if ok:
            self.font_preview.setText(f"{font.family()}, {font.pointSize()}pt")
            self.font_size_spin.setValue(font.pointSize())

    def choose_color(self, color_type):
        """Выбор цвета"""
        color = QColorDialog.getColor(Qt.green, self, f"Выберите {color_type} цвет")
        if color.isValid():
            if color_type == "primary":
                self.primary_color_btn.setStyleSheet(f"background-color: {color.name()}; color: white;")
            else:
                self.secondary_color_btn.setStyleSheet(f"background-color: {color.name()}; color: white;")

    def choose_sound_file(self):
        """Выбор звукового файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите звуковой файл", "",
            "Звуковые файлы (*.wav *.mp3);;Все файлы (*.*)"
        )
        if file_path:
            self.sound_file_edit.setText(file_path)

    def choose_backup_path(self):
        """Выбор пути для бэкапов"""
        path = QFileDialog.getExistingDirectory(self, "Выберите папку для бэкапов")
        if path:
            self.backup_path.setText(path)

    def choose_logs_path(self):
        """Выбор пути для логов"""
        path = QFileDialog.getExistingDirectory(self, "Выберите папку для логов")
        if path:
            self.logs_path.setText(path)

    def test_db_connection(self):
        """Тестирование подключения к БД"""
        try:
            import mysql.connector
            connection = mysql.connector.connect(
                host=self.db_host.text(),
                port=self.db_port.value(),
                user=self.db_user.text(),
                password=self.db_password.text(),
                database=self.db_name.text(),
                connect_timeout=5
            )
            connection.close()
            QMessageBox.information(self, "Успех", "Подключение к базе данных успешно!")
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к БД:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения:\n{str(e)}")

    def create_backup(self):
        """Создание резервной копии БД"""
        try:
            import subprocess
            import datetime

            backup_path = self.backup_path.text()
            if not backup_path:
                backup_path = os.path.expanduser("~/Documents/CRM_Backups")
                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_path, f"crm_backup_{timestamp}.sql")

            # Формируем команду mysqldump
            cmd = [
                "mysqldump",
                f"--host={self.db_host.text()}",
                f"--port={self.db_port.value()}",
                f"--user={self.db_user.text()}",
                f"--password={self.db_password.text()}",
                self.db_name.text(),
                "--result-file=" + backup_file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                QMessageBox.information(self, "Успех", f"Резервная копия создана:\n{backup_file}")
            else:
                QMessageBox.warning(self, "Предупреждение", f"Бэкап создан, но с предупреждениями:\n{result.stderr}")

        except subprocess.TimeoutExpired:
            QMessageBox.critical(self, "Ошибка", "Создание бэкапа превысило время ожидания")
        except FileNotFoundError:
            QMessageBox.critical(self, "Ошибка", "mysqldump не найден. Убедитесь, что MySQL установлен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать бэкап:\n{str(e)}")

    def clear_cache(self):
        """Очистка кэша"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите очистить кэш?\nЭто действие необратимо.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                import shutil
                temp_dir = os.path.join(os.path.expanduser("~"), ".crm_cache")
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                QMessageBox.information(self, "Успех", "Кэш успешно очищен!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось очистить кэш:\n{str(e)}")

    def reset_settings(self):
        """Сброс всех настроек"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите сбросить все настройки?\n"
            "Это действие необратимо и вернет все настройки к значениям по умолчанию.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.settings.clear()
            self.load_settings()
            QMessageBox.information(self, "Успех", "Настройки сброшены к значениям по умолчанию!")

    def apply_theme(self):
        """Применяет выбранную тему"""
        theme_index = self.theme_combo.currentIndex()
        self.theme_changed.emit(self.theme_combo.currentText())

        # Обновляем предпросмотр
        themes = {
            0: """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1a1a1a, stop:1 #2a2a2a);
                }
            """,
            1: """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #f5f5f5, stop:1 #ffffff);
                }
            """,
            2: """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1976D2, stop:1 #2196F3);
                }
            """,
            3: """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #388E3C, stop:1 #4CAF50);
                }
            """,
            4: """
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #F57C00, stop:1 #FF9800);
                }
            """
        }

        if theme_index in themes:
            self.preview_frame.setStyleSheet(themes[theme_index])

    def apply_font(self):
        """Применяет выбранный шрифт"""
        font_family = self.font_preview.text().split(',')[0] if ',' in self.font_preview.text() else "Segoe UI"
        font_size = self.font_size_spin.value()
        font = QFont(font_family, font_size)
        self.font_changed.emit(font)


# ==================== ТЕСТИРОВАНИЕ ====================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())