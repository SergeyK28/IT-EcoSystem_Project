# -*- coding: utf-8 -*-
"""
Модуль для отображения трендов и аналитики CRM (упрощённый дизайн)
"""

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
                             QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
                             QWidget, QScrollArea, QSizePolicy)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm


class TrendsDialog(QDialog):
    """Диалог для отображения трендов и аналитики (упрощённый)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IT-EcoSystem - Тренды и аналитика")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        self.setup_ui()
        self.setStyleSheet(self.get_simple_style())
        self.load_data()

    def get_simple_style(self):
        """Возвращает простой тёмный стиль"""
        return """
            QDialog {
                background-color: #2e2e2e;
            }
            QFrame {
                background-color: #3a3a3a;
                border-radius: 3px;
            }
            QLabel {
                color: #f0f0f0;
            }
            QComboBox {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 2px;
                padding: 4px 8px;
                min-width: 100px;
                font-size: 12px;
            }
            QComboBox:hover {
                background-color: #4a4a4a;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #808080;
                margin-right: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: #f0f0f0;
                selection-background-color: #2d7d3a;
            }
            QTableWidget {
                background-color: #3a3a3a;
                color: #f0f0f0;
                gridline-color: #555;
                selection-background-color: #2d7d3a;
                border: none;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #2d7d3a;
            }
            QHeaderView::section {
                background-color: #2d7d3a;
                color: white;
                padding: 4px;
                border: 1px solid #555;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #f0f0f0;
                border: 1px solid #5a5a5a;
                border-radius: 2px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#refreshBtn {
                background-color: #2d7d3a;
                border: none;
                color: white;
            }
            QPushButton#refreshBtn:hover {
                background-color: #3a9a4a;
            }
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
            QScrollBar:horizontal {
                background-color: #2a2a2a;
                height: 10px;
                border-radius: 2px;
            }
            QScrollBar::handle:horizontal {
                background-color: #4a4a4a;
                border-radius: 2px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #2d7d3a;
            }
        """

    def setup_ui(self):
        """Настройка интерфейса (упрощённый)"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ===== Верхняя панель =====
        top_frame = QFrame()
        top_frame.setFixedHeight(80)
        top_frame.setStyleSheet("background-color: #333; border-radius: 3px;")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel("📊 Тренды и аналитика")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d7d3a;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        period_label = QLabel("Период:")
        period_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        top_layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["7 дней", "30 дней", "90 дней", "Год"])
        self.period_combo.setFixedWidth(100)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        top_layout.addWidget(self.period_combo)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setObjectName("refreshBtn")
        self.refresh_btn.clicked.connect(self.load_data)
        top_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(top_frame)

        # ===== Основная область (ScrollArea) =====
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: transparent;")

        content_widget = QWidget()
        content_widget.setMinimumWidth(1100)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(5, 5, 5, 5)

        # ===== Ряд 1: Метрики =====
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        self.avg_check_frame = self.create_metric_frame("💰 Средний чек заказов", "0 ₽")
        metrics_layout.addWidget(self.avg_check_frame)

        self.avg_sales_frame = self.create_metric_frame("📈 Средний чек продаж", "0 ₽")
        metrics_layout.addWidget(self.avg_sales_frame)

        self.urgent_frame = self.create_metric_frame("⚠️ Срочные заказы", "0")
        metrics_layout.addWidget(self.urgent_frame)

        self.overdue_frame = self.create_metric_frame("⏰ Просроченные заказы", "0")
        metrics_layout.addWidget(self.overdue_frame)

        content_layout.addLayout(metrics_layout)

        # ===== Ряд 2: Графики =====
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        self.orders_chart_frame = self.create_chart_frame("📅 Заказы по дням")
        charts_layout.addWidget(self.orders_chart_frame)

        self.payments_chart_frame = self.create_chart_frame("💵 Платежи по дням")
        charts_layout.addWidget(self.payments_chart_frame)

        content_layout.addLayout(charts_layout)

        # ===== Ряд 3: Платежи по статьям + Заказы по сотрудникам =====
        extra_metrics_layout = QHBoxLayout()
        extra_metrics_layout.setSpacing(15)

        # Платежи по статьям
        self.payments_by_category_frame = QFrame()
        self.payments_by_category_frame.setStyleSheet("background-color: #333; border-radius: 3px;")
        self.payments_by_category_frame.setMinimumHeight(280)
        self.payments_by_category_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        payments_layout = QVBoxLayout(self.payments_by_category_frame)
        payments_layout.setContentsMargins(10, 10, 10, 10)

        payments_title = QLabel("💰 Платежи по статьям - Топ 9")
        payments_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d7d3a;")
        payments_layout.addWidget(payments_title)

        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(2)
        self.payments_table.setHorizontalHeaderLabels(["Статья", "Сумма"])
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.payments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.payments_table.setAlternatingRowColors(True)
        payments_layout.addWidget(self.payments_table)

        extra_metrics_layout.addWidget(self.payments_by_category_frame)

        # Заказы по сотрудникам
        self.orders_by_employee_frame = QFrame()
        self.orders_by_employee_frame.setStyleSheet("background-color: #333; border-radius: 3px;")
        self.orders_by_employee_frame.setMinimumHeight(280)
        self.orders_by_employee_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        employee_layout = QVBoxLayout(self.orders_by_employee_frame)
        employee_layout.setContentsMargins(10, 10, 10, 10)

        employee_title = QLabel("👥 Заказы по сотрудникам")
        employee_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d7d3a;")
        employee_layout.addWidget(employee_title)

        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(2)
        self.employee_table.setHorizontalHeaderLabels(["Сотрудник", "Кол-во заказов"])
        self.employee_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.employee_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.employee_table.setAlternatingRowColors(True)
        employee_layout.addWidget(self.employee_table)

        extra_metrics_layout.addWidget(self.orders_by_employee_frame)

        content_layout.addLayout(extra_metrics_layout)

        # ===== Ряд 4: Продажи по дням (детально) =====
        self.sales_detail_frame = self.create_chart_frame("📊 Продажи по дням")
        self.sales_detail_frame.setMinimumHeight(200)
        content_layout.addWidget(self.sales_detail_frame)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def create_metric_frame(self, title, value):
        """Создаёт фрейм для метрики (упрощённый)"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #333; border-radius: 3px;")
        frame.setMinimumHeight(90)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2d7d3a;")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)

        frame.value_label = value_label
        return frame

    def create_chart_frame(self, title):
        """Создаёт фрейм для графика (упрощённый)"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #333; border-radius: 3px;")
        frame.setMinimumHeight(180)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2d7d3a;")
        layout.addWidget(title_label)

        chart_container = QWidget()
        chart_container.setMinimumHeight(120)
        chart_container.setStyleSheet("background-color: #333;")

        chart_scroll = QScrollArea()
        chart_scroll.setWidgetResizable(True)
        chart_scroll.setStyleSheet("border: none; background-color: transparent;")
        chart_scroll.setWidget(chart_container)

        layout.addWidget(chart_scroll)

        frame.chart_container = chart_container
        frame.chart_scroll = chart_scroll
        return frame

    def on_period_changed(self, period):
        self.load_data()

    def load_data(self):
        """Загружает данные из базы"""
        try:
            days = self.get_days_from_period()
            self.load_orders_statistics(days)
            self.load_payments_by_day(days)
            self.load_orders_by_day(days)
            self.load_payments_by_category(days)
            self.load_orders_by_employee(days)
            self.load_sales_by_day(days)
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def get_days_from_period(self):
        period = self.period_combo.currentText()
        if period == "7 дней":
            return 7
        elif period == "30 дней":
            return 30
        elif period == "90 дней":
            return 90
        else:
            return 365

    def load_orders_statistics(self, days):
        connection = db_crm.get_crm_connection()
        if not connection:
            return
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT AVG(FinalAmount) as avg_check
                FROM Orders
                WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND Status NOT IN ('Закрыто неуспешно', 'Отменено')
            """, (days,))
            result = cursor.fetchone()
            avg_check = result['avg_check'] if result['avg_check'] else 0
            self.avg_check_frame.value_label.setText(f"{avg_check:,.2f} ₽")

            cursor.execute("""
                SELECT AVG(FinalAmount) as avg_sales
                FROM Orders
                WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND IsPaid = 1
            """, (days,))
            result = cursor.fetchone()
            avg_sales = result['avg_sales'] if result['avg_sales'] else 0
            self.avg_sales_frame.value_label.setText(f"{avg_sales:,.2f} ₽")

            cursor.execute("""
                SELECT COUNT(*) as urgent_count
                FROM Orders
                WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND Priority = 'Критичный'
            """, (days,))
            result = cursor.fetchone()
            self.urgent_frame.value_label.setText(str(result['urgent_count']))

            cursor.execute("""
                SELECT COUNT(*) as overdue_count
                FROM Orders
                WHERE EstimatedCompletion < NOW()
                  AND Status NOT IN ('Завершен', 'Готовое', 'Закрыто неуспешно')
            """)
            result = cursor.fetchone()
            self.overdue_frame.value_label.setText(str(result['overdue_count']))
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_orders_by_day(self, days):
        connection = db_crm.get_crm_connection()
        if not connection:
            return
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    DATE(OrderDate) as date,
                    COUNT(*) as count
                FROM Orders
                WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY DATE(OrderDate)
                ORDER BY date
            """, (days,))
            results = cursor.fetchall()

            if results:
                max_count = max(r['count'] for r in results)
                html = '<table style="width: 100%; font-family: monospace; font-size: 12px;">'
                for row in results:
                    date_str = row['date'].strftime('%d.%m') if row['date'] else ''
                    count = row['count']
                    bar_length = int(count / max_count * 200) if max_count > 0 else 0
                    bar = '<div style="background-color: #2d7d3a; height: 18px; width: {}px; border-radius: 2px;"></div>'.format(bar_length)
                    html += f'''
                    <tr>
                        <td style="padding: 3px; color: #b0b0b0; width: 70px;">{date_str}</td>
                        <td style="padding: 3px; width: 210px;">{bar}</td>
                        <td style="padding: 3px; color: #2d7d3a; font-weight: bold;">{count}</td>
                    </tr>
                    '''
                html += '</table>'

                layout = self.orders_chart_frame.chart_container.layout()
                if layout:
                    while layout.count():
                        item = layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                else:
                    layout = QVBoxLayout(self.orders_chart_frame.chart_container)
                    layout.setContentsMargins(0, 0, 0, 0)

                chart_label = QLabel(html)
                chart_label.setTextFormat(Qt.RichText)
                chart_label.setStyleSheet("background-color: #333;")
                chart_label.setWordWrap(True)
                layout.addWidget(chart_label)
        except Exception as e:
            print(f"Ошибка загрузки заказов по дням: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_payments_by_day(self, days):
        connection = db_crm.get_crm_connection()
        if not connection:
            return
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    DATE(PaymentDate) as date,
                    SUM(Amount) as total
                FROM Payments
                WHERE PaymentDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND PaymentType != 'Возврат'
                GROUP BY DATE(PaymentDate)
                ORDER BY date
            """, (days,))
            results = cursor.fetchall()

            if results:
                max_total = max(r['total'] for r in results)
                html = '<table style="width: 100%; font-family: monospace; font-size: 12px;">'
                for row in results:
                    date_str = row['date'].strftime('%d.%m') if row['date'] else ''
                    total = row['total']
                    bar_length = int(total / max_total * 200) if max_total > 0 else 0
                    bar = '<div style="background-color: #e0a800; height: 18px; width: {}px; border-radius: 2px;"></div>'.format(bar_length)
                    html += f'''
                    <tr>
                        <td style="padding: 3px; color: #b0b0b0; width: 70px;">{date_str}</td>
                        <td style="padding: 3px; width: 210px;">{bar}</td>
                        <td style="padding: 3px; color: #e0a800; font-weight: bold;">{total:,.0f} ₽</td>
                    </tr>
                    '''
                html += '</table>'

                layout = self.payments_chart_frame.chart_container.layout()
                if layout:
                    while layout.count():
                        item = layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                else:
                    layout = QVBoxLayout(self.payments_chart_frame.chart_container)
                    layout.setContentsMargins(0, 0, 0, 0)

                chart_label = QLabel(html)
                chart_label.setTextFormat(Qt.RichText)
                chart_label.setStyleSheet("background-color: #333;")
                chart_label.setWordWrap(True)
                layout.addWidget(chart_label)
        except Exception as e:
            print(f"Ошибка загрузки платежей по дням: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_sales_by_day(self, days):
        connection = db_crm.get_crm_connection()
        if not connection:
            return
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    DATE(OrderDate) as date,
                    SUM(FinalAmount) as total_sales
                FROM Orders
                WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND Status NOT IN ('Закрыто неуспешно', 'Отменено')
                GROUP BY DATE(OrderDate)
                ORDER BY date
            """, (days,))
            results = cursor.fetchall()

            if results:
                max_sales = max(r['total_sales'] for r in results)
                html = '<table style="width: 100%; font-family: monospace; font-size: 12px;">'
                for row in results:
                    date_str = row['date'].strftime('%d.%m') if row['date'] else ''
                    total = row['total_sales']
                    bar_length = int(total / max_sales * 200) if max_sales > 0 else 0
                    bar = '<div style="background-color: #2d7d3a; height: 18px; width: {}px; border-radius: 2px;"></div>'.format(bar_length)
                    html += f'''
                    <tr>
                        <td style="padding: 3px; color: #b0b0b0; width: 70px;">{date_str}</td>
                        <td style="padding: 3px; width: 210px;">{bar}</td>
                        <td style="padding: 3px; color: #2d7d3a; font-weight: bold;">{total:,.0f} ₽</td>
                    </tr>
                    '''
                html += '</table>'

                layout = self.sales_detail_frame.chart_container.layout()
                if layout:
                    while layout.count():
                        item = layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                else:
                    layout = QVBoxLayout(self.sales_detail_frame.chart_container)
                    layout.setContentsMargins(0, 0, 0, 0)

                chart_label = QLabel(html)
                chart_label.setTextFormat(Qt.RichText)
                chart_label.setStyleSheet("background-color: #333;")
                chart_label.setWordWrap(True)
                layout.addWidget(chart_label)
        except Exception as e:
            print(f"Ошибка загрузки продаж по дням: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_payments_by_category(self, days):
        connection = db_crm.get_crm_connection()
        if not connection:
            return
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    COALESCE(ar.Category, 'Общая') as category,
                    SUM(p.Amount) as total
                FROM Payments p
                JOIN Orders o ON p.OrderID = o.OrderID
                LEFT JOIN AppealReasons ar ON o.AppealReasonID = ar.ReasonID
                WHERE p.PaymentDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND p.PaymentType != 'Возврат'
                GROUP BY ar.Category
                ORDER BY total DESC
                LIMIT 9
            """, (days,))
            results = cursor.fetchall()

            self.payments_table.setRowCount(len(results))
            total_sum = sum(r['total'] for r in results)

            for i, row in enumerate(results):
                category = row['category'] if row['category'] else 'Общая'
                total = row['total']
                self.payments_table.setItem(i, 0, QTableWidgetItem(category))
                total_item = QTableWidgetItem(f"{total:,.2f} ₽")
                total_item.setTextAlignment(Qt.AlignRight)
                self.payments_table.setItem(i, 1, total_item)

            if results:
                self.payments_table.insertRow(len(results))
                total_item = QTableWidgetItem("ИТОГО:")
                total_item.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
                self.payments_table.setItem(len(results), 0, total_item)
                total_sum_item = QTableWidgetItem(f"{total_sum:,.2f} ₽")
                total_sum_item.setFont(QtGui.QFont("Segoe UI", 10, QtGui.QFont.Bold))
                total_sum_item.setTextAlignment(Qt.AlignRight)
                self.payments_table.setItem(len(results), 1, total_sum_item)

            self.payments_table.resizeRowsToContents()
        except Exception as e:
            print(f"Ошибка загрузки платежей по статьям: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_orders_by_employee(self, days):
        connection = db_crm.get_crm_connection()
        if not connection:
            return
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    CONCAT(e.FirstName, ' ', e.LastName) as employee_name,
                    COUNT(o.OrderID) as order_count
                FROM Orders o
                JOIN ListEmployee e ON o.ExecutorID = e.EmployeeID
                WHERE o.OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND o.ExecutorID IS NOT NULL
                GROUP BY e.EmployeeID
                ORDER BY order_count DESC
                LIMIT 10
            """, (days,))
            results = cursor.fetchall()

            self.employee_table.setRowCount(len(results))
            for i, row in enumerate(results):
                self.employee_table.setItem(i, 0, QTableWidgetItem(row['employee_name']))
                count_item = QTableWidgetItem(str(row['order_count']))
                count_item.setTextAlignment(Qt.AlignRight)
                self.employee_table.setItem(i, 1, count_item)

            self.employee_table.resizeRowsToContents()
        except Exception as e:
            print(f"Ошибка загрузки заказов по сотрудникам: {e}")
        finally:
            cursor.close()
            connection.close()