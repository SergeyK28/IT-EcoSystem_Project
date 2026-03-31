# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from typing import Dict, List, Any
from Server import db_crm


class NotificationsDialog(QtWidgets.QDialog):
    def __init__(self, employee_id: int, parent=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.notifications = []
        self.setup_ui()
        self.load_notifications()

    def setup_ui(self):
        """Настраивает интерфейс диалога"""
        self.setWindowTitle("Уведомления")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        # Стиль окна
        self.setStyleSheet("""
            QDialog {
                background-color: #2a2a2a;
                border-radius: 10px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QListWidget {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                color: #ffffff;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #4a4a4a;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
        """)

        # Основной layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QtWidgets.QLabel("📬 Уведомления")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding-bottom: 10px;")
        layout.addWidget(title_label)

        # Список уведомлений
        self.notifications_list = QtWidgets.QListWidget()
        self.notifications_list.itemDoubleClicked.connect(self.on_notification_clicked)
        layout.addWidget(self.notifications_list)

        # Кнопки
        buttons_layout = QtWidgets.QHBoxLayout()

        self.mark_all_read_btn = QtWidgets.QPushButton("✓ Отметить все как прочитанные")
        self.mark_all_read_btn.clicked.connect(self.mark_all_read)

        self.clear_btn = QtWidgets.QPushButton("🗑 Очистить прочитанные")
        self.clear_btn.clicked.connect(self.clear_read)

        self.close_btn = QtWidgets.QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(self.mark_all_read_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)

        layout.addLayout(buttons_layout)

    def load_notifications(self):
        """Загружает уведомления из БД"""
        self.notifications = db_crm.get_user_notifications(self.employee_id, limit=100, include_read=True)
        self.update_list()

    def update_list(self):
        """Обновляет список уведомлений"""
        self.notifications_list.clear()

        for notif in self.notifications:
            # Создаем виджет для уведомления
            widget = QtWidgets.QWidget()
            widget_layout = QtWidgets.QVBoxLayout(widget)
            widget_layout.setSpacing(5)
            widget_layout.setContentsMargins(10, 10, 10, 10)

            # Заголовок с иконкой типа
            title_layout = QtWidgets.QHBoxLayout()

            # Иконка в зависимости от типа
            icon_map = {
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌',
                'order': '📦',
                'stock': '📊',
                'payment': '💰'
            }
            icon = icon_map.get(notif['Type'], '🔔')

            title_label = QtWidgets.QLabel(f"{icon} {notif['Title']}")
            title_label.setStyleSheet("font-weight: bold; font-size: 13px;")

            date_label = QtWidgets.QLabel(notif['CreatedAtFormatted'])
            date_label.setStyleSheet("color: #888888; font-size: 10px;")

            title_layout.addWidget(title_label)
            title_layout.addStretch()
            title_layout.addWidget(date_label)

            widget_layout.addLayout(title_layout)

            # Сообщение
            message_label = QtWidgets.QLabel(notif['Message'])
            message_label.setWordWrap(True)
            message_label.setStyleSheet("color: #cccccc; font-size: 11px;")
            widget_layout.addWidget(message_label)

            # Статус прочтения
            if not notif['IsRead']:
                unread_label = QtWidgets.QLabel("● Новое")
                unread_label.setStyleSheet("color: #4CAF50; font-size: 9px;")
                widget_layout.addWidget(unread_label)

            # Добавляем виджет в список
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.notifications_list.addItem(item)
            self.notifications_list.setItemWidget(item, widget)

            # Сохраняем ID уведомления для элемента
            item.setData(Qt.UserRole, notif['NotificationID'])
            item.setData(Qt.UserRole + 1, notif)

    def on_notification_clicked(self, item):
        """Обработка двойного клика по уведомлению"""
        notification_id = item.data(Qt.UserRole)
        notification_data = item.data(Qt.UserRole + 1)

        # Отмечаем как прочитанное
        db_crm.mark_notification_as_read(notification_id, self.employee_id)

        # Обновляем вид элемента
        self.load_notifications()

        # Если есть ссылка, открываем её
        link_to = notification_data.get('LinkTo')
        if link_to:
            # Здесь можно реализовать переход по ссылке
            print(f"Переход по ссылке: {link_to}")

    def mark_all_read(self):
        """Отмечает все уведомления как прочитанные"""
        count = db_crm.mark_all_notifications_as_read(self.employee_id)
        if count > 0:
            self.load_notifications()
            QtWidgets.QMessageBox.information(
                self, "Успех", f"Отмечено {count} уведомлений как прочитанные"
            )

    def clear_read(self):
        """Удаляет прочитанные уведомления"""
        deleted = 0
        for notif in self.notifications:
            if notif['IsRead']:
                if db_crm.delete_notification(notif['NotificationID'], self.employee_id):
                    deleted += 1

        if deleted > 0:
            self.load_notifications()
            QtWidgets.QMessageBox.information(
                self, "Успех", f"Удалено {deleted} прочитанных уведомлений"
            )