# -*- coding: utf-8 -*-
"""
Модуль главного окна CRM системы IT-EcoSystem (упрощённый дизайн).
Содержит основной интерфейс для управления заказами, клиентами, складом и другими функциями.
"""

import sys
import os
from typing import Dict, List, Any

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import (
    QMessageBox, QDialog, QTableWidgetItem,
    QApplication
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Handlers.Employees.employee_session import employee_session
from Handlers.Dialog.reports_dialog import ReportsDialog
from Handlers.Employees.employee_profile import EmployeeProfileDialog
from Handlers.Dialog.trends_dialog import TrendsDialog
from Server import db_crm


class Ui_main_window_CRM:
    """
    Класс, отвечающий за создание и управление интерфейсом главного окна CRM.
    Упрощённый дизайн – без теней, градиентов и излишних декораций.
    """

    def setupUi(self, main_window_CRM):
        main_window_CRM.setObjectName("main_window_CRM")
        main_window_CRM.resize(1400, 950)

        # Простой тёмный фон
        main_window_CRM.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
        """)

        icon_path = "../Pictures/Screenshot from 2025-09-15 14-30-16.png"
        if os.path.exists(icon_path):
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            main_window_CRM.setWindowIcon(icon)

        # ===== Главный горизонтальный макет =====
        self.horizontalLayout = QtWidgets.QHBoxLayout(main_window_CRM)
        self.horizontalLayout.setContentsMargins(15, 15, 15, 15)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # ===== Область прокрутки =====
        self.scrollArea = QtWidgets.QScrollArea(main_window_CRM)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 10px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 2px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #2d7d3a;
            }
        """)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setStyleSheet("background-color: transparent;")
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_4.setSpacing(15)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        # ===== Левая панель навигации =====
        self.left_panel = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.left_panel.setFixedWidth(220)
        self.left_panel.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 3px;
                padding: 10px;
            }
        """)

        self.left_layout = QtWidgets.QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(8, 15, 8, 15)
        self.left_layout.setSpacing(8)

        # Логотип
        self.logo_label = QtWidgets.QLabel("IT-EcoSystem\nCRM")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                color: #2d7d3a;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 5px;
                border-bottom: 1px solid #444;
                margin-bottom: 10px;
            }
        """)
        self.left_layout.addWidget(self.logo_label)

        # Кнопки навигации (простые, без теней)
        nav_button_style = """
            QPushButton {
                background-color: transparent;
                color: #d0d0d0;
                border: none;
                border-radius: 2px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2d7d3a;
            }
        """

        self.PB_Trends = self._create_nav_button("📊 Тренды", nav_button_style)
        self.left_layout.addWidget(self.PB_Trends)

        self.PB_Objectives = self._create_nav_button("✅ Задачи", nav_button_style)
        self.left_layout.addWidget(self.PB_Objectives)

        self.PB_Pay = self._create_nav_button("💰 Платежи", nav_button_style)
        self.left_layout.addWidget(self.PB_Pay)

        self.PB_Customers = self._create_nav_button("👥 Клиенты", nav_button_style)
        self.left_layout.addWidget(self.PB_Customers)

        self.PB_Services = self._create_nav_button("🛠️ Услуги", nav_button_style)
        self.left_layout.addWidget(self.PB_Services)

        self.PB_Warehouses = self._create_nav_button("📦 Склад", nav_button_style)
        self.left_layout.addWidget(self.PB_Warehouses)

        self.PB_Shops = self._create_nav_button("🏪 Магазин", nav_button_style)
        self.left_layout.addWidget(self.PB_Shops)

        self.PB_Reports = self._create_nav_button("📈 Отчеты", nav_button_style)
        self.left_layout.addWidget(self.PB_Reports)

        self.PB_Customization = self._create_nav_button("⚙️ Настройка", nav_button_style)
        self.left_layout.addWidget(self.PB_Customization)

        self.left_layout.addStretch()
        self.horizontalLayout_4.addWidget(self.left_panel)

        # ===== Правая панель (основной контент) =====
        self.right_panel = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 3px;
                padding: 15px;
            }
        """)

        self.right_layout = QtWidgets.QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(10)

        # ===== Верхняя информационная панель =====
        self.top_info_frame = QtWidgets.QFrame()
        self.top_info_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 2px;
                padding: 4px;
            }
        """)
        top_layout = QtWidgets.QHBoxLayout(self.top_info_frame)
        top_layout.setContentsMargins(10, 6, 10, 6)

        self.date_label = QtWidgets.QLabel()
        self.date_label.setText(QDate.currentDate().toString("dd MMMM yyyy"))
        self.date_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")

        self.stats_label = QtWidgets.QLabel("Активных заказов: 0 | Новых: 0")
        self.stats_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")

        top_layout.addWidget(self.date_label)
        top_layout.addStretch()
        top_layout.addWidget(self.stats_label)

        self.right_layout.addWidget(self.top_info_frame)

        # ===== Хедер (заголовок и поиск) =====
        self.header_frame = QtWidgets.QFrame()
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 2px;
                padding: 8px;
            }
        """)
        header_layout = QtWidgets.QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 8, 10, 8)
        header_layout.setSpacing(15)

        self.LBTEXT_Ordes = QtWidgets.QLabel("Заказы /")
        self.LBTEXT_Ordes.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")

        header_layout.addWidget(self.LBTEXT_Ordes)

        # Кнопки фильтрации по типу заказа
        button_style = """
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                border: none;
                border-radius: 2px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2d7d3a;
            }
        """

        self.PB_Paid = QtWidgets.QPushButton("Платные")
        self.PB_Paid.setStyleSheet(button_style)
        header_layout.addWidget(self.PB_Paid)

        self.PB_TWC = QtWidgets.QPushButton("Гарантийные")
        self.PB_TWC.setStyleSheet(button_style)
        header_layout.addWidget(self.PB_TWC)

        header_layout.addStretch()

        # Поле поиска
        self.Search = QtWidgets.QLineEdit()
        self.Search.setPlaceholderText("🔍 Поиск заказов...")
        self.Search.setMinimumWidth(220)
        self.Search.setMinimumHeight(30)
        self.Search.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 4px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #2d7d3a;
                background-color: #404040;
            }
        """)
        header_layout.addWidget(self.Search)

        # Кнопка уведомлений
        self.PB_Notification = QtWidgets.QPushButton("🔔")
        self.PB_Notification.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                border: none;
                border-radius: 2px;
                padding: 6px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: white;
            }
        """)
        header_layout.addWidget(self.PB_Notification)

        # Контейнер авторизации
        self.auth_container = QtWidgets.QWidget()
        auth_layout = QtWidgets.QHBoxLayout(self.auth_container)
        auth_layout.setContentsMargins(0, 0, 0, 0)

        self.Enter_PushButton = QtWidgets.QPushButton("👤 Войти")
        self.Enter_PushButton.setStyleSheet("""
            QPushButton {
                background-color: #2d7d3a;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a9a4a;
            }
        """)

        self.Profile_PushButton = QtWidgets.QPushButton("👤 Профиль")
        self.Profile_PushButton.setStyleSheet("""
            QPushButton {
                background-color: #2d7d3a;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a9a4a;
            }
        """)
        self.Profile_PushButton.hide()

        auth_layout.addWidget(self.Enter_PushButton)
        auth_layout.addWidget(self.Profile_PushButton)
        header_layout.addWidget(self.auth_container)

        self.right_layout.addWidget(self.header_frame)

        # ===== Панель фильтров по статусу =====
        self.filter_frame = QtWidgets.QFrame()
        self.filter_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 2px;
                padding: 4px;
            }
        """)
        filter_layout = QtWidgets.QHBoxLayout(self.filter_frame)
        filter_layout.setContentsMargins(8, 4, 8, 4)
        filter_layout.setSpacing(4)

        filter_button_style = """
            QPushButton {
                background-color: transparent;
                color: #d0d0d0;
                border: none;
                border-radius: 2px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2d7d3a;
            }
        """

        self.PB_All = QtWidgets.QPushButton("Все")
        self.PB_All.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_All)

        self.PB_New = QtWidgets.QPushButton("Новое")
        self.PB_New.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_New)

        self.PB_Active = QtWidgets.QPushButton("Активное")
        self.PB_Active.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_Active)

        self.PB_Urgent = QtWidgets.QPushButton("Срочное")
        self.PB_Urgent.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_Urgent)

        self.PB_Work = QtWidgets.QPushButton("В работе")
        self.PB_Work.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_Work)

        self.PB_WFSP = QtWidgets.QPushButton("Ждут запчасти")
        self.PB_WFSP.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_WFSP)

        self.PB_Done = QtWidgets.QPushButton("Готовое")
        self.PB_Done.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_Done)

        self.PB_CloUns = QtWidgets.QPushButton("Закрыто неуспешно")
        self.PB_CloUns.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_CloUns)

        self.PB_Carrying = QtWidgets.QPushButton("Несут заказ")
        self.PB_Carrying.setStyleSheet(filter_button_style)
        filter_layout.addWidget(self.PB_Carrying)

        filter_layout.addStretch()

        self.PB_Filter = QtWidgets.QPushButton("🔍 Фильтр")
        self.PB_Filter.setStyleSheet("""
            QPushButton {
                background-color: #2d7d3a;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a9a4a;
            }
        """)
        filter_layout.addWidget(self.PB_Filter)

        self.right_layout.addWidget(self.filter_frame)

        # ===== Таблица заказов =====
        self.tableCRM = QtWidgets.QTableWidget()
        self.tableCRM.setStyleSheet("""
            QTableWidget {
                color: #f0f0f0;
                background-color: #3a3a3a;
                gridline-color: #555;
                alternate-background-color: #404040;
                selection-background-color: #2d7d3a;
                border: none;
                border-radius: 2px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #2d7d3a;
                color: white;
                padding: 6px;
                border: 1px solid #555;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #2d7d3a;
                border: 1px solid #555;
            }
        """)
        self.tableCRM.setAlternatingRowColors(True)

        self.tableCRM.setColumnCount(11)
        headers = [
            "Заказы", "Статус", "Клиент", "Менеджер", "Исполнитель",
            "Причины обращения", "Бренд", "Модель", "Тип устройства",
            "Внешний вид", "OrderID"
        ]
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableCRM.setHorizontalHeaderItem(i, item)

        self.tableCRM.setColumnHidden(10, True)
        self.tableCRM.setRowCount(0)
        self.tableCRM.horizontalHeader().setStretchLastSection(True)
        self.tableCRM.horizontalHeader().setDefaultSectionSize(110)

        self.right_layout.addWidget(self.tableCRM)

        # ===== Нижняя панель =====
        self.bottom_frame = QtWidgets.QFrame()
        self.bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 2px;
                padding: 6px;
            }
        """)
        bottom_layout = QtWidgets.QHBoxLayout(self.bottom_frame)
        bottom_layout.setContentsMargins(10, 6, 10, 6)

        self.pagination_label = QtWidgets.QLabel("Строк: 0")
        self.pagination_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")

        self.PB_Add_Order = QtWidgets.QPushButton("Добавить заказ")
        self.PB_Add_Order.setStyleSheet("""
            QPushButton {
                background-color: #2d7d3a;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a9a4a;
            }
        """)

        bottom_layout.addWidget(self.pagination_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.PB_Add_Order)

        self.right_layout.addWidget(self.bottom_frame)

        self.horizontalLayout_4.addWidget(self.right_panel)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)

        # ===== Подключение сигналов =====
        self._connect_signals()

        # ===== Загрузка данных =====
        self.load_orders_data()
        self.update_login_button()

        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.update_notification_badge)
        self.notification_timer.start(30000)

        self.date_timer = QTimer()
        self.date_timer.timeout.connect(self._update_current_date)
        self.date_timer.start(60000)

    def _create_nav_button(self, text: str, style: str) -> QtWidgets.QPushButton:
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet(style)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def _connect_signals(self):
        self.tableCRM.cellDoubleClicked.connect(self.open_order_details)
        self.Search.returnPressed.connect(self.apply_search_filter)
        self.PB_Filter.clicked.connect(self.apply_search_filter)

        self.PB_Trends.clicked.connect(self.open_trends)
        self.PB_Objectives.clicked.connect(self.open_objectives)
        self.PB_Services.clicked.connect(self.open_services)
        self.PB_Warehouses.clicked.connect(self.open_warehouse)
        self.PB_Pay.clicked.connect(self.open_payments)
        self.PB_Customers.clicked.connect(self.open_customers)
        self.PB_Shops.clicked.connect(self.open_shops)
        self.PB_Reports.clicked.connect(self.open_reports)
        self.PB_Customization.clicked.connect(self.open_settings)

        self.PB_All.clicked.connect(lambda: self.load_orders_data())
        self.PB_New.clicked.connect(lambda: self.load_orders_data("Новая"))
        self.PB_Active.clicked.connect(lambda: self.load_orders_data("Активная"))
        self.PB_Urgent.clicked.connect(lambda: self.load_orders_data("Срочное"))
        self.PB_WFSP.clicked.connect(lambda: self.load_orders_data("Ждут запчасти"))
        self.PB_Work.clicked.connect(lambda: self.load_orders_data("В работе"))
        self.PB_Done.clicked.connect(lambda: self.load_orders_data("Готовое"))
        self.PB_CloUns.clicked.connect(lambda: self.load_orders_data("Закрыто неуспешно"))
        self.PB_Carrying.clicked.connect(lambda: self.load_orders_data("Клиент несет заказ"))

        self.PB_Add_Order.clicked.connect(self.add_new_order)
        self.Enter_PushButton.clicked.connect(self.open_profile)
        self.Profile_PushButton.clicked.connect(self.open_profile)
        self.PB_Notification.clicked.connect(self.show_notifications)

    def _update_current_date(self):
        self.date_label.setText(QDate.currentDate().toString("dd MMMM yyyy"))

    # ===== Методы работы с заказами =====
    def load_orders_data(self, status_filter: str = None):
        try:
            orders = db_crm.get_orders_for_crm_table(filter_status=status_filter)
            self._update_table_with_data(orders)
            new_count = sum(1 for o in orders if o.get('Статус') == 'Новая')
            active_count = len(orders)
            self.stats_label.setText(f"Активных заказов: {active_count} | Новых: {new_count}")
            self.update_notification_badge()
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(None, "Ошибка", f"Ошибка при загрузке данных: {e}")

    def _update_table_with_data(self, orders: List[Dict[str, Any]]):
        self.tableCRM.setRowCount(len(orders))
        fields = [
            'Заказы', 'Статус', 'Клиент', 'Менеджер', 'Исполнитель',
            'Причины обращения', 'Бренд', 'Модель', 'Тип устройства', 'Внешний вид'
        ]
        for row, order in enumerate(orders):
            for col, field in enumerate(fields):
                value = order.get(field, '')
                if value is None:
                    value = ''
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if field == 'Статус':
                    item.setTextAlignment(Qt.AlignCenter)
                    self._color_status_item(item, str(value))
                elif col == 0:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableCRM.setItem(row, col, item)
            order_id = order.get('OrderID', '')
            if order_id:
                order_id_item = QTableWidgetItem(str(order_id))
                self.tableCRM.setItem(row, 10, order_id_item)

        self.tableCRM.resizeColumnsToContents()
        self.LBTEXT_Ordes.setText(f"Заказы ({len(orders)}) /")
        self.pagination_label.setText(f"Строк: {len(orders)}")

    def _color_status_item(self, item: QTableWidgetItem, status: str):
        colors = {
            'Новая': QColor(66, 135, 245),
            'Активная': QColor(255, 193, 7),
            'Срочное': QColor(220, 53, 69),
            'В работе': QColor(25, 135, 84),
            'Ждут запчасти': QColor(255, 149, 0),
            'Готовое': QColor(40, 167, 69),
            'Завершен': QColor(108, 117, 125),
            'Закрыто неуспешно': QColor(108, 117, 125),
            'Клиент несет заказ': QColor(155, 89, 182)
        }
        if status in colors:
            item.setBackground(colors[status])
            item.setForeground(QColor(255, 255, 255))

    def apply_search_filter(self):
        search_text = self.Search.text().strip()
        if not search_text:
            self.load_orders_data()
            return
        try:
            orders = db_crm.get_orders_for_crm_table(search_text=search_text)
            self._update_table_with_data(orders)
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            QMessageBox.critical(None, "Ошибка", f"Ошибка при поиске: {e}")

    def open_order_details(self, row: int, column: int):
        try:
            order_id_item = self.tableCRM.item(row, 10)
            if not order_id_item:
                QMessageBox.warning(None, "Ошибка", "Не удалось получить ID заказа")
                return
            order_id = int(order_id_item.text())
            order_data = db_crm.get_order_for_edit_form(order_id)
            if not order_data:
                QMessageBox.warning(None, "Ошибка", f"Не удалось загрузить данные заказа #{order_id}")
                return
            self._open_order_edit_dialog(order_id, order_data)
        except ValueError as e:
            print(f"Ошибка преобразования ID заказа: {e}")
            QMessageBox.warning(None, "Ошибка", "Некорректный ID заказа")
        except Exception as e:
            print(f"Ошибка открытия деталей заказа: {e}")
            QMessageBox.warning(None, "Ошибка", f"Не удалось открыть детали заказа: {e}")

    def _open_order_edit_dialog(self, order_id: int, order_data: Dict[str, Any]):
        try:
            from CRM_Order_Edit import OrderEditDialog
            dialog = OrderEditDialog(order_id, order_data)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                self.load_orders_data()
                QMessageBox.information(None, "Успех", "Изменения сохранены")
        except ImportError as e:
            print(f"Не удалось импортировать модуль редактирования: {e}")
            QMessageBox.warning(None, "Функция недоступна", "Модуль редактирования заказов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия диалога редактирования: {e}")
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть форму редактирования: {e}")

    def add_new_order(self):
        try:
            from CRM_Add_Order import AddOrderDialog
            dialog = AddOrderDialog()
            result = dialog.exec_()
            if result == QDialog.Accepted:
                self.load_orders_data()
                QMessageBox.information(None, "Успех", "Новый заказ добавлен!")
        except ImportError as e:
            print(f"Не удалось импортировать модуль добавления заказа: {e}")
            QMessageBox.critical(None, "Ошибка", "Модуль добавления заказов не найден")
        except Exception as e:
            print(f"Ошибка открытия формы добавления заказа: {e}")
            QMessageBox.critical(None, "Ошибка", f"Не удалось открыть форму добавления заказа: {e}")

    # ===== Методы авторизации =====
    def update_login_button(self):
        if employee_session.is_authenticated():
            self.Enter_PushButton.hide()
            name = employee_session.get_employee_name()
            if name:
                short_name = name.split()[0] if name else "Профиль"
                self.Profile_PushButton.setText(f"👤 {short_name}")
            else:
                self.Profile_PushButton.setText("👤 Профиль")
            self.Profile_PushButton.show()
            self.update_notification_badge()
        else:
            self.Profile_PushButton.hide()
            self.Enter_PushButton.show()
            self.PB_Notification.setText("🔔")

    def open_profile(self):
        if employee_session.is_authenticated():
            profile_dialog = EmployeeProfileDialog(self.Profile_PushButton)
            profile_dialog.exec_()
            self.update_login_button()
        else:
            from Handlers.Employees.employee_login import EmployeeLoginDialog
            login_dialog = EmployeeLoginDialog(self.Enter_PushButton)
            result = login_dialog.exec_()
            if result == QDialog.Accepted:
                employee_data = login_dialog.get_employee_data()
                if employee_data:
                    employee_session.login(employee_data)
                    self.update_login_button()
                    QMessageBox.information(
                        self.Enter_PushButton,
                        "Добро пожаловать!",
                        f"✅ Вы вошли как {employee_data.get('FirstName')} {employee_data.get('LastName')}\n"
                        f"Должность: {employee_data.get('Position', 'Сотрудник')}"
                    )
                    self.load_orders_data()

    # ===== Методы уведомлений =====
    def show_notifications(self):
        if not employee_session.is_authenticated():
            QMessageBox.warning(
                self.PB_Notification,
                "Требуется авторизация",
                "Пожалуйста, войдите в систему для просмотра уведомлений"
            )
            return
        try:
            from Handlers.Dialog.notifications_dialog import NotificationsDialog
            notifications_dialog = NotificationsDialog(
                employee_id=employee_session.get_employee_id(),
                parent=self.PB_Notification
            )
            notifications_dialog.exec_()
            self.update_notification_badge()
        except ImportError as e:
            print(f"Ошибка импорта модуля уведомлений: {e}")
            QMessageBox.warning(self.PB_Notification, "Функция недоступна", "Модуль уведомлений временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия уведомлений: {e}")
            QMessageBox.critical(self.PB_Notification, "Ошибка", f"Не удалось открыть уведомления: {e}")

    def update_notification_badge(self):
        if not employee_session.is_authenticated():
            self.PB_Notification.setText("🔔")
            return
        try:
            unread_count = db_crm.get_unread_notifications_count(employee_session.get_employee_id())
            if unread_count > 0:
                self.PB_Notification.setText(f"🔔 {unread_count}" if unread_count <= 99 else f"🔔{unread_count}")
            else:
                self.PB_Notification.setText("🔔")
        except Exception as e:
            print(f"Ошибка обновления счетчика уведомлений: {e}")

    # ===== Методы открытия разделов =====
    def open_objectives(self):
        try:
            from Handlers.Employees.employee_objectives import ObjectivesDialog
            dialog = ObjectivesDialog(self.PB_Objectives)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля задач: {e}")
            QMessageBox.warning(self.PB_Objectives, "Функция недоступна", "Модуль задач временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна задач: {e}")
            QMessageBox.critical(self.PB_Objectives, "Ошибка", f"Не удалось открыть окно задач: {e}")

    def open_customers(self):
        try:
            from Handlers.Employees.employee_customers import CustomersDialog
            dialog = CustomersDialog(self.PB_Customers)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля клиентов: {e}")
            QMessageBox.warning(self.PB_Customers, "Функция недоступна", "Модуль управления клиентами временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна клиентов: {e}")
            QMessageBox.critical(self.PB_Customers, "Ошибка", f"Не удалось открыть окно клиентов: {e}")

    def open_shops(self):
        try:
            from Handlers.Dialog.shops_dialog import ShopsDialog
            dialog = ShopsDialog(self.PB_Shops)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля магазинов: {e}")
            QMessageBox.warning(self.PB_Shops, "Функция недоступна", "Модуль магазинов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна магазинов: {e}")
            QMessageBox.critical(self.PB_Shops, "Ошибка", f"Не удалось открыть окно магазинов: {e}")

    def open_warehouse(self):
        try:
            from Handlers.Dialog.warehouse_dialog import WarehouseDialog
            dialog = WarehouseDialog(self.PB_Warehouses)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля склада: {e}")
            QMessageBox.warning(self.PB_Warehouses, "Функция недоступна", "Модуль управления складом временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна склада: {e}")
            QMessageBox.critical(self.PB_Warehouses, "Ошибка", f"Не удалось открыть окно склада: {e}")

    def open_payments(self):
        try:
            from Handlers.Dialog.payments_dialog import PaymentsDialog
            dialog = PaymentsDialog(self.PB_Pay)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля платежей: {e}")
            QMessageBox.warning(self.PB_Pay, "Функция недоступна", "Модуль платежей временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна платежей: {e}")
            QMessageBox.critical(self.PB_Pay, "Ошибка", f"Не удалось открыть окно платежей: {e}")

    def open_services(self):
        try:
            from Handlers.Dialog.services_dialog import ServicesDialog
            dialog = ServicesDialog(self.PB_Services)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля услуг: {e}")
            QMessageBox.warning(self.PB_Services, "Функция недоступна", "Модуль управления услугами временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна услуг: {e}")
            QMessageBox.critical(self.PB_Services, "Ошибка", f"Не удалось открыть окно услуг: {e}")

    def open_reports(self):
        try:
            dialog = ReportsDialog(self.PB_Reports)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля отчетов: {e}")
            QMessageBox.warning(self.PB_Reports, "Функция недоступна", "Модуль отчетов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна отчетов: {e}")
            QMessageBox.critical(self.PB_Reports, "Ошибка", f"Не удалось открыть окно отчетов: {e}")

    def open_trends(self):
        try:
            dialog = TrendsDialog(self.PB_Trends)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля трендов: {e}")
            QMessageBox.warning(self.PB_Trends, "Функция недоступна", "Модуль трендов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна трендов: {e}")
            QMessageBox.critical(self.PB_Trends, "Ошибка", f"Не удалось открыть окно трендов: {e}")

    def open_settings(self):
        try:
            from Handlers.Dialog.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self.PB_Customization)
            dialog.settings_saved.connect(self._on_settings_saved)
            dialog.theme_changed.connect(self._apply_theme_from_settings)
            dialog.font_changed.connect(self._apply_font_from_settings)
            dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля настроек: {e}")
            QMessageBox.warning(self.PB_Customization, "Функция недоступна", "Модуль настроек временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна настроек: {e}")
            QMessageBox.critical(self.PB_Customization, "Ошибка", f"Не удалось открыть окно настроек: {e}")

    def _on_settings_saved(self):
        self.load_orders_data()
        self.update_login_button()

    def _apply_theme_from_settings(self, theme_name: str):
        print(f"Применяем тему: {theme_name}")

    def _apply_font_from_settings(self, font: QFont):
        self.tableCRM.setFont(font)
        self.Search.setFont(font)
        self.LBTEXT_Ordes.setFont(font)


class MainCRMWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_main_window_CRM()
        self.ui.setupUi(self)
        employee_session.set_main_window(self.ui)
        if not employee_session.is_authenticated():
            QtCore.QTimer.singleShot(100, self._show_login_dialog)

    def _show_login_dialog(self):
        from Handlers.Employees.employee_login import EmployeeLoginDialog
        login_dialog = EmployeeLoginDialog(self)
        result = login_dialog.exec_()
        if result == QDialog.Accepted:
            employee_data = login_dialog.get_employee_data()
            if employee_data:
                employee_session.login(employee_data)
                self.ui.update_login_button()
                QMessageBox.information(
                    self,
                    "Добро пожаловать!",
                    f"✅ Вы вошли как {employee_data.get('FirstName')} {employee_data.get('LastName')}\n"
                    f"Должность: {employee_data.get('Position', 'Сотрудник')}"
                )
                self.ui.load_orders_data()

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
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
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    main_window = MainCRMWindow()
    main_window.show()
    sys.exit(app.exec_())