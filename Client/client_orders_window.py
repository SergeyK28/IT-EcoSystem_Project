# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette, QPixmap, QPainter, QPen, QPainterPath, \
    QMouseEvent
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLabel, QPushButton, QFrame, \
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QSpacerItem, QSizePolicy, QTableWidget, \
    QTableWidgetItem, QHeaderView, QAbstractItemView, QApplication

from datetime import datetime
from Server import db_crm
from session_manager import session


class OrderStatusBadge(QLabel):
    """Виджет для отображения статуса заказа с цветовой индикацией"""

    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.status = status
        self.setup_ui()

    def setup_ui(self):
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(120)
        self.setMaximumHeight(30)

        # Определяем цвет и текст в зависимости от статуса
        status_colors = {
            'Новая': ('#FFA500', '🆕 Новая'),
            'Активная': ('#4CAF50', '✅ Активная'),
            'Срочное': ('#FF4444', '⚠️ Срочное'),
            'Ждут запчасти': ('#FF8C00', '📦 Ждут запчасти'),
            'В работе': ('#2196F3', '🔧 В работе'),
            'Готовое': ('#4CAF50', '✨ Готово'),
            'Закрыто неуспешно': ('#9E9E9E', '❌ Закрыто'),
            'Завершен': ('#4CAF50', '✅ Завершен'),
            'Клиент несет заказ': ('#FF9800', '🚶 Клиент несет заказ')
        }

        color, display_text = status_colors.get(self.status, ('#808080', self.status))

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 15px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        self.setText(display_text)


