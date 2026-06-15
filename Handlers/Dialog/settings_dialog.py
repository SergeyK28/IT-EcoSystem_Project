# -*- coding: utf-8 -*-
"""
Модуль настроек CRM системы.
Содержит диалоговое окно с настройками: профиль (только просмотр, смена пароля),
уведомления, база данных, о программе.
"""

import sys
import os
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                             QLineEdit, QPushButton, QCheckBox, QComboBox, QSpinBox,
                             QGroupBox, QFormLayout, QMessageBox, QFileDialog, QListWidget,
                             QListWidgetItem, QStackedWidget)

# Добавляем путь к корневой директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Handlers.Employees.employee_session import employee_session
from Server import db_crm

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env'


class SettingsDialog(QDialog):
    """Диалоговое окно настроек CRM"""

    settings_saved = pyqtSignal()
    theme_changed = pyqtSignal(str)
    font_changed = pyqtSignal(QFont)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("IT-EcoSystem", "CRM")

        # Получаем данные текущего сотрудника
        self.current_user = None
        self.employee_id = None
        if employee_session.is_authenticated():
            self.current_user = employee_session.get_employee_data()
            self.employee_id = employee_session.get_employee_id()

        self.setWindowTitle("Настройки CRM - IT-EcoSystem")
        self.setMinimumSize(900, 650)
        self.resize(950, 700)

        # Устанавливаем иконку
        icon_path = os.path.join(ROOT_DIR, "Pictures", "Screenshot from 2025-09-15 14-30-16.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        splitter = QtWidgets.QSplitter(Qt.Horizontal)

        # Левая панель навигации
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

        nav_items = [
            ("👤 Профиль", "profile"),
            ("🔔 Уведомления", "notifications"),
            ("📁 База данных", "database"),
            ("ℹ️ О программе", "about")
        ]

        for text, data in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, data)
            self.nav_list.addItem(item)

        splitter.addWidget(self.nav_list)

        # Правая панель (стек)
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        self.profile_page = self.create_profile_page()
        self.notifications_page = self.create_notifications_page()
        self.database_page = self.create_database_page()
        self.about_page = self.create_about_page()

        self.content_stack.addWidget(self.profile_page)
        self.content_stack.addWidget(self.notifications_page)
        self.content_stack.addWidget(self.database_page)
        self.content_stack.addWidget(self.about_page)

        splitter.addWidget(self.content_stack)
        splitter.setSizes([200, 700])

        main_layout.addWidget(splitter)

        # Кнопки внизу
        button_layout = QHBoxLayout()
        button_layout.addStretch()

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

        # Навигация
        self.nav_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        self.nav_list.setCurrentRow(0)

    def create_profile_page(self):
        """Страница профиля (только чтение + смена пароля)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        title = QLabel("Настройки профиля")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding-bottom: 10px;")
        layout.addWidget(title)

        # Личная информация (только чтение)
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

        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        self.surname_edit = QLineEdit()
        self.surname_edit.setReadOnly(True)
        self.email_edit = QLineEdit()
        self.email_edit.setReadOnly(True)
        self.phone_edit = QLineEdit()
        self.phone_edit.setReadOnly(True)

        for le in (self.name_edit, self.surname_edit, self.email_edit, self.phone_edit):
            le.setStyleSheet("""
                QLineEdit {
                    background-color: #3a3a3a;
                    color: #cccccc;
                    border: 1px solid #4a4a4a;
                    border-radius: 5px;
                    padding: 8px 12px;
                }
            """)

        personal_layout.addRow("Имя:", self.name_edit)
        personal_layout.addRow("Фамилия:", self.surname_edit)
        personal_layout.addRow("Email:", self.email_edit)
        personal_layout.addRow("Телефон:", self.phone_edit)

        layout.addWidget(personal_group)

        # Смена пароля
        password_group = QGroupBox("Смена пароля")
        password_group.setStyleSheet(personal_group.styleSheet())

        password_layout = QFormLayout(password_group)
        password_layout.setSpacing(15)
        password_layout.setLabelAlignment(Qt.AlignRight)

        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setPlaceholderText("Введите текущий пароль")
        self.old_password.setMinimumHeight(35)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Введите новый пароль (мин. 6 символов)")
        self.new_password.setMinimumHeight(35)

        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Подтвердите новый пароль")
        self.confirm_password.setMinimumHeight(35)

        for le in (self.old_password, self.new_password, self.confirm_password):
            le.setStyleSheet("""
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

        password_layout.addRow("Текущий пароль:", self.old_password)
        password_layout.addRow("Новый пароль:", self.new_password)
        password_layout.addRow("Подтверждение:", self.confirm_password)

        layout.addWidget(password_group)

        hint = QLabel("Пароль должен содержать не менее 6 символов")
        hint.setStyleSheet("color: #808080; font-size: 11px; margin-top: 5px;")
        layout.addWidget(hint)

        layout.addStretch()
        return page

    def create_notifications_page(self):
        """Настройки уведомлений"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        title = QLabel("Настройки уведомлений")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding-bottom: 10px;")
        layout.addWidget(title)

        # Общие
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
        self.notify_status_change = QCheckBox("Изменение статуса заказа")
        self.notify_comments = QCheckBox("Новые комментарии к заказу")
        self.notify_deadlines = QCheckBox("Приближение срока выполнения")
        for cb in (self.notify_new_orders, self.notify_status_change,
                   self.notify_comments, self.notify_deadlines):
            cb.setStyleSheet("color: #d0d0d0; padding: 5px;")
            general_layout.addWidget(cb)
        layout.addWidget(general_group)

        # Звук
        sound_group = QGroupBox("Звуковые уведомления")
        sound_group.setStyleSheet(general_group.styleSheet())
        sound_layout = QVBoxLayout(sound_group)
        self.enable_sound = QCheckBox("Включить звуковые уведомления")
        self.enable_sound.setStyleSheet("color: #d0d0d0; padding: 5px;")
        sound_layout.addWidget(self.enable_sound)

        file_layout = QHBoxLayout()
        self.sound_file_edit = QLineEdit()
        self.sound_file_edit.setReadOnly(True)
        self.sound_file_edit.setPlaceholderText("Выберите звуковой файл...")
        choose_btn = QPushButton("Обзор...")
        choose_btn.clicked.connect(self.choose_sound_file)
        for w in (self.sound_file_edit, choose_btn):
            w.setStyleSheet("""
                QLineEdit, QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: 1px solid #4a4a4a;
                    border-radius: 5px;
                    padding: 8px 12px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
            """)
        file_layout.addWidget(self.sound_file_edit)
        file_layout.addWidget(choose_btn)
        sound_layout.addLayout(file_layout)
        layout.addWidget(sound_group)

        # Email
        email_group = QGroupBox("Уведомления на почту")
        email_group.setStyleSheet(general_group.styleSheet())
        email_layout = QVBoxLayout(email_group)
        self.enable_email = QCheckBox("Отправлять уведомления на почту")
        self.email_digest = QCheckBox("Ежедневный дайджест")
        for cb in (self.enable_email, self.email_digest):
            cb.setStyleSheet("color: #d0d0d0; padding: 5px;")
            email_layout.addWidget(cb)
        layout.addWidget(email_group)

        layout.addStretch()
        return page

    def create_database_page(self):
        """Настройки базы данных с сохранением в .env"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        title = QLabel("Настройки базы данных")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50; padding-bottom: 10px;")
        layout.addWidget(title)

        # Группа подключения
        conn_group = QGroupBox("Параметры подключения")
        conn_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        conn_layout = QFormLayout(conn_group)
        conn_layout.setSpacing(15)
        conn_layout.setLabelAlignment(Qt.AlignRight)

        self.db_host = QLineEdit()
        self.db_port = QSpinBox()
        self.db_name = QLineEdit()
        self.db_user = QLineEdit()
        self.db_password = QLineEdit()
        self.db_password.setEchoMode(QLineEdit.Password)

        for w in (self.db_host, self.db_name, self.db_user, self.db_password):
            w.setStyleSheet("""
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
        self.db_port.setStyleSheet("""
            QSpinBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.db_port.setRange(1, 65535)
        self.db_port.setValue(3306)

        conn_layout.addRow("Хост:", self.db_host)
        conn_layout.addRow("Порт:", self.db_port)
        conn_layout.addRow("База данных:", self.db_name)
        conn_layout.addRow("Пользователь:", self.db_user)
        conn_layout.addRow("Пароль:", self.db_password)

        test_btn = QPushButton("🔌 Тестировать подключение")
        test_btn.clicked.connect(self.test_db_connection)
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
        conn_layout.addRow(test_btn)

        layout.addWidget(conn_group)

        # Резервное копирование
        backup_group = QGroupBox("Резервное копирование")
        backup_group.setStyleSheet(conn_group.styleSheet())
        backup_layout = QVBoxLayout(backup_group)

        self.auto_backup = QCheckBox("Автоматическое резервное копирование")
        self.auto_backup.setStyleSheet("color: #d0d0d0; padding: 5px;")
        backup_layout.addWidget(self.auto_backup)

        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Частота:"))
        self.backup_freq = QComboBox()
        self.backup_freq.addItems(["Ежедневно", "Еженедельно", "Ежемесячно"])
        freq_layout.addWidget(self.backup_freq)
        freq_layout.addStretch()
        backup_layout.addLayout(freq_layout)

        path_layout = QHBoxLayout()
        self.backup_path = QLineEdit()
        self.backup_path.setPlaceholderText("Путь для сохранения бэкапов...")
        self.backup_path.setStyleSheet(self.db_host.styleSheet())
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.choose_backup_path)
        browse_btn.setStyleSheet("""
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
        path_layout.addWidget(self.backup_path)
        path_layout.addWidget(browse_btn)
        backup_layout.addLayout(path_layout)

        create_backup_btn = QPushButton("💾 Создать резервную копию сейчас")
        create_backup_btn.clicked.connect(self.create_backup)
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
        backup_layout.addWidget(create_backup_btn)

        layout.addWidget(backup_group)
        layout.addStretch()
        return page

    def create_about_page(self):
        """О программе"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        logo = QLabel("IT-EcoSystem\nCRM")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 32px; font-weight: bold; color: #4CAF50; padding: 20px;")

        version = QLabel("Версия 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #b0b0b0; font-size: 14px;")

        desc = QLabel(
            "CRM система для управления сервисным центром IT-EcoSystem.\n"
            "Позволяет управлять заказами, клиентами, складом и финансами.\n\n"
            "© 2026 IT-EcoSystem. Все права защищены."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #d0d0d0; font-size: 12px; padding: 20px;")

        dev = QLabel(
            "Разработка: IT-EcoSystem Team\n"
            "Поддержка: support@it-ecosystem.ru\n"
            "Веб-сайт: www.it-ecosystem.ru"
        )
        dev.setAlignment(Qt.AlignCenter)
        dev.setStyleSheet("color: #808080; font-size: 11px;")

        layout.addWidget(logo)
        layout.addWidget(version)
        layout.addWidget(desc)
        layout.addWidget(dev)
        layout.addStretch()
        return page

    def load_settings(self):
        """Загрузка сохранённых настроек"""
        # Профиль (из сессии)
        if self.current_user:
            self.name_edit.setText(self.current_user.get('FirstName', ''))
            self.surname_edit.setText(self.current_user.get('LastName', ''))
            self.email_edit.setText(self.current_user.get('Email', ''))
            self.phone_edit.setText(self.current_user.get('PhoneNumber', ''))

        # Уведомления
        self.notify_new_orders.setChecked(self.settings.value("notifications/new_orders", True, bool))
        self.notify_status_change.setChecked(self.settings.value("notifications/status_change", True, bool))
        self.notify_comments.setChecked(self.settings.value("notifications/comments", True, bool))
        self.notify_deadlines.setChecked(self.settings.value("notifications/deadlines", True, bool))
        self.enable_sound.setChecked(self.settings.value("notifications/enable_sound", False, bool))
        self.sound_file_edit.setText(self.settings.value("notifications/sound_file", ""))
        self.enable_email.setChecked(self.settings.value("notifications/enable_email", False, bool))
        self.email_digest.setChecked(self.settings.value("notifications/email_digest", False, bool))

        # База данных
        self.db_host.setText(self.settings.value("database/host", "localhost"))
        self.db_port.setValue(self.settings.value("database/port", 3306, int))
        self.db_name.setText(self.settings.value("database/name", "SQL_IT_EcoSyttem_BD"))
        self.db_user.setText(self.settings.value("database/user", ""))
        # пароль не загружаем
        self.auto_backup.setChecked(self.settings.value("database/auto_backup", False, bool))
        self.backup_freq.setCurrentIndex(self.settings.value("database/backup_freq", 1, int))
        self.backup_path.setText(self.settings.value("database/backup_path", ""))

    def save_settings(self):
        """Сохранение настроек"""
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
        if self.db_password.text():
            self.settings.setValue("database/password", self.db_password.text())
        self.settings.setValue("database/auto_backup", self.auto_backup.isChecked())
        self.settings.setValue("database/backup_freq", self.backup_freq.currentIndex())
        self.settings.setValue("database/backup_path", self.backup_path.text())

        # Сохраняем в .env
        self.save_db_settings_to_env()

        # Смена пароля
        old = self.old_password.text().strip()
        new = self.new_password.text().strip()
        confirm = self.confirm_password.text().strip()

        if old and new and confirm:
            if new != confirm:
                QMessageBox.warning(self, "Ошибка", "Новый пароль и подтверждение не совпадают")
                return
            if len(new) < 6:
                QMessageBox.warning(self, "Ошибка", "Пароль должен содержать не менее 6 символов")
                return
            if not self.employee_id:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить сотрудника")
                return

            try:
                success, msg = db_crm.update_employee_password(self.employee_id, old, new)
                if success:
                    QMessageBox.information(self, "Успех", msg)
                    self.old_password.clear()
                    self.new_password.clear()
                    self.confirm_password.clear()
                else:
                    QMessageBox.warning(self, "Ошибка", msg)
                    return
            except AttributeError:
                QMessageBox.critical(self, "Ошибка", "Функция обновления пароля не найдена в db_crm")
                return

        self.settings_saved.emit()
        QMessageBox.information(self, "Успех", "Настройки успешно сохранены!")
        self.accept()

    def save_db_settings_to_env(self):
        """Сохраняет параметры БД в .env файл"""
        if not ENV_PATH.exists():
            ENV_PATH.touch()

        params = {
            'DB_HOST': self.db_host.text(),
            'DB_PORT': str(self.db_port.value()),
            'DB_NAME': self.db_name.text(),
            'DB_USER': self.db_user.text(),
            'DB_PASSWORD': self.db_password.text() if self.db_password.text() else ''
        }

        lines = []
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated = set()
        for i, line in enumerate(lines):
            for key, val in params.items():
                if line.startswith(f'{key}='):
                    lines[i] = f'{key}={val}\n'
                    updated.add(key)
                    break

        for key, val in params.items():
            if key not in updated:
                lines.append(f'{key}={val}\n')

        with open(ENV_PATH, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def choose_sound_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите звуковой файл", "", "Звуковые файлы (*.wav *.mp3);;Все файлы (*.*)")
        if path:
            self.sound_file_edit.setText(path)

    def choose_backup_path(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку для бэкапов")
        if path:
            self.backup_path.setText(path)

    def test_db_connection(self):
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=self.db_host.text(),
                port=self.db_port.value(),
                user=self.db_user.text(),
                password=self.db_password.text(),
                database=self.db_name.text(),
                connect_timeout=5
            )
            conn.close()
            QMessageBox.information(self, "Успех", "Подключение к базе данных успешно!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения:\n{str(e)}")

    def create_backup(self):
        try:
            import subprocess, datetime
            backup_path = self.backup_path.text().strip()
            if not backup_path:
                backup_path = os.path.expanduser("~/Documents/CRM_Backups")
                os.makedirs(backup_path, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_path, f"crm_backup_{timestamp}.sql")

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
                QMessageBox.warning(self, "Предупреждение", f"Бэкап создан с предупреждениями:\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать бэкап:\n{str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dlg = SettingsDialog()
    dlg.show()
    sys.exit(app.exec_())