# -*- coding: utf-8 -*-
"""
Модуль для управления платежами (упрощённый дизайн)
"""

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QDateEdit,
    QFrame, QMessageBox
)
from PyQt5.QtGui import QColor

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server import db_crm
from Handlers.Employees.employee_session import employee_session


class PaymentsDialog(QDialog):
    """Диалог управления платежами (упрощённый дизайн)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IT-EcoSystem - Платежи")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Настройка интерфейса (упрощённый)"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Простой тёмный стиль (без градиентов и сложных декораций)
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QFrame {
                background-color: #3a3a3a;
                border-radius: 3px;
                padding: 10px;
            }
            QLabel {
                color: #f0f0f0;
            }
            QLabel[heading="true"] {
                font-size: 16px;
                font-weight: bold;
                color: #2d7d3a;
                padding-bottom: 5px;
            }
            QLabel[value="true"] {
                font-size: 22px;
                font-weight: bold;
                color: #f0f0f0;
            }
            QLabel[income="true"] {
                color: #2d7d3a;
            }
            QLabel[expense="true"] {
                color: #dc3545;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #2d7d3a;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #f0f0f0;
                border: 1px solid #5a5a5a;
                border-radius: 2px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton[secondary="true"] {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
            }
            QPushButton[secondary="true"]:hover {
                background-color: #5a5a5a;
            }
            QPushButton#addBtn {
                background-color: #2d7d3a;
                border: none;
                color: white;
            }
            QPushButton#addBtn:hover {
                background-color: #3a9a4a;
            }
            QTableWidget {
                background-color: #3a3a3a;
                alternate-background-color: #404040;
                gridline-color: #555;
                border: none;
                border-radius: 2px;
            }
            QTableWidget::item {
                padding: 4px;
                color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #2d7d3a;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)

        # ===== Верхняя панель с балансом =====
        balance_frame = QFrame()
        balance_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 3px;")
        balance_layout = QHBoxLayout(balance_frame)

        balance_widget = QFrame()
        balance_widget.setStyleSheet("background: transparent;")
        balance_vlayout = QVBoxLayout(balance_widget)

        balance_label = QLabel("Баланс")
        balance_label.setProperty("heading", True)
        self.balance_value = QLabel("0 ₽")
        self.balance_value.setProperty("value", True)
        self.balance_value.setStyleSheet("font-size: 28px; color: #2d7d3a;")

        balance_vlayout.addWidget(balance_label)
        balance_vlayout.addWidget(self.balance_value)

        income_widget = QFrame()
        income_widget.setStyleSheet("background: transparent;")
        income_vlayout = QVBoxLayout(income_widget)

        income_label = QLabel("Приход (30 дн)")
        income_label.setProperty("heading", True)
        income_label.setStyleSheet("font-size: 13px;")
        self.income_value = QLabel("0 ₽")
        self.income_value.setProperty("value", True)
        self.income_value.setProperty("income", True)
        self.income_value.setStyleSheet("color: #2d7d3a;")

        income_vlayout.addWidget(income_label)
        income_vlayout.addWidget(self.income_value)

        expense_widget = QFrame()
        expense_widget.setStyleSheet("background: transparent;")
        expense_vlayout = QVBoxLayout(expense_widget)

        expense_label = QLabel("Расход (30 дн)")
        expense_label.setProperty("heading", True)
        expense_label.setStyleSheet("font-size: 13px;")
        self.expense_value = QLabel("0 ₽")
        self.expense_value.setProperty("value", True)
        self.expense_value.setProperty("expense", True)
        self.expense_value.setStyleSheet("color: #dc3545;")

        expense_vlayout.addWidget(expense_label)
        expense_vlayout.addWidget(self.expense_value)

        total_widget = QFrame()
        total_widget.setStyleSheet("background: transparent;")
        total_vlayout = QVBoxLayout(total_widget)

        total_label = QLabel("Итого (30 дн)")
        total_label.setProperty("heading", True)
        total_label.setStyleSheet("font-size: 13px;")
        self.total_value = QLabel("0 ₽")
        self.total_value.setProperty("value", True)

        total_vlayout.addWidget(total_label)
        total_vlayout.addWidget(self.total_value)

        balance_layout.addWidget(balance_widget)
        balance_layout.addStretch()
        balance_layout.addWidget(income_widget)
        balance_layout.addStretch()
        balance_layout.addWidget(expense_widget)
        balance_layout.addStretch()
        balance_layout.addWidget(total_widget)

        main_layout.addWidget(balance_frame)

        # ===== Панель фильтров =====
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 3px;")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(8)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setDisplayFormat("dd.MM.yyyy")
        filter_layout.addWidget(QLabel("Дата с:"))
        filter_layout.addWidget(self.date_from)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("dd.MM.yyyy")
        filter_layout.addWidget(QLabel("по:"))
        filter_layout.addWidget(self.date_to)

        filter_layout.addWidget(QLabel("Тип:"))
        self.payment_type_filter = QComboBox()
        self.payment_type_filter.addItem("Все", "")
        self.payment_type_filter.addItem("Оплата", "Оплата")
        self.payment_type_filter.addItem("Предоплата", "Предоплата")
        self.payment_type_filter.addItem("Возврат", "Возврат")
        filter_layout.addWidget(self.payment_type_filter)

        filter_layout.addWidget(QLabel("Метод:"))
        self.payment_method_filter = QComboBox()
        self.payment_method_filter.addItem("Все", "")
        self.payment_method_filter.addItem("Наличные", "Наличные")
        self.payment_method_filter.addItem("Карта", "Карта")
        self.payment_method_filter.addItem("Перевод", "Перевод")
        self.payment_method_filter.addItem("Онлайн", "Онлайн")
        filter_layout.addWidget(self.payment_method_filter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по номеру заказа, клиенту...")
        self.search_input.setMinimumWidth(220)
        filter_layout.addWidget(self.search_input)

        self.filter_btn = QPushButton("Применить")
        self.filter_btn.clicked.connect(self.load_data)
        filter_layout.addWidget(self.filter_btn)

        self.reset_btn = QPushButton("Сбросить")
        self.reset_btn.setProperty("secondary", True)
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)

        main_layout.addWidget(filter_frame)

        # ===== Таблица платежей =====
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(11)

        headers = [
            "Дата", "Сумма", "Тип", "Метод", "Заказ", "Клиент",
            "Устройство", "Чек", "Создал", "Основание", "PaymentID"
        ]

        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setHorizontalHeaderItem(i, item)

        self.table.setColumnHidden(10, True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(90)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self.open_payment_details)

        main_layout.addWidget(self.table)

        # ===== Нижняя панель =====
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 3px;")
        bottom_layout = QHBoxLayout(bottom_frame)

        self.stats_label = QLabel("Записей: 0")
        self.stats_label.setStyleSheet("color: #b0b0b0;")

        self.add_btn = QPushButton("+ Добавить платеж")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.clicked.connect(self.add_payment)

        self.export_btn = QPushButton("📊 Экспорт")
        self.export_btn.setProperty("secondary", True)
        self.export_btn.clicked.connect(self.export_data)

        bottom_layout.addWidget(self.stats_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.export_btn)
        bottom_layout.addWidget(self.add_btn)

        main_layout.addWidget(bottom_frame)

        self.update_financial_summary()

    def reset_filters(self):
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.payment_type_filter.setCurrentIndex(0)
        self.payment_method_filter.setCurrentIndex(0)
        self.search_input.clear()
        self.load_data()

    def load_data(self):
        try:
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            payment_type = self.payment_type_filter.currentData()
            payment_method = self.payment_method_filter.currentData()
            search_text = self.search_input.text().strip() or None

            payments = db_crm.get_all_payments_with_details(
                start_date=date_from,
                end_date=date_to,
                payment_type=payment_type,
                payment_method=payment_method,
                search_text=search_text,
                limit=500
            )

            self.update_table(payments)

        except Exception as e:
            print(f"Ошибка загрузки платежей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить платежи: {e}")

    def update_table(self, payments):
        self.table.setRowCount(len(payments))

        for row, payment in enumerate(payments):
            date_item = QTableWidgetItem()
            if payment.get('PaymentDate'):
                date_str = payment['PaymentDate'].strftime("%d.%m %H:%M") if hasattr(payment['PaymentDate'],
                                                                                     'strftime') else str(
                    payment['PaymentDate'])[:16]
                date_item.setText(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, date_item)

            amount = float(payment.get('Amount', 0))
            amount_item = QTableWidgetItem(f"{amount:,.2f} ₽".replace(",", " "))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            if payment.get('PaymentType') == 'Возврат':
                amount_item.setForeground(QColor(244, 67, 54))
            else:
                amount_item.setForeground(QColor(76, 175, 80))

            self.table.setItem(row, 1, amount_item)

            type_item = QTableWidgetItem(payment.get('PaymentType', ''))
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, type_item)

            method_item = QTableWidgetItem(payment.get('PaymentMethod', ''))
            method_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, method_item)

            order_item = QTableWidgetItem(payment.get('OrderNumber', ''))
            order_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, order_item)

            client_item = QTableWidgetItem(payment.get('ClientName', ''))
            self.table.setItem(row, 5, client_item)

            device = f"{payment.get('DeviceBrand', '')} {payment.get('DeviceModel', '')}".strip()
            if not device:
                device = payment.get('DeviceType', '')
            device_item = QTableWidgetItem(device)
            self.table.setItem(row, 6, device_item)

            receipt = payment.get('ReceiptNumber', '')
            receipt_item = QTableWidgetItem(receipt if receipt else "Нет")
            receipt_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 7, receipt_item)

            employee_item = QTableWidgetItem(payment.get('EmployeeName', ''))
            self.table.setItem(row, 8, employee_item)

            notes = payment.get('PaymentNotes', '') or payment.get('OrderType', '')
            notes_item = QTableWidgetItem(notes)
            self.table.setItem(row, 9, notes_item)

            payment_id_item = QTableWidgetItem(str(payment.get('PaymentID', '')))
            self.table.setItem(row, 10, payment_id_item)

        self.table.resizeColumnsToContents()
        self.stats_label.setText(f"Записей: {len(payments)}")
        self.update_financial_summary()

    def update_financial_summary(self):
        try:
            summary = db_crm.get_financial_summary_with_categories()

            self.balance_value.setText(f"{summary.get('total_balance', 0):,.2f} ₽".replace(",", " "))

            order_income = summary.get('order_income', 0)
            other_income = summary.get('other_income', 0)
            total_income = summary.get('total_income', 0)

            self.income_value.setText(f"+{total_income:,.2f} ₽".replace(",", " "))
            self.income_value.setToolTip(
                f"Доходы от заказов: {order_income:,.2f} ₽\nПрочие доходы: {other_income:,.2f} ₽")

            expense = summary.get('expense', 0)
            self.expense_value.setText(f"-{expense:,.2f} ₽".replace(",", " "))

            net_profit = summary.get('net_profit', 0)
            total_color = "#2d7d3a" if net_profit >= 0 else "#dc3545"
            self.total_value.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {total_color};")
            self.total_value.setText(f"{net_profit:+,.2f} ₽".replace(",", " "))

        except Exception as e:
            print(f"Ошибка обновления сводки: {e}")

    def open_payment_details(self, row, column):
        payment_id_item = self.table.item(row, 10)
        if payment_id_item:
            QMessageBox.information(self, "Детали платежа",
                                    f"ID платежа: {payment_id_item.text()}\n"
                                    "Подробная информация будет доступна в следующей версии.")

    def add_payment(self):
        try:
            from Handlers.Dialog.add_payment_dialog import AddPaymentDialog
            dialog = AddPaymentDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_data()
                self.update_financial_summary()
                QMessageBox.information(self, "Успех", "Платеж успешно добавлен")
        except ImportError as e:
            print(f"Ошибка импорта модуля добавления платежа: {e}")
            self.show_simple_add_payment_dialog()
        except Exception as e:
            print(f"Ошибка открытия диалога добавления платежа: {e}")
            self.show_simple_add_payment_dialog()

    def show_simple_add_payment_dialog(self):
        from PyQt5.QtWidgets import QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить платеж")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
            }
            QLineEdit, QComboBox {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 4px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #f0f0f0;
                border: 1px solid #5a5a5a;
                border-radius: 2px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton[text="OK"] {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton[text="OK"]:hover {
                background-color: #3a9a4a;
            }
        """)
        layout = QVBoxLayout(dialog)

        order_input = QLineEdit()
        order_input.setPlaceholderText("Номер заказа (например: ORD-20260323-0001)")
        layout.addWidget(QLabel("Заказ:"))
        layout.addWidget(order_input)

        amount_input = QLineEdit()
        amount_input.setPlaceholderText("Сумма")
        layout.addWidget(QLabel("Сумма:"))
        layout.addWidget(amount_input)

        method_combo = QComboBox()
        method_combo.addItems(["Наличные", "Карта", "Перевод", "Онлайн"])
        layout.addWidget(QLabel("Метод оплаты:"))
        layout.addWidget(method_combo)

        type_combo = QComboBox()
        type_combo.addItems(["Оплата", "Предоплата", "Возврат"])
        layout.addWidget(QLabel("Тип платежа:"))
        layout.addWidget(type_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            order_number = order_input.text().strip()
            try:
                amount = float(amount_input.text().strip())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректную сумму")
                return

            order_id = db_crm.get_order_id_by_number(order_number)
            if not order_id:
                QMessageBox.warning(self, "Ошибка", f"Заказ {order_number} не найден")
                return

            payment_data = {
                'amount': amount,
                'payment_method': method_combo.currentText(),
                'payment_type': type_combo.currentText(),
                'receipt_number': None,
                'notes': f"Платеж по заказу {order_number}",
                'employee_id': employee_session.get_employee_id() if employee_session.is_authenticated() else None
            }

            success, message = db_crm.add_payment_with_validation(order_id, payment_data)
            if success:
                self.load_data()
                self.update_financial_summary()
                QMessageBox.information(self, "Успех", message)
            else:
                QMessageBox.critical(self, "Ошибка", message)

    def export_data(self):
        from PyQt5.QtWidgets import QFileDialog
        import csv

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчет", "payments_report.csv", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)

                    headers = []
                    for i in range(self.table.columnCount() - 1):
                        headers.append(self.table.horizontalHeaderItem(i).text())
                    writer.writerow(headers)

                    for row in range(self.table.rowCount()):
                        row_data = []
                        for col in range(self.table.columnCount() - 1):
                            item = self.table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)

                QMessageBox.information(self, "Успех", f"Отчет сохранен в {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить отчет: {e}")