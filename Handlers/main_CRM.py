# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QLinearGradient, QPalette
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox, QDialog
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Handlers.employee_session import employee_session
from Handlers.employee_profile import EmployeeProfileDialog
from Server import db_crm


class Ui_main_window_CRM(object):
    def setupUi(self, main_window_CRM):
        main_window_CRM.setObjectName("main_window_CRM")
        main_window_CRM.resize(1400, 950)

        # Главный градиентный фон
        main_window_CRM.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #232323, stop:1 #1a1a1a);
            }
        """)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Pictures/Screenshot from 2025-09-15 14-30-16.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        main_window_CRM.setWindowIcon(icon)

        self.horizontalLayout = QtWidgets.QHBoxLayout(main_window_CRM)
        self.horizontalLayout.setContentsMargins(20, 20, 20, 20)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")

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

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setStyleSheet("background-color: transparent;")
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        # ========== ЛЕВАЯ ПАНЕЛЬ С КНОПКАМИ ==========
        self.left_panel = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.left_panel.setFixedWidth(240)
        self.left_panel.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 15px;
                padding: 15px;
            }
        """)

        # Тень для левой панели
        panel_shadow = QGraphicsDropShadowEffect()
        panel_shadow.setBlurRadius(20)
        panel_shadow.setColor(QColor(0, 0, 0, 100))
        panel_shadow.setOffset(0, 5)
        self.left_panel.setGraphicsEffect(panel_shadow)

        self.left_layout = QtWidgets.QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(10, 20, 10, 20)
        self.left_layout.setSpacing(10)

        # Логотип в левой панели
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

        # Стиль для кнопок левой панели (как в main_window)
        left_button_style = """
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
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
        """

        # Создаем кнопки (НЕ checkable, как в оригинале)
        self.PB_Trends = self.create_nav_button("📊 Тренды", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Trends)

        self.PB_Objectives = self.create_nav_button("✅ Задачи", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Objectives)

        self.PB_Orders = self.create_nav_button("📦 Заказы", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Orders)

        self.PB_Pay = self.create_nav_button("💰 Платежи", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Pay)

        self.PB_Customers = self.create_nav_button("👥 Клиенты", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Customers)

        self.PB_Warehouses = self.create_nav_button("📦 Склад", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Warehouses)

        self.PB_Shops = self.create_nav_button("🏪 Магазин", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Shops)

        self.PB_Reports = self.create_nav_button("📈 Отчеты", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Reports)

        self.PB_Customization = self.create_nav_button("⚙️ Настройка", left_button_style, checkable=False)
        self.left_layout.addWidget(self.PB_Customization)

        self.left_layout.addStretch()

        self.horizontalLayout_4.addWidget(self.left_panel)

        # ========== ПРАВАЯ ПАНЕЛЬ С ТАБЛИЦЕЙ ==========
        self.right_panel = QtWidgets.QFrame(self.scrollAreaWidgetContents)
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        # Тень для правой панели
        right_shadow = QGraphicsDropShadowEffect()
        right_shadow.setBlurRadius(20)
        right_shadow.setColor(QColor(0, 0, 0, 100))
        right_shadow.setOffset(0, 5)
        self.right_panel.setGraphicsEffect(right_shadow)

        self.right_layout = QtWidgets.QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(20, 20, 20, 20)
        self.right_layout.setSpacing(15)

        # ========== ВЕРХНЯЯ ПАНЕЛЬ (как в main_window) ==========
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

        self.date_label = QtWidgets.QLabel()
        self.date_label.setText(QtCore.QDate.currentDate().toString("dd MMMM yyyy"))
        self.date_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
                font-weight: 400;
                padding: 5px;
            }
        """)

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

        # ========== ХЕДЕР (как в main_window) ==========
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

        # Заголовок раздела
        self.LBTEXT_Ordes = QtWidgets.QLabel("Заказы /")
        self.LBTEXT_Ordes.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.LBTEXT_Ordes)

        # Кнопки статусов
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

        # Правая часть хедера (как в main_window - поиск, уведомления, профиль)
        # ПОИСК (как в main_window)
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

        # Кнопка уведомлений
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

        # КОНТЕЙНЕР ДЛЯ КНОПОК ВХОДА/ПРОФИЛЯ (как в main_window)
        self.auth_container = QtWidgets.QWidget()
        auth_layout = QtWidgets.QHBoxLayout(self.auth_container)
        auth_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопка входа (стиль как в main_window)
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

        # Кнопка профиля (изначально скрыта)
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
        self.Profile_PushButton.hide()

        auth_layout.addWidget(self.Enter_PushButton)
        auth_layout.addWidget(self.Profile_PushButton)

        header_layout.addWidget(self.auth_container)

        self.right_layout.addWidget(self.header_frame)

        # ========== ПАНЕЛЬ ФИЛЬТРОВ (как в оригинале) ==========
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

        # Кнопка фильтра
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

        # ========== ТАБЛИЦА CRM ==========
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

        # Устанавливаем количество столбцов
        self.tableCRM.setColumnCount(11)  # 10 видимых + 1 скрытый

        # Устанавливаем заголовки столбцов
        headers = [
            "Заказы", "Статус", "Клиент", "Менеджер", "Исполнитель",
            "Причины обращения", "Бренд", "Модель", "Тип устройства", "Внешний вид", "OrderID"
        ]
        for i, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(header)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableCRM.setHorizontalHeaderItem(i, item)

        # Скрываем последний столбец с OrderID
        self.tableCRM.setColumnHidden(10, True)

        self.tableCRM.setRowCount(0)
        self.tableCRM.horizontalHeader().setStretchLastSection(True)
        self.tableCRM.horizontalHeader().setDefaultSectionSize(120)

        self.right_layout.addWidget(self.tableCRM)

        # ========== НИЖНЯЯ ПАНЕЛЬ ==========
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

        self.pagination_label = QtWidgets.QLabel("Строк: 0")
        self.pagination_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")

        # Кнопка добавления заказа (как в оригинале)
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
        self.PB_Add_Order.setIcon(QtGui.QIcon())
        self.PB_Add_Order.setIconSize(QtCore.QSize(20, 20))

        bottom_layout.addWidget(self.pagination_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.PB_Add_Order)

        self.right_layout.addWidget(self.bottom_frame)

        self.horizontalLayout_4.addWidget(self.right_panel)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)

        # ПОДКЛЮЧАЕМ СИГНАЛЫ
        self.tableCRM.cellDoubleClicked.connect(self.open_order_details)
        self.Search.returnPressed.connect(self.apply_search_filter)
        self.PB_Filter.clicked.connect(self.apply_search_filter)
        self.PB_Add_Order.clicked.connect(self.add_new_order)
        self.Enter_PushButton.clicked.connect(self.open_profile)
        self.Profile_PushButton.clicked.connect(self.open_profile)

        # Подключаем фильтры
        self.PB_All.clicked.connect(lambda: self.load_orders_data())
        self.PB_New.clicked.connect(lambda: self.load_orders_data("Новая"))
        self.PB_Active.clicked.connect(lambda: self.load_orders_data("Активная"))
        self.PB_Urgent.clicked.connect(lambda: self.load_orders_data("Срочное"))
        self.PB_WFSP.clicked.connect(lambda: self.load_orders_data("Ждут запчасти"))
        self.PB_Work.clicked.connect(lambda: self.load_orders_data("В работе"))
        self.PB_Done.clicked.connect(lambda: self.load_orders_data("Готовое"))
        self.PB_CloUns.clicked.connect(lambda: self.load_orders_data("Закрыто неуспешно"))
        self.PB_Carrying.clicked.connect(lambda: self.load_orders_data("Клиент несет заказ"))

        # Подключаем остальные кнопки
        self.PB_Objectives.clicked.connect(self.open_objectives)
        self.PB_Customers.clicked.connect(self.open_customers)
        self.PB_Shops.clicked.connect(self.open_shops)

        self.retranslateUi(main_window_CRM)
        QtCore.QMetaObject.connectSlotsByName(main_window_CRM)

        # Загружаем данные
        self.load_orders_data()
        self.update_login_button()

    def create_nav_button(self, text, style, checkable=False):
        """Создает кнопку навигации"""
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet(style)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def retranslateUi(self, main_window_CRM):
        _translate = QtCore.QCoreApplication.translate
        main_window_CRM.setWindowTitle(_translate("main_window_CRM", "IT-EcoSystem - CRM"))

    def update_login_button(self):
        """Обновляет отображение кнопки входа/профиля"""
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
        else:
            # Пользователь не авторизован - показываем кнопку входа
            self.Profile_PushButton.hide()
            self.Enter_PushButton.show()

    def open_profile(self):
        """Открывает профиль сотрудника или окно входа"""
        if employee_session.is_authenticated():
            from Handlers.employee_profile import EmployeeProfileDialog
            self.profile_dialog = EmployeeProfileDialog(self.Profile_PushButton)
            self.profile_dialog.exec_()
            self.update_login_button()
        else:
            from Handlers.employee_login import EmployeeLoginDialog
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

    def load_orders_data(self, status_filter=None):
        """Загружает данные заказов из базы данных в таблицу"""
        try:
            orders = db_crm.get_orders_for_crm_table(filter_status=status_filter)
            self.update_table_with_data(orders)

            # Обновляем статистику
            new_count = sum(1 for o in orders if o.get('Статус') == 'Новая')
            active_count = len(orders)
            self.stats_label.setText(f"Активных заказов: {active_count} | Новых: {new_count}")

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Ошибка при загрузке данных: {e}")

    def apply_search_filter(self):
        """Применяет поисковый фильтр"""
        search_text = self.Search.text().strip()
        if not search_text:
            self.load_orders_data()
            return

        try:
            orders = db_crm.get_orders_for_crm_table(search_text=search_text)
            self.update_table_with_data(orders)
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Ошибка при поиске: {e}")

    def update_table_with_data(self, orders):
        """Обновляет таблицу с полученными данными"""
        self.tableCRM.setRowCount(len(orders))

        for row, order in enumerate(orders):
            for col, field in enumerate([
                'Заказы', 'Статус', 'Клиент', 'Менеджер', 'Исполнитель',
                'Причины обращения', 'Бренд', 'Модель', 'Тип устройства', 'Внешний вид'
            ]):
                value = order.get(field, '')
                if value is None:
                    value = ''

                item = QtWidgets.QTableWidgetItem(str(value))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

                if col == 0:  # Заказы
                    item.setTextAlignment(Qt.AlignCenter)
                elif col == 1:  # Статус
                    item.setTextAlignment(Qt.AlignCenter)
                    self.color_status_item(item, str(value))

                self.tableCRM.setItem(row, col, item)

            # Добавляем OrderID в скрытый столбец
            order_id = order.get('OrderID', '')
            if order_id:
                order_id_item = QtWidgets.QTableWidgetItem(str(order_id))
                self.tableCRM.setItem(row, 10, order_id_item)

        self.tableCRM.resizeColumnsToContents()
        self.LBTEXT_Ordes.setText(f"Заказы ({len(orders)}) /")
        self.pagination_label.setText(f"Строк: {len(orders)}")

    def color_status_item(self, item, status):
        """Добавляет цветовое оформление для ячеек статуса (как в оригинале)"""
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

    def open_order_details(self, row, column):
        """Открывает детальную форму заказа при двойном клике"""
        try:
            order_id_item = self.tableCRM.item(row, 10)
            if not order_id_item:
                QtWidgets.QMessageBox.warning(None, "Ошибка",
                                              "Не удалось получить ID заказа")
                return

            order_id = int(order_id_item.text())
            order_data = db_crm.get_order_for_edit_form(order_id)

            if not order_data:
                QtWidgets.QMessageBox.warning(None, "Ошибка",
                                              f"Не удалось загрузить данные заказа #{order_id}")
                return

            self.open_order_edit_dialog(order_id, order_data)

        except ValueError as e:
            print(f"Ошибка преобразования ID заказа: {e}")
            QtWidgets.QMessageBox.warning(None, "Ошибка",
                                          "Некорректный ID заказа")
        except Exception as e:
            print(f"Ошибка открытия деталей заказа: {e}")
            QtWidgets.QMessageBox.warning(None, "Ошибка",
                                          f"Не удалось открыть детали заказа: {e}")

    def open_order_edit_dialog(self, order_id, order_data):
        """Открывает диалог редактирования заказа"""
        try:
            from CRM_Order_Edit import OrderEditDialog
            dialog = OrderEditDialog(order_id, order_data)
            result = dialog.exec_()

            if result == QtWidgets.QDialog.Accepted:
                self.load_orders_data()
                QtWidgets.QMessageBox.information(None, "Успех", "Изменения сохранены")

        except ImportError as e:
            print(f"Не удалось импортировать модуль редактирования: {e}")
            QtWidgets.QMessageBox.warning(None, "Функция недоступна",
                                          "Модуль редактирования заказов временно недоступен")
        except Exception as e:
            print(f"Ошибка открытия диалога редактирования: {e}")
            QtWidgets.QMessageBox.critical(None, "Ошибка",
                                           f"Не удалось открыть форму редактирования: {e}")

    def open_objectives(self):
        """Открывает окно задач"""
        try:
            from Handlers.employee_objectives import ObjectivesDialog
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
        """Открывает окно управления клиентами"""
        try:
            from Handlers.employee_customers import CustomersDialog
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
        """Открывает окно с магазинами"""
        try:
            from Handlers.shops_dialog import ShopsDialog
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

    def add_new_order(self):
        """Открывает форму добавления нового заказа"""
        try:
            try:
                from CRM_Add_Order import AddOrderDialog
            except ImportError as e:
                print(f"Не удалось импортировать модуль добавления заказа: {e}")
                QtWidgets.QMessageBox.critical(None, "Ошибка",
                                               "Модуль добавления заказов не найден")
                return

            dialog = AddOrderDialog()
            result = dialog.exec_()

            if result == QtWidgets.QDialog.Accepted:
                self.load_orders_data()
                QtWidgets.QMessageBox.information(None, "Успех", "Новый заказ добавлен!")

        except Exception as e:
            print(f"Ошибка открытия формы добавления заказа: {e}")
            QtWidgets.QMessageBox.critical(None, "Ошибка",
                                           f"Не удалось открыть форму добавления заказа: {e}")


class MainCRMWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_main_window_CRM()
        self.ui.setupUi(self)

        employee_session.set_main_window(self.ui)

        if not employee_session.is_authenticated():
            QTimer.singleShot(100, self.show_login_dialog)

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainCRMWindow()
    main_window.show()
    sys.exit(app.exec_())