# -*- coding: utf-8 -*-
"""
Модуль для отображения отчетов CRM системы.
Содержит диалог с вкладками для различных типов отчетов.
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QDateEdit, QComboBox, QLabel, QMessageBox, QHeaderView, QFrame, QGroupBox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm


class ReportsDialog(QDialog):
    """Диалог для отображения отчетов CRM"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Отчеты CRM")
        self.setMinimumSize(1000, 700)
        self.setModal(True)

        # Устанавливаем стиль
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #d0d0d0;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #404040;
            }
            QGroupBox {
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QComboBox, QDateEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:hover, QDateEdit:hover {
                border-color: #4CAF50;
            }
            QTableWidget {
                background-color: #2a2a2a;
                color: white;
                gridline-color: #3a3a3a;
                alternate-background-color: #323232;
                selection-background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
            }
            QLabel {
                color: #d0d0d0;
            }
        """)

        self.setup_ui()
        self.load_default_reports()

    def setup_ui(self):
        """Создает интерфейс диалога"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Заголовок
        title_label = QLabel("Аналитика и отчеты CRM")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Создаем вкладки
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Вкладка 1: Общие отчеты
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "📊 Общие отчеты")

        # Вкладка 2: Финансовые отчеты
        self.financial_tab = self.create_financial_tab()
        self.tab_widget.addTab(self.financial_tab, "💰 Финансовые отчеты")

        # Вкладка 3: Товары и услуги
        self.products_tab = self.create_products_tab()
        self.tab_widget.addTab(self.products_tab, "📦 Товары и услуги")

        # Вкладка 4: Аналитика по полям
        self.fields_tab = self.create_fields_tab()
        self.tab_widget.addTab(self.fields_tab, "🔍 Аналитика по полям")

        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(120)
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)
        main_layout.addLayout(close_layout)

    def create_general_tab(self):
        """Создает вкладку общих отчетов"""
        tab = QtWidgets.QWidget()
        layout = QVBoxLayout(tab)

        # Панель фильтров
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #2d2d2d; border-radius: 8px; padding: 10px;")
        filter_layout = QHBoxLayout(filter_frame)

        filter_layout.addWidget(QLabel("Период:"))

        self.general_start_date = QDateEdit()
        self.general_start_date.setCalendarPopup(True)
        self.general_start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.general_start_date)

        filter_layout.addWidget(QLabel("по"))

        self.general_end_date = QDateEdit()
        self.general_end_date.setCalendarPopup(True)
        self.general_end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.general_end_date)

        filter_layout.addStretch()

        self.general_refresh_btn = QPushButton("Обновить")
        self.general_refresh_btn.clicked.connect(self.load_general_report)
        filter_layout.addWidget(self.general_refresh_btn)

        layout.addWidget(filter_frame)

        # Таблица для сводного отчета
        self.general_table = QTableWidget()
        self.general_table.setAlternatingRowColors(True)
        layout.addWidget(self.general_table)

        return tab

    def create_financial_tab(self):
        """Создает вкладку финансовых отчетов"""
        tab = QtWidgets.QWidget()
        layout = QVBoxLayout(tab)

        # Панель фильтров
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #2d2d2d; border-radius: 8px; padding: 10px;")
        filter_layout = QHBoxLayout(filter_frame)

        filter_layout.addWidget(QLabel("Период:"))

        self.financial_start_date = QDateEdit()
        self.financial_start_date.setCalendarPopup(True)
        self.financial_start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.financial_start_date)

        filter_layout.addWidget(QLabel("по"))

        self.financial_end_date = QDateEdit()
        self.financial_end_date.setCalendarPopup(True)
        self.financial_end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.financial_end_date)

        filter_layout.addWidget(QLabel("Тип отчета:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Приходы и расходы", "Прибыль по заказам", "Сводка платежей"])
        filter_layout.addWidget(self.report_type_combo)

        filter_layout.addStretch()

        self.financial_refresh_btn = QPushButton("Обновить")
        self.financial_refresh_btn.clicked.connect(self.load_financial_report)
        filter_layout.addWidget(self.financial_refresh_btn)

        layout.addWidget(filter_frame)

        # Группа для итогов
        summary_group = QGroupBox("Итоги за период")
        summary_layout = QHBoxLayout(summary_group)

        self.total_income_label = QLabel("Доходы: 0 ₽")
        self.total_income_label.setStyleSheet("font-size: 14px; color: #4CAF50;")
        summary_layout.addWidget(self.total_income_label)

        self.total_expense_label = QLabel("Расходы: 0 ₽")
        self.total_expense_label.setStyleSheet("font-size: 14px; color: #f44336;")
        summary_layout.addWidget(self.total_expense_label)

        self.net_profit_label = QLabel("Прибыль: 0 ₽")
        self.net_profit_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFC107;")
        summary_layout.addWidget(self.net_profit_label)

        summary_layout.addStretch()
        layout.addWidget(summary_group)

        # Таблица для финансового отчета
        self.financial_table = QTableWidget()
        self.financial_table.setAlternatingRowColors(True)
        layout.addWidget(self.financial_table)

        return tab

    def create_products_tab(self):
        """Создает вкладку отчетов по товарам и услугам"""
        tab = QtWidgets.QWidget()
        layout = QVBoxLayout(tab)

        # Панель фильтров
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #2d2d2d; border-radius: 8px; padding: 10px;")
        filter_layout = QHBoxLayout(filter_frame)

        filter_layout.addWidget(QLabel("Тип отчета:"))
        self.products_report_type = QComboBox()
        self.products_report_type.addItems(["Товары - сводка", "Товары - реализация", "Услуги - сводка"])
        filter_layout.addWidget(self.products_report_type)

        filter_layout.addStretch()

        self.products_refresh_btn = QPushButton("Обновить")
        self.products_refresh_btn.clicked.connect(self.load_products_report)
        filter_layout.addWidget(self.products_refresh_btn)

        layout.addWidget(filter_frame)

        # Таблица для отчета по товарам
        self.products_table = QTableWidget()
        self.products_table.setAlternatingRowColors(True)
        layout.addWidget(self.products_table)

        return tab

    def create_fields_tab(self):
        """Создает вкладку аналитики по полям"""
        tab = QtWidgets.QWidget()
        layout = QVBoxLayout(tab)

        # Панель фильтров
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #2d2d2d; border-radius: 8px; padding: 10px;")
        filter_layout = QHBoxLayout(filter_frame)

        filter_layout.addWidget(QLabel("Поле для анализа:"))
        self.field_combo = QComboBox()
        self.field_combo.addItems(["Причины обращений", "Откуда узнали", "Тип устройства", "Бренд"])
        filter_layout.addWidget(self.field_combo)

        filter_layout.addStretch()

        self.fields_refresh_btn = QPushButton("Обновить")
        self.fields_refresh_btn.clicked.connect(self.load_fields_report)
        filter_layout.addWidget(self.fields_refresh_btn)

        layout.addWidget(filter_frame)

        # Таблица для аналитики по полям
        self.fields_table = QTableWidget()
        self.fields_table.setAlternatingRowColors(True)
        layout.addWidget(self.fields_table)

        return tab

    def load_default_reports(self):
        """Загружает отчеты по умолчанию"""
        self.load_general_report()
        self.load_financial_report()
        self.load_products_report()
        self.load_fields_report()

    def load_general_report(self):
        """Загружает общий сводный отчет по компании"""
        try:
            start_date = self.general_start_date.date().toString("yyyy-MM-dd")
            end_date = self.general_end_date.date().toString("yyyy-MM-dd")

            # Получаем данные из БД
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            # Сводный отчет: количество заказов, сумма, по типам
            query = """
                SELECT 
                    DATE(OrderDate) as date,
                    COUNT(*) as orders_count,
                    SUM(FinalAmount) as total_amount,
                    SUM(CASE WHEN OrderType = 'Платный' THEN FinalAmount ELSE 0 END) as paid_amount,
                    SUM(CASE WHEN OrderType = 'Гарантийный' THEN FinalAmount ELSE 0 END) as warranty_amount,
                    COUNT(CASE WHEN Status = 'Завершен' OR Status = 'Готовое' THEN 1 END) as completed_orders
                FROM Orders
                WHERE OrderDate BETWEEN %s AND %s
                GROUP BY DATE(OrderDate)
                ORDER BY date DESC
                LIMIT 30
            """

            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()
            cursor.close()
            connection.close()

            # Заполняем таблицу
            self.general_table.setRowCount(len(results))
            headers = ["Дата", "Заказов", "Сумма", "Платные", "Гарантийные", "Завершено"]
            self.general_table.setColumnCount(len(headers))
            self.general_table.setHorizontalHeaderLabels(headers)

            for row, data in enumerate(results):
                self.general_table.setItem(row, 0, QTableWidgetItem(str(data.get('date', ''))))
                self.general_table.setItem(row, 1, QTableWidgetItem(str(data.get('orders_count', 0))))
                self.general_table.setItem(row, 2, QTableWidgetItem(f"{data.get('total_amount', 0):.2f} ₽"))
                self.general_table.setItem(row, 3, QTableWidgetItem(f"{data.get('paid_amount', 0):.2f} ₽"))
                self.general_table.setItem(row, 4, QTableWidgetItem(f"{data.get('warranty_amount', 0):.2f} ₽"))
                self.general_table.setItem(row, 5, QTableWidgetItem(str(data.get('completed_orders', 0))))

            self.general_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка загрузки общего отчета: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить отчет: {e}")

    def load_financial_report(self):
        """Загружает финансовый отчет"""
        try:
            start_date = self.financial_start_date.date().toString("yyyy-MM-dd")
            end_date = self.financial_end_date.date().toString("yyyy-MM-dd")
            report_type = self.report_type_combo.currentText()

            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            if report_type == "Приходы и расходы":
                # Отчет по статьям приходов и расходов
                query = """
                    SELECT 
                        PaymentMethod as Статья,
                        SUM(CASE WHEN PaymentType = 'Оплата' OR PaymentType = 'Предоплата' 
                                 THEN Amount ELSE 0 END) as Приход,
                        SUM(CASE WHEN PaymentType = 'Возврат' THEN Amount ELSE 0 END) as Расход
                    FROM Payments p
                    JOIN Orders o ON p.OrderID = o.OrderID
                    WHERE DATE(p.PaymentDate) BETWEEN %s AND %s
                    GROUP BY PaymentMethod
                """
                cursor.execute(query, (start_date, end_date))
                results = cursor.fetchall()

                headers = ["Статья", "Приход", "Расход"]
                self.financial_table.setColumnCount(len(headers))
                self.financial_table.setHorizontalHeaderLabels(headers)

                total_income = 0
                total_expense = 0

                for row, data in enumerate(results):
                    self.financial_table.insertRow(row)
                    self.financial_table.setItem(row, 0, QTableWidgetItem(str(data.get('Статья', ''))))
                    self.financial_table.setItem(row, 1, QTableWidgetItem(f"{data.get('Приход', 0):.2f} ₽"))
                    self.financial_table.setItem(row, 2, QTableWidgetItem(f"{data.get('Расход', 0):.2f} ₽"))
                    total_income += data.get('Приход', 0)
                    total_expense += data.get('Расход', 0)

                self.total_income_label.setText(f"Доходы: {total_income:.2f} ₽")
                self.total_expense_label.setText(f"Расходы: {total_expense:.2f} ₽")
                self.net_profit_label.setText(f"Прибыль: {total_income - total_expense:.2f} ₽")

            elif report_type == "Прибыль по заказам":
                # Прибыль по заказам
                query = """
                    SELECT 
                        o.OrderNumber,
                        o.OrderDate,
                        o.FinalAmount,
                        o.Prepayment,
                        o.IsPaid,
                        c.FirstName as ClientName
                    FROM Orders o
                    LEFT JOIN Client c ON o.ClientID = c.ID
                    WHERE o.OrderDate BETWEEN %s AND %s
                    ORDER BY o.OrderDate DESC
                """
                cursor.execute(query, (start_date, end_date))
                results = cursor.fetchall()

                headers = ["Заказ", "Дата", "Клиент", "Сумма", "Предоплата", "Статус оплаты"]
                self.financial_table.setColumnCount(len(headers))
                self.financial_table.setHorizontalHeaderLabels(headers)

                total_profit = 0
                total_prepayments = 0

                for row, data in enumerate(results):
                    self.financial_table.insertRow(row)
                    self.financial_table.setItem(row, 0, QTableWidgetItem(str(data.get('OrderNumber', ''))))
                    self.financial_table.setItem(row, 1, QTableWidgetItem(str(data.get('OrderDate', ''))[:10]))
                    self.financial_table.setItem(row, 2, QTableWidgetItem(str(data.get('ClientName', ''))))
                    self.financial_table.setItem(row, 3, QTableWidgetItem(f"{data.get('FinalAmount', 0):.2f} ₽"))
                    self.financial_table.setItem(row, 4, QTableWidgetItem(f"{data.get('Prepayment', 0):.2f} ₽"))
                    paid_status = "Оплачен" if data.get('IsPaid') else "Не оплачен"
                    self.financial_table.setItem(row, 5, QTableWidgetItem(paid_status))

                    total_profit += data.get('FinalAmount', 0)
                    total_prepayments += data.get('Prepayment', 0)

                self.total_income_label.setText(f"Общая выручка: {total_profit:.2f} ₽")
                self.total_expense_label.setText(f"Всего предоплат: {total_prepayments:.2f} ₽")
                self.net_profit_label.setText(f"Заказов: {len(results)}")

            else:  # Сводка платежей
                query = """
                    SELECT 
                        PaymentMethod,
                        COUNT(*) as count,
                        SUM(Amount) as total
                    FROM Payments
                    WHERE DATE(PaymentDate) BETWEEN %s AND %s
                    GROUP BY PaymentMethod
                """
                cursor.execute(query, (start_date, end_date))
                results = cursor.fetchall()

                headers = ["Метод оплаты", "Количество", "Сумма"]
                self.financial_table.setColumnCount(len(headers))
                self.financial_table.setHorizontalHeaderLabels(headers)

                total_amount = 0

                for row, data in enumerate(results):
                    self.financial_table.insertRow(row)
                    self.financial_table.setItem(row, 0, QTableWidgetItem(str(data.get('PaymentMethod', ''))))
                    self.financial_table.setItem(row, 1, QTableWidgetItem(str(data.get('count', 0))))
                    self.financial_table.setItem(row, 2, QTableWidgetItem(f"{data.get('total', 0):.2f} ₽"))
                    total_amount += data.get('total', 0)

                self.total_income_label.setText(f"Всего платежей: {total_amount:.2f} ₽")
                self.total_expense_label.setText(f"Количество операций: {len(results)}")
                self.net_profit_label.setText("")

            cursor.close()
            connection.close()
            self.financial_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка загрузки финансового отчета: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить отчет: {e}")

    def load_products_report(self):
        """Загружает отчет по товарам и услугам"""
        try:
            report_type = self.products_report_type.currentText()
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            if report_type == "Товары - сводка":
                # Сводка по товарам на складе
                query = """
                    SELECT 
                        ds.DetailName as Товар,
                        ds.DetailCode as Код,
                        ds.Brand as Бренд,
                        ds.Category as Категория,
                        ds.CountInStock as Остаток,
                        ds.Price as Цена,
                        ds.CostPrice as Себестоимость,
                        (ds.Price - ds.CostPrice) as Прибыль
                    FROM DetailStock ds
                    WHERE ds.IsActive = TRUE
                    ORDER BY ds.Category, ds.DetailName
                """
                cursor.execute(query)
                results = cursor.fetchall()

                headers = ["Товар", "Код", "Бренд", "Категория", "Остаток", "Цена", "Себестоимость", "Прибыль"]
                self.products_table.setColumnCount(len(headers))
                self.products_table.setHorizontalHeaderLabels(headers)

                for row, data in enumerate(results):
                    self.products_table.insertRow(row)
                    self.products_table.setItem(row, 0, QTableWidgetItem(str(data.get('Товар', ''))))
                    self.products_table.setItem(row, 1, QTableWidgetItem(str(data.get('Код', ''))))
                    self.products_table.setItem(row, 2, QTableWidgetItem(str(data.get('Бренд', '') or '')))
                    self.products_table.setItem(row, 3, QTableWidgetItem(str(data.get('Категория', '') or '')))
                    self.products_table.setItem(row, 4, QTableWidgetItem(str(data.get('Остаток', 0))))
                    self.products_table.setItem(row, 5, QTableWidgetItem(f"{data.get('Цена', 0):.2f} ₽"))
                    self.products_table.setItem(row, 6, QTableWidgetItem(f"{data.get('Себестоимость', 0):.2f} ₽"))
                    self.products_table.setItem(row, 7, QTableWidgetItem(f"{data.get('Прибыль', 0):.2f} ₽"))

            elif report_type == "Товары - реализация":
                # Отчет по реализации товаров
                query = """
                    SELECT 
                        ds.DetailName as Товар,
                        ds.DetailCode as Код,
                        COUNT(od.OrderDetailID) as Продано_раз,
                        SUM(od.Quantity) as Всего_продано,
                        SUM(od.TotalPrice) as Выручка
                    FROM OrderDetails od
                    JOIN DetailStock ds ON od.StockID = ds.StockID
                    GROUP BY ds.StockID
                    ORDER BY Всего_продано DESC
                    LIMIT 50
                """
                cursor.execute(query)
                results = cursor.fetchall()

                headers = ["Товар", "Код", "Продано раз", "Всего продано", "Выручка"]
                self.products_table.setColumnCount(len(headers))
                self.products_table.setHorizontalHeaderLabels(headers)

                for row, data in enumerate(results):
                    self.products_table.insertRow(row)
                    self.products_table.setItem(row, 0, QTableWidgetItem(str(data.get('Товар', ''))))
                    self.products_table.setItem(row, 1, QTableWidgetItem(str(data.get('Код', ''))))
                    self.products_table.setItem(row, 2, QTableWidgetItem(str(data.get('Продано_раз', 0))))
                    self.products_table.setItem(row, 3, QTableWidgetItem(str(data.get('Всего_продано', 0))))
                    self.products_table.setItem(row, 4, QTableWidgetItem(f"{data.get('Выручка', 0):.2f} ₽"))

            else:  # Услуги - сводка
                # Сводка по услугам
                query = """
                    SELECT 
                        st.ServiceDescription as Услуга,
                        st.Category as Категория,
                        st.BasePrice as Цена,
                        COUNT(os.OrderServiceID) as Количество,
                        SUM(os.TotalPrice) as Выручка
                    FROM OrderServices os
                    JOIN ServiceTypes st ON os.ServiceTypeID = st.ServiceTypeID
                    GROUP BY st.ServiceTypeID
                    ORDER BY Количество DESC
                """
                cursor.execute(query)
                results = cursor.fetchall()

                headers = ["Услуга", "Категория", "Цена", "Количество", "Выручка"]
                self.products_table.setColumnCount(len(headers))
                self.products_table.setHorizontalHeaderLabels(headers)

                for row, data in enumerate(results):
                    self.products_table.insertRow(row)
                    self.products_table.setItem(row, 0, QTableWidgetItem(str(data.get('Услуга', ''))))
                    self.products_table.setItem(row, 1, QTableWidgetItem(str(data.get('Категория', '') or '')))
                    self.products_table.setItem(row, 2, QTableWidgetItem(f"{data.get('Цена', 0):.2f} ₽"))
                    self.products_table.setItem(row, 3, QTableWidgetItem(str(data.get('Количество', 0))))
                    self.products_table.setItem(row, 4, QTableWidgetItem(f"{data.get('Выручка', 0):.2f} ₽"))

            cursor.close()
            connection.close()
            self.products_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка загрузки отчета по товарам: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить отчет: {e}")

    def load_fields_report(self):
        """Загружает аналитику по полям"""
        try:
            field = self.field_combo.currentText()
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            if field == "Причины обращений":
                # Отчет по причинам обращений
                query = """
                    SELECT 
                        ar.ReasonName as Причина,
                        COUNT(o.OrderID) as Количество,
                        SUM(o.FinalAmount) as Сумма
                    FROM AppealReasons ar
                    LEFT JOIN Orders o ON ar.ReasonID = o.AppealReasonID
                    WHERE ar.Category = 'Общая' OR ar.Category IS NULL
                    GROUP BY ar.ReasonID
                    ORDER BY Количество DESC
                """
                cursor.execute(query)
                results = cursor.fetchall()

                headers = ["Причина обращения", "Количество заказов", "Сумма"]
                self.fields_table.setColumnCount(len(headers))
                self.fields_table.setHorizontalHeaderLabels(headers)

                for row, data in enumerate(results):
                    self.fields_table.insertRow(row)
                    self.fields_table.setItem(row, 0, QTableWidgetItem(str(data.get('Причина', ''))))
                    self.fields_table.setItem(row, 1, QTableWidgetItem(str(data.get('Количество', 0))))
                    self.fields_table.setItem(row, 2, QTableWidgetItem(f"{data.get('Сумма', 0):.2f} ₽"))

            else:
                # Общий отчет по заказам с группировкой
                field_column = {
                    "Откуда узнали": "SourceInfo",
                    "Тип устройства": "DeviceType",
                    "Бренд": "DeviceBrand"
                }.get(field, "DeviceType")

                # Проверяем, существует ли колонка (если нет, показываем сообщение)
                query = f"""
                    SELECT 
                        {field_column} as Значение,
                        COUNT(*) as Количество,
                        SUM(FinalAmount) as Сумма
                    FROM Orders
                    WHERE {field_column} IS NOT NULL AND {field_column} != ''
                    GROUP BY {field_column}
                    ORDER BY Количество DESC
                """
                cursor.execute(query)
                results = cursor.fetchall()

                if results:
                    headers = [field, "Количество заказов", "Сумма"]
                    self.fields_table.setColumnCount(len(headers))
                    self.fields_table.setHorizontalHeaderLabels(headers)

                    for row, data in enumerate(results):
                        self.fields_table.insertRow(row)
                        self.fields_table.setItem(row, 0, QTableWidgetItem(str(data.get('Значение', ''))))
                        self.fields_table.setItem(row, 1, QTableWidgetItem(str(data.get('Количество', 0))))
                        self.fields_table.setItem(row, 2, QTableWidgetItem(f"{data.get('Сумма', 0):.2f} ₽"))
                else:
                    self.fields_table.setRowCount(1)
                    self.fields_table.setColumnCount(1)
                    self.fields_table.setHorizontalHeaderLabels(["Информация"])
                    self.fields_table.setItem(0, 0, QTableWidgetItem(f"Нет данных для поля '{field}'"))

            cursor.close()
            connection.close()
            self.fields_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка загрузки аналитики по полям: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить отчет: {e}")