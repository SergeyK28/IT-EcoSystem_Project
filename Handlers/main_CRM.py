# -*- coding: utf-8 -*-
"""
Модуль главного окна CRM системы IT-EcoSystem.
Содержит основной интерфейс для управления заказами, клиентами, складом и другими функциями.

Основные возможности:
- Отображение списка заказов в таблице
- Фильтрация заказов по статусу
- Поиск заказов по тексту
- Открытие детальной информации о заказе
- Навигация по разделам CRM (клиенты, склад, услуги, платежи и т.д.)
- Авторизация сотрудников
- Уведомления о событиях
"""

import sys
import os
from typing import Dict, List, Any

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import (
    QGraphicsDropShadowEffect, QMessageBox, QDialog, QTableWidgetItem,
    QApplication
)

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорты из других модулей проекта
from Handlers.Employees.employee_session import employee_session
from Handlers.Dialog.reports_dialog import ReportsDialog
from Handlers.Employees.employee_profile import EmployeeProfileDialog
from Handlers.Dialog.trends_dialog import TrendsDialog
from Server import db_crm


class Ui_main_window_CRM:
    """
    Класс, отвечающий за создание и управление интерфейсом главного окна CRM.
    Содержит все элементы управления и их обработчики.
    """

    def setupUi(self, main_window_CRM):
        """
        Настраивает пользовательский интерфейс главного окна.

        Аргументы:
            main_window_CRM: Родительское окно, в которое встраивается интерфейс
        """
        # ==================== ОСНОВНЫЕ НАСТРОЙКИ ОКНА ====================
        main_window_CRM.setObjectName("main_window_CRM")
        main_window_CRM.resize(1400, 950)

        # Устанавливаем градиентный фон для главного окна
        main_window_CRM.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #232323, stop:1 #1a1a1a);
            }
        """)

        # Устанавливаем иконку окна
        icon_path = "../Pictures/Screenshot from 2025-09-15 14-30-16.png"
        if os.path.exists(icon_path):
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            main_window_CRM.setWindowIcon(icon)

        # ==================== ГЛАВНЫЙ КОНТЕЙНЕР ====================
        # Основной горизонтальный макет с отступами
        self.horizontalLayout = QtWidgets.QHBoxLayout(main_window_CRM)
        self.horizontalLayout.setContentsMargins(20, 20, 20, 20)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # ==================== ОБЛАСТЬ ПРОКРУТКИ ====================
        # Создаем область прокрутки для всего содержимого
        self.scrollArea = QtWidgets.QScrollArea(main_window_CRM)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 6px;
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
        self.scrollArea.setObjectName("scrollArea")

        # Контейнер для содержимого области прокрутки
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setStyleSheet("background-color: transparent;")
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # Горизонтальный макет внутри контейнера
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        # ==================== ЛЕВАЯ ПАНЕЛЬ НАВИГАЦИИ ====================
        self.left_panel = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.left_panel.setFixedWidth(240)
        self.left_panel.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 15px;
                padding: 15px;
            }
        """)

        # Добавляем тень для левой панели
        panel_shadow = QGraphicsDropShadowEffect()
        panel_shadow.setBlurRadius(20)
        panel_shadow.setColor(QColor(0, 0, 0, 100))
        panel_shadow.setOffset(0, 5)
        self.left_panel.setGraphicsEffect(panel_shadow)

        # Вертикальный макет для кнопок навигации
        self.left_layout = QtWidgets.QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(10, 20, 10, 20)
        self.left_layout.setSpacing(10)

        # ========== ЛОГОТИП ==========
        self.logo_label = QtWidgets.QLabel("IT-EcoSystem\nCRM")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 20px;
                font-weight: bold;
                padding: 20px 10px;
                border-bottom: 2px solid #3a3a3a;
                margin-bottom: 15px;
            }
        """)
        self.left_layout.addWidget(self.logo_label)

        # ========== КНОПКИ НАВИГАЦИИ ==========
        # Стиль для кнопок навигации
        nav_button_style = """
            QPushButton {
                background-color: transparent;
                color: #d0d0d0;
                border: none;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                font-weight: 500;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #404040;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """

        # Создаем все кнопки навигации
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

        # Растягивающий элемент для прижатия кнопок к верху
        self.left_layout.addStretch()

        # Добавляем левую панель в основной макет
        self.horizontalLayout_4.addWidget(self.left_panel)

        # ==================== ПРАВАЯ ПАНЕЛЬ (ОСНОВНОЙ КОНТЕНТ) ====================
        self.right_panel = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        # Добавляем тень для правой панели
        right_shadow = QGraphicsDropShadowEffect()
        right_shadow.setBlurRadius(20)
        right_shadow.setColor(QColor(0, 0, 0, 100))
        right_shadow.setOffset(0, 5)
        self.right_panel.setGraphicsEffect(right_shadow)

        # Вертикальный макет для содержимого правой панели
        self.right_layout = QtWidgets.QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(20, 20, 20, 20)
        self.right_layout.setSpacing(15)

        # ==================== ВЕРХНЯЯ ИНФОРМАЦИОННАЯ ПАНЕЛЬ ====================
        self.top_info_frame = QtWidgets.QFrame()
        self.top_info_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 5px;
            }
        """)

        top_layout = QtWidgets.QHBoxLayout(self.top_info_frame)
        top_layout.setContentsMargins(15, 8, 15, 8)

        # Текущая дата
        self.date_label = QtWidgets.QLabel()
        self.date_label.setText(QDate.currentDate().toString("dd MMMM yyyy"))
        self.date_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
                font-weight: 400;
                padding: 5px;
            }
        """)

        # Статистика заказов
        self.stats_label = QtWidgets.QLabel("Активных заказов: 0 | Новых: 0")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
                font-weight: 400;
                padding: 5px;
            }
        """)

        top_layout.addWidget(self.date_label)
        top_layout.addStretch()
        top_layout.addWidget(self.stats_label)

        self.right_layout.addWidget(self.top_info_frame)

        # ==================== ХЕДЕР (ЗАГОЛОВОК И ПОИСК) ====================
        self.header_frame = QtWidgets.QFrame()
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 10px;
            }
        """)

        header_layout = QtWidgets.QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(20)

        # Заголовок раздела с количеством заказов
        self.LBTEXT_Ordes = QtWidgets.QLabel("Заказы /")
        self.LBTEXT_Ordes.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.LBTEXT_Ordes)

        # Кнопки фильтрации по типу заказа
        button_style = """
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #404040;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """

        self.PB_Paid = QtWidgets.QPushButton("Платные")
        self.PB_Paid.setStyleSheet(button_style)
        header_layout.addWidget(self.PB_Paid)

        self.PB_TWC = QtWidgets.QPushButton("Гарантийные")
        self.PB_TWC.setStyleSheet(button_style)
        header_layout.addWidget(self.PB_TWC)

        header_layout.addStretch()

        # ========== ПОЛЕ ПОИСКА ==========
        self.Search = QtWidgets.QLineEdit()
        self.Search.setPlaceholderText("🔍 Поиск заказов...")
        self.Search.setMinimumWidth(250)
        self.Search.setMinimumHeight(35)
        self.Search.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 2px solid #4a4a4a;
                border-radius: 17px;
                padding: 5px 15px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #404040;
            }
            QLineEdit:hover {
                background-color: #424242;
            }
        """)
        header_layout.addWidget(self.Search)

        # ========== КНОПКА УВЕДОМЛЕНИЙ ==========
        self.PB_Notification = QtWidgets.QPushButton("🔔")
        self.PB_Notification.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #404040;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """)
        header_layout.addWidget(self.PB_Notification)

        # ========== КОНТЕЙНЕР АВТОРИЗАЦИИ ==========
        self.auth_container = QtWidgets.QWidget()
        auth_layout = QtWidgets.QHBoxLayout(self.auth_container)
        auth_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопка входа (показывается когда пользователь не авторизован)
        self.Enter_PushButton = QtWidgets.QPushButton("👤 Войти")
        self.Enter_PushButton.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3d8b40, stop:1 #357a38);
            }
        """)

        # Кнопка профиля (показывается когда пользователь авторизован)
        self.Profile_PushButton = QtWidgets.QPushButton("👤 Профиль")
        self.Profile_PushButton.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3d8b40, stop:1 #357a38);
            }
        """)
        self.Profile_PushButton.hide()  # Изначально скрыта

        auth_layout.addWidget(self.Enter_PushButton)
        auth_layout.addWidget(self.Profile_PushButton)

        header_layout.addWidget(self.auth_container)

        self.right_layout.addWidget(self.header_frame)

        # ==================== ПАНЕЛЬ ФИЛЬТРОВ ПО СТАТУСУ ====================
        self.filter_frame = QtWidgets.QFrame()
        self.filter_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        filter_layout = QtWidgets.QHBoxLayout(self.filter_frame)
        filter_layout.setContentsMargins(10, 5, 10, 5)
        filter_layout.setSpacing(5)

        # Стиль для кнопок фильтра
        filter_button_style = """
            QPushButton {
                background-color: transparent;
                color: #d0d0d0;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #404040;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """

        # Создаем все кнопки фильтрации по статусу
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

        # Кнопка принудительного поиска/фильтра
        self.PB_Filter = QtWidgets.QPushButton("🔍 Фильтр")
        self.PB_Filter.setStyleSheet("""
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
        """)
        filter_layout.addWidget(self.PB_Filter)

        self.right_layout.addWidget(self.filter_frame)

        # ==================== ТАБЛИЦА ЗАКАЗОВ ====================
        self.tableCRM = QtWidgets.QTableWidget()
        self.tableCRM.setStyleSheet("""
            QTableWidget {
                color: rgb(255, 255, 255);
                background-color: rgb(40, 40, 40);
                gridline-color: rgb(80, 80, 80);
                alternate-background-color: rgb(50, 50, 50);
                selection-background-color: rgb(103, 155, 118);
                border: none;
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: rgb(103, 155, 118);
                color: rgb(255, 255, 255);
                padding: 10px;
                border: 1px solid rgb(80, 80, 80);
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: rgb(103, 155, 118);
                border: 1px solid rgb(80, 80, 80);
            }
        """)
        self.tableCRM.setAlternatingRowColors(True)

        # Настройка столбцов таблицы
        self.tableCRM.setColumnCount(11)  # 10 видимых + 1 скрытый

        # Заголовки столбцов
        headers = [
            "Заказы", "Статус", "Клиент", "Менеджер", "Исполнитель",
            "Причины обращения", "Бренд", "Модель", "Тип устройства",
            "Внешний вид", "OrderID"
        ]

        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setTextAlignment(Qt.AlignCenter)
            self.tableCRM.setHorizontalHeaderItem(i, item)

        # Скрываем столбец с OrderID (он нужен для внутренней работы)
        self.tableCRM.setColumnHidden(10, True)

        self.tableCRM.setRowCount(0)
        self.tableCRM.horizontalHeader().setStretchLastSection(True)
        self.tableCRM.horizontalHeader().setDefaultSectionSize(120)

        self.right_layout.addWidget(self.tableCRM)

        # ==================== НИЖНЯЯ ПАНЕЛЬ ====================
        self.bottom_frame = QtWidgets.QFrame()
        self.bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        bottom_layout = QtWidgets.QHBoxLayout(self.bottom_frame)
        bottom_layout.setContentsMargins(15, 10, 15, 10)

        # Информация о количестве строк
        self.pagination_label = QtWidgets.QLabel("Строк: 0")
        self.pagination_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")

        # Кнопка добавления нового заказа
        self.PB_Add_Order = QtWidgets.QPushButton("Добавить заказ")
        self.PB_Add_Order.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3d8b40, stop:1 #357a38);
            }
        """)

        bottom_layout.addWidget(self.pagination_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.PB_Add_Order)

        self.right_layout.addWidget(self.bottom_frame)

        # Завершаем сборку интерфейса
        self.horizontalLayout_4.addWidget(self.right_panel)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)

        # ==================== ПОДКЛЮЧЕНИЕ СИГНАЛОВ ====================
        self._connect_signals()

        # ==================== ЗАГРУЗКА ДАННЫХ ====================
        self.load_orders_data()
        self.update_login_button()

        # Устанавливаем таймер для обновления уведомлений (каждые 30 секунд)
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.update_notification_badge)
        self.notification_timer.start(30000)  # 30 секунд

        # Запускаем таймер обновления даты
        self.date_timer = QTimer()
        self.date_timer.timeout.connect(self._update_current_date)
        self.date_timer.start(60000)  # Обновлять каждую минуту

    def _create_nav_button(self, text: str, style: str) -> QtWidgets.QPushButton:
        """
        Создает кнопку навигации с заданным стилем.

        Аргументы:
            text: Текст кнопки
            style: CSS стиль для кнопки

        Returns:
            QPushButton: Созданная кнопка
        """
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet(style)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def _connect_signals(self):
        """
        Подключает все сигналы к соответствующим слотам.
        """
        # Сигналы таблицы
        self.tableCRM.cellDoubleClicked.connect(self.open_order_details)

        # Сигналы поиска и фильтрации
        self.Search.returnPressed.connect(self.apply_search_filter)
        self.PB_Filter.clicked.connect(self.apply_search_filter)

        # Сигналы кнопок навигации
        self.PB_Trends.clicked.connect(self.open_trends)
        self.PB_Objectives.clicked.connect(self.open_objectives)
        self.PB_Services.clicked.connect(self.open_services)
        self.PB_Warehouses.clicked.connect(self.open_warehouse)
        self.PB_Pay.clicked.connect(self.open_payments)
        self.PB_Customers.clicked.connect(self.open_customers)
        self.PB_Shops.clicked.connect(self.open_shops)
        self.PB_Reports.clicked.connect(self.open_reports)
        self.PB_Customization.clicked.connect(self.open_settings)

        # Сигналы кнопок фильтрации по статусу
        self.PB_All.clicked.connect(lambda: self.load_orders_data())
        self.PB_New.clicked.connect(lambda: self.load_orders_data("Новая"))
        self.PB_Active.clicked.connect(lambda: self.load_orders_data("Активная"))
        self.PB_Urgent.clicked.connect(lambda: self.load_orders_data("Срочное"))
        self.PB_WFSP.clicked.connect(lambda: self.load_orders_data("Ждут запчасти"))
        self.PB_Work.clicked.connect(lambda: self.load_orders_data("В работе"))
        self.PB_Done.clicked.connect(lambda: self.load_orders_data("Готовое"))
        self.PB_CloUns.clicked.connect(lambda: self.load_orders_data("Закрыто неуспешно"))
        self.PB_Carrying.clicked.connect(lambda: self.load_orders_data("Клиент несет заказ"))

        # Сигналы авторизации
        self.PB_Add_Order.clicked.connect(self.add_new_order)
        self.Enter_PushButton.clicked.connect(self.open_profile)
        self.Profile_PushButton.clicked.connect(self.open_profile)

        # Сигнал уведомлений
        self.PB_Notification.clicked.connect(self.show_notifications)

    def _update_current_date(self):
        """
        Обновляет текущую дату в интерфейсе.
        """
        self.date_label.setText(QDate.currentDate().toString("dd MMMM yyyy"))

    # ==================== МЕТОДЫ РАБОТЫ С ЗАКАЗАМИ ====================

    def load_orders_data(self, status_filter: str = None):
        """
        Загружает данные заказов из базы данных в таблицу.

        Аргументы:
            status_filter: Фильтр по статусу (None - все заказы)
        """
        try:
            # Получаем заказы из базы данных
            orders = db_crm.get_orders_for_crm_table(filter_status=status_filter)
            self._update_table_with_data(orders)

            # Обновляем статистику
            new_count = sum(1 for o in orders if o.get('Статус') == 'Новая')
            active_count = len(orders)
            self.stats_label.setText(f"Активных заказов: {active_count} | Новых: {new_count}")

            # Обновляем счетчик уведомлений
            self.update_notification_badge()

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(None, "Ошибка", f"Ошибка при загрузке данных: {e}")

    def _update_table_with_data(self, orders: List[Dict[str, Any]]):
        """
        Обновляет таблицу полученными данными.

        Аргументы:
            orders: Список словарей с данными заказов
        """
        self.tableCRM.setRowCount(len(orders))

        # Список полей для отображения в таблице (порядок соответствует заголовкам)
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

                # Специальная обработка для столбца со статусом
                if field == 'Статус':
                    item.setTextAlignment(Qt.AlignCenter)
                    self._color_status_item(item, str(value))
                elif col == 0:  # Номер заказа
                    item.setTextAlignment(Qt.AlignCenter)

                self.tableCRM.setItem(row, col, item)

            # Сохраняем OrderID в скрытый столбец
            order_id = order.get('OrderID', '')
            if order_id:
                order_id_item = QTableWidgetItem(str(order_id))
                self.tableCRM.setItem(row, 10, order_id_item)

        # Настраиваем размеры столбцов
        self.tableCRM.resizeColumnsToContents()
        self.LBTEXT_Ordes.setText(f"Заказы ({len(orders)}) /")
        self.pagination_label.setText(f"Строк: {len(orders)}")

    def _color_status_item(self, item: QTableWidgetItem, status: str):
        """
        Добавляет цветовое оформление для ячеек статуса.

        Аргументы:
            item: Элемент таблицы
            status: Текст статуса
        """
        colors = {
            'Новая': QColor(66, 135, 245),  # Синий
            'Активная': QColor(255, 193, 7),  # Желтый
            'Срочное': QColor(220, 53, 69),  # Красный
            'В работе': QColor(25, 135, 84),  # Зеленый
            'Ждут запчасти': QColor(255, 149, 0),  # Оранжевый
            'Готовое': QColor(40, 167, 69),  # Зеленый
            'Завершен': QColor(108, 117, 125),  # Серый
            'Закрыто неуспешно': QColor(108, 117, 125),  # Серый
            'Клиент несет заказ': QColor(155, 89, 182)  # Фиолетовый
        }

        if status in colors:
            item.setBackground(colors[status])
            item.setForeground(QColor(255, 255, 255))

    def apply_search_filter(self):
        """
        Применяет поисковый фильтр при вводе текста в поле поиска.
        """
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
        """
        Открывает форму редактирования заказа при двойном клике.

        Аргументы:
            row: Номер строки
            column: Номер столбца
        """
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
        """
        Открывает диалог редактирования заказа.

        Аргументы:
            order_id: ID заказа
            order_data: Данные заказа
        """
        try:
            from CRM_Order_Edit import OrderEditDialog
            dialog = OrderEditDialog(order_id, order_data)
            result = dialog.exec_()

            if result == QDialog.Accepted:
                self.load_orders_data()
                QMessageBox.information(None, "Успех", "Изменения сохранены")

        except ImportError as e:
            print(f"Не удалось импортировать модуль редактирования: {e}")
            QMessageBox.warning(None, "Функция недоступна",
                                "Модуль редактирования заказов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия диалога редактирования: {e}")
            QMessageBox.critical(None, "Ошибка",
                                 f"Не удалось открыть форму редактирования: {e}")

    def add_new_order(self):
        """
        Открывает форму добавления нового заказа.
        """
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
            QMessageBox.critical(None, "Ошибка",
                                 f"Не удалось открыть форму добавления заказа: {e}")

    # ==================== МЕТОДЫ АВТОРИЗАЦИИ ====================

    def update_login_button(self):
        """
        Обновляет отображение кнопки входа/профиля в зависимости от статуса авторизации.
        """
        if employee_session.is_authenticated():
            # Пользователь авторизован - показываем кнопку профиля
            self.Enter_PushButton.hide()
            name = employee_session.get_employee_name()
            if name:
                short_name = name.split()[0] if name else "Профиль"
                self.Profile_PushButton.setText(f"👤 {short_name}")
            else:
                self.Profile_PushButton.setText("👤 Профиль")
            self.Profile_PushButton.show()

            # Обновляем счетчик уведомлений
            self.update_notification_badge()
        else:
            # Пользователь не авторизован - показываем кнопку входа
            self.Profile_PushButton.hide()
            self.Enter_PushButton.show()
            self.PB_Notification.setText("🔔")

    def open_profile(self):
        """
        Открывает профиль сотрудника или окно входа в зависимости от статуса авторизации.
        """
        if employee_session.is_authenticated():
            # Открываем профиль авторизованного сотрудника
            profile_dialog = EmployeeProfileDialog(self.Profile_PushButton)
            profile_dialog.exec_()
            self.update_login_button()
        else:
            # Открываем окно входа
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

    # ==================== МЕТОДЫ УВЕДОМЛЕНИЙ ====================

    def show_notifications(self):
        """
        Показывает диалог с уведомлениями.
        """
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

            # После закрытия диалога обновляем счетчик уведомлений
            self.update_notification_badge()

        except ImportError as e:
            print(f"Ошибка импорта модуля уведомлений: {e}")
            QMessageBox.warning(
                self.PB_Notification,
                "Функция недоступна",
                "Модуль уведомлений временно недоступен"
            )
        except Exception as e:
            print(f"Ошибка открытия уведомлений: {e}")
            QMessageBox.critical(
                self.PB_Notification,
                "Ошибка",
                f"Не удалось открыть уведомления: {e}"
            )

    def update_notification_badge(self):
        """
        Обновляет значок-счетчик непрочитанных уведомлений на кнопке.
        """
        if not employee_session.is_authenticated():
            self.PB_Notification.setText("🔔")
            return

        try:
            unread_count = db_crm.get_unread_notifications_count(
                employee_session.get_employee_id()
            )

            if unread_count > 0:
                # Показываем значок с количеством
                if unread_count > 99:
                    self.PB_Notification.setText(f"🔔{unread_count}")
                else:
                    self.PB_Notification.setText(f"🔔 {unread_count}")
            else:
                self.PB_Notification.setText("🔔")

        except Exception as e:
            print(f"Ошибка обновления счетчика уведомлений: {e}")

    # ==================== МЕТОДЫ ОТКРЫТИЯ РАЗДЕЛОВ ====================

    def open_objectives(self):
        """
        Открывает окно задач.
        """
        try:
            from Handlers.Employees.employee_objectives import ObjectivesDialog
            objectives_dialog = ObjectivesDialog(self.PB_Objectives)
            objectives_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля задач: {e}")
            QMessageBox.warning(self.PB_Objectives, "Функция недоступна",
                                "Модуль задач временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна задач: {e}")
            QMessageBox.critical(self.PB_Objectives, "Ошибка",
                                 f"Не удалось открыть окно задач: {e}")

    def open_customers(self):
        """
        Открывает окно управления клиентами.
        """
        try:
            from Handlers.Employees.employee_customers import CustomersDialog
            customers_dialog = CustomersDialog(self.PB_Customers)
            customers_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля клиентов: {e}")
            QMessageBox.warning(self.PB_Customers, "Функция недоступна",
                                "Модуль управления клиентами временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна клиентов: {e}")
            QMessageBox.critical(self.PB_Customers, "Ошибка",
                                 f"Не удалось открыть окно клиентов: {e}")

    def open_shops(self):
        """
        Открывает окно с магазинами.
        """
        try:
            from Handlers.Dialog.shops_dialog import ShopsDialog
            shops_dialog = ShopsDialog(self.PB_Shops)
            shops_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля магазинов: {e}")
            QMessageBox.warning(self.PB_Shops, "Функция недоступна",
                                "Модуль магазинов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна магазинов: {e}")
            QMessageBox.critical(self.PB_Shops, "Ошибка",
                                 f"Не удалось открыть окно магазинов: {e}")

    def open_warehouse(self):
        """
        Открывает окно управления складом.
        """
        try:
            from Handlers.Dialog.warehouse_dialog import WarehouseDialog
            warehouse_dialog = WarehouseDialog(self.PB_Warehouses)
            warehouse_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля склада: {e}")
            QMessageBox.warning(self.PB_Warehouses, "Функция недоступна",
                                "Модуль управления складом временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна склада: {e}")
            QMessageBox.critical(self.PB_Warehouses, "Ошибка",
                                 f"Не удалось открыть окно склада: {e}")

    def open_payments(self):
        """
        Открывает окно платежей.
        """
        try:
            from Handlers.Dialog.payments_dialog import PaymentsDialog
            payments_dialog = PaymentsDialog(self.PB_Pay)
            payments_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля платежей: {e}")
            QMessageBox.warning(self.PB_Pay, "Функция недоступна",
                                "Модуль платежей временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна платежей: {e}")
            QMessageBox.critical(self.PB_Pay, "Ошибка",
                                 f"Не удалось открыть окно платежей: {e}")

    def open_services(self):
        """
        Открывает окно управления услугами.
        """
        try:
            from Handlers.Dialog.services_dialog import ServicesDialog
            services_dialog = ServicesDialog(self.PB_Services)
            services_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля услуг: {e}")
            QMessageBox.warning(self.PB_Services, "Функция недоступна",
                                "Модуль управления услугами временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна услуг: {e}")
            QMessageBox.critical(self.PB_Services, "Ошибка",
                                 f"Не удалось открыть окно услуг: {e}")

    def open_reports(self):
        """
        Открывает окно отчетов.
        """
        try:
            reports_dialog = ReportsDialog(self.PB_Reports)
            reports_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля отчетов: {e}")
            QMessageBox.warning(self.PB_Reports, "Функция недоступна",
                                "Модуль отчетов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна отчетов: {e}")
            QMessageBox.critical(self.PB_Reports, "Ошибка",
                                 f"Не удалось открыть окно отчетов: {e}")

    def open_trends(self):
        """
        Открывает окно трендов и аналитики.
        """
        try:
            trends_dialog = TrendsDialog(self.PB_Trends)
            trends_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля трендов: {e}")
            QMessageBox.warning(self.PB_Trends, "Функция недоступна",
                                "Модуль трендов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна трендов: {e}")
            QMessageBox.critical(self.PB_Trends, "Ошибка",
                                 f"Не удалось открыть окно трендов: {e}")

    def open_settings(self):
        """
        Открывает окно настроек CRM.
        """
        try:
            from Handlers.Dialog.settings_dialog import SettingsDialog
            settings_dialog = SettingsDialog(self.PB_Customization)

            # Подключаем сигналы для обновления интерфейса после сохранения
            settings_dialog.settings_saved.connect(self._on_settings_saved)
            settings_dialog.theme_changed.connect(self._apply_theme_from_settings)
            settings_dialog.font_changed.connect(self._apply_font_from_settings)

            settings_dialog.exec_()
        except ImportError as e:
            print(f"Ошибка импорта модуля настроек: {e}")
            QMessageBox.warning(self.PB_Customization, "Функция недоступна",
                                "Модуль настроек временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия окна настроек: {e}")
            QMessageBox.critical(self.PB_Customization, "Ошибка",
                                 f"Не удалось открыть окно настроек: {e}")

    def _on_settings_saved(self):
        """
        Обработчик сохранения настроек.
        """
        self.load_orders_data()
        self.update_login_button()

    def _apply_theme_from_settings(self, theme_name: str):
        """
        Применяет тему из настроек.

        Аргументы:
            theme_name: Название темы
        """
        print(f"Применяем тему: {theme_name}")
        # Здесь можно реализовать смену темы интерфейса

    def _apply_font_from_settings(self, font: QFont):
        """
        Применяет шрифт из настроек ко всем элементам интерфейса.

        Аргументы:
            font: Объект шрифта
        """
        self.tableCRM.setFont(font)
        self.Search.setFont(font)
        self.LBTEXT_Ordes.setFont(font)


class MainCRMWindow(QtWidgets.QDialog):
    """
    Главное окно CRM приложения.
    """

    def __init__(self, parent=None):
        """
        Инициализирует главное окно CRM.

        Аргументы:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.ui = Ui_main_window_CRM()
        self.ui.setupUi(self)

        # Сохраняем ссылку на интерфейс в сессии
        employee_session.set_main_window(self.ui)

        # Если пользователь не авторизован, показываем окно входа через 100 мс
        if not employee_session.is_authenticated():
            QTimer.singleShot(100, self._show_login_dialog)

    def _show_login_dialog(self):
        """
        Показывает диалог входа в систему.
        """
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
        """
        Обработчик закрытия окна.

        Аргументы:
            event: Событие закрытия
        """
        event.accept()


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Настройка темной палитры
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

    # Устанавливаем шрифт
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Создаем и показываем главное окно
    main_window = MainCRMWindow()
    main_window.show()

    sys.exit(app.exec_())