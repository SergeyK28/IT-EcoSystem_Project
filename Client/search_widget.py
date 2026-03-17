# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget


class SearchResultItem(QFrame):
    """Элемент результата поиска"""

    clicked = pyqtSignal(dict)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(70)
        self.setMaximumHeight(70)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            SearchResultItem {
                background-color: #2d2d2d;
                border-radius: 8px;
                margin: 2px 5px;
            }
            SearchResultItem:hover {
                background-color: #3a3a3a;
                border: 1px solid #4CAF50;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Иконка в зависимости от типа
        icon_label = QLabel()
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignCenter)

        if self.data.get('type') == 'service':
            icon_label.setText("🔧")
            icon_label.setStyleSheet("font-size: 20px; color: #4CAF50;")
        elif self.data.get('type') == 'part':
            icon_label.setText("⚙️")
            icon_label.setStyleSheet("font-size: 20px; color: #FFA500;")
        else:
            icon_label.setText("📁")
            icon_label.setStyleSheet("font-size: 20px; color: #888;")

        layout.addWidget(icon_label)

        # Информация
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        # Название
        name_label = QLabel(self.data.get('name', ''))
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: 600;
            }
        """)
        info_layout.addWidget(name_label)

        # Детали
        details_layout = QHBoxLayout()
        details_layout.setSpacing(10)

        if self.data.get('type') == 'service':
            price_label = QLabel(f"💰 {self.data.get('price', 0)} ₽")
            price_label.setStyleSheet("color: #4CAF50; font-size: 12px;")

            duration_label = QLabel(f"⏱️ {self.data.get('duration', 60)} мин")
            duration_label.setStyleSheet("color: #888; font-size: 12px;")

            details_layout.addWidget(price_label)
            details_layout.addWidget(duration_label)

        elif self.data.get('type') == 'part':
            price_label = QLabel(f"💰 {self.data.get('price', 0)} ₽")
            price_label.setStyleSheet("color: #4CAF50; font-size: 12px;")

            stock_label = QLabel(f"📦 {self.data.get('stock', 0)} шт.")
            stock_label.setStyleSheet("color: #888; font-size: 12px;")

            details_layout.addWidget(price_label)
            details_layout.addWidget(stock_label)

        else:
            category_label = QLabel(f"📁 Категория")
            category_label.setStyleSheet("color: #888; font-size: 12px;")
            details_layout.addWidget(category_label)

        info_layout.addLayout(details_layout)
        layout.addLayout(info_layout, 1)

        # Кнопка действия
        action_btn = QPushButton("→")
        action_btn.setFixedSize(30, 30)
        action_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(action_btn)

        # Обработчики
        action_btn.clicked.connect(lambda: self.clicked.emit(self.data))

    def mousePressEvent(self, event):
        self.clicked.emit(self.data)
        super().mousePressEvent(event)


class SearchResultsWidget(QFrame):
    """Виджет с результатами поиска"""

    result_selected = pyqtSignal(dict)
    show_results_signal = pyqtSignal(dict)  # Сигнал для показа результатов из другого потока

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.hide()
        # Подключаем сигнал
        self.show_results_signal.connect(self.show_results)

    def setup_ui(self):
        self.setStyleSheet("""
            SearchResultsWidget {
                background-color: #262626;
                border-radius: 10px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Тень
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Заголовок
        self.title_label = QLabel("Результаты поиска")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(self.title_label)

        # Контейнер для результатов
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(400)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 4px;
                min-height: 30px;
            }
        """)

        self.results_container = QWidget()
        self.results_container.setStyleSheet("background-color: transparent;")
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(2)
        self.results_layout.addStretch()

        self.scroll_area.setWidget(self.results_container)
        layout.addWidget(self.scroll_area)

        # Сообщение о пустых результатах
        self.empty_label = QLabel("🔍 Ничего не найдено")
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 14px;
                padding: 30px;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.empty_label.hide()
        layout.addWidget(self.empty_label)

    def show_results(self, results: dict):
        """Показывает результаты поиска"""
        print(f"SearchResultsWidget.show_results вызван с результатами: {results}")

        # Очищаем предыдущие результаты
        self.clear_results()

        total_count = len(results.get('services', [])) + len(results.get('parts', [])) + len(
            results.get('categories', []))

        print(f"Всего элементов для отображения: {total_count}")

        if total_count == 0:
            self.title_label.hide()
            self.scroll_area.hide()
            self.empty_label.show()
            self.setFixedHeight(150)
            print("Показано сообщение 'Ничего не найдено'")
            return

        self.title_label.show()
        self.scroll_area.show()
        self.empty_label.hide()

        # Добавляем категории
        if results.get('categories'):
            self.add_section_header("📁 Категории")
            for category in results['categories']:
                item = SearchResultItem(category)
                item.clicked.connect(self.result_selected.emit)
                self.results_layout.insertWidget(self.results_layout.count() - 1, item)

        # Добавляем услуги
        if results.get('services'):
            self.add_section_header("🔧 Услуги")
            for service in results['services']:
                item = SearchResultItem(service)
                item.clicked.connect(self.result_selected.emit)
                self.results_layout.insertWidget(self.results_layout.count() - 1, item)

        # Добавляем товары
        if results.get('parts'):
            self.add_section_header("⚙️ Запчасти")
            for part in results['parts']:
                item = SearchResultItem(part)
                item.clicked.connect(self.result_selected.emit)
                self.results_layout.insertWidget(self.results_layout.count() - 1, item)

        # Вычисляем высоту
        item_height = 74
        headers = sum(
            1 for section in [results.get('categories'), results.get('services'), results.get('parts')] if section)

        height = min(400, total_count * item_height + headers * 30 + 60)
        self.setFixedHeight(height)
        self.show()
        self.raise_()  # Поднимаем на передний план
        print(f"Виджет показан, высота: {height}")

    def add_section_header(self, title):
        """Добавляет заголовок секции"""
        header = QLabel(title)
        header.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                font-weight: 600;
                padding: 5px 5px 0 5px;
                background: none;
            }
        """)
        self.results_layout.insertWidget(self.results_layout.count() - 1, header)

    def clear_results(self):
        """Очищает результаты"""
        while self.results_layout.count() > 1:
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_loading(self):
        """Показывает индикатор загрузки"""
        self.clear_results()
        loading_label = QLabel("⏳ Поиск...")
        loading_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 14px;
                padding: 30px;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.results_layout.insertWidget(0, loading_label)
        self.title_label.hide()
        self.empty_label.hide()
        self.scroll_area.show()
        self.setFixedHeight(150)
        self.show()

    def focusOutEvent(self, event):
        """Обработчик потери фокуса"""
        # Не скрываем виджет при потере фокуса
        # Скрытие будет обрабатываться через eventFilter в главном окне
        pass