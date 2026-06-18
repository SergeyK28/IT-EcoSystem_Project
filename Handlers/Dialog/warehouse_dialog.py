# -*- coding: utf-8 -*-
"""
Модуль для управления складом в CRM
Содержит классы для отображения и управления складскими запасами
"""
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QFrame, QHeaderView,
    QMessageBox, QWidget, QGroupBox, QGridLayout, QSpinBox,
    QDoubleSpinBox, QTextEdit, QCheckBox, QDateEdit, QTabWidget, QMenu,
    QAction
)
import sys
import os

# Добавляем путь к корневой директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server import db_crm


class WarehouseDialog(QDialog):
    """
    Диалоговое окно для управления складом
    Позволяет просматривать, добавлять, редактировать и удалять товары на складе
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление складом - IT-EcoSystem")
        self.setMinimumSize(1400, 800)

        # Устанавливаем иконку
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "Pictures", "Screenshot from 2025-09-15 14-30-16.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Текущие фильтры
        self.current_category = None
        self.current_brand = None
        self.low_stock_only = False
        self.search_text = ""

        # Кэш для данных
        self.categories = []
        self.brands = []
        self.current_items = []

        # Настройка интерфейса
        self.setup_ui()

        # Загрузка данных
        self.load_categories_and_brands()
        self.load_data()

        # Применяем темную тему
        self.setStyleSheet(self.get_dark_style())

    def get_dark_style(self):
        """Возвращает стили для темной темы"""
        return """
            QDialog {
                background-color: #1e1e1e;
            }
            QGroupBox {
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #d0d0d0;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4CAF50;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            QPushButton#successButton {
                background-color: #4CAF50;
                border: none;
            }
            QPushButton#successButton:hover {
                background-color: #45a049;
            }
            QPushButton#dangerButton {
                background-color: #f44336;
                border: none;
            }
            QPushButton#dangerButton:hover {
                background-color: #da190b;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #808080;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #4CAF50;
            }
            QTableWidget {
                background-color: #252525;
                color: #ffffff;
                gridline-color: #3a3a3a;
                selection-background-color: #4CAF50;
                border: none;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #3a3a3a;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #d0d0d0;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3d3d3d;
            }
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ========== ВЕРХНЯЯ ПАНЕЛЬ С ЗАГОЛОВКОМ ==========
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)

        # Заголовок
        title_label = QLabel("📦 Управление складом")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(header_frame)

        # ========== ПАНЕЛЬ СТАТИСТИКИ ==========
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        stats_layout = QHBoxLayout(self.stats_frame)

        # Создаем виджеты для статистики
        self.stats_widgets = []
        stats_config = [
            ("📊 Всего позиций", "0", "#4CAF50"),
            ("🏷️ Категорий", "0", "#FFC107"),
            ("📦 Единиц товара", "0", "#17A2B8"),
            ("💰 Стоимость запасов", "0 ₽", "#28A745"),
            ("⚠️ Малый запас", "0", "#DC3545")
        ]

        for title, value, color in stats_config:
            stat_widget = self.create_stat_widget(title, value, color)
            stats_layout.addWidget(stat_widget)
            self.stats_widgets.append(stat_widget)

        main_layout.addWidget(self.stats_frame)

        # ========== ПАНЕЛЬ ФИЛЬТРОВ ==========
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по названию, коду, описанию...")
        self.search_input.setMinimumWidth(300)
        self.search_input.returnPressed.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)

        # Фильтр по категории
        filter_layout.addWidget(QLabel("Категория:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("Все категории", None)
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        filter_layout.addWidget(self.category_combo)

        # Фильтр по бренду
        filter_layout.addWidget(QLabel("Бренд:"))
        self.brand_combo = QComboBox()
        self.brand_combo.addItem("Все бренды", None)
        self.brand_combo.currentIndexChanged.connect(self.on_brand_changed)
        filter_layout.addWidget(self.brand_combo)

        # Чекбокс "Только малый запас"
        self.low_stock_check = QCheckBox("⚠️ Только малый запас")
        self.low_stock_check.setStyleSheet("color: #d0d0d0;")
        self.low_stock_check.stateChanged.connect(self.on_low_stock_changed)
        filter_layout.addWidget(self.low_stock_check)

        filter_layout.addStretch()

        # Кнопка применения фильтров
        apply_filter_btn = QPushButton("Применить фильтры")
        apply_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        apply_filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(apply_filter_btn)

        main_layout.addWidget(filter_frame)

        # ========== ОСНОВНАЯ ЧАСТЬ С ТАБЛИЦЕЙ ==========
        # Создаем вкладки для разных представлений
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                background-color: #252525;
            }
        """)

        # Вкладка со списком товаров
        self.items_tab = QWidget()
        self.setup_items_tab()
        self.tab_widget.addTab(self.items_tab, "📋 Список товаров")

        # Вкладка с категориями
        self.categories_tab = QWidget()
        self.setup_categories_tab()
        self.tab_widget.addTab(self.categories_tab, "🏷️ Категории")

        # Вкладка с аналитикой
        self.analytics_tab = QWidget()
        self.setup_analytics_tab()
        self.tab_widget.addTab(self.analytics_tab, "📊 Аналитика")

        main_layout.addWidget(self.tab_widget)

        # ========== НИЖНЯЯ ПАНЕЛЬ ==========
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_frame)

        # Кнопки действий
        self.add_btn = QPushButton("➕ Добавить товар")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setObjectName("successButton")
        self.add_btn.clicked.connect(self.add_item)
        bottom_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(self.edit_item)
        bottom_layout.addWidget(self.edit_btn)

        self.restock_btn = QPushButton("📦 Пополнить запас")
        self.restock_btn.setCursor(Qt.PointingHandCursor)
        self.restock_btn.clicked.connect(self.restock_item)
        bottom_layout.addWidget(self.restock_btn)

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.clicked.connect(self.delete_item)
        bottom_layout.addWidget(self.delete_btn)

        bottom_layout.addStretch()

        # Информация о количестве записей
        self.records_label = QLabel("Записей: 0")
        self.records_label.setStyleSheet("color: #b0b0b0;")
        bottom_layout.addWidget(self.records_label)

        main_layout.addWidget(bottom_frame)

    def create_stat_widget(self, title, value, color):
        """Создает виджет для отображения статистики"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 10px;
                border-left: 4px solid {color};
            }}
        """)
        layout = QVBoxLayout(frame)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
        layout.addWidget(value_label)

        return frame

    def setup_items_tab(self):
        """Настройка вкладки со списком товаров"""
        layout = QVBoxLayout(self.items_tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Таблица товаров
        self.table = QTableWidget()
        self.table.setColumnCount(14)  # Увеличили количество столбцов
        self.table.setHorizontalHeaderLabels([
            "ID", "Код", "Наименование", "Категория", "Бренд",
            "Кол-во", "Мин. запас", "Цена", "Себестоимость", "Прибыль",
            "Поставщик", "Расположение", "Статус", "Детали"
        ])

        # Настройка отображения столбцов
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Код
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Наименование
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Контекстное меню
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Двойной клик для редактирования
        self.table.doubleClicked.connect(self.edit_item)

        layout.addWidget(self.table)

    def setup_categories_tab(self):
        """Настройка вкладки с категориями"""
        layout = QVBoxLayout(self.categories_tab)

        # Таблица категорий
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(4)
        self.categories_table.setHorizontalHeaderLabels([
            "Категория", "Кол-во товаров", "Всего единиц", "Общая стоимость"
        ])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.categories_table)

    def setup_analytics_tab(self):
        """Настройка вкладки с аналитикой"""
        layout = QVBoxLayout(self.analytics_tab)

        # Создаем группы для разных метрик
        # Группа с основными показателями
        metrics_group = QGroupBox("Ключевые показатели")
        metrics_layout = QGridLayout(metrics_group)

        metrics = [
            ("Общая стоимость запасов:", "0 ₽", "#4CAF50"),
            ("Потенциальная выручка:", "0 ₽", "#FFC107"),
            ("Потенциальная прибыль:", "0 ₽", "#17A2B8"),
            ("Средняя маржинальность:", "0%", "#28A745"),
            ("Товаров с малым запасом:", "0", "#DC3545"),
            ("Товаров нет в наличии:", "0", "#FF6B6B")
        ]

        for i, (label, value, color) in enumerate(metrics):
            row = i // 2
            col = i % 2

            container = QFrame()
            container.setStyleSheet(f"""
                QFrame {{
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    padding: 10px;
                    border-left: 3px solid {color};
                }}
            """)
            container_layout = QVBoxLayout(container)

            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #b0b0b0; font-size: 12px;")
            container_layout.addWidget(label_widget)

            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
            container_layout.addWidget(value_widget)

            metrics_layout.addWidget(container, row, col)

        layout.addWidget(metrics_group)

        # Группа с топ категориями
        top_categories_group = QGroupBox("Топ категорий по стоимости")
        top_categories_layout = QVBoxLayout(top_categories_group)

        self.top_categories_table = QTableWidget()
        self.top_categories_table.setColumnCount(4)
        self.top_categories_table.setHorizontalHeaderLabels([
            "Категория", "Товаров", "Единиц", "Стоимость"
        ])
        self.top_categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        top_categories_layout.addWidget(self.top_categories_table)
        layout.addWidget(top_categories_group)

        # Группа с топ брендами
        top_brands_group = QGroupBox("Топ брендов по количеству")
        top_brands_layout = QVBoxLayout(top_brands_group)

        self.top_brands_table = QTableWidget()
        self.top_brands_table.setColumnCount(3)
        self.top_brands_table.setHorizontalHeaderLabels([
            "Бренд", "Товаров", "Единиц"
        ])
        self.top_brands_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        top_brands_layout.addWidget(self.top_brands_table)
        layout.addWidget(top_brands_group)

    def load_categories_and_brands(self):
        """Загружает категории и бренды для фильтров"""
        try:
            self.categories = db_crm.get_warehouse_categories()
            self.brands = db_crm.get_warehouse_brands()

            # Обновляем комбобоксы
            current_category = self.category_combo.currentData()
            current_brand = self.brand_combo.currentData()

            self.category_combo.clear()
            self.category_combo.addItem("Все категории", None)
            for category in self.categories:
                self.category_combo.addItem(category, category)

            self.brand_combo.clear()
            self.brand_combo.addItem("Все бренды", None)
            for brand in self.brands:
                self.brand_combo.addItem(brand, brand)

            # Восстанавливаем выбранные значения
            if current_category:
                index = self.category_combo.findData(current_category)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)

            if current_brand:
                index = self.brand_combo.findData(current_brand)
                if index >= 0:
                    self.brand_combo.setCurrentIndex(index)

        except Exception as e:
            print(f"Ошибка загрузки категорий и брендов: {e}")

    def load_data(self):
        """Загружает данные о товарах на складе"""
        try:
            # Получаем данные с фильтрацией
            self.current_items = db_crm.get_all_warehouse_items(
                category=self.current_category,
                brand=self.current_brand,
                low_stock_only=self.low_stock_only,
                search=self.search_text
            )

            # Обновляем таблицу
            self.update_table()

            # Обновляем статистику
            self.update_statistics()

            # Обновляем информацию о категориях
            self.update_categories_table()

            # Обновляем аналитику
            self.update_analytics()

        except Exception as e:
            print(f"Ошибка загрузки данных склада: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные склада: {e}")

    def update_table(self):
        """Обновляет таблицу с товарами"""
        self.table.setRowCount(len(self.current_items))

        for row, item in enumerate(self.current_items):
            # ID
            self.table.setItem(row, 0, self.create_centered_item(str(item.get('StockID', ''))))

            # Код
            self.table.setItem(row, 1, self.create_centered_item(item.get('DetailCode', '')))

            # Наименование
            name_item = QTableWidgetItem(item.get('DetailName', ''))
            name_item.setToolTip(item.get('Description', ''))
            self.table.setItem(row, 2, name_item)

            # Категория
            self.table.setItem(row, 3, self.create_centered_item(item.get('Category', '')))

            # Бренд
            self.table.setItem(row, 4, self.create_centered_item(item.get('Brand', '')))

            # Количество
            count = item.get('CountInStock', 0)
            min_level = item.get('MinStockLevel', 5)
            count_item = self.create_centered_item(str(count))
            if count <= 0:
                count_item.setForeground(QColor(255, 99, 71))  # Красный
                count_item.setToolTip("Нет в наличии")
            elif count <= min_level:
                count_item.setForeground(QColor(255, 193, 7))  # Желтый
                count_item.setToolTip("Малый запас")
            else:
                count_item.setForeground(QColor(76, 175, 80))  # Зеленый
            self.table.setItem(row, 5, count_item)

            # Минимальный запас
            self.table.setItem(row, 6, self.create_centered_item(str(item.get('MinStockLevel', 5))))

            # Цена
            price = item.get('Price', 0)
            price_item = self.create_centered_item(f"{price:,.2f} ₽".replace(',', ' '))
            self.table.setItem(row, 7, price_item)

            # Себестоимость
            cost = item.get('CostPrice', 0)
            cost_item = self.create_centered_item(f"{cost:,.2f} ₽".replace(',', ' '))
            self.table.setItem(row, 8, cost_item)

            # Прибыль
            profit = item.get('ProfitPerUnit', 0)
            profit_item = self.create_centered_item(f"{profit:,.2f} ₽".replace(',', ' '))
            if profit > 0:
                profit_item.setForeground(QColor(76, 175, 80))
            elif profit < 0:
                profit_item.setForeground(QColor(255, 99, 71))
            self.table.setItem(row, 9, profit_item)

            # Поставщик
            self.table.setItem(row, 10, self.create_centered_item(item.get('Supplier', '')))

            # Расположение
            self.table.setItem(row, 11, self.create_centered_item(item.get('Location', '')))

            # Статус
            status = item.get('StockStatus', '')
            status_item = self.create_centered_item(status)
            status_colors = {
                'Нет в наличии': QColor(220, 53, 69),
                'Мало': QColor(255, 193, 7),
                'Достаточно': QColor(40, 167, 69),
                'Много': QColor(0, 123, 255)
            }
            if status in status_colors:
                status_item.setBackground(status_colors[status])
                status_item.setForeground(QColor(255, 255, 255))
            self.table.setItem(row, 12, status_item)

            # Детали (кнопка)
            details_btn = QPushButton("Подробнее")
            details_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 3px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            details_btn.clicked.connect(lambda checked, r=row: self.show_item_details(r))
            self.table.setCellWidget(row, 13, details_btn)

        # Обновляем количество записей
        self.records_label.setText(f"Записей: {len(self.current_items)}")

        # Автоматически подгоняем столбцы
        self.table.resizeColumnsToContents()

    def create_centered_item(self, text):
        """Создает ячейку с центрированным текстом"""
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def update_statistics(self):
        """Обновляет статистику на верхней панели"""
        try:
            stats = db_crm.get_warehouse_statistics()

            # Обновляем значения
            self.stats_widgets[0].findChild(QLabel, "", Qt.FindChildrenRecursively).setText(
                str(stats.get('total_items', 0))
            )
            self.stats_widgets[1].findChild(QLabel, "", Qt.FindChildrenRecursively).setText(
                str(stats.get('total_categories', 0))
            )
            self.stats_widgets[2].findChild(QLabel, "", Qt.FindChildrenRecursively).setText(
                str(stats.get('total_units', 0))
            )
            self.stats_widgets[3].findChild(QLabel, "", Qt.FindChildrenRecursively).setText(
                f"{stats.get('total_investment', 0):,.2f} ₽".replace(',', ' ')
            )
            self.stats_widgets[4].findChild(QLabel, "", Qt.FindChildrenRecursively).setText(
                str(stats.get('low_stock_count', 0))
            )

        except Exception as e:
            print(f"Ошибка обновления статистики: {e}")

    def update_categories_table(self):
        """Обновляет таблицу категорий"""
        try:
            # Группируем товары по категориям
            categories = {}
            for item in self.current_items:
                category = item.get('Category', 'Без категории')
                if category not in categories:
                    categories[category] = {
                        'count': 0,
                        'total_units': 0,
                        'total_value': 0
                    }
                categories[category]['count'] += 1
                categories[category]['total_units'] += item.get('CountInStock', 0)
                categories[category]['total_value'] += item.get('CountInStock', 0) * item.get('Price', 0)

            self.categories_table.setRowCount(len(categories))

            for row, (category, data) in enumerate(sorted(categories.items())):
                self.categories_table.setItem(row, 0, self.create_centered_item(category))
                self.categories_table.setItem(row, 1, self.create_centered_item(str(data['count'])))
                self.categories_table.setItem(row, 2, self.create_centered_item(str(data['total_units'])))
                self.categories_table.setItem(row, 3, self.create_centered_item(
                    f"{data['total_value']:,.2f} ₽".replace(',', ' ')
                ))

        except Exception as e:
            print(f"Ошибка обновления таблицы категорий: {e}")

    def update_analytics(self):
        """Обновляет аналитику"""
        try:
            stats = db_crm.get_warehouse_statistics()

            # Обновляем метрики (пока просто заглушка)
            # В реальном проекте здесь нужно обновлять все виджеты на вкладке аналитики

            # Обновляем топ категории
            if 'top_categories' in stats:
                self.top_categories_table.setRowCount(len(stats['top_categories']))
                for row, cat in enumerate(stats['top_categories']):
                    self.top_categories_table.setItem(row, 0, self.create_centered_item(cat.get('Category', '')))
                    self.top_categories_table.setItem(row, 1, self.create_centered_item(str(cat.get('item_count', 0))))
                    self.top_categories_table.setItem(row, 2, self.create_centered_item(str(cat.get('total_units', 0))))
                    self.top_categories_table.setItem(row, 3, self.create_centered_item(
                        f"{cat.get('total_value', 0):,.2f} ₽".replace(',', ' ')
                    ))

            # Обновляем топ бренды
            if 'top_brands' in stats:
                self.top_brands_table.setRowCount(len(stats['top_brands']))
                for row, brand in enumerate(stats['top_brands']):
                    self.top_brands_table.setItem(row, 0, self.create_centered_item(brand.get('Brand', '')))
                    self.top_brands_table.setItem(row, 1, self.create_centered_item(str(brand.get('item_count', 0))))
                    self.top_brands_table.setItem(row, 2, self.create_centered_item(str(brand.get('total_units', 0))))

        except Exception as e:
            print(f"Ошибка обновления аналитики: {e}")

    def show_item_details(self, row):
        """Показывает детальную информацию о товаре"""
        if 0 <= row < len(self.current_items):
            item = self.current_items[row]
            stock_id = item.get('StockID')

            # Получаем детальную информацию
            details = db_crm.get_warehouse_item_detail(stock_id)

            if details:
                # Создаем диалог с деталями
                details_dialog = ItemDetailsDialog(details, self)
                details_dialog.exec_()

    def show_context_menu(self, position):
        """Показывает контекстное меню для таблицы"""
        menu = QMenu()

        edit_action = QAction("✏️ Редактировать", self)
        edit_action.triggered.connect(self.edit_item)
        menu.addAction(edit_action)

        restock_action = QAction("📦 Пополнить запас", self)
        restock_action.triggered.connect(self.restock_item)
        menu.addAction(restock_action)

        menu.addSeparator()

        delete_action = QAction("🗑️ Удалить", self)
        delete_action.triggered.connect(self.delete_item)
        delete_action.setIcon(QIcon())  # Можно добавить иконку
        menu.addAction(delete_action)

        menu.exec_(self.table.viewport().mapToGlobal(position))

    def get_selected_item(self):
        """Возвращает выбранный товар"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.current_items):
            return self.current_items[current_row]
        return None

    def add_item(self):
        """Открывает диалог добавления товара"""
        dialog = AddEditItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()

    def edit_item(self):
        """Открывает диалог редактирования товара"""
        item = self.get_selected_item()
        if not item:
            QMessageBox.warning(self, "Предупреждение", "Выберите товар для редактирования")
            return

        dialog = AddEditItemDialog(self, item)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()

    def restock_item(self):
        """Открывает диалог пополнения запаса"""
        item = self.get_selected_item()
        if not item:
            QMessageBox.warning(self, "Предупреждение", "Выберите товар для пополнения")
            return

        dialog = RestockDialog(item, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()

    def delete_item(self):
        """Удаляет выбранный товар"""
        item = self.get_selected_item()
        if not item:
            QMessageBox.warning(self, "Предупреждение", "Выберите товар для удаления")
            return

        result = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить товар '{item.get('DetailName')}'?\n"
            "Это действие можно отменить только через административную панель.",
            QMessageBox.Yes | QMessageBox.No
        )

        if result == QMessageBox.Yes:
            try:
                # Деактивируем товар
                success = db_crm.update_warehouse_item(
                    item.get('StockID'),
                    {**item, 'is_active': False}
                )

                if success:
                    QMessageBox.information(self, "Успех", "Товар удален")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить товар")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")

    def on_category_changed(self, index):
        """Обработчик изменения категории"""
        self.current_category = self.category_combo.currentData()

    def on_brand_changed(self, index):
        """Обработчик изменения бренда"""
        self.current_brand = self.brand_combo.currentData()

    def on_low_stock_changed(self, state):
        """Обработчик изменения чекбокса малого запаса"""
        self.low_stock_only = (state == Qt.Checked)

    def apply_filters(self):
        """Применяет все фильтры"""
        self.search_text = self.search_input.text().strip()
        self.load_data()

    def refresh_data(self):
        """Обновляет все данные"""
        self.load_categories_and_brands()
        self.load_data()


