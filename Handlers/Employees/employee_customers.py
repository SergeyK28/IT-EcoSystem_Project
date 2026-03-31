# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
                             QGraphicsDropShadowEffect, QWidget, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QGridLayout,
                             QSplitter, QAbstractItemView, QDateEdit)
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm


class CustomersDialog(QDialog):
    """Окно управления клиентами"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_client_id = None
        self.setup_ui()
        self.load_customers()

    def setup_ui(self):
        self.setObjectName("CustomersDialog")
        self.setWindowTitle("IT-EcoSystem CRM - Клиенты")
        self.setFixedSize(1200, 800)

        # Основной стиль
        self.setStyleSheet("""
            QDialog {
                background-color: rgb(23, 23, 23);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
                min-height: 25px;
            }
            QPushButton#closeBtn {
                background-color: rgb(119, 118, 123);
                color: rgb(255, 255, 255);
                min-width: 35px;
                max-width: 35px;
                min-height: 35px;
                max-height: 35px;
                font-size: 16px;
                padding: 0px;
            }
            QPushButton#closeBtn:hover {
                background-color: rgb(139, 138, 143);
            }
            QPushButton#addBtn {
                background-color: rgb(40, 167, 69);
                color: white;
                font-size: 12pt;
                padding: 10px;
            }
            QPushButton#addBtn:hover {
                background-color: rgb(50, 187, 79);
            }
            QPushButton#editBtn {
                background-color: rgb(255, 193, 7);
                color: black;
            }
            QPushButton#editBtn:hover {
                background-color: rgb(255, 213, 27);
            }
            QPushButton#ordersBtn {
                background-color: rgb(23, 162, 184);
                color: white;
            }
            QPushButton#ordersBtn:hover {
                background-color: rgb(33, 172, 194);
            }
            QTabWidget::pane {
                border: 1px solid rgb(103, 155, 118);
                background-color: rgb(30, 30, 30);
            }
            QTabBar::tab {
                background-color: rgb(45, 45, 45);
                color: rgb(255, 255, 255);
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: rgb(103, 155, 118);
                color: white;
            }
            QTabBar::tab:hover {
                background-color: rgb(60, 60, 60);
            }
            QTableWidget {
                background-color: rgb(40, 40, 40);
                color: rgb(255, 255, 255);
                gridline-color: rgb(80, 80, 80);
                alternate-background-color: rgb(50, 50, 50);
                selection-background-color: rgb(103, 155, 118);
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: rgb(103, 155, 118);
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid rgb(80, 80, 80);
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: rgb(45, 45, 45);
                color: rgb(255, 255, 255);
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 3px;
            }
            QFrame#clientCard {
                background-color: rgb(35, 35, 35);
                border-radius: 10px;
                border: 1px solid rgb(103, 155, 118);
            }
            QFrame#infoCard {
                background-color: rgb(40, 40, 40);
                border-radius: 8px;
                border-left: 4px solid rgb(103, 155, 118);
            }
        """)

        # Убираем стандартные рамки окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 1200, 800)
        main_container.setStyleSheet("""
            QFrame {
                background-color: rgb(23, 23, 23);
                border-radius: 15px;
                border: 2px solid rgb(103, 155, 118);
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Верхняя панель
        header_layout = QHBoxLayout()

        title_label = QLabel("👥 КЛИЕНТЫ")
        title_label.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: rgb(103, 155, 118);
            padding: 5px;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Панель поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск клиентов (имя, телефон, email)...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self.search_customers)
        header_layout.addWidget(self.search_input)

        # Кнопка добавления клиента
        self.add_btn = QPushButton("➕ Новый клиент")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.show_add_customer_dialog)
        header_layout.addWidget(self.add_btn)

        # Кнопка закрытия
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Основной сплиттер
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель - список клиентов
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Статистика
        stats_layout = QHBoxLayout()

        self.total_clients_label = QLabel("Всего клиентов: 0")
        self.total_clients_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px;")
        stats_layout.addWidget(self.total_clients_label)

        self.active_clients_label = QLabel("Активных: 0")
        self.active_clients_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px;")
        stats_layout.addWidget(self.active_clients_label)

        self.with_orders_label = QLabel("С заказами: 0")
        self.with_orders_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px;")
        stats_layout.addWidget(self.with_orders_label)

        stats_layout.addStretch()
        left_layout.addLayout(stats_layout)

        # Таблица клиентов
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Email", "Дата рег.", "Заказов"])
        self.customers_table.setColumnHidden(0, True)  # Скрываем ID
        self.customers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.customers_table.itemSelectionChanged.connect(self.on_customer_selected)
        self.customers_table.doubleClicked.connect(self.show_customer_details)

        # Настройка ширины столбцов
        self.customers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # ФИО
        self.customers_table.setColumnWidth(2, 150)  # Телефон
        self.customers_table.setColumnWidth(3, 200)  # Email
        self.customers_table.setColumnWidth(4, 100)  # Дата рег.
        self.customers_table.setColumnWidth(5, 80)  # Заказов

        left_layout.addWidget(self.customers_table)

        # Правая панель - детальная информация о клиенте
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Карточка клиента
        self.client_card = QFrame()
        self.client_card.setObjectName("clientCard")
        self.client_card.setVisible(False)
        card_layout = QVBoxLayout(self.client_card)

        # Верхняя часть карточки с аватаром и основными данными
        card_header = QHBoxLayout()

        # Аватар
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setStyleSheet("""
            background-color: rgb(103, 155, 118);
            border-radius: 40px;
            color: white;
            font-size: 36px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
        """)
        card_header.addWidget(self.avatar_label)

        # Основная информация
        info_layout = QVBoxLayout()

        self.client_name_label = QLabel()
        self.client_name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        info_layout.addWidget(self.client_name_label)

        self.client_contacts_label = QLabel()
        self.client_contacts_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 14px;")
        info_layout.addWidget(self.client_contacts_label)

        self.client_reg_label = QLabel()
        self.client_reg_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 12px;")
        info_layout.addWidget(self.client_reg_label)

        card_header.addLayout(info_layout)
        card_header.addStretch()

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        self.edit_client_btn = QPushButton("✏️ Редактировать")
        self.edit_client_btn.setObjectName("editBtn")
        self.edit_client_btn.setCursor(Qt.PointingHandCursor)
        self.edit_client_btn.clicked.connect(self.edit_current_client)
        buttons_layout.addWidget(self.edit_client_btn)

        self.view_orders_btn = QPushButton("📦 Заказы клиента")
        self.view_orders_btn.setObjectName("ordersBtn")
        self.view_orders_btn.setCursor(Qt.PointingHandCursor)
        self.view_orders_btn.clicked.connect(self.view_client_orders)
        buttons_layout.addWidget(self.view_orders_btn)

        card_layout.addLayout(card_header)
        card_layout.addLayout(buttons_layout)

        right_layout.addWidget(self.client_card)

        # Табы с дополнительной информацией
        self.info_tabs = QTabWidget()
        self.info_tabs.setVisible(False)

        # Вкладка с заказами клиента
        self.orders_tab = QWidget()
        self.setup_orders_tab()
        self.info_tabs.addTab(self.orders_tab, "Заказы клиента")

        # Вкладка с историей обращений
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.info_tabs.addTab(self.history_tab, "История обращений")

        # Вкладка с устройствами
        self.devices_tab = QWidget()
        self.setup_devices_tab()
        self.info_tabs.addTab(self.devices_tab, "Устройства")

        right_layout.addWidget(self.info_tabs)

        # Добавляем панели в сплиттер
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 600])  # Равные размеры

        layout.addWidget(splitter)

    def setup_orders_tab(self):
        """Настраивает вкладку с заказами клиента"""
        layout = QVBoxLayout(self.orders_tab)

        # Таблица заказов
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "№ заказа", "Дата", "Статус", "Устройство", "Проблема", "Сумма", "Статус оплаты"
        ])
        self.orders_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.orders_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.orders_table.doubleClicked.connect(self.open_order_from_client)

        # Настройка ширины столбцов
        self.orders_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # Проблема
        self.orders_table.setColumnWidth(0, 100)  # № заказа
        self.orders_table.setColumnWidth(1, 100)  # Дата
        self.orders_table.setColumnWidth(2, 120)  # Статус
        self.orders_table.setColumnWidth(3, 150)  # Устройство
        self.orders_table.setColumnWidth(5, 80)  # Сумма
        self.orders_table.setColumnWidth(6, 100)  # Статус оплаты

        layout.addWidget(self.orders_table)

    def setup_history_tab(self):
        """Настраивает вкладку с историей обращений"""
        layout = QVBoxLayout(self.history_tab)

        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Тип", "Описание", "Ответственный"])
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        layout.addWidget(self.history_table)

    def setup_devices_tab(self):
        """Настраивает вкладку с устройствами клиента"""
        layout = QVBoxLayout(self.devices_tab)

        # Таблица устройств
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(5)
        self.devices_table.setHorizontalHeaderLabels(["Тип", "Бренд", "Модель", "IMEI/SN", "Последний ремонт"])
        self.devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.devices_table)

    def load_customers(self, search_text=""):
        """Загружает список клиентов"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            if search_text:
                # Поиск клиентов
                search_pattern = f"%{search_text}%"
                cursor.execute("""
                    SELECT 
                        c.ID,
                        c.FirstName,
                        c.LastName,
                        c.PhoneNumber,
                        c.Email,
                        c.RegistrationDate,
                        c.IsActive,
                        (SELECT COUNT(*) FROM Orders o WHERE o.ClientID = c.ID) as OrdersCount
                    FROM Client c
                    WHERE c.FirstName LIKE %s 
                       OR c.LastName LIKE %s 
                       OR c.PhoneNumber LIKE %s 
                       OR c.Email LIKE %s
                       OR CONCAT(c.FirstName, ' ', c.LastName) LIKE %s
                    ORDER BY c.RegistrationDate DESC
                    LIMIT 100
                """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            else:
                # Все клиенты
                cursor.execute("""
                    SELECT 
                        c.ID,
                        c.FirstName,
                        c.LastName,
                        c.PhoneNumber,
                        c.Email,
                        c.RegistrationDate,
                        c.IsActive,
                        (SELECT COUNT(*) FROM Orders o WHERE o.ClientID = c.ID) as OrdersCount
                    FROM Client c
                    ORDER BY c.RegistrationDate DESC
                    LIMIT 100
                """)

            customers = cursor.fetchall()
            cursor.close()
            connection.close()

            # Обновляем статистику
            self.update_statistics(customers)

            # Заполняем таблицу
            self.customers_table.setRowCount(len(customers))

            for row, customer in enumerate(customers):
                # ID
                self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer['ID'])))

                # ФИО
                full_name = f"{customer['FirstName']} {customer['LastName']}".strip()
                name_item = QTableWidgetItem(full_name)
                self.customers_table.setItem(row, 1, name_item)

                # Телефон
                phone_item = QTableWidgetItem(customer.get('PhoneNumber', ''))
                self.customers_table.setItem(row, 2, phone_item)

                # Email
                email_item = QTableWidgetItem(customer.get('Email', ''))
                self.customers_table.setItem(row, 3, email_item)

                # Дата регистрации
                reg_date = customer.get('RegistrationDate')
                if reg_date:
                    if isinstance(reg_date, datetime):
                        reg_str = reg_date.strftime('%d.%m.%Y')
                    else:
                        reg_str = str(reg_date)[:10]
                else:
                    reg_str = ''
                self.customers_table.setItem(row, 4, QTableWidgetItem(reg_str))

                # Количество заказов
                orders_count = QTableWidgetItem(str(customer.get('OrdersCount', 0)))
                orders_count.setTextAlignment(Qt.AlignCenter)
                self.customers_table.setItem(row, 5, orders_count)

            # Автоматический выбор первого клиента
            if customers and self.customers_table.rowCount() > 0:
                self.customers_table.selectRow(0)

        except Exception as e:
            print(f"Ошибка загрузки клиентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить клиентов: {e}")

    def update_statistics(self, customers):
        """Обновляет статистику клиентов"""
        try:
            total = len(customers)
            active = sum(1 for c in customers if c.get('IsActive', True))
            with_orders = sum(1 for c in customers if c.get('OrdersCount', 0) > 0)

            self.total_clients_label.setText(f"Всего клиентов: {total}")
            self.active_clients_label.setText(f"Активных: {active}")
            self.with_orders_label.setText(f"С заказами: {with_orders}")
        except:
            pass

    def search_customers(self):
        """Поиск клиентов"""
        search_text = self.search_input.text().strip()
        self.load_customers(search_text)

    def on_customer_selected(self):
        """Обработчик выбора клиента в таблице"""
        current_row = self.customers_table.currentRow()
        if current_row >= 0:
            client_id_item = self.customers_table.item(current_row, 0)
            if client_id_item:
                client_id = int(client_id_item.text())
                self.load_client_details(client_id)

    def load_client_details(self, client_id):
        """Загружает детальную информацию о клиенте"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            # Основная информация о клиенте
            cursor.execute("""
                SELECT 
                    ID,
                    FirstName,
                    LastName,
                    PhoneNumber,
                    Email,
                    Birthdate,
                    RegistrationDate,
                    LastLogin,
                    IsActive
                FROM Client 
                WHERE ID = %s
            """, (client_id,))

            client = cursor.fetchone()
            cursor.close()
            connection.close()

            if client:
                self.current_client_id = client_id
                self.display_client_info(client)
                self.load_client_orders(client_id)
                self.load_client_history(client_id)
                self.load_client_devices(client_id)

                # Показываем карточку и табы
                self.client_card.setVisible(True)
                self.info_tabs.setVisible(True)

        except Exception as e:
            print(f"Ошибка загрузки деталей клиента: {e}")

    def display_client_info(self, client):
        """Отображает информацию о клиенте в карточке"""
        # Имя
        first_name = client.get('FirstName', '')
        last_name = client.get('LastName', '')
        full_name = f"{first_name} {last_name}".strip()
        self.client_name_label.setText(full_name if full_name else "Без имени")

        # Инициалы для аватара
        initials = ""
        if first_name and last_name:
            initials = first_name[0] + last_name[0]
        elif first_name:
            initials = first_name[0]
        elif last_name:
            initials = last_name[0]
        else:
            initials = "👤"

        self.avatar_label.setText(initials.upper())

        # Контакты
        phone = client.get('PhoneNumber', '')
        email = client.get('Email', '')
        contacts = []
        if phone:
            contacts.append(f"📞 {phone}")
        if email:
            contacts.append(f"📧 {email}")
        self.client_contacts_label.setText(" | ".join(contacts) if contacts else "Нет контактных данных")

        # Дата регистрации
        reg_date = client.get('RegistrationDate')
        if reg_date:
            if isinstance(reg_date, datetime):
                reg_str = reg_date.strftime('%d.%m.%Y')
            else:
                reg_str = str(reg_date)[:10]
            self.client_reg_label.setText(f"Клиент с {reg_str}")

    def load_client_orders(self, client_id):
        """Загружает заказы клиента"""
        try:
            orders = db_crm.get_client_orders(client_id)

            self.orders_table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                # Номер заказа
                order_num = QTableWidgetItem(order.get('OrderNumber', f"#{order['OrderID']}"))
                self.orders_table.setItem(row, 0, order_num)

                # Дата
                order_date = order.get('OrderDate')
                if order_date:
                    if isinstance(order_date, datetime):
                        date_str = order_date.strftime('%d.%m.%Y')
                    else:
                        date_str = str(order_date)[:10]
                else:
                    date_str = ''
                self.orders_table.setItem(row, 1, QTableWidgetItem(date_str))

                # Статус
                status = order.get('Status', '')
                status_item = QTableWidgetItem(status)
                self.color_status_item(status_item, status)
                self.orders_table.setItem(row, 2, status_item)

                # Устройство
                device = f"{order.get('DeviceBrand', '')} {order.get('DeviceModel', '')}".strip()
                self.orders_table.setItem(row, 3, QTableWidgetItem(device))

                # Проблема
                problem = order.get('ProblemDescription', '')
                if len(problem) > 50:
                    problem = problem[:50] + "..."
                self.orders_table.setItem(row, 4, QTableWidgetItem(problem))

                # Сумма
                amount = order.get('FinalAmount', 0)
                amount_item = QTableWidgetItem(f"{amount:.2f} ₽")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.orders_table.setItem(row, 5, amount_item)

                # Статус оплаты
                is_paid = order.get('IsPaid', False)
                paid_text = "✅ Оплачен" if is_paid else "❌ Не оплачен"
                paid_item = QTableWidgetItem(paid_text)
                if is_paid:
                    paid_item.setForeground(QColor(40, 167, 69))
                else:
                    paid_item.setForeground(QColor(220, 53, 69))
                self.orders_table.setItem(row, 6, paid_item)

                # Сохраняем ID заказа
                order_num.setData(Qt.UserRole, order['OrderID'])

            # Автонастройка высоты строк
            for row in range(self.orders_table.rowCount()):
                self.orders_table.setRowHeight(row, 30)

        except Exception as e:
            print(f"Ошибка загрузки заказов клиента: {e}")

    def load_client_history(self, client_id):
        """Загружает историю обращений клиента"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT 
                    o.OrderDate as Date,
                    'Заказ' as Type,
                    CONCAT('Заказ #', o.OrderNumber, ': ', o.ProblemDescription) as Description,
                    CONCAT(e.FirstName, ' ', e.LastName) as EmployeeName
                FROM Orders o
                LEFT JOIN ListEmployee e ON o.ManagerID = e.EmployeeID
                WHERE o.ClientID = %s
                UNION ALL
                SELECT 
                    oc.CommentDate as Date,
                    'Комментарий' as Type,
                    oc.CommentText as Description,
                    CONCAT(e.FirstName, ' ', e.LastName) as EmployeeName
                FROM OrderComments oc
                JOIN Orders o ON oc.OrderID = o.OrderID
                LEFT JOIN ListEmployee e ON oc.EmployeeID = e.EmployeeID
                WHERE o.ClientID = %s
                ORDER BY Date DESC
                LIMIT 50
            """, (client_id, client_id))

            history = cursor.fetchall()
            cursor.close()
            connection.close()

            self.history_table.setRowCount(len(history))

            for row, item in enumerate(history):
                # Дата
                date = item.get('Date')
                if date:
                    if isinstance(date, datetime):
                        date_str = date.strftime('%d.%m.%Y %H:%M')
                    else:
                        date_str = str(date)[:16]
                else:
                    date_str = ''
                self.history_table.setItem(row, 0, QTableWidgetItem(date_str))

                # Тип
                type_item = QTableWidgetItem(item.get('Type', ''))
                if item.get('Type') == 'Заказ':
                    type_item.setForeground(QColor(103, 155, 118))
                else:
                    type_item.setForeground(QColor(255, 193, 7))
                self.history_table.setItem(row, 1, type_item)

                # Описание
                self.history_table.setItem(row, 2, QTableWidgetItem(item.get('Description', '')))

                # Ответственный
                self.history_table.setItem(row, 3, QTableWidgetItem(item.get('EmployeeName', 'Система')))

        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")

    def load_client_devices(self, client_id):
        """Загружает устройства клиента"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT DISTINCT
                    o.DeviceType,
                    o.DeviceBrand,
                    o.DeviceModel,
                    o.DeviceIMEI_SN,
                    MAX(o.CompletionDate) as LastRepair
                FROM Orders o
                WHERE o.ClientID = %s AND o.DeviceType IS NOT NULL
                GROUP BY o.DeviceType, o.DeviceBrand, o.DeviceModel, o.DeviceIMEI_SN
                ORDER BY LastRepair DESC
            """, (client_id,))

            devices = cursor.fetchall()
            cursor.close()
            connection.close()

            self.devices_table.setRowCount(len(devices))

            for row, device in enumerate(devices):
                self.devices_table.setItem(row, 0, QTableWidgetItem(device.get('DeviceType', '')))
                self.devices_table.setItem(row, 1, QTableWidgetItem(device.get('DeviceBrand', '')))
                self.devices_table.setItem(row, 2, QTableWidgetItem(device.get('DeviceModel', '')))
                self.devices_table.setItem(row, 3, QTableWidgetItem(device.get('DeviceIMEI_SN', '')))

                last_repair = device.get('LastRepair')
                if last_repair:
                    if isinstance(last_repair, datetime):
                        repair_str = last_repair.strftime('%d.%m.%Y')
                    else:
                        repair_str = str(last_repair)[:10]
                else:
                    repair_str = '-'
                self.devices_table.setItem(row, 4, QTableWidgetItem(repair_str))

        except Exception as e:
            print(f"Ошибка загрузки устройств: {e}")

    def color_status_item(self, item, status):
        """Добавляет цветовое оформление для статусов"""
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

    def show_customer_details(self):
        """Показывает детальную информацию о клиенте (при двойном клике)"""
        current_row = self.customers_table.currentRow()
        if current_row >= 0:
            # Уже загружено в on_customer_selected
            pass

    def edit_current_client(self):
        """Редактирует текущего клиента"""
        if not self.current_client_id:
            return

        dialog = EditCustomerDialog(self.current_client_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_customers(self.search_input.text().strip())

    def view_client_orders(self):
        """Показывает заказы клиента"""
        if not self.current_client_id:
            return

        # Переключаемся на вкладку с заказами
        self.info_tabs.setCurrentIndex(0)

    def open_order_from_client(self):
        """Открывает заказ из таблицы заказов клиента"""
        current_row = self.orders_table.currentRow()
        if current_row >= 0:
            order_num_item = self.orders_table.item(current_row, 0)
            if order_num_item:
                order_id = order_num_item.data(Qt.UserRole)
                if order_id:
                    self.open_order(order_id)

    def open_order(self, order_id):
        """Открывает заказ в форме редактирования"""
        try:
            from CRM_Order_Edit import OrderEditDialog

            order_data = db_crm.get_order_for_edit_form(order_id)
            if order_data:
                dialog = OrderEditDialog(order_id, order_data, self)
                if dialog.exec_() == QDialog.Accepted:
                    self.load_client_orders(self.current_client_id)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные заказа")
        except Exception as e:
            print(f"Ошибка открытия заказа: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть заказ: {e}")

    def show_add_customer_dialog(self):
        """Показывает диалог добавления нового клиента"""
        dialog = AddCustomerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_customers(self.search_input.text().strip())

    def mousePressEvent(self, event):
        """Для перетаскивания окна"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Для перетаскивания окна"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class AddCustomerDialog(QDialog):
    """Диалог добавления нового клиента"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("AddCustomerDialog")
        self.setWindowTitle("Новый клиент")
        self.setFixedSize(500, 600)

        self.setStyleSheet("""
            QDialog {
                background-color: rgb(23, 23, 23);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QPushButton {
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#createBtn {
                background-color: rgb(40, 167, 69);
                color: white;
            }
            QPushButton#cancelBtn {
                background-color: rgb(108, 117, 125);
                color: white;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: rgb(45, 45, 45);
                color: white;
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 3px;
            }
        """)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 500, 600)
        main_container.setStyleSheet("""
            QFrame {
                background-color: rgb(23, 23, 23);
                border-radius: 15px;
                border: 2px solid rgb(103, 155, 118);
            }
        """)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        header_layout = QHBoxLayout()

        title_label = QLabel("➕ НОВЫЙ КЛИЕНТ")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: rgb(103, 155, 118);")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(119, 118, 123);
                color: white;
                min-width: 35px;
                max-width: 35px;
                min-height: 35px;
                max-height: 35px;
                font-size: 16px;
                border-radius: 4px;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Форма
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)

        # Имя
        form_layout.addWidget(QLabel("Имя*:"), 0, 0)
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Введите имя")
        form_layout.addWidget(self.first_name, 0, 1, 1, 3)

        # Фамилия
        form_layout.addWidget(QLabel("Фамилия*:"), 1, 0)
        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Введите фамилию")
        form_layout.addWidget(self.last_name, 1, 1, 1, 3)

        # Телефон
        form_layout.addWidget(QLabel("Телефон*:"), 2, 0)
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        form_layout.addWidget(self.phone, 2, 1, 1, 3)

        # Email
        form_layout.addWidget(QLabel("Email:"), 3, 0)
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@example.com")
        form_layout.addWidget(self.email, 3, 1, 1, 3)

        # Дата рождения
        form_layout.addWidget(QLabel("Дата рождения:"), 4, 0)
        self.birthdate = QDateEdit()
        self.birthdate.setCalendarPopup(True)
        self.birthdate.setDisplayFormat("dd.MM.yyyy")
        self.birthdate.setDate(QDate(1990, 1, 1))
        form_layout.addWidget(self.birthdate, 4, 1, 1, 3)

        layout.addLayout(form_layout)

        layout.addStretch()

        # Информация
        info_label = QLabel("* - обязательные поля")
        info_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 10px;")
        layout.addWidget(info_label)

        # Кнопки
        buttons_layout = QHBoxLayout()

        create_btn = QPushButton("✅ Создать клиента")
        create_btn.setObjectName("createBtn")
        create_btn.clicked.connect(self.create_customer)
        buttons_layout.addWidget(create_btn)

        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def create_customer(self):
        """Создает нового клиента"""
        # Валидация
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        phone = self.phone.text().strip()

        if not first_name:
            QMessageBox.warning(self, "Ошибка", "Введите имя клиента")
            return
        if not last_name:
            QMessageBox.warning(self, "Ошибка", "Введите фамилию клиента")
            return
        if not phone:
            QMessageBox.warning(self, "Ошибка", "Введите телефон клиента")
            return

        # Подготовка данных
        client_data = {
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone,
            'email': self.email.text().strip(),
            'birthdate': self.birthdate.date().toString("yyyy-MM-dd")
        }

        try:
            # Создание клиента в БД
            connection = db_crm.get_crm_connection()
            if not connection:
                QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
                return

            cursor = connection.cursor()

            # Генерируем логин
            import random
            login = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}"

            # Генерируем временный пароль
            import hashlib
            import secrets
            temp_password = secrets.token_urlsafe(8)
            full_hash = hashlib.sha256(temp_password.encode()).hexdigest()
            password_hash = full_hash[:60]

            cursor.execute("""
                INSERT INTO Client (
                    Login, PasswordHash, FirstName, LastName, 
                    PhoneNumber, Email, Birthdate, RegistrationDate
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                login,
                password_hash,
                first_name,
                last_name,
                phone,
                client_data['email'] or None,
                client_data['birthdate'] or None
            ))

            new_client_id = cursor.lastrowid
            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Успех",
                f"Клиент успешно создан!\n\n"
                f"Логин: {login}\n"
                f"Пароль: {temp_password}\n\n"
                f"⚠️ Сохраните эти данные для клиента!")

            self.accept()

        except Exception as e:
            print(f"Ошибка создания клиента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать клиента: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class EditCustomerDialog(QDialog):
    """Диалог редактирования клиента"""

    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.setup_ui()
        self.load_client_data()

    def setup_ui(self):
        self.setObjectName("EditCustomerDialog")
        self.setWindowTitle("Редактирование клиента")
        self.setFixedSize(500, 600)

        self.setStyleSheet("""
            QDialog {
                background-color: rgb(23, 23, 23);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QPushButton {
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#saveBtn {
                background-color: rgb(40, 167, 69);
                color: white;
            }
            QPushButton#cancelBtn {
                background-color: rgb(108, 117, 125);
                color: white;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: rgb(45, 45, 45);
                color: white;
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 3px;
            }
        """)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 500, 600)
        main_container.setStyleSheet("""
            QFrame {
                background-color: rgb(23, 23, 23);
                border-radius: 15px;
                border: 2px solid rgb(103, 155, 118);
            }
        """)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        header_layout = QHBoxLayout()

        title_label = QLabel("✏️ РЕДАКТИРОВАНИЕ КЛИЕНТА")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: rgb(103, 155, 118);")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(119, 118, 123);
                color: white;
                min-width: 35px;
                max-width: 35px;
                min-height: 35px;
                max-height: 35px;
                font-size: 16px;
                border-radius: 4px;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Форма
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)

        # Имя
        form_layout.addWidget(QLabel("Имя*:"), 0, 0)
        self.first_name = QLineEdit()
        form_layout.addWidget(self.first_name, 0, 1, 1, 3)

        # Фамилия
        form_layout.addWidget(QLabel("Фамилия*:"), 1, 0)
        self.last_name = QLineEdit()
        form_layout.addWidget(self.last_name, 1, 1, 1, 3)

        # Телефон
        form_layout.addWidget(QLabel("Телефон*:"), 2, 0)
        self.phone = QLineEdit()
        form_layout.addWidget(self.phone, 2, 1, 1, 3)

        # Email
        form_layout.addWidget(QLabel("Email:"), 3, 0)
        self.email = QLineEdit()
        form_layout.addWidget(self.email, 3, 1, 1, 3)

        # Дата рождения
        form_layout.addWidget(QLabel("Дата рождения:"), 4, 0)
        self.birthdate = QDateEdit()
        self.birthdate.setCalendarPopup(True)
        self.birthdate.setDisplayFormat("dd.MM.yyyy")
        form_layout.addWidget(self.birthdate, 4, 1, 1, 3)

        layout.addLayout(form_layout)

        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Сохранить")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.save_changes)
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def load_client_data(self):
        """Загружает данные клиента"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT FirstName, LastName, PhoneNumber, Email, Birthdate
                FROM Client WHERE ID = %s
            """, (self.client_id,))

            client = cursor.fetchone()
            cursor.close()
            connection.close()

            if client:
                self.first_name.setText(client.get('FirstName', ''))
                self.last_name.setText(client.get('LastName', ''))
                self.phone.setText(client.get('PhoneNumber', ''))
                self.email.setText(client.get('Email', ''))

                birthdate = client.get('Birthdate')
                if birthdate:
                    if isinstance(birthdate, (datetime, date)):
                        qdate = QDate(birthdate.year, birthdate.month, birthdate.day)
                    else:
                        try:
                            qdate = QDate.fromString(str(birthdate), "yyyy-MM-dd")
                        except:
                            qdate = QDate(1990, 1, 1)
                    self.birthdate.setDate(qdate)

        except Exception as e:
            print(f"Ошибка загрузки данных клиента: {e}")

    def save_changes(self):
        """Сохраняет изменения"""
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        phone = self.phone.text().strip()

        if not first_name or not last_name or not phone:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return

        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Client SET
                    FirstName = %s,
                    LastName = %s,
                    PhoneNumber = %s,
                    Email = %s,
                    Birthdate = %s
                WHERE ID = %s
            """, (
                first_name,
                last_name,
                phone,
                self.email.text().strip() or None,
                self.birthdate.date().toString("yyyy-MM-dd"),
                self.client_id
            ))

            connection.commit()
            cursor.close()
            connection.close()

            QMessageBox.information(self, "Успех", "Данные клиента обновлены")
            self.accept()

        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()