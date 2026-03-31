# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QUrl, QPropertyAnimation, QTimer
from PyQt5.QtGui import QDesktopServices, QColor, QFont
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
                             QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QTextEdit, QComboBox, QWidget, QGraphicsOpacityEffect, QStackedWidget,
                             QScrollArea, QGridLayout)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm
from Handlers.Employees.employee_session import employee_session


class ModernButton(QPushButton):
    """Современная кнопка с анимацией"""

    def __init__(self, text="", parent=None, icon=None, primary=False):
        super().__init__(text, parent)
        self.primary = primary
        self.setCursor(Qt.PointingHandCursor)

        if icon:
            self.setIcon(icon)

        # Базовая настройка
        self.setMinimumHeight(40)

        # Стиль в зависимости от типа
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                              stop: 0 #4CAF50, stop: 1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                              stop: 0 #45a049, stop: 1 #3d8b40);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                              stop: 0 #3d8b40, stop: 1 #357a38);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #404040;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    border-color: #4CAF50;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #252525;
                }
            """)


class ModernLineEdit(QLineEdit):
    """Современное поле ввода с подсветкой"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: #4CAF50;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
                background-color: #333333;
            }
            QLineEdit:hover {
                border-color: #555555;
            }
        """)


class ModernTextEdit(QTextEdit):
    """Современное текстовое поле"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: #4CAF50;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
                background-color: #333333;
            }
            QTextEdit:hover {
                border-color: #555555;
            }
        """)


class ModernComboBox(QComboBox):
    """Современный выпадающий список"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #555555;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #888888;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                selection-background-color: #4CAF50;
            }
        """)


class ShopsDialog(QDialog):
    """Окно управления ссылками на магазины (улучшенный дизайн)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shops_data = []
        self.view_mode = 'table'  # 'table' или 'cards'
        self.setup_ui()
        self.load_shops_from_db()

        # Анимация появления
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def setup_ui(self):
        self.setObjectName("ShopsDialog")
        self.setWindowTitle("IT-EcoSystem CRM - Магазины")
        self.setFixedSize(1200, 800)

        # Основной стиль
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton#closeBtn {
                background-color: #dc3545;
                color: white;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
                font-size: 18px;
                padding: 0px;
                border-radius: 20px;
            }
            QPushButton#closeBtn:hover {
                background-color: #c82333;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                gridline-color: #404040;
                alternate-background-color: #333333;
                selection-background-color: #4CAF50;
                border-radius: 12px;
                border: 1px solid #404040;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #4CAF50;
                padding: 12px 8px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #4CAF50;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 6px;
                min-height: 20px;
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
                min-width: 20px;
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
                background-color: #1a1a1a;
                border-radius: 20px;
                border: 1px solid #333333;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(shadow)

        # Основной layout
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Верхняя панель
        header_layout = QHBoxLayout()

        # Заголовок с градиентом
        title_container = QFrame()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel("🛒")
        icon_label.setStyleSheet("font-size: 32px; background: transparent;")
        title_layout.addWidget(icon_label)

        title_label = QLabel("МАГАЗИНЫ")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                  stop: 0 #4CAF50, stop: 1 #8BC34A);
            background: transparent;
            letter-spacing: 1px;
        """)
        title_layout.addWidget(title_label)

        header_layout.addWidget(title_container)
        header_layout.addStretch()

        # Переключатель вида
        self.view_toggle_btn = ModernButton("📱 Карточки")
        self.view_toggle_btn.clicked.connect(self.toggle_view)
        header_layout.addWidget(self.view_toggle_btn)

        # Кнопка добавления магазина
        self.add_btn = ModernButton("➕ Добавить магазин", primary=True)
        self.add_btn.clicked.connect(self.show_add_shop_dialog)
        header_layout.addWidget(self.add_btn)

        # Кнопка закрытия
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Панель поиска и фильтров
        filters_frame = QFrame()
        filters_frame.setStyleSheet("""
            QFrame {
                background-color: #242424;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(15)

        # Поиск
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 18px; background: transparent;")
        filters_layout.addWidget(search_icon)

        self.search_input = ModernLineEdit("Название магазина или категория...")
        self.search_input.textChanged.connect(self.filter_shops)
        filters_layout.addWidget(self.search_input, 1)

        # Категории
        category_icon = QLabel("📂")
        category_icon.setStyleSheet("font-size: 18px; background: transparent;")
        filters_layout.addWidget(category_icon)

        self.category_combo = ModernComboBox()
        self.category_combo.addItem("Все категории")
        self.category_combo.currentTextChanged.connect(self.filter_shops)
        filters_layout.addWidget(self.category_combo)

        # Кнопка сброса фильтров
        reset_btn = ModernButton("⟲ Сброс")
        reset_btn.clicked.connect(self.reset_filters)
        filters_layout.addWidget(reset_btn)

        layout.addWidget(filters_frame)

        # Статистика
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #242424;
                border-radius: 10px;
                padding: 10px 15px;
            }
        """)

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        self.total_shops_label = QLabel("0 магазинов")
        self.total_shops_label.setStyleSheet("""
            color: #4CAF50;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
        """)
        stats_layout.addWidget(self.total_shops_label)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #404040; max-width: 2px;")
        stats_layout.addWidget(separator)

        self.categories_count_label = QLabel("0 категорий")
        self.categories_count_label.setStyleSheet("""
            color: #b0b0b0;
            font-size: 14px;
            background: transparent;
        """)
        stats_layout.addWidget(self.categories_count_label)

        stats_layout.addStretch()

        layout.addWidget(stats_frame)

        # Стек для переключения между таблицей и карточками
        self.stacked_widget = QStackedWidget()

        # Таблица
        self.table_widget = QWidget()
        self.setup_table_view()
        self.stacked_widget.addWidget(self.table_widget)

        # Карточки
        self.cards_widget = QWidget()
        self.setup_cards_view()
        self.stacked_widget.addWidget(self.cards_widget)

        layout.addWidget(self.stacked_widget, 1)

    def setup_table_view(self):
        """Настраивает табличное представление"""
        layout = QVBoxLayout(self.table_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.shops_table = QTableWidget()
        self.shops_table.setColumnCount(6)
        self.shops_table.setHorizontalHeaderLabels(["ID", "Название", "Категория", "Ссылка", "Описание", "Действия"])
        self.shops_table.setColumnHidden(0, True)  # Скрываем ID столбец
        self.shops_table.setAlternatingRowColors(True)
        self.shops_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.shops_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Настройка растяжения
        header = self.shops_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Название
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Категория
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Ссылка
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Описание
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Действия

        self.shops_table.verticalHeader().setVisible(False)
        self.shops_table.verticalHeader().setDefaultSectionSize(45)

        layout.addWidget(self.shops_table)

    def setup_cards_view(self):
        """Настраивает отображение карточками"""
        layout = QVBoxLayout(self.cards_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Область прокрутки для карточек
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.cards_container)
        layout.addWidget(scroll_area)

    def toggle_view(self):
        """Переключает между таблицей и карточками"""
        if self.view_mode == 'table':
            self.view_mode = 'cards'
            self.view_toggle_btn.setText("📋 Таблица")
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.view_mode = 'table'
            self.view_toggle_btn.setText("📱 Карточки")
            self.stacked_widget.setCurrentIndex(0)

        self.update_shops_table()

    def load_shops_from_db(self):
        """Загружает данные магазинов из БД"""
        try:
            self.shops_data = db_crm.get_all_shops(only_active=True)
            print(f"Загружено {len(self.shops_data)} магазинов из БД")

            self.update_categories()
            self.update_shops_table()
            self.update_statistics()

        except Exception as e:
            print(f"Ошибка загрузки магазинов из БД: {e}")
            self.shops_data = []
            self.update_shops_table()

    def update_categories(self):
        """Обновляет список категорий"""
        try:
            categories = db_crm.get_shop_categories()

            self.category_combo.clear()
            self.category_combo.addItem("Все категории")

            if categories:
                for category in sorted(categories):
                    if category:
                        self.category_combo.addItem(category)

        except Exception as e:
            print(f"Ошибка обновления категорий: {e}")

    def update_statistics(self):
        """Обновляет статистику"""
        total = len(self.shops_data)
        categories = len(set(shop.get('category', '') for shop in self.shops_data if shop.get('category')))

        self.total_shops_label.setText(f"{total} магазин{self.get_plural_suffix(total)}")
        self.categories_count_label.setText(f"{categories} категори{self.get_category_plural_suffix(categories)}")

    def get_plural_suffix(self, count):
        """Возвращает окончание для слова 'магазин'"""
        if count % 10 == 1 and count % 100 != 11:
            return ""
        elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
            return "а"
        else:
            return "ов"

    def get_category_plural_suffix(self, count):
        """Возвращает окончание для слова 'категория'"""
        if count % 10 == 1 and count % 100 != 11:
            return "я"
        elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
            return "и"
        else:
            return "й"

    def update_shops_table(self):
        """Обновляет отображение магазинов"""
        try:
            filtered_data = self.get_filtered_data()

            if self.view_mode == 'table':
                self.update_table_view(filtered_data)
            else:
                self.update_cards_view(filtered_data)

            self.update_statistics()

        except Exception as e:
            print(f"Ошибка обновления: {e}")

    def update_table_view(self, filtered_data):
        """Обновляет табличное представление с текстовыми кнопками"""
        self.shops_table.setRowCount(len(filtered_data))

        # Убеждаемся, что у таблицы правильное количество столбцов
        if self.shops_table.columnCount() != 6:
            self.shops_table.setColumnCount(6)
            self.shops_table.setHorizontalHeaderLabels(
                ["ID", "Название", "Категория", "Ссылка", "Описание", "Действия"])
            self.shops_table.setColumnHidden(0, True)  # Скрываем ID

        for row, shop in enumerate(filtered_data):
            # ID (скрытый)
            id_item = QTableWidgetItem(str(shop.get('id', '')))
            self.shops_table.setItem(row, 0, id_item)

            # Название
            name_item = QTableWidgetItem(shop.get('name', ''))
            name_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.shops_table.setItem(row, 1, name_item)

            # Категория
            category_item = QTableWidgetItem(shop.get('category', ''))
            category_item.setTextAlignment(Qt.AlignCenter)
            category_item.setBackground(QColor(60, 60, 60))
            self.shops_table.setItem(row, 2, category_item)

            # Ссылка
            url_item = QTableWidgetItem(shop.get('url', ''))
            url_item.setForeground(QColor(76, 175, 80))
            self.shops_table.setItem(row, 3, url_item)

            # Описание
            desc_item = QTableWidgetItem(shop.get('description', ''))
            self.shops_table.setItem(row, 4, desc_item)

            # Действия - создаем виджет с кнопками
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(4)

            # Кнопка открыть
            open_btn = QPushButton("🔗 Открыть")
            open_btn.setToolTip("Открыть ссылку в браузере")
            open_btn.setFixedSize(80, 28)
            open_btn.setCursor(Qt.PointingHandCursor)
            open_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            open_btn.clicked.connect(lambda checked, url=shop.get('url', ''): self.open_url(url))
            actions_layout.addWidget(open_btn)

            # Кнопка редактировать
            edit_btn = QPushButton("✏️ Ред.")
            edit_btn.setToolTip("Редактировать магазин")
            edit_btn.setFixedSize(70, 28)
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffc107;
                    color: black;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #e0a800;
                }
            """)
            edit_btn.clicked.connect(lambda checked, s=shop: self.edit_shop(s))
            actions_layout.addWidget(edit_btn)

            # Кнопка удалить
            delete_btn = QPushButton("🗑️ Удал.")
            delete_btn.setToolTip("Удалить магазин")
            delete_btn.setFixedSize(70, 28)
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            delete_btn.clicked.connect(lambda checked, s=shop: self.delete_shop(s))
            actions_layout.addWidget(delete_btn)

            actions_layout.addStretch()
            self.shops_table.setCellWidget(row, 5, actions_widget)

        # Настраиваем ширину столбцов
        self.shops_table.setColumnWidth(0, 50)  # ID (скрыт)
        self.shops_table.setColumnWidth(1, 200)  # Название
        self.shops_table.setColumnWidth(2, 120)  # Категория
        self.shops_table.setColumnWidth(3, 250)  # Ссылка
        self.shops_table.setColumnWidth(4, 300)  # Описание
        self.shops_table.setColumnWidth(5, 240)  # Действия

        # Альтернативный вариант - автоматическая подгонка
        # self.shops_table.resizeColumnsToContents()

    def update_cards_view(self, filtered_data):
        """Обновляет отображение карточками"""
        # Очищаем контейнер
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Добавляем карточки
        cols = 3  # Количество карточек в ряду
        for i, shop in enumerate(filtered_data):
            card = self.create_shop_card(shop)
            row = i // cols
            col = i % cols
            self.cards_layout.addWidget(card, row, col)

        # Если нет данных
        if not filtered_data:
            no_data_label = QLabel("✨ Магазины не найдены")
            no_data_label.setStyleSheet("""
                color: #666666;
                font-size: 18px;
                padding: 100px;
                background: transparent;
            """)
            no_data_label.setAlignment(Qt.AlignCenter)
            self.cards_layout.addWidget(no_data_label, 0, 0, 1, cols)

    def create_shop_card(self, shop_data):
        """Создает карточку магазина"""
        card = QFrame()
        card.setFixedSize(300, 220)
        card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 12px;
                border: 1px solid #404040;
            }
            QFrame:hover {
                border-color: #4CAF50;
                background-color: #333333;
            }
            QLabel {
                color: #ffffff;
                background: transparent;
            }
        """)

        # Тень для карточки
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Заголовок
        header_layout = QHBoxLayout()

        icon_label = QLabel(self.get_category_icon(shop_data.get('category', '')))
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)

        name_label = QLabel(shop_data.get('name', ''))
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        name_label.setWordWrap(True)
        header_layout.addWidget(name_label, 1)

        layout.addLayout(header_layout)

        # Категория
        category_label = QLabel(shop_data.get('category', ''))
        category_label.setStyleSheet("""
            background-color: #404040;
            color: #e0e0e0;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            max-width: 100px;
        """)
        category_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(category_label)

        # Описание
        description = shop_data.get('description', '')
        if len(description) > 80:
            description = description[:80] + "..."
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        open_btn = QPushButton("🔗 Открыть")
        open_btn.setFixedSize(90, 32)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        open_btn.clicked.connect(lambda: self.open_url(shop_data.get('url', '')))
        buttons_layout.addWidget(open_btn)

        edit_btn = QPushButton("✏️ Ред.")
        edit_btn.setFixedSize(70, 32)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                border-radius: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_shop(shop_data))
        buttons_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ Удал.")
        delete_btn.setFixedSize(70, 32)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_shop(shop_data))
        buttons_layout.addWidget(delete_btn)

        layout.addLayout(buttons_layout)

        return card

    def get_category_icon(self, category):
        """Возвращает иконку для категории"""
        category_lower = category.lower()
        icons = {
            'электроника': '💻',
            'маркетплейс': '🛍️',
            'одежда': '👕',
            'книги': '📚',
            'продукты': '🍎',
            'стройка': '🔨',
            'авто': '🚗',
            'спорт': '⚽'
        }

        for key, icon in icons.items():
            if key in category_lower:
                return icon
        return '🛒'

    def get_filtered_data(self):
        """Возвращает отфильтрованные данные"""
        try:
            search_text = self.search_input.text().strip().lower()
            category = self.category_combo.currentText()

            filtered = []
            for shop in self.shops_data:
                if category != "Все категории" and shop.get('category') != category:
                    continue

                if search_text:
                    if (search_text not in shop.get('name', '').lower() and
                            search_text not in shop.get('category', '').lower() and
                            search_text not in shop.get('description', '').lower()):
                        continue

                filtered.append(shop)

            return filtered

        except Exception as e:
            print(f"Ошибка фильтрации: {e}")
            return []

    def filter_shops(self):
        """Фильтрует магазины"""
        self.update_shops_table()

    def reset_filters(self):
        """Сбрасывает фильтры"""
        self.search_input.clear()
        self.category_combo.setCurrentIndex(0)

    def open_url(self, url):
        """Открывает ссылку в браузере с анимацией"""
        try:
            if url:
                QDesktopServices.openUrl(QUrl(url))
                self.show_notification("✅ Ссылка открыта в браузере")
            else:
                QMessageBox.warning(self, "Ошибка", "Ссылка не указана")
        except Exception as e:
            print(f"Ошибка открытия ссылки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть ссылку: {e}")

    def show_add_shop_dialog(self):
        """Показывает диалог добавления магазина"""
        dialog = AddEditShopDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            shop_data = dialog.get_shop_data()
            if shop_data:
                created_by = employee_session.get_employee_id()
                new_id = db_crm.create_shop(shop_data, created_by)

                if new_id:
                    self.load_shops_from_db()
                    self.show_notification("✅ Магазин успешно добавлен")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось добавить магазин")

    def edit_shop(self, shop):
        """Редактирует магазин"""
        dialog = AddEditShopDialog(self, shop)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_shop_data()
            if new_data:
                if db_crm.update_shop(shop['id'], new_data):
                    self.load_shops_from_db()
                    self.show_notification("✅ Магазин успешно обновлен")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить магазин")

    def delete_shop(self, shop):
        """Удаляет магазин"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение удаления")
        msg.setText(f"Удалить магазин '{shop.get('name')}'?")
        msg.setInformativeText("Это действие нельзя отменить")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1a;
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton[text="&Yes"] {
                background-color: #dc3545;
                color: white;
            }
            QPushButton[text="&No"] {
                background-color: #6c757d;
                color: white;
            }
        """)

        if msg.exec_() == QMessageBox.Yes:
            try:
                if db_crm.delete_shop(shop['id'], hard_delete=False):
                    self.load_shops_from_db()
                    self.show_notification("🗑️ Магазин удален")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить магазин")
            except Exception as e:
                print(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить магазин: {e}")

    def show_notification(self, message):
        """Показывает всплывающее уведомление"""
        notification = QLabel(message, self)
        notification.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        notification.adjustSize()

        # Центрируем
        x = (self.width() - notification.width()) // 2
        y = 100
        notification.move(x, y)
        notification.show()

        # Анимация появления и исчезновения
        opacity_effect = QGraphicsOpacityEffect()
        notification.setGraphicsEffect(opacity_effect)

        fade_in = QPropertyAnimation(opacity_effect, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)

        fade_out = QPropertyAnimation(opacity_effect, b"opacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)

        fade_in.start()
        QTimer.singleShot(2000, fade_out.start)
        QTimer.singleShot(2300, notification.deleteLater)

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


class AddEditShopDialog(QDialog):
    """Диалог добавления/редактирования магазина (улучшенный)"""

    def __init__(self, parent=None, shop_data=None):
        super().__init__(parent)
        self.shop_data = shop_data
        self.setup_ui()

        if shop_data:
            self.setWindowTitle("Редактирование магазина")
            self.fill_data()
        else:
            self.setWindowTitle("Добавление магазина")

        # Анимация появления
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def setup_ui(self):
        self.setFixedSize(550, 600)

        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
        """)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 550, 600)
        main_container.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 25px;
                border: 1px solid #333333;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        header_layout = QHBoxLayout()

        title_text = "✏️ РЕДАКТИРОВАНИЕ" if self.shop_data else "➕ ДОБАВЛЕНИЕ МАГАЗИНА"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                  stop: 0 #4CAF50, stop: 1 #8BC34A);
            background: transparent;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
                font-size: 18px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Форма
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #242424;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # Название
        name_label = QLabel("📝 Название магазина")
        name_label.setStyleSheet("color: #4CAF50; font-size: 13px; margin-top: 5px;")
        form_layout.addWidget(name_label)

        self.name_input = ModernLineEdit("Введите название магазина")
        form_layout.addWidget(self.name_input)

        # Категория
        category_label = QLabel("📂 Категория")
        category_label.setStyleSheet("color: #4CAF50; font-size: 13px; margin-top: 5px;")
        form_layout.addWidget(category_label)

        self.category_input = ModernLineEdit("Например: Электроника, Маркетплейс")
        form_layout.addWidget(self.category_input)

        # Подсказки категорий
        hints_layout = QHBoxLayout()
        categories = ["Электроника", "Маркетплейс", "Одежда", "Книги", "Продукты"]
        for cat in categories:
            hint_btn = QPushButton(cat)
            hint_btn.setFixedHeight(30)
            hint_btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: #b0b0b0;
                    border: 1px solid #404040;
                    border-radius: 15px;
                    padding: 5px 10px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #404040;
                    border-color: #4CAF50;
                    color: white;
                }
            """)
            hint_btn.clicked.connect(lambda checked, c=cat: self.category_input.setText(c))
            hints_layout.addWidget(hint_btn)
        hints_layout.addStretch()
        form_layout.addLayout(hints_layout)

        # Ссылка
        url_label = QLabel("🔗 Ссылка на магазин")
        url_label.setStyleSheet("color: #4CAF50; font-size: 13px; margin-top: 5px;")
        form_layout.addWidget(url_label)

        self.url_input = ModernLineEdit("https://example.com")
        form_layout.addWidget(self.url_input)

        # Описание
        desc_label = QLabel("📝 Описание (необязательно)")
        desc_label.setStyleSheet("color: #4CAF50; font-size: 13px; margin-top: 5px;")
        form_layout.addWidget(desc_label)

        self.description_input = ModernTextEdit("Краткое описание магазина...")
        self.description_input.setMaximumHeight(100)
        form_layout.addWidget(self.description_input)

        layout.addWidget(form_frame)

        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #4CAF50, stop: 1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #45a049, stop: 1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3d8b40, stop: 1 #357a38);
            }
        """)
        self.save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

        # Подсказка для перетаскивания
        hint_label = QLabel("👆 Перетащите окно за заголовок")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("""
            color: #666666;
            font-size: 10px;
            padding: 5px;
        """)
        layout.addWidget(hint_label)

    def fill_data(self):
        """Заполняет поля данными"""
        if self.shop_data:
            self.name_input.setText(self.shop_data.get('name', ''))
            self.category_input.setText(self.shop_data.get('category', ''))
            self.url_input.setText(self.shop_data.get('url', ''))
            self.description_input.setText(self.shop_data.get('description', ''))

    def get_shop_data(self):
        """Возвращает данные магазина"""
        name = self.name_input.text().strip()
        category = self.category_input.text().strip()
        url = self.url_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not name:
            self.show_error("Введите название магазина")
            return None

        if not category:
            self.show_error("Введите категорию магазина")
            return None

        if not url:
            self.show_error("Введите ссылку на магазин")
            return None

        # Добавляем https:// если нет протокола
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        return {
            'name': name,
            'category': category,
            'url': url,
            'description': description
        }

    def show_error(self, message):
        """Показывает ошибку"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Ошибка")
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1a;
                color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
        """)
        msg.exec_()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()