class OrderDetailDialog(QDialog):
    """Диалог детального просмотра заказа"""

    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.dragging = False
        self.drag_position = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(600, 700)
        self.setup_ui()

    def setup_ui(self):
        # Главный контейнер
        main_container = QFrame(self)
        main_container.setObjectName("main_container")
        main_container.setGeometry(0, 0, self.width(), self.height())
        main_container.setStyleSheet("""
            QFrame#main_container {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 25px;
                border: 2px solid #3a3a3a;
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
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # ===== ВЕРХНЯЯ ПАНЕЛЬ =====
        header_layout = QHBoxLayout()

        # Кнопка закрытия
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        # Заголовок
        title_label = QLabel(f"📋 Заказ #{self.order_data.get('OrderNumber', '')}")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: 600;
                margin-left: 10px;
            }
        """)

        header_layout.addWidget(self.btn_close)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Создаем скролл-область для контента
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #45a049;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #2d2d2d;
                height: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background-color: #4CAF50;
                border-radius: 5px;
                min-width: 30px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)

        # ===== СТАТУС =====
        status_layout = QHBoxLayout()

        status_label = QLabel("Статус:")
        status_label.setStyleSheet("color: #808080; font-size: 14px;")

        self.status_badge = OrderStatusBadge(self.order_data.get('Status', 'Новая'))

        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_badge)
        status_layout.addStretch()

        content_layout.addLayout(status_layout)

        # ===== ИНФОРМАЦИЯ О ЗАКАЗЕ =====
        info_frame = self.create_info_frame()
        content_layout.addWidget(info_frame)

        # ===== ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ =====
        device_frame = self.create_device_frame()
        content_layout.addWidget(device_frame)

        # ===== ОПИСАНИЕ ПРОБЛЕМЫ =====
        problem_frame = self.create_problem_frame()
        content_layout.addWidget(problem_frame)

        # ===== ДИАГНОСТИКА (если есть) =====
        diagnosis = self.order_data.get('Diagnosis')
        if diagnosis:
            diagnosis_frame = self.create_diagnosis_frame(diagnosis)
            content_layout.addWidget(diagnosis_frame)

        # ===== ФИНАНСЫ =====
        finance_frame = self.create_finance_frame()
        content_layout.addWidget(finance_frame)

        # Добавляем растяжку в конце
        content_layout.addStretch()

        scroll_content.setLayout(content_layout)
        scroll_area.setWidget(scroll_content)

        layout.addWidget(scroll_area)

        # Кнопка закрытия внизу
        self.btn_ok = QPushButton("Закрыть")
        self.btn_ok.setMinimumHeight(45)
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
        """)
        self.btn_ok.clicked.connect(self.close)
        layout.addWidget(self.btn_ok)

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        main_container = self.findChild(QFrame, "main_container")
        if main_container:
            main_container.setGeometry(0, 0, self.width(), self.height())

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши для перемещения окна"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Обработка движения мыши для перемещения окна"""
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обработка отпускания мыши"""
        self.dragging = False
        event.accept()

    def create_info_frame(self):
        """Создает фрейм с информацией о заказе"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(76, 175, 80, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(76, 175, 80, 0.3);
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        # Дата заказа
        order_date = self.order_data.get('OrderDate', '')
        if isinstance(order_date, datetime):
            order_date = order_date.strftime('%d.%m.%Y %H:%M')
        self.add_info_row(layout, "📅 Дата заказа:", order_date)

        # Тип заказа
        order_type = self.order_data.get('OrderType', 'Платный')
        self.add_info_row(layout, "💰 Тип заказа:", order_type)

        # Приоритет
        priority = self.order_data.get('Priority', 'Средний')
        priority_colors = {
            'Низкий': '#808080',
            'Средний': '#FFA500',
            'Высокий': '#FF4444',
            'Критичный': '#FF0000'
        }
        priority_color = priority_colors.get(priority, '#808080')
        priority_html = f'<span style="color: {priority_color}; font-weight: bold;">{priority}</span>'
        self.add_info_row(layout, "⚡ Приоритет:", priority_html, is_html=True)

        return frame

    def create_device_frame(self):
        """Создает фрейм с информацией об устройстве"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #3a3a3a;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("📱 Устройство")
        title.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        layout.addWidget(title)

        # Тип устройства
        device_type = self.order_data.get('DeviceType', 'Не указано')
        self.add_info_row(layout, "Тип:", device_type)

        # Бренд
        device_brand = self.order_data.get('DeviceBrand', 'Не указано')
        self.add_info_row(layout, "Бренд:", device_brand)

        # Модель
        device_model = self.order_data.get('DeviceModel', 'Не указано')
        self.add_info_row(layout, "Модель:", device_model)

        # IMEI/SN
        device_imei = self.order_data.get('DeviceIMEI_SN', 'Не указан')
        self.add_info_row(layout, "IMEI/SN:", device_imei)

        return frame

    def create_problem_frame(self):
        """Создает фрейм с описанием проблемы"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #3a3a3a;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("❓ Описание проблемы")
        title.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        layout.addWidget(title)

        problem_text = QLabel(self.order_data.get('ProblemDescription', 'Описание отсутствует'))
        problem_text.setWordWrap(True)
        problem_text.setStyleSheet("color: white; font-size: 13px; line-height: 1.5;")

        layout.addWidget(problem_text)

        return frame

    def create_diagnosis_frame(self, diagnosis):
        """Создает фрейм с диагностикой"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #3a3a3a;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("🔍 Диагностика")
        title.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        layout.addWidget(title)

        diagnosis_text = QLabel(diagnosis)
        diagnosis_text.setWordWrap(True)
        diagnosis_text.setStyleSheet("color: white; font-size: 13px; line-height: 1.5;")

        layout.addWidget(diagnosis_text)

        return frame

    def create_finance_frame(self):
        """Создает фрейм с финансовой информацией"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #3a3a3a;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)

        title = QLabel("💰 Финансовая информация")
        title.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        layout.addWidget(title)

        # Общая сумма
        total_amount = float(self.order_data.get('TotalAmount', 0))
        self.add_info_row(layout, "Сумма заказа:", f"{total_amount:,.0f} ₽".replace(',', ' '))

        # Предоплата
        prepayment = float(self.order_data.get('Prepayment', 0))
        if prepayment > 0:
            self.add_info_row(layout, "Предоплата:", f"{prepayment:,.0f} ₽".replace(',', ' '))

        # Скидка
        discount = float(self.order_data.get('Discount', 0))
        if discount > 0:
            self.add_info_row(layout, "Скидка:", f"{discount}%")

        # Итоговая сумма
        final_amount = float(self.order_data.get('FinalAmount', 0))
        final_label = QLabel(f"{final_amount:,.0f} ₽".replace(',', ' '))
        final_label.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold;")

        final_row = QHBoxLayout()
        final_row.addWidget(QLabel("К оплате:"))
        final_row.addStretch()
        final_row.addWidget(final_label)

        layout.addLayout(final_row)

        # Статус оплаты
        is_paid = self.order_data.get('IsPaid', False)
        payment_status = "✅ Оплачено" if is_paid else "⏳ Ожидает оплаты"
        payment_color = "#4CAF50" if is_paid else "#FFA500"
        payment_label = QLabel(payment_status)
        payment_label.setStyleSheet(f"color: {payment_color}; font-weight: bold;")
        payment_row = QHBoxLayout()
        payment_row.addWidget(QLabel("Статус оплаты:"))
        payment_row.addStretch()
        payment_row.addWidget(payment_label)

        layout.addLayout(payment_row)

        return frame

    def add_info_row(self, parent_layout, label_text, value_text, is_html=False):
        """Добавляет строку с информацией"""
        row_layout = QHBoxLayout()

        label = QLabel(label_text)
        label.setStyleSheet("color: #808080; font-size: 13px; min-width: 100px;")

        if is_html:
            value = QLabel()
            value.setTextFormat(Qt.RichText)
            value.setText(value_text)
        else:
            value = QLabel(value_text)
            value.setStyleSheet("color: white; font-size: 13px;")

        value.setWordWrap(True)

        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(value)

        parent_layout.addLayout(row_layout)