class AddEditItemDialog(QDialog):
    """Диалог добавления/редактирования товара"""

    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.item_data = item_data
        self.is_edit = item_data is not None

        self.setWindowTitle("Редактирование товара" if self.is_edit else "Добавление товара")
        self.setMinimumWidth(600)

        self.setup_ui()

        if self.is_edit:
            self.load_item_data()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Основная форма
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)

        row = 0

        # Код детали
        form_layout.addWidget(QLabel("Код детали:"), row, 0)
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("Например: SCR-001 или оставьте пустым для автогенерации")
        form_layout.addWidget(self.code_edit, row, 1)
        row += 1

        # Наименование
        form_layout.addWidget(QLabel("Наименование:*"), row, 0)
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_edit, row, 1)
        row += 1

        # Описание
        form_layout.addWidget(QLabel("Описание:"), row, 0)
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        form_layout.addWidget(self.desc_edit, row, 1)
        row += 1

        # Категория и бренд в одной строке
        form_layout.addWidget(QLabel("Категория:*"), row, 0)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.load_categories()
        form_layout.addWidget(self.category_combo, row, 1)

        form_layout.addWidget(QLabel("Бренд:"), row, 2)
        self.brand_combo = QComboBox()
        self.brand_combo.setEditable(True)
        self.load_brands()
        form_layout.addWidget(self.brand_combo, row, 3)
        row += 1

        # Количество и минимальный уровень
        form_layout.addWidget(QLabel("Количество:*"), row, 0)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(0, 999999)
        self.count_spin.setValue(0)
        form_layout.addWidget(self.count_spin, row, 1)

        form_layout.addWidget(QLabel("Мин. запас:"), row, 2)
        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setRange(0, 999999)
        self.min_stock_spin.setValue(5)
        form_layout.addWidget(self.min_stock_spin, row, 3)
        row += 1

        # Цена и себестоимость
        form_layout.addWidget(QLabel("Цена продажи:*"), row, 0)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 9999999)
        self.price_spin.setPrefix("₽ ")
        self.price_spin.setDecimals(2)
        form_layout.addWidget(self.price_spin, row, 1)

        form_layout.addWidget(QLabel("Себестоимость:"), row, 2)
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 9999999)
        self.cost_spin.setPrefix("₽ ")
        self.cost_spin.setDecimals(2)
        form_layout.addWidget(self.cost_spin, row, 3)
        row += 1

        # Поставщик и расположение
        form_layout.addWidget(QLabel("Поставщик:"), row, 0)
        self.supplier_edit = QLineEdit()
        form_layout.addWidget(self.supplier_edit, row, 1)

        form_layout.addWidget(QLabel("Расположение:"), row, 2)
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Например: Стеллаж А, полка 3")
        form_layout.addWidget(self.location_edit, row, 3)
        row += 1

        # Гарантия и дата последнего пополнения
        form_layout.addWidget(QLabel("Гарантия (дней):"), row, 0)
        self.warranty_spin = QSpinBox()
        self.warranty_spin.setRange(0, 9999)
        self.warranty_spin.setValue(90)
        form_layout.addWidget(self.warranty_spin, row, 1)

        form_layout.addWidget(QLabel("Последнее пополнение:"), row, 2)
        self.restock_date = QDateEdit()
        self.restock_date.setDate(QtCore.QDate.currentDate())
        self.restock_date.setCalendarPopup(True)
        form_layout.addWidget(self.restock_date, row, 3)
        row += 1

        # Совместимые модели
        form_layout.addWidget(QLabel("Совместимые модели:"), row, 0)
        self.models_edit = QTextEdit()
        self.models_edit.setPlaceholderText("Введите модели через запятую или в формате JSON")
        self.models_edit.setMaximumHeight(60)
        form_layout.addWidget(self.models_edit, row, 1, 1, 3)
        row += 1

        # Активен
        self.active_check = QCheckBox("Товар активен")
        self.active_check.setChecked(True)
        form_layout.addWidget(self.active_check, row, 0, 1, 2)
        row += 1

        layout.addWidget(form_widget)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setObjectName("successButton")
        self.save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("✖ Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

    def load_categories(self):
        """Загружает категории"""
        try:
            categories = db_crm.get_warehouse_categories()
            self.category_combo.clear()
            self.category_combo.addItems(categories)
        except Exception as e:
            print(f"Ошибка загрузки категорий: {e}")

    def load_brands(self):
        """Загружает бренды"""
        try:
            brands = db_crm.get_warehouse_brands()
            self.brand_combo.clear()
            self.brand_combo.addItems(brands)
        except Exception as e:
            print(f"Ошибка загрузки брендов: {e}")

    def load_item_data(self):
        """Загружает данные товара в форму"""
        if not self.item_data:
            return

        self.code_edit.setText(self.item_data.get('DetailCode', ''))
        self.name_edit.setText(self.item_data.get('DetailName', ''))
        self.desc_edit.setPlainText(self.item_data.get('Description', ''))

        category = self.item_data.get('Category', '')
        index = self.category_combo.findText(category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        else:
            self.category_combo.setEditText(category)

        brand = self.item_data.get('Brand', '')
        index = self.brand_combo.findText(brand)
        if index >= 0:
            self.brand_combo.setCurrentIndex(index)
        else:
            self.brand_combo.setEditText(brand)

        self.count_spin.setValue(self.item_data.get('CountInStock', 0))
        self.min_stock_spin.setValue(self.item_data.get('MinStockLevel', 5))
        self.price_spin.setValue(self.item_data.get('Price', 0))
        self.cost_spin.setValue(self.item_data.get('CostPrice', 0))
        self.supplier_edit.setText(self.item_data.get('Supplier', ''))
        self.location_edit.setText(self.item_data.get('Location', ''))
        self.warranty_spin.setValue(self.item_data.get('WarrantyDays', 90))

        if self.item_data.get('LastRestockDate'):
            self.restock_date.setDate(QtCore.QDate.fromString(str(self.item_data.get('LastRestockDate')), 'yyyy-MM-dd'))

        self.models_edit.setPlainText(self.item_data.get('CompatibleModels', ''))
        self.active_check.setChecked(self.item_data.get('IsActive', True))

    def get_item_data(self):
        """Возвращает данные из формы"""
        return {
            'detail_code': self.code_edit.text().strip(),
            'detail_name': self.name_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip(),
            'category': self.category_combo.currentText().strip(),
            'brand': self.brand_combo.currentText().strip(),
            'count_in_stock': self.count_spin.value(),
            'min_stock_level': self.min_stock_spin.value(),
            'price': self.price_spin.value(),
            'cost_price': self.cost_spin.value(),
            'supplier': self.supplier_edit.text().strip(),
            'location': self.location_edit.text().strip(),
            'warranty_days': self.warranty_spin.value(),
            'last_restock_date': self.restock_date.date().toString('yyyy-MM-dd'),
            'compatible_models': self.models_edit.toPlainText().strip(),
            'is_active': self.active_check.isChecked()
        }

    def accept(self):
        """Сохраняет данные"""
        # Валидация
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Наименование товара обязательно")
            return

        if not self.category_combo.currentText().strip():
            QMessageBox.warning(self, "Ошибка", "Категория обязательна")
            return

        if self.price_spin.value() <= 0:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть больше 0")
            return

        # Сохраняем в БД
        try:
            data = self.get_item_data()

            if self.is_edit:
                success = db_crm.update_warehouse_item(self.item_data.get('StockID'), data)
            else:
                new_id = db_crm.create_warehouse_item(data)
                success = new_id is not None

            if success:
                super().accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить товар")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")


class RestockDialog(QDialog):
    """Диалог пополнения запаса"""

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setWindowTitle(f"Пополнение запаса - {item_data.get('DetailName')}")
        self.setMinimumWidth(400)

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Информация о товаре
        info_group = QGroupBox("Информация о товаре")
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("Наименование:"), 0, 0)
        info_layout.addWidget(QLabel(self.item_data.get('DetailName', '')), 0, 1)

        info_layout.addWidget(QLabel("Текущий запас:"), 1, 0)
        current_count = self.item_data.get('CountInStock', 0)
        info_layout.addWidget(QLabel(str(current_count)), 1, 1)

        info_layout.addWidget(QLabel("Мин. запас:"), 2, 0)
        info_layout.addWidget(QLabel(str(self.item_data.get('MinStockLevel', 5))), 2, 1)

        layout.addWidget(info_group)

        # Форма пополнения
        form_group = QGroupBox("Пополнение")
        form_layout = QFormLayout(form_group)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999999)
        self.quantity_spin.setValue(10)
        form_layout.addRow("Количество:", self.quantity_spin)

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 9999999)
        self.price_spin.setPrefix("₽ ")
        self.price_spin.setDecimals(2)
        self.price_spin.setValue(self.item_data.get('CostPrice', 0))
        form_layout.addRow("Новая закупочная цена:", self.price_spin)

        layout.addWidget(form_group)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.ok_btn = QPushButton("✅ Пополнить")
        self.ok_btn.setObjectName("successButton")
        self.ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("✖ Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

    def accept(self):
        """Выполняет пополнение"""
        try:
            success = db_crm.restock_item(
                self.item_data.get('StockID'),
                self.quantity_spin.value(),
                self.price_spin.value()
            )

            if success:
                QMessageBox.information(self, "Успех", "Запас успешно пополнен")
                super().accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось пополнить запас")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при пополнении: {e}")


class ItemDetailsDialog(QDialog):
    """Диалог с детальной информацией о товаре"""

    def __init__(self, details, parent=None):
        super().__init__(parent)
        self.details = details
        self.setWindowTitle(f"Детали товара - {details.get('DetailName')}")
        self.setMinimumSize(600, 500)

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_layout = QGridLayout(info_group)

        row = 0
        fields = [
            ("Код:", "DetailCode"),
            ("Наименование:", "DetailName"),
            ("Категория:", "Category"),
            ("Бренд:", "Brand"),
            ("Описание:", "Description"),
            ("Поставщик:", "Supplier"),
            ("Расположение:", "Location"),
            ("Гарантия:", "WarrantyDays", " дней"),
            ("Дата пополнения:", "LastRestockDate"),
        ]

        for label, field, suffix in [(f[0], f[1], f[2] if len(f) > 2 else "") for f in fields]:
            info_layout.addWidget(QLabel(label), row, 0)
            value = self.details.get(field, '')
            if value is None:
                value = ''
            info_layout.addWidget(QLabel(f"{value}{suffix}"), row, 1)
            row += 1

        layout.addWidget(info_group)

        # Финансовая информация
        finance_group = QGroupBox("Финансовая информация")
        finance_layout = QGridLayout(finance_group)

        finance_fields = [
            ("Цена продажи:", "Price", " ₽"),
            ("Себестоимость:", "CostPrice", " ₽"),
            ("Прибыль с ед.:", "ProfitPerUnit", " ₽"),
            ("Общая стоимость запасов:", "TotalCostValue", " ₽"),
            ("Потенциальная выручка:", "TotalPotentialRevenue", " ₽"),
        ]

        for i, (label, field, suffix) in enumerate(finance_fields):
            finance_layout.addWidget(QLabel(label), i, 0)
            value = self.details.get(field, 0)
            if value:
                finance_layout.addWidget(QLabel(f"{value:,.2f}{suffix}".replace(',', ' ')), i, 1)

        layout.addWidget(finance_group)

        # Статистика использования
        stats_group = QGroupBox("Статистика использования")
        stats_layout = QGridLayout(stats_group)

        stats_fields = [
            ("Продано всего:", "TotalSold"),
            ("Количество заказов:", "TimesOrdered"),
            ("Средняя цена продажи:", "AvgSellingPrice", " ₽"),
            ("Последняя продажа:", "LastSoldDate"),
            ("Ожидающие заказы:", "WaitingOrders"),
        ]

        for i, (label, field, suffix) in enumerate([(f[0], f[1], f[2] if len(f) > 2 else "") for f in stats_fields]):
            stats_layout.addWidget(QLabel(label), i, 0)
            value = self.details.get(field, '')
            if value is None:
                value = ''
            if field in ['AvgSellingPrice'] and value:
                stats_layout.addWidget(QLabel(f"{float(value):,.2f}{suffix}".replace(',', ' ')), i, 1)
            else:
                stats_layout.addWidget(QLabel(str(value)), i, 1)

        layout.addWidget(stats_group)

        # Совместимые модели
        if self.details.get('CompatibleModelsList'):
            models_group = QGroupBox("Совместимые модели")
            models_layout = QVBoxLayout(models_group)

            for model in self.details.get('CompatibleModelsList', []):
                models_layout.addWidget(QLabel(f"• {model}"))

            layout.addWidget(models_group)

        # Кнопка закрытия
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)