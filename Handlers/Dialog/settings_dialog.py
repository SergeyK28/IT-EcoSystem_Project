# -*- coding: utf-8 -*-
"""
Модуль настроек CRM системы.
Содержит диалоговое окно с настройками: профиль (только просмотр, смена пароля),
уведомления, о программе.
"""

import sys
import os
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                             QLineEdit, QPushButton, QCheckBox, QGroupBox,
                             QFormLayout, QMessageBox, QFileDialog, QListWidget,
                             QListWidgetItem, QStackedWidget)

# Добавляем путь к корневой директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Handlers.Employees.employee_session import employee_session
from Server import db_crm

ROOT_DIR = Path(__file__).resolve().parent.parent


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
        self.about_page = self.create_about_page()

        self.content_stack.addWidget(self.profile_page)
        self.content_stack.addWidget(self.notifications_page)
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

    def choose_sound_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите звуковой файл", "", "Звуковые файлы (*.wav *.mp3);;Все файлы (*.*)")
        if path:
            self.sound_file_edit.setText(path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dlg = SettingsDialog()
    dlg.show()
    sys.exit(app.exec_())