class ClientOrdersWindow(QDialog):
    """Окно со списком заказов клиента"""

    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.orders = []
        self.dragging = False
        self.drag_position = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(900, 600)
        self.resize(900, 600)
        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        # Главный контейнер
        main_container = QFrame(self)
        main_container.setObjectName("main_container")
        main_container.setGeometry(0, 0, self.width(), self.height())
        main_container.setStyleSheet("""
            QFrame#main_container {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 25px;
                border: 2px solid #3a3a3a;
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
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # ===== ВЕРХНЯЯ ПАНЕЛЬ =====
        header_layout = QHBoxLayout()

        # Кнопка закрытия
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        # Заголовок
        title_label = QLabel("📋 Мои заказы")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: 600;
                margin-left: 10px;
            }
        """)

        # Кнопка обновления
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(35, 35)
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_orders)

        header_layout.addWidget(self.btn_close)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)

        layout.addLayout(header_layout)

        # ===== ИНФОРМАЦИОННЫЙ БЛОК =====
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(76, 175, 80, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(76, 175, 80, 0.3);
                padding: 15px;
            }
        """)

        info_layout = QHBoxLayout(info_frame)

        info_icon = QLabel("ℹ️")
        info_icon.setStyleSheet("font-size: 20px; background: none;")

        info_text = QLabel("Здесь отображаются все ваши заказы. Нажмите на заказ для просмотра детальной информации.")
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #b0b0b0; font-size: 13px; background: none;")

        info_layout.addWidget(info_icon)
        info_layout.addWidget(info_text, 1)

        layout.addWidget(info_frame)

        # ===== ТАБЛИЦА ЗАКАЗОВ =====
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "№ Заказа", "Дата", "Устройство", "Статус", "Сумма", "Действия"
        ])

        # Настройка таблицы
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                gridline-color: #3a3a3a;
                border-radius: 10px;
                border: 1px solid #3a3a3a;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: rgba(76, 175, 80, 0.3);
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #45a049;
            }
            QTableWidget::item:alternate {
                background-color: #333333;
            }
        """)

        # Настройка растяжения колонок
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        main_container = self.findChild(QFrame, "main_container")
        if main_container:
            main_container.setGeometry(0, 0, self.width(), self.height())

    def mousePressEvent(self, event: QMouseEvent):
        """Обработка нажатия мыши для перемещения окна"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Обработка движения мыши для перемещения окна"""
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Обработка отпускания мыши"""
        self.dragging = False
        event.accept()

    def load_orders(self):
        """Загружает заказы клиента из БД"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
                return

            cursor = connection.cursor(dictionary=True)

            # Получаем заказы клиента
            cursor.execute("""
                SELECT 
                    o.OrderID,
                    o.OrderNumber,
                    o.OrderDate,
                    o.Status,
                    o.OrderType,
                    o.DeviceType,
                    o.DeviceBrand,
                    o.DeviceModel,
                    o.ProblemDescription,
                    o.TotalAmount,
                    o.FinalAmount,
                    o.IsPaid,
                    o.Prepayment,
                    o.Diagnosis,
                    o.CompletionDate,
                    o.EstimatedCompletion
                FROM Orders o
                WHERE o.ClientID = %s
                ORDER BY o.OrderDate DESC
            """, (self.user_id,))

            self.orders = cursor.fetchall()
            cursor.close()
            connection.close()

            self.display_orders()

        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заказы: {e}")

    def display_orders(self):
        """Отображает заказы в таблице"""
        self.table.setRowCount(len(self.orders))

        for row, order in enumerate(self.orders):
            # Номер заказа
            order_num = order.get('OrderNumber', f"#{order.get('OrderID')}")
            num_item = QTableWidgetItem(order_num)
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, num_item)

            # Дата заказа
            order_date = order.get('OrderDate')
            if isinstance(order_date, datetime):
                date_str = order_date.strftime('%d.%m.%Y')
            else:
                date_str = str(order_date) if order_date else '—'
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, date_item)

            # Устройство
            device_parts = []
            if order.get('DeviceBrand'):
                device_parts.append(order['DeviceBrand'])
            if order.get('DeviceModel'):
                device_parts.append(order['DeviceModel'])
            device_str = ' '.join(device_parts) if device_parts else 'Не указано'
            device_item = QTableWidgetItem(device_str)
            self.table.setItem(row, 2, device_item)

            # Статус
            status = order.get('Status', 'Новая')
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(5, 5, 5, 5)
            status_layout.setAlignment(Qt.AlignCenter)

            status_badge = OrderStatusBadge(status)
            status_layout.addWidget(status_badge)

            self.table.setCellWidget(row, 3, status_widget)

            # Сумма
            amount = float(order.get('FinalAmount', 0))
            amount_str = f"{amount:,.0f} ₽".replace(',', ' ')
            amount_item = QTableWidgetItem(amount_str)
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            if order.get('IsPaid'):
                amount_item.setForeground(QColor('#4CAF50'))
            else:
                amount_item.setForeground(QColor('#FFA500'))

            self.table.setItem(row, 4, amount_item)

            # Кнопка просмотра
            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(35, 35)
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 17px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)

            btn_view.clicked.connect(lambda checked, o=order: self.show_order_details(o))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(btn_view)

            self.table.setCellWidget(row, 5, btn_widget)

        # Подгоняем высоту строк
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 50)

    def show_order_details(self, order_data):
        """Показывает детальную информацию о заказе"""
        full_order_data = db_crm.get_order_for_edit_form(order_data['OrderID'])
        if full_order_data:
            dialog = OrderDetailDialog(full_order_data, self)
        else:
            dialog = OrderDetailDialog(order_data, self)

        dialog.setModal(True)
        dialog.show()


# Для тестирования
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # Применяем темную палитру
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    app.setPalette(palette)

    dialog = ClientOrdersWindow(1)
    dialog.show()

    sys.exit(app.exec_())