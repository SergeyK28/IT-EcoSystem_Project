# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QWidget, \
    QTabWidget, QMessageBox


class SearchResultsDialog(QDialog):
    """Диалоговое окно с результатами поиска"""

    result_selected = pyqtSignal(object)  # Сигнал при выборе результата

    def __init__(self, results, search_text, parent=None):
        super().__init__(parent)
        self.results = results
        self.search_text = search_text
        self.setWindowTitle(f"Результаты поиска: {search_text}")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        title_layout = QHBoxLayout(title_frame)

        title_label = QLabel(f"📊 Результаты поиска: \"{self.search_text}\"")
        title_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        # Счетчик результатов
        total_results = (len(self.results.get('services', [])) +
                         len(self.results.get('parts', [])) +
                         len(self.results.get('categories', [])))

        count_label = QLabel(f"Найдено: {total_results}")
        count_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
            }
        """)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(count_label)

        main_layout.addWidget(title_frame)

        # Табы с результатами
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                background-color: #2a2a2a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #b0b0b0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #4a4a4a;
            }
        """)

        # Вкладка с услугами
        services = self.results.get('services', [])
        services_widget = self.create_results_tab(services, 'service')
        self.tab_widget.addTab(services_widget, f"🔧 Услуги ({len(services)})")

        # Вкладка с товарами
        parts = self.results.get('parts', [])
        parts_widget = self.create_results_tab(parts, 'part')
        self.tab_widget.addTab(parts_widget, f"📦 Товары ({len(parts)})")

        # Вкладка с категориями
        categories = self.results.get('categories', [])
        categories_widget = self.create_categories_tab(categories)
        self.tab_widget.addTab(categories_widget, f"📁 Категории ({len(categories)})")

        main_layout.addWidget(self.tab_widget)

        # Кнопка закрытия
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        button_layout = QHBoxLayout(button_frame)
        button_layout.addStretch()

        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #5a5a5a;
            }
        """)
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(close_btn)
        main_layout.addWidget(button_frame)

    def create_results_tab(self, items, item_type):
        """Создает вкладку с результатами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        if not items:
            # Нет результатов
            empty_label = QLabel("😕 Ничего не найдено")
            empty_label.setStyleSheet("""
                QLabel {
                    color: #808080;
                    font-size: 16px;
                    padding: 50px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            layout.addWidget(empty_label)
            return widget

        # Создаем скролл для результатов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
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
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)

        for item in items:
            item_widget = self.create_result_item(item, item_type)
            scroll_layout.addWidget(item_widget)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        return widget

    def create_categories_tab(self, categories):
        """Создает вкладку с категориями"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        if not categories:
            empty_label = QLabel("😕 Категории не найдены")
            empty_label.setStyleSheet("""
                QLabel {
                    color: #808080;
                    font-size: 16px;
                    padding: 50px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            layout.addWidget(empty_label)
            return widget

        # Сетка для категорий
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(15)

        for i, category in enumerate(categories):
            row, col = divmod(i, 3)
            category_widget = self.create_category_item(category)
            grid_layout.addWidget(category_widget, row, col)

        layout.addLayout(grid_layout)
        layout.addStretch()

        return widget

    def create_result_item(self, item, item_type):
        """Создает элемент результата"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                background-color: #3a3a3a;
                border: 1px solid #4CAF50;
            }
        """)

        # Устанавливаем курсор-указатель
        frame.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 10, 15, 10)

        if item_type == 'service':
            # Иконка услуги
            icon_label = QLabel("🔧")
            icon_label.setStyleSheet("font-size: 24px;")

            # Информация
            info_layout = QVBoxLayout()

            name_label = QLabel(item.get('name', 'Без названия'))
            name_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)

            category_label = QLabel(f"📁 {item.get('category', 'Без категории')}")
            category_label.setStyleSheet("color: #b0b0b0; font-size: 13px;")

            info_layout.addWidget(name_label)
            info_layout.addWidget(category_label)

            # Цена
            price_label = QLabel(f"{item.get('price', 0)} ₽")
            price_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)

            layout.addWidget(icon_label)
            layout.addLayout(info_layout, 1)
            layout.addWidget(price_label)

        elif item_type == 'part':
            # Иконка товара
            icon_label = QLabel("📦")
            icon_label.setStyleSheet("font-size: 24px;")

            # Информация
            info_layout = QVBoxLayout()

            name_label = QLabel(item.get('name', 'Без названия'))
            name_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)

            details = []
            if item.get('brand'):
                details.append(f"🏷️ {item.get('brand')}")
            if item.get('code'):
                details.append(f"📋 {item.get('code')}")
            if item.get('stock', 0) > 0:
                details.append(f"✅ В наличии: {item.get('stock')} шт.")
            else:
                details.append("❌ Нет в наличии")

            details_label = QLabel(" • ".join(details))
            details_label.setStyleSheet("color: #b0b0b0; font-size: 13px;")

            info_layout.addWidget(name_label)
            info_layout.addWidget(details_label)

            # Цена
            price_label = QLabel(f"{item.get('price', 0)} ₽")
            price_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)

            layout.addWidget(icon_label)
            layout.addLayout(info_layout, 1)
            layout.addWidget(price_label)

        # Сохраняем данные в frame
        frame.item_data = item
        frame.item_type = item_type

        # Обработчик клика
        frame.mousePressEvent = lambda event, f=frame: self.on_item_clicked(f)

        return frame

    def create_category_item(self, category):
        """Создает элемент категории"""
        frame = QFrame()
        frame.setMinimumSize(200, 100)
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #333333);
                border-radius: 10px;
                padding: 15px;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 1px solid #4CAF50;
            }
        """)

        # Устанавливаем курсор-указатель
        frame.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(frame)

        icon_label = QLabel("📁")
        icon_label.setStyleSheet("font-size: 32px; qproperty-alignment: AlignCenter;")

        name_label = QLabel(category.get('name', 'Без названия'))
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }
        """)

        layout.addWidget(icon_label)
        layout.addWidget(name_label)

        # Сохраняем данные в frame
        frame.item_data = category
        frame.item_type = 'category'

        # Обработчик клика
        frame.mousePressEvent = lambda event, f=frame: self.on_item_clicked(f)

        return frame

    def on_item_clicked(self, frame):
        """Обработчик клика по элементу"""
        if hasattr(frame, 'item_data') and hasattr(frame, 'item_type'):
            item_data = frame.item_data
            item_data['type'] = frame.item_type

            # Спрашиваем подтверждение
            if frame.item_type == 'part':
                reply = QMessageBox.question(
                    self,
                    "Подтверждение",
                    f"Добавить '{item_data.get('name')}' в корзину?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    self.result_selected.emit(item_data)
                    self.accept()
            else:
                self.result_selected.emit(item_data)
                self.accept()