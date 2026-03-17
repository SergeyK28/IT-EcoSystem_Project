# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette, QPixmap, QIcon
from PyQt5.QtWidgets import (QGraphicsDropShadowEffect, QLabel, QPushButton, QFrame,
                             QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QWidget, QGridLayout, QMenu, QAction)

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from Server import db
import Server.globals as globals
from session_manager import session


class FavoriteItemWidget(QFrame):
    """Виджет для отображения одного элемента избранного"""

    removed = pyqtSignal(int)  # Сигнал при удалении элемента

    def __init__(self, favorite_data, parent=None):
        super().__init__(parent)
        self.favorite_id = favorite_data['FavoriteID']
        self.item_type = favorite_data['ItemType']
        self.item_id = favorite_data['ItemID']
        self.item_name = favorite_data['ItemName']
        self.item_price = favorite_data['ItemPrice']
        self.item_category = favorite_data['ItemCategory']
        self.date_added = favorite_data.get('DateAddedFormatted', '')
        self.notes = favorite_data.get('Notes', '')

        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)
        self.setStyleSheet("""
            FavoriteItemWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #252525);
                border-radius: 15px;
                border: 1px solid #3a3a3a;
            }
            FavoriteItemWidget:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d2d, stop:1 #282828);
                border: 1px solid #4CAF50;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)

        # Иконка в зависимости от типа
        icon_frame = QFrame()
        icon_frame.setFixedSize(60, 60)
        icon_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(76, 175, 80, 0.2), stop:1 rgba(76, 175, 80, 0.1));
                border-radius: 12px;
                border: 1px solid #4CAF50;
            }
        """)

        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)

        # Выбираем иконку в зависимости от типа
        if self.item_type == 'service':
            icon_label.setText("🔧")
        else:
            icon_label.setText("🔩")

        icon_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 30px;
                background: none;
                border: none;
            }
        """)

        icon_layout.addWidget(icon_label)

        # Информация о товаре
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        # Название и тип
        title_layout = QHBoxLayout()

        name_label = QLabel(self.item_name)
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)

        type_badge = QLabel("Услуга" if self.item_type == 'service' else "Запчасть")
        type_badge.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 11px;
                font-weight: 600;
                background-color: rgba(76, 175, 80, 0.15);
                border: 1px solid #4CAF50;
                border-radius: 10px;
                padding: 2px 10px;
            }
        """)

        title_layout.addWidget(name_label)
        title_layout.addStretch()
        title_layout.addWidget(type_badge)

        info_layout.addLayout(title_layout)

        # Категория
        if self.item_category:
            category_label = QLabel(f"📁 {self.item_category}")
            category_label.setStyleSheet("""
                QLabel {
                    color: #b0b0b0;
                    font-size: 13px;
                }
            """)
            info_layout.addWidget(category_label)

        # Цена и дата
        details_layout = QHBoxLayout()

        price_label = QLabel(f"💰 {self.item_price:.2f} ₽" if self.item_price else "💰 Цена по запросу")
        price_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 600;
            }
        """)

        if self.date_added:
            date_label = QLabel(f"📅 {self.date_added}")
            date_label.setStyleSheet("""
                QLabel {
                    color: #808080;
                    font-size: 12px;
                }
            """)
            details_layout.addWidget(date_label)

        details_layout.addStretch()
        details_layout.addWidget(price_label)

        info_layout.addLayout(details_layout)

        # Кнопки действий
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)

        # Кнопка удалить
        self.remove_btn = QPushButton("🗑️")
        self.remove_btn.setFixedSize(36, 36)
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ff6b6b;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                color: white;
            }
            QPushButton:pressed {
                background-color: #ff5252;
            }
        """)
        self.remove_btn.clicked.connect(self.on_remove_clicked)

        # Кнопка перейти
        self.view_btn = QPushButton("👁️")
        self.view_btn.setFixedSize(36, 36)
        self.view_btn.setCursor(Qt.PointingHandCursor)
        self.view_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #4CAF50;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:pressed {
                background-color: #45a049;
            }
        """)
        self.view_btn.clicked.connect(self.on_view_clicked)

        buttons_layout.addWidget(self.remove_btn)
        buttons_layout.addWidget(self.view_btn)

        layout.addWidget(icon_frame)
        layout.addLayout(info_layout, 1)
        layout.addLayout(buttons_layout)

    def on_remove_clicked(self):
        """Обработчик удаления из избранного"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить '{self.item_name}' из избранного?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if db.remove_from_favorites(session.get_user_id(), self.favorite_id):
                self.removed.emit(self.favorite_id)

    def on_view_clicked(self):
        """Обработчик перехода к элементу"""
        if self.item_type == 'service':
            # Открываем окно услуги
            if "телефон" in self.item_name.lower():
                self.open_service_window("telefon")
            elif "ноутбук" in self.item_name.lower():
                self.open_service_window("laptop")
            else:
                QMessageBox.information(
                    self,
                    "Информация",
                    f"Просмотр услуги: {self.item_name}"
                )
        else:
            # Для запчастей
            QMessageBox.information(
                self,
                "Информация",
                f"Просмотр запчасти: {self.item_name}\nЦена: {self.item_price} ₽"
            )

    def open_service_window(self, service_type):
        """Открывает окно соответствующей услуги"""
        if service_type == "telefon":
            from Client.Remont_windows.remont_telefonov import Ui_Ui_Remont_Telefonov_Dialog
            self.dialog = QtWidgets.QDialog()
            self.ui = Ui_Ui_Remont_Telefonov_Dialog()
            self.ui.setupUi(self.dialog)
            self.dialog.show()
        elif service_type == "laptop":
            from Client.Remont_windows.remont_laptop import Ui_Ui_Remont_Laptop_Dialog
            self.dialog = QtWidgets.QDialog()
            self.ui = Ui_Ui_Remont_Laptop_Dialog()
            self.ui.setupUi(self.dialog)
            self.dialog.show()


class FavoritesWindow(QDialog):
    """Окно избранного"""

    def __init__(self, parent=None):
        super(FavoritesWindow, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(900, 700)
        self.setMinimumSize(800, 500)

        self.favorites = []
        self.setupUi()
        self.load_favorites()

    def setupUi(self):
        # Главный контейнер с тенью
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, self.width(), self.height())
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 30px;
                border: 1px solid #3a3a3a;
            }
        """)

        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(30)
        main_shadow.setColor(QColor(0, 0, 0, 150))
        main_shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(main_shadow)

        # Основной layout
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Верхняя панель
        top_layout = QHBoxLayout()

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
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        # Заголовок
        title_label = QLabel("❤️ Моё избранное")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        # Кнопка очистить всё
        self.btn_clear_all = QPushButton("🗑️ Очистить всё")
        self.btn_clear_all.setCursor(Qt.PointingHandCursor)
        self.btn_clear_all.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ff6b6b;
                border: 2px solid #ff6b6b;
                border-radius: 10px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                color: white;
            }
            QPushButton:pressed {
                background-color: #ff5252;
            }
        """)
        self.btn_clear_all.clicked.connect(self.clear_all_favorites)

        top_layout.addWidget(self.btn_close)
        top_layout.addStretch()
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_clear_all)

        main_layout.addLayout(top_layout)

        # Статистика
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # Всего элементов
        self.total_count_label = QLabel("📊 Всего: 0")
        self.total_count_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: 600;
                background-color: rgba(76, 175, 80, 0.1);
                border: 1px solid #4CAF50;
                border-radius: 10px;
                padding: 10px 20px;
            }
        """)

        # Услуг
        self.services_count_label = QLabel("🔧 Услуг: 0")
        self.services_count_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px 20px;
            }
        """)

        # Запчастей
        self.parts_count_label = QLabel("🔩 Запчастей: 0")
        self.parts_count_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px 20px;
            }
        """)

        stats_layout.addWidget(self.total_count_label)
        stats_layout.addWidget(self.services_count_label)
        stats_layout.addWidget(self.parts_count_label)
        stats_layout.addStretch()

        main_layout.addLayout(stats_layout)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                max-height: 1px;
                min-height: 1px;
                margin: 5px 0;
            }
        """)
        main_layout.addWidget(separator)

        # Область прокрутки для элементов избранного
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 5px;
                min-height: 40px;
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

        # Контейнер для элементов
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")

        self.favorites_layout = QVBoxLayout(self.scroll_content)
        self.favorites_layout.setContentsMargins(5, 5, 5, 5)
        self.favorites_layout.setSpacing(15)
        self.favorites_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # Сообщение о пустом избранном
        self.empty_message = QLabel(
            "✨ Ваше избранное пусто\n\nДобавляйте понравившиеся услуги и товары,\nнажимая на сердечко ❤️")
        self.empty_message.setAlignment(Qt.AlignCenter)
        self.empty_message.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 18px;
                font-weight: 500;
                padding: 50px;
            }
        """)
        self.empty_message.hide()
        self.favorites_layout.addWidget(self.empty_message)

        self.setLayout(main_layout)

    def load_favorites(self):
        """Загружает избранное пользователя"""
        if not session.is_authenticated():
            self.close()
            return

        user_id = session.get_user_id()
        self.favorites = db.get_user_favorites(user_id)

        # Обновляем статистику
        self.update_statistics()

        # Очищаем существующие элементы
        self.clear_favorites_display()

        if not self.favorites:
            self.empty_message.show()
            return

        self.empty_message.hide()

        # Добавляем элементы
        for fav in self.favorites:
            widget = FavoriteItemWidget(fav)
            widget.removed.connect(self.on_item_removed)
            self.favorites_layout.insertWidget(self.favorites_layout.count() - 1, widget)

    def clear_favorites_display(self):
        """Очищает отображение избранного"""
        for i in reversed(range(self.favorites_layout.count() - 1)):
            item = self.favorites_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

    def update_statistics(self):
        """Обновляет статистику"""
        total = len(self.favorites)
        services = sum(1 for f in self.favorites if f['ItemType'] == 'service')
        parts = sum(1 for f in self.favorites if f['ItemType'] == 'part')

        self.total_count_label.setText(f"📊 Всего: {total}")
        self.services_count_label.setText(f"🔧 Услуг: {services}")
        self.parts_count_label.setText(f"🔩 Запчастей: {parts}")

    def on_item_removed(self, favorite_id):
        """Обработчик удаления элемента"""
        # Удаляем виджет
        for i in range(self.favorites_layout.count()):
            item = self.favorites_layout.itemAt(i)
            if item and item.widget() and hasattr(item.widget(), 'favorite_id'):
                if item.widget().favorite_id == favorite_id:
                    item.widget().deleteLater()
                    break

        # Обновляем список избранного
        self.favorites = [f for f in self.favorites if f['FavoriteID'] != favorite_id]

        # Обновляем статистику
        self.update_statistics()

        # Если избранное пустое, показываем сообщение
        if not self.favorites:
            self.empty_message.show()

    def clear_all_favorites(self):
        """Очищает всё избранное"""
        if not self.favorites:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите очистить всё избранное?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if db.clear_all_favorites(session.get_user_id()):
                # Очищаем отображение
                self.clear_favorites_display()
                self.favorites = []
                self.update_statistics()
                self.empty_message.show()

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        main_container = self.findChild(QFrame)
        if main_container:
            main_container.setGeometry(0, 0, self.width(), self.height())