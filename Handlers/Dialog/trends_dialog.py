# -*- coding: utf-8 -*-
"""
Модуль для отображения трендов и аналитики CRM
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QLinearGradient, QPainter, QPen, QBrush, QFont, QFontMetrics
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QComboBox, QTableWidget, \
    QTableWidgetItem, QHeaderView, QWidget, QScrollArea, QGraphicsDropShadowEffect, QSizePolicy
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm


class TrendsDialog(QDialog):
    """Диалог для отображения трендов и аналитики"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IT-EcoSystem - Тренды и аналитика")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Устанавливаем стиль
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QFrame {
                background-color: #2a2a2a;
                border-radius: 15px;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                padding: 8px 15px;
                min-width: 120px;
                font-size: 13px;
            }
            QComboBox:hover {
                background-color: #4a4a4a;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: white;
                selection-background-color: #4CAF50;
            }
            QTableWidget {
                font-size: 12px;
            }
            QHeaderView::section {
                font-size: 12px;
                font-weight: bold;
            }
        """)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Настройка интерфейса"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ========== ВЕРХНЯЯ ПАНЕЛЬ ==========
        top_frame = QFrame()
        top_frame.setFixedHeight(80)
        top_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 15px;")

        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(20, 15, 20, 15)

        # Заголовок
        title_label = QLabel("📊 Тренды и аналитика")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        # Выбор периода
        period_label = QLabel("Период:")
        period_label.setStyleSheet("color: #b0b0b0; font-size: 13px;")
        top_layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["7 дней", "30 дней", "90 дней", "Год"])
        self.period_combo.setFixedWidth(120)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        top_layout.addWidget(self.period_combo)

        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_data)
        top_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(top_frame)

        # ========== ОСНОВНАЯ ОБЛАСТЬ (ScrollArea) ==========
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
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
            QScrollBar:horizontal {
                background-color: #2d2d2d;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #4CAF50;
                border-radius: 6px;
                min-width: 30px;
            }
        """)

        content_widget = QWidget()
        content_widget.setMinimumWidth(1100)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(5, 5, 5, 5)

        # ========== РЯД 1: КЛЮЧЕВЫЕ МЕТРИКИ ==========
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)

        # Средний чек заказов
        self.avg_check_frame = self.create_metric_frame("💰 Средний чек заказов", "0 ₽")
        metrics_layout.addWidget(self.avg_check_frame)

        # Средний чек продаж
        self.avg_sales_frame = self.create_metric_frame("📈 Средний чек продаж", "0 ₽")
        metrics_layout.addWidget(self.avg_sales_frame)

        # Срочные заказы
        self.urgent_frame = self.create_metric_frame("⚠️ Срочные заказы", "0")
        metrics_layout.addWidget(self.urgent_frame)

        # Просроченные заказы
        self.overdue_frame = self.create_metric_frame("⏰ Просроченные заказы", "0")
        metrics_layout.addWidget(self.overdue_frame)

        content_layout.addLayout(metrics_layout)

        # ========== РЯД 2: ГРАФИКИ ==========
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # График заказов по дням
        self.orders_chart_frame = self.create_chart_frame("📅 Заказы по дням")
        charts_layout.addWidget(self.orders_chart_frame)

        # График платежей по дням
        self.payments_chart_frame = self.create_chart_frame("💵 Платежи по дням")
        charts_layout.addWidget(self.payments_chart_frame)

        content_layout.addLayout(charts_layout)

        # ========== РЯД 3: ДОПОЛНИТЕЛЬНЫЕ МЕТРИКИ ==========
        extra_metrics_layout = QHBoxLayout()
        extra_metrics_layout.setSpacing(20)

        # Платежи по статьям
        self.payments_by_category_frame = QFrame()
        self.payments_by_category_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 15px;")
        self.payments_by_category_frame.setMinimumHeight(300)
        self.payments_by_category_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        payments_layout = QVBoxLayout(self.payments_by_category_frame)
        payments_layout.setContentsMargins(15, 15, 15, 15)

        payments_title_layout = QHBoxLayout()
        payments_title = QLabel("💰 Платежи по статьям - Топ 9")
        payments_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        payments_title_layout.addWidget(payments_title)
        payments_title_layout.addStretch()

        # Кнопка "Подробнее"
        more_btn = QPushButton("Подробнее >")
        more_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4CAF50;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #45a049;
                text-decoration: underline;
            }
        """)
        payments_title_layout.addWidget(more_btn)

        payments_layout.addLayout(payments_title_layout)

        self.payments_table = QTableWidget()
        self.payments_table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                border: none;
                color: white;
                gridline-color: #3a3a3a;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        self.payments_table.setColumnCount(2)
        self.payments_table.setHorizontalHeaderLabels(["Статья", "Сумма"])
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.payments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.payments_table.setAlternatingRowColors(True)
        payments_layout.addWidget(self.payments_table)

        extra_metrics_layout.addWidget(self.payments_by_category_frame)

        # Заказы по сотрудникам
        self.orders_by_employee_frame = QFrame()
        self.orders_by_employee_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 15px;")
        self.orders_by_employee_frame.setMinimumHeight(300)
        self.orders_by_employee_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        employee_layout = QVBoxLayout(self.orders_by_employee_frame)
        employee_layout.setContentsMargins(15, 15, 15, 15)

        employee_title = QLabel("👥 Заказы по сотрудникам")
        employee_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        employee_layout.addWidget(employee_title)

        self.employee_table = QTableWidget()
        self.employee_table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                border: none;
                color: white;
                gridline-color: #3a3a3a;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        self.employee_table.setColumnCount(2)
        self.employee_table.setHorizontalHeaderLabels(["Сотрудник", "Кол-во заказов"])
        self.employee_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.employee_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.employee_table.setAlternatingRowColors(True)
        employee_layout.addWidget(self.employee_table)

        extra_metrics_layout.addWidget(self.orders_by_employee_frame)

        content_layout.addLayout(extra_metrics_layout)

        # ========== РЯД 4: ПРОДАЖИ ПО ДНЯМ (ДЕТАЛЬНО) ==========
        self.sales_detail_frame = self.create_chart_frame("📊 Продажи по дням")
        self.sales_detail_frame.setMinimumHeight(250)
        content_layout.addWidget(self.sales_detail_frame)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def create_metric_frame(self, title, value):
        """Создает фрейм для отображения метрики"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #2a2a2a; border-radius: 15px;")
        frame.setMinimumHeight(120)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #b0b0b0; font-size: 13px; font-weight: 500;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #4CAF50;")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)

        # Сохраняем ссылку на лейбл значения для обновления
        frame.value_label = value_label
        return frame

    def create_chart_frame(self, title):
        """Создает фрейм для графика"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #2a2a2a; border-radius: 15px;")
        frame.setMinimumHeight(220)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(title_label)

        # Контейнер для графика
        chart_container = QWidget()
        chart_container.setMinimumHeight(150)
        chart_container.setStyleSheet("background-color: #2a2a2a;")

        # Добавляем скролл для графика, если текста много
        chart_scroll = QScrollArea()
        chart_scroll.setWidgetResizable(True)
        chart_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 4px;
            }
        """)
        chart_scroll.setWidget(chart_container)

        layout.addWidget(chart_scroll)

        frame.chart_container = chart_container
        frame.chart_scroll = chart_scroll
        return frame

    def on_period_changed(self, period):
        """Обработчик изменения периода"""
        self.load_data()

    def load_data(self):
        """Загружает данные из базы"""
        try:
            # Получаем количество дней из выбранного периода
            days = self.get_days_from_period()

            # Загружаем статистику заказов
            self.load_orders_statistics(days)

            # Загружаем платежи по дням
            self.load_payments_by_day(days)

            # Загружаем заказы по дням
            self.load_orders_by_day(days)

            # Загружаем платежи по статьям
            self.load_payments_by_category(days)

            # Загружаем заказы по сотрудникам
            self.load_orders_by_employee(days)

            # Загружаем продажи по дням
            self.load_sales_by_day(days)

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def get_days_from_period(self):
        """Возвращает количество дней из выбранного периода"""
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
        """Загружает статистику заказов"""
        connection = db_crm.get_crm_connection()
        if not connection:
            return

        cursor = connection.cursor(dictionary=True)

        try:
            # Средний чек заказов
            cursor.execute("""
                SELECT AVG(FinalAmount) as avg_check
                FROM Orders
                WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND Status NOT IN ('Закрыто неуспешно', 'Отменено')
            """, (days,))
            result = cursor.fetchone()
            avg_check = result['avg_check'] if result['avg_check'] else 0
            self.avg_check_frame.value_label.setText(f"{avg_check:,.2f} ₽")

            # Средний чек продаж (только оплаченные)
            cursor.execute("""
                SELECT AVG(FinalAmount) as avg_sales
                FROM Orders
                WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND IsPaid = 1
            """, (days,))
            result = cursor.fetchone()
            avg_sales = result['avg_sales'] if result['avg_sales'] else 0
            self.avg_sales_frame.value_label.setText(f"{avg_sales:,.2f} ₽")

            # Срочные заказы
            cursor.execute("""
                SELECT COUNT(*) as urgent_count
                FROM Orders
                WHERE OrderDate >= DATE_SUB(NOW(), INTERVAL %s DAY)
                  AND Priority = 'Критичный'
            """, (days,))
            result = cursor.fetchone()
            self.urgent_frame.value_label.setText(str(result['urgent_count']))

            # Просроченные заказы
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
        """Загружает заказы по дням для графика"""
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

            # Создаем HTML-таблицу для лучшего отображения
            if results:
                max_count = max(r['count'] for r in results)
                html = '<table style="width: 100%; font-family: monospace; font-size: 12px;">'
                for row in results:
                    date_str = row['date'].strftime('%d.%m') if row['date'] else ''
                    count = row['count']
                    bar_length = int(count / max_count * 200) if max_count > 0 else 0
                    bar = '<div style="background-color: #4CAF50; height: 20px; width: {}px; border-radius: 3px;"></div>'.format(
                        bar_length)
                    html += f'''
                    <tr>
                        <td style="padding: 4px; color: #b0b0b0; width: 80px;">{date_str}</td>
                        <td style="padding: 4px; width: 220px;">{bar}</td>
                        <td style="padding: 4px; color: #4CAF50; font-weight: bold;">{count}</td>
                    </tr>
                    '''
                html += '</table>'

                if hasattr(self.orders_chart_frame, 'chart_container'):
                    # Очищаем контейнер
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
                    chart_label.setStyleSheet("""
                        QLabel {
                            background-color: #2a2a2a;
                        }
                    """)
                    chart_label.setWordWrap(True)
                    layout.addWidget(chart_label)

        except Exception as e:
            print(f"Ошибка загрузки заказов по дням: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_payments_by_day(self, days):
        """Загружает платежи по дням для графика"""
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
                    bar = '<div style="background-color: #FF9800; height: 20px; width: {}px; border-radius: 3px;"></div>'.format(
                        bar_length)
                    html += f'''
                    <tr>
                        <td style="padding: 4px; color: #b0b0b0; width: 80px;">{date_str}</td>
                        <td style="padding: 4px; width: 220px;">{bar}</td>
                        <td style="padding: 4px; color: #FF9800; font-weight: bold;">{total:,.0f} ₽</td>
                    </tr>
                    '''
                html += '</table>'

                if hasattr(self.payments_chart_frame, 'chart_container'):
                    layout = self.payments_chart_frame.chart_container.layout()
                    if not layout:
                        layout = QVBoxLayout(self.payments_chart_frame.chart_container)
                        layout.setContentsMargins(0, 0, 0, 0)
                    else:
                        while layout.count():
                            item = layout.takeAt(0)
                            if item.widget():
                                item.widget().deleteLater()

                    chart_label = QLabel(html)
                    chart_label.setTextFormat(Qt.RichText)
                    chart_label.setStyleSheet("""
                        QLabel {
                            background-color: #2a2a2a;
                        }
                    """)
                    chart_label.setWordWrap(True)
                    layout.addWidget(chart_label)

        except Exception as e:
            print(f"Ошибка загрузки платежей по дням: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_sales_by_day(self, days):
        """Загружает продажи по дням (детальный график)"""
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
                    bar = '<div style="background-color: #4CAF50; height: 20px; width: {}px; border-radius: 3px;"></div>'.format(
                        bar_length)
                    html += f'''
                    <tr>
                        <td style="padding: 4px; color: #b0b0b0; width: 80px;">{date_str}</td>
                        <td style="padding: 4px; width: 220px;">{bar}</td>
                        <td style="padding: 4px; color: #4CAF50; font-weight: bold;">{total:,.0f} ₽</td>
                    </tr>
                    '''
                html += '</table>'

                if hasattr(self.sales_detail_frame, 'chart_container'):
                    layout = self.sales_detail_frame.chart_container.layout()
                    if not layout:
                        layout = QVBoxLayout(self.sales_detail_frame.chart_container)
                        layout.setContentsMargins(0, 0, 0, 0)
                    else:
                        while layout.count():
                            item = layout.takeAt(0)
                            if item.widget():
                                item.widget().deleteLater()

                    chart_label = QLabel(html)
                    chart_label.setTextFormat(Qt.RichText)
                    chart_label.setStyleSheet("""
                        QLabel {
                            background-color: #2a2a2a;
                        }
                    """)
                    chart_label.setWordWrap(True)
                    layout.addWidget(chart_label)

        except Exception as e:
            print(f"Ошибка загрузки продаж по дням: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_payments_by_category(self, days):
        """Загружает платежи по статьям"""
        connection = db_crm.get_crm_connection()
        if not connection:
            return

        cursor = connection.cursor(dictionary=True)

        try:
            # Получаем платежи сгруппированные по статьям из AppealReasons
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

                category_item = QTableWidgetItem(category)
                category_item.setToolTip(category)
                self.payments_table.setItem(i, 0, category_item)

                total_item = QTableWidgetItem(f"{total:,.2f} ₽")
                total_item.setTextAlignment(Qt.AlignRight)
                total_item.setToolTip(f"{total:,.2f} ₽")
                self.payments_table.setItem(i, 1, total_item)

            # Добавляем итоговую строку
            if results:
                self.payments_table.insertRow(len(results))
                total_item = QTableWidgetItem("ИТОГО:")
                total_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.payments_table.setItem(len(results), 0, total_item)

                total_sum_item = QTableWidgetItem(f"{total_sum:,.2f} ₽")
                total_sum_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                total_sum_item.setTextAlignment(Qt.AlignRight)
                self.payments_table.setItem(len(results), 1, total_sum_item)

            # Настраиваем высоту строк
            self.payments_table.resizeRowsToContents()

        except Exception as e:
            print(f"Ошибка загрузки платежей по статьям: {e}")
        finally:
            cursor.close()
            connection.close()

    def load_orders_by_employee(self, days):
        """Загружает заказы по сотрудникам"""
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
                employee_name = row['employee_name']
                order_count = row['order_count']

                name_item = QTableWidgetItem(employee_name)
                name_item.setToolTip(employee_name)
                self.employee_table.setItem(i, 0, name_item)

                count_item = QTableWidgetItem(str(order_count))
                count_item.setTextAlignment(Qt.AlignRight)
                count_item.setToolTip(str(order_count))
                self.employee_table.setItem(i, 1, count_item)

            # Настраиваем высоту строк
            self.employee_table.resizeRowsToContents()

        except Exception as e:
            print(f"Ошибка загрузки заказов по сотрудникам: {e}")
        finally:
            cursor.close()
            connection.close()