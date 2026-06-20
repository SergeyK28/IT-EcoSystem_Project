# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
                             QWidget, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
                             QGridLayout, QSplitter, QAbstractItemView, QDateEdit)
import sys
import os
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm


class CustomersDialog(QDialog):
    """Окно управления клиентами (упрощённый дизайн)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_client_id = None
        self.setup_ui()
        self.load_customers()

    def setup_ui(self):
        self.setObjectName("CustomersDialog")
        self.setWindowTitle("IT-EcoSystem CRM - Клиенты")
        self.resize(1200, 800)

        # Базовый стиль – тёмный, без излишеств
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 11pt;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#addBtn {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#addBtn:hover {
                background-color: #3a9a4a;
            }
            QPushButton#editBtn {
                background-color: #e0a800;
                color: #222;
                border: none;
            }
            QPushButton#editBtn:hover {
                background-color: #f0c000;
            }
            QPushButton#ordersBtn {
                background-color: #1a7a8a;
                border: none;
            }
            QPushButton#ordersBtn:hover {
                background-color: #2a9aaa;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2a2a2a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #ddd;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2d7d3a;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            QTableWidget {
                background-color: #3a3a3a;
                color: #f0f0f0;
                gridline-color: #555;
                alternate-background-color: #404040;
                selection-background-color: #2d7d3a;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #2d7d3a;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #555;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
            QFrame#clientCard {
                background-color: #333;
                border-radius: 4px;
                border: 1px solid #2d7d3a;
            }
            QFrame#infoCard {
                background-color: #3a3a3a;
                border-radius: 3px;
                border-left: 3px solid #2d7d3a;
            }
        """)

        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Верхняя панель
        header_layout = QHBoxLayout()

        title_label = QLabel("👥 КЛИЕНТЫ")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск клиентов (имя, телефон, email)...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self.search_customers)
        header_layout.addWidget(self.search_input)

        self.add_btn = QPushButton("➕ Новый клиент")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.show_add_customer_dialog)
        header_layout.addWidget(self.add_btn)

        # Кнопка закрытия теперь стандартная, не добавляем свою
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
        self.total_clients_label.setStyleSheet("color: #bbb; font-size: 12px;")
        stats_layout.addWidget(self.total_clients_label)

        self.active_clients_label = QLabel("Активных: 0")
        self.active_clients_label.setStyleSheet("color: #bbb; font-size: 12px;")
        stats_layout.addWidget(self.active_clients_label)

        self.with_orders_label = QLabel("С заказами: 0")
        self.with_orders_label.setStyleSheet("color: #bbb; font-size: 12px;")
        stats_layout.addWidget(self.with_orders_label)

        stats_layout.addStretch()
        left_layout.addLayout(stats_layout)

        # Таблица клиентов
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Email", "Дата рег.", "Заказов"])
        self.customers_table.setColumnHidden(0, True)
        self.customers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.customers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.customers_table.itemSelectionChanged.connect(self.on_customer_selected)
        self.customers_table.doubleClicked.connect(self.show_customer_details)

        self.customers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.customers_table.setColumnWidth(2, 150)
        self.customers_table.setColumnWidth(3, 200)
        self.customers_table.setColumnWidth(4, 100)
        self.customers_table.setColumnWidth(5, 80)

        left_layout.addWidget(self.customers_table)

        # Правая панель - детальная информация
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)

        # Карточка клиента
        self.client_card = QFrame()
        self.client_card.setObjectName("clientCard")
        self.client_card.setVisible(False)
        card_layout = QVBoxLayout(self.client_card)

        card_header = QHBoxLayout()
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setStyleSheet("""
            background-color: #2d7d3a;
            border-radius: 40px;
            color: white;
            font-size: 36px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
        """)
        card_header.addWidget(self.avatar_label)

        info_layout = QVBoxLayout()
        self.client_name_label = QLabel()
        self.client_name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        info_layout.addWidget(self.client_name_label)

        self.client_contacts_label = QLabel()
        self.client_contacts_label.setStyleSheet("color: #bbb; font-size: 14px;")
        info_layout.addWidget(self.client_contacts_label)

        self.client_reg_label = QLabel()
        self.client_reg_label.setStyleSheet("color: #999; font-size: 12px;")
        info_layout.addWidget(self.client_reg_label)

        card_header.addLayout(info_layout)
        card_header.addStretch()

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

        self.orders_tab = QWidget()
        self.setup_orders_tab()
        self.info_tabs.addTab(self.orders_tab, "Заказы клиента")

        self.history_tab = QWidget()
        self.setup_history_tab()
        self.info_tabs.addTab(self.history_tab, "История обращений")

        self.devices_tab = QWidget()
        self.setup_devices_tab()
        self.info_tabs.addTab(self.devices_tab, "Устройства")

        right_layout.addWidget(self.info_tabs)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 600])

        layout.addWidget(splitter)

    def setup_orders_tab(self):
        layout = QVBoxLayout(self.orders_tab)
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(7)
        self.orders_table.setHorizontalHeaderLabels([
            "№ заказа", "Дата", "Статус", "Устройство", "Проблема", "Сумма", "Статус оплаты"
        ])
        self.orders_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.orders_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.orders_table.doubleClicked.connect(self.open_order_from_client)

        self.orders_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.orders_table.setColumnWidth(0, 100)
        self.orders_table.setColumnWidth(1, 100)
        self.orders_table.setColumnWidth(2, 120)
        self.orders_table.setColumnWidth(3, 150)
        self.orders_table.setColumnWidth(5, 80)
        self.orders_table.setColumnWidth(6, 100)

        layout.addWidget(self.orders_table)

    def setup_history_tab(self):
        layout = QVBoxLayout(self.history_tab)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Тип", "Описание", "Ответственный"])
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.history_table)

    def setup_devices_tab(self):
        layout = QVBoxLayout(self.devices_tab)
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(5)
        self.devices_table.setHorizontalHeaderLabels(["Тип", "Бренд", "Модель", "IMEI/SN", "Последний ремонт"])
        self.devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.devices_table)

    def load_customers(self, search_text=""):
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return
            cursor = connection.cursor(dictionary=True)

            if search_text:
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

            self.update_statistics(customers)

            self.customers_table.setRowCount(len(customers))

            for row, customer in enumerate(customers):
                self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer['ID'])))
                full_name = f"{customer['FirstName']} {customer['LastName']}".strip()
                self.customers_table.setItem(row, 1, QTableWidgetItem(full_name))
                self.customers_table.setItem(row, 2, QTableWidgetItem(customer.get('PhoneNumber', '')))
                self.customers_table.setItem(row, 3, QTableWidgetItem(customer.get('Email', '')))

                reg_date = customer.get('RegistrationDate')
                if reg_date:
                    if isinstance(reg_date, datetime):
                        reg_str = reg_date.strftime('%d.%m.%Y')
                    else:
                        reg_str = str(reg_date)[:10]
                else:
                    reg_str = ''
                self.customers_table.setItem(row, 4, QTableWidgetItem(reg_str))

                orders_count = QTableWidgetItem(str(customer.get('OrdersCount', 0)))
                orders_count.setTextAlignment(Qt.AlignCenter)
                self.customers_table.setItem(row, 5, orders_count)

            if customers and self.customers_table.rowCount() > 0:
                self.customers_table.selectRow(0)

        except Exception as e:
            print(f"Ошибка загрузки клиентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить клиентов: {e}")

    def update_statistics(self, customers):
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
        search_text = self.search_input.text().strip()
        self.load_customers(search_text)

    def on_customer_selected(self):
        current_row = self.customers_table.currentRow()
        if current_row >= 0:
            client_id_item = self.customers_table.item(current_row, 0)
            if client_id_item:
                client_id = int(client_id_item.text())
                self.load_client_details(client_id)

    def load_client_details(self, client_id):
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return
            cursor = connection.cursor(dictionary=True)

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

                self.client_card.setVisible(True)
                self.info_tabs.setVisible(True)

        except Exception as e:
            print(f"Ошибка загрузки деталей клиента: {e}")

    def display_client_info(self, client):
        first_name = client.get('FirstName', '')
        last_name = client.get('LastName', '')
        full_name = f"{first_name} {last_name}".strip()
        self.client_name_label.setText(full_name if full_name else "Без имени")

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

        phone = client.get('PhoneNumber', '')
        email = client.get('Email', '')
        contacts = []
        if phone:
            contacts.append(f"📞 {phone}")
        if email:
            contacts.append(f"📧 {email}")
        self.client_contacts_label.setText(" | ".join(contacts) if contacts else "Нет контактных данных")

        reg_date = client.get('RegistrationDate')
        if reg_date:
            if isinstance(reg_date, datetime):
                reg_str = reg_date.strftime('%d.%m.%Y')
            else:
                reg_str = str(reg_date)[:10]
            self.client_reg_label.setText(f"Клиент с {reg_str}")

    def load_client_orders(self, client_id):
        try:
            orders = db_crm.get_client_orders(client_id)
            self.orders_table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                order_num = QTableWidgetItem(order.get('OrderNumber', f"#{order['OrderID']}"))
                self.orders_table.setItem(row, 0, order_num)

                order_date = order.get('OrderDate')
                if order_date:
                    if isinstance(order_date, datetime):
                        date_str = order_date.strftime('%d.%m.%Y')
                    else:
                        date_str = str(order_date)[:10]
                else:
                    date_str = ''
                self.orders_table.setItem(row, 1, QTableWidgetItem(date_str))

                status = order.get('Status', '')
                status_item = QTableWidgetItem(status)
                self.color_status_item(status_item, status)
                self.orders_table.setItem(row, 2, status_item)

                device = f"{order.get('DeviceBrand', '')} {order.get('DeviceModel', '')}".strip()
                self.orders_table.setItem(row, 3, QTableWidgetItem(device))

                problem = order.get('ProblemDescription', '')
                if len(problem) > 50:
                    problem = problem[:50] + "..."
                self.orders_table.setItem(row, 4, QTableWidgetItem(problem))

                amount = order.get('FinalAmount', 0)
                amount_item = QTableWidgetItem(f"{amount:.2f} ₽")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.orders_table.setItem(row, 5, amount_item)

                is_paid = order.get('IsPaid', False)
                paid_text = "✅ Оплачен" if is_paid else "❌ Не оплачен"
                paid_item = QTableWidgetItem(paid_text)
                if is_paid:
                    paid_item.setForeground(QColor(40, 167, 69))
                else:
                    paid_item.setForeground(QColor(220, 53, 69))
                self.orders_table.setItem(row, 6, paid_item)

                order_num.setData(Qt.UserRole, order['OrderID'])

            for row in range(self.orders_table.rowCount()):
                self.orders_table.setRowHeight(row, 30)

        except Exception as e:
            print(f"Ошибка загрузки заказов клиента: {e}")

    def load_client_history(self, client_id):
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
                date = item.get('Date')
                if date:
                    if isinstance(date, datetime):
                        date_str = date.strftime('%d.%m.%Y %H:%M')
                    else:
                        date_str = str(date)[:16]
                else:
                    date_str = ''
                self.history_table.setItem(row, 0, QTableWidgetItem(date_str))

                type_item = QTableWidgetItem(item.get('Type', ''))
                if item.get('Type') == 'Заказ':
                    type_item.setForeground(QColor(40, 167, 69))
                else:
                    type_item.setForeground(QColor(255, 193, 7))
                self.history_table.setItem(row, 1, type_item)

                self.history_table.setItem(row, 2, QTableWidgetItem(item.get('Description', '')))
                self.history_table.setItem(row, 3, QTableWidgetItem(item.get('EmployeeName', 'Система')))

        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")

    def load_client_devices(self, client_id):
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
        pass  # уже загружено при выборе

    def edit_current_client(self):
        if not self.current_client_id:
            return
        dialog = EditCustomerDialog(self.current_client_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_customers(self.search_input.text().strip())

    def view_client_orders(self):
        if not self.current_client_id:
            return
        self.info_tabs.setCurrentIndex(0)

    def open_order_from_client(self):
        current_row = self.orders_table.currentRow()
        if current_row >= 0:
            order_num_item = self.orders_table.item(current_row, 0)
            if order_num_item:
                order_id = order_num_item.data(Qt.UserRole)
                if order_id:
                    self.open_order(order_id)

    def open_order(self, order_id):
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
        dialog = AddCustomerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_customers(self.search_input.text().strip())


class AddCustomerDialog(QDialog):
    """Диалог добавления нового клиента (упрощённый дизайн)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("AddCustomerDialog")
        self.setWindowTitle("Новый клиент")
        self.resize(500, 580)

        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#createBtn {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#createBtn:hover {
                background-color: #3a9a4a;
            }
            QPushButton#cancelBtn {
                background-color: #6c6c6c;
                border: none;
            }
            QPushButton#cancelBtn:hover {
                background-color: #8c8c8c;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("➕ НОВЫЙ КЛИЕНТ")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        # Кнопка закрытия стандартная, не добавляем свою
        layout.addLayout(header_layout)

        # Форма
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)

        form_layout.addWidget(QLabel("Имя*:"), 0, 0)
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Введите имя")
        form_layout.addWidget(self.first_name, 0, 1, 1, 3)

        form_layout.addWidget(QLabel("Фамилия*:"), 1, 0)
        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Введите фамилию")
        form_layout.addWidget(self.last_name, 1, 1, 1, 3)

        form_layout.addWidget(QLabel("Телефон*:"), 2, 0)
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("+7 (XXX) XXX-XX-XX")
        form_layout.addWidget(self.phone, 2, 1, 1, 3)

        form_layout.addWidget(QLabel("Email:"), 3, 0)
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@example.com")
        form_layout.addWidget(self.email, 3, 1, 1, 3)

        form_layout.addWidget(QLabel("Дата рождения:"), 4, 0)
        self.birthdate = QDateEdit()
        self.birthdate.setCalendarPopup(True)
        self.birthdate.setDisplayFormat("dd.MM.yyyy")
        self.birthdate.setDate(QDate(1990, 1, 1))
        form_layout.addWidget(self.birthdate, 4, 1, 1, 3)

        layout.addLayout(form_layout)

        layout.addStretch()

        info_label = QLabel("* - обязательные поля")
        info_label.setStyleSheet("color: #999; font-size: 10px;")
        layout.addWidget(info_label)

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

        client_data = {
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone,
            'email': self.email.text().strip(),
            'birthdate': self.birthdate.date().toString("yyyy-MM-dd")
        }

        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
                return

            cursor = connection.cursor()

            import random
            login = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}"

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


class EditCustomerDialog(QDialog):
    """Диалог редактирования клиента (упрощённый дизайн)"""

    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.setup_ui()
        self.load_client_data()

    def setup_ui(self):
        self.setObjectName("EditCustomerDialog")
        self.setWindowTitle("Редактирование клиента")
        self.resize(500, 580)

        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#saveBtn {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#saveBtn:hover {
                background-color: #3a9a4a;
            }
            QPushButton#cancelBtn {
                background-color: #6c6c6c;
                border: none;
            }
            QPushButton#cancelBtn:hover {
                background-color: #8c8c8c;
            }
            QLineEdit, QTextEdit, QDateEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        title_label = QLabel("✏️ РЕДАКТИРОВАНИЕ КЛИЕНТА")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)

        form_layout.addWidget(QLabel("Имя*:"), 0, 0)
        self.first_name = QLineEdit()
        form_layout.addWidget(self.first_name, 0, 1, 1, 3)

        form_layout.addWidget(QLabel("Фамилия*:"), 1, 0)
        self.last_name = QLineEdit()
        form_layout.addWidget(self.last_name, 1, 1, 1, 3)

        form_layout.addWidget(QLabel("Телефон*:"), 2, 0)
        self.phone = QLineEdit()
        form_layout.addWidget(self.phone, 2, 1, 1, 3)

        form_layout.addWidget(QLabel("Email:"), 3, 0)
        self.email = QLineEdit()
        form_layout.addWidget(self.email, 3, 1, 1, 3)

        form_layout.addWidget(QLabel("Дата рождения:"), 4, 0)
        self.birthdate = QDateEdit()
        self.birthdate.setCalendarPopup(True)
        self.birthdate.setDisplayFormat("dd.MM.yyyy")
        form_layout.addWidget(self.birthdate, 4, 1, 1, 3)

        layout.addLayout(form_layout)

        layout.addStretch()

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