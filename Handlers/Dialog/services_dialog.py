# -*- coding: utf-8 -*-
"""
Модуль для управления услугами (улучшенная версия)
Аналог дизайна warehouse_dialog.py
Отображает:
- Список услуг с категориями
- Форму добавления/редактирования услуги
- Статистику по услугам
- Аналитику использования
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QFrame, QMessageBox, QHeaderView, QGroupBox,
    QFormLayout, QTextEdit, QSplitter, QCheckBox, QWidget,
    QTabWidget, QMenu, QAction, QGridLayout
)
from PyQt5.QtGui import QColor, QIcon

import sys
import os
import csv
from datetime import datetime

# Добавляем путь к корневой директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server import db_crm


class ServicesDialog(QDialog):
    """
    Диалог управления услугами (улучшенная версия).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Настройка окна
        self.setWindowTitle("IT-EcoSystem - Услуги")
        self.setMinimumSize(1600, 950)
        self.resize(1600, 950)
        self.setModal(False)

        # Инициализация переменных
        self.current_service_id = None
        self.all_services = []
        self.current_category = None
        self.current_status = None
        self.search_text = ""

        # Кэш для категорий
        self.categories = []

        # Устанавливаем иконку
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "Pictures", "Screenshot from 2025-09-15 14-30-16.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Настройка интерфейса
        self.setup_ui()

        # Загрузка данных
        self.load_services()

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
                color: #4CAF50;
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
                font-weight: bold;
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
            QPushButton#warningButton {
                background-color: #FF9800;
                border: none;
            }
            QPushButton#warningButton:hover {
                background-color: #F57C00;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, 
            QTextEdit:focus, QDateEdit:focus {
                border-color: #4CAF50;
            }
            QTextEdit {
                padding: 12px;
                line-height: 1.4;
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
                alternate-background-color: #2d2d2d;
            }
            QTableWidget::item {
                padding: 10px 8px;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #3a3a3a;
                font-weight: bold;
                font-size: 13px;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #d0d0d0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
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
            QCheckBox {
                color: #d0d0d0;
                spacing: 10px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #4a4a4a;
                background-color: #3a3a3a;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4CAF50;
            }
            QFrame[frameType="card"] {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """

    def setup_ui(self):
        """
        Настройка пользовательского интерфейса.
        """
        # Главный вертикальный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ==================== ВЕРХНЯЯ ПАНЕЛЬ ====================
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel("📋 Управление услугами")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Кнопка обновления
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(header_frame)

        # ==================== ПАНЕЛЬ СТАТИСТИКИ ====================
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
            ("📊 Всего услуг", "0", "#4CAF50"),
            ("🏷️ Категорий", "0", "#FFC107"),
            ("✅ Активных", "0", "#17A2B8"),
            ("💰 Общая выручка", "0 ₽", "#28A745"),
            ("📈 Популярных", "0", "#DC3545")
        ]

        for title, value, color in stats_config:
            stat_widget = self.create_stat_widget(title, value, color)
            stats_layout.addWidget(stat_widget)
            self.stats_widgets.append(stat_widget)

        main_layout.addWidget(self.stats_frame)

        # ==================== ПАНЕЛЬ ФИЛЬТРОВ ====================
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
        self.search_input.setPlaceholderText("🔍 Поиск по названию или категории...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)

        # Фильтр по категории
        filter_layout.addWidget(QLabel("Категория:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("📁 Все категории", "")
        self.category_filter.setMinimumWidth(180)
        self.category_filter.setMinimumHeight(40)
        self.category_filter.currentIndexChanged.connect(self.on_category_filter_changed)
        filter_layout.addWidget(self.category_filter)

        # Фильтр по статусу
        filter_layout.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("📌 Все", "")
        self.status_filter.addItem("✅ Активные", "active")
        self.status_filter.addItem("❌ Неактивные", "inactive")
        self.status_filter.setMinimumWidth(140)
        self.status_filter.setMinimumHeight(40)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_filter)

        filter_layout.addStretch()

        # Кнопка сброса фильтров
        self.reset_btn = QPushButton("🔄 Сбросить")
        self.reset_btn.setMinimumHeight(40)
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)

        # Кнопка экспорта
        self.export_btn = QPushButton("📊 Экспорт")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self.export_services)
        filter_layout.addWidget(self.export_btn)

        main_layout.addWidget(filter_frame)

        # ==================== ОСНОВНАЯ ЧАСТЬ С ВКЛАДКАМИ ====================
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                background-color: #252525;
            }
        """)

        # Вкладка со списком услуг
        self.services_tab = QWidget()
        self.setup_services_tab()
        self.tab_widget.addTab(self.services_tab, "📋 Список услуг")

        # Вкладка с категориями
        self.categories_tab = QWidget()
        self.setup_categories_tab()
        self.tab_widget.addTab(self.categories_tab, "🏷️ Категории")

        # Вкладка с аналитикой
        self.analytics_tab = QWidget()
        self.setup_analytics_tab()
        self.tab_widget.addTab(self.analytics_tab, "📊 Аналитика")

        main_layout.addWidget(self.tab_widget)

        # ==================== НИЖНЯЯ ПАНЕЛЬ ====================
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
        self.add_btn = QPushButton("➕ Создать услугу")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setObjectName("successButton")
        self.add_btn.clicked.connect(self.add_service)
        bottom_layout.addWidget(self.add_btn)

        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_service)
        bottom_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.clicked.connect(self.delete_service)
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
        value_label.setObjectName("stat_value")
        layout.addWidget(value_label)

        return frame

    def setup_services_tab(self):
        """Настройка вкладки со списком услуг"""
        layout = QVBoxLayout(self.services_tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Создаем сплиттер для разделения таблицы и формы
        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizes([850, 700])

        # ----- ЛЕВАЯ ПАНЕЛЬ: ТАБЛИЦА УСЛУГ -----
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Таблица услуг
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setColumnCount(7)

        headers = ["ID", "Название услуги", "Категория", "Цена", "Время", "Использовано", "Статус"]
        for i, header in enumerate(headers):
            item = QTableWidgetItem(header)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setHorizontalHeaderItem(i, item)

        # Настройка столбцов
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnHidden(0, True)
        self.table.setColumnWidth(1, 400)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 100)

        # Контекстное меню
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Двойной клик для редактирования
        self.table.doubleClicked.connect(self.on_service_double_clicked)
        self.table.itemSelectionChanged.connect(self.on_service_selected)

        left_layout.addWidget(self.table)

        splitter.addWidget(left_panel)

        # ----- ПРАВАЯ ПАНЕЛЬ: ФОРМА РЕДАКТИРОВАНИЯ -----
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)

        # Группа информации
        info_group = QGroupBox("📝 Информация об услуге")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(12)
        info_layout.setLabelAlignment(Qt.AlignRight)

        # Название
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите полное название услуги...")
        self.name_input.setMinimumHeight(40)
        info_layout.addRow("Название *:", self.name_input)

        # Категория
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(40)
        info_layout.addRow("Категория:", self.category_combo)

        # Цена и себестоимость
        price_layout = QHBoxLayout()
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000)
        self.price_input.setPrefix("₽ ")
        self.price_input.setDecimals(2)
        self.price_input.setMinimumHeight(40)
        price_layout.addWidget(self.price_input)

        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 1000000)
        self.cost_price_input.setPrefix("₽ ")
        self.cost_price_input.setDecimals(2)
        self.cost_price_input.setMinimumHeight(40)
        price_layout.addWidget(self.cost_price_input)
        price_layout.addStretch()
        info_layout.addRow("Цена / Себестоимость:", price_layout)

        # Время и гарантия
        time_layout = QHBoxLayout()
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 1440)
        self.time_input.setSuffix(" мин")
        self.time_input.setMinimumHeight(40)
        time_layout.addWidget(self.time_input)

        self.warranty_input = QSpinBox()
        self.warranty_input.setRange(0, 3650)
        self.warranty_input.setSuffix(" дн")
        self.warranty_input.setMinimumHeight(40)
        time_layout.addWidget(self.warranty_input)
        time_layout.addStretch()
        info_layout.addRow("Время / Гарантия:", time_layout)

        # Активность
        self.active_check = QCheckBox("Услуга активна и доступна для заказов")
        self.active_check.setChecked(True)
        self.active_check.setMinimumHeight(35)
        info_layout.addRow("", self.active_check)

        right_layout.addWidget(info_group)

        # Описание
        desc_group = QGroupBox("📄 Описание услуги")
        desc_layout = QVBoxLayout(desc_group)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Введите подробное описание услуги...\n\n"
            "Пример описания:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Что входит в услугу:\n"
            "• Полная диагностика устройства\n"
            "• Замена неисправных компонентов\n"
            "• Настройка программного обеспечения\n"
            "• Тестирование после ремонта"
        )
        self.description_input.setMinimumHeight(120)
        self.description_input.setMaximumHeight(150)
        desc_layout.addWidget(self.description_input)
        right_layout.addWidget(desc_group)

        # Статистика использования
        stats_group = QGroupBox("📊 Статистика использования")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(10)

        stats_layout.addWidget(QLabel("📈 Использовано:"), 0, 0)
        self.usage_label = QLabel("0 раз")
        self.usage_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 18px;")
        stats_layout.addWidget(self.usage_label, 0, 1)

        stats_layout.addWidget(QLabel("💰 Выручка:"), 1, 0)
        self.revenue_label = QLabel("0 ₽")
        self.revenue_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 18px;")
        stats_layout.addWidget(self.revenue_label, 1, 1)

        stats_layout.addWidget(QLabel("📊 Маржинальность:"), 2, 0)
        self.margin_label = QLabel("0%")
        self.margin_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 18px;")
        stats_layout.addWidget(self.margin_label, 2, 1)

        stats_layout.addWidget(QLabel("🕐 Последнее использование:"), 3, 0)
        self.last_used_label = QLabel("Не использовалась")
        self.last_used_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        stats_layout.addWidget(self.last_used_label, 3, 1)

        right_layout.addWidget(stats_group)

        # Кнопки действий в форме
        form_buttons_layout = QHBoxLayout()
        self.clear_form_btn = QPushButton("❌ Очистить")
        self.clear_form_btn.clicked.connect(self.clear_form)
        form_buttons_layout.addWidget(self.clear_form_btn)

        form_buttons_layout.addStretch()

        right_layout.addLayout(form_buttons_layout)
        right_layout.addStretch()

        splitter.addWidget(right_panel)
        layout.addWidget(splitter)

    def setup_categories_tab(self):
        """Настройка вкладки с категориями"""
        layout = QVBoxLayout(self.categories_tab)

        # Таблица категорий
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(5)
        self.categories_table.setHorizontalHeaderLabels([
            "Категория", "Кол-во услуг", "Средняя цена", "Общая выручка", "Популярность"
        ])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.categories_table)

    def setup_analytics_tab(self):
        """Настройка вкладки с аналитикой"""
        layout = QVBoxLayout(self.analytics_tab)

        # Группа с ключевыми показателями
        metrics_group = QGroupBox("Ключевые показатели")
        metrics_layout = QGridLayout(metrics_group)

        metrics = [
            ("Средняя цена услуги:", "0 ₽", "#4CAF50"),
            ("Средняя маржинальность:", "0%", "#FFC107"),
            ("Самая популярная услуга:", "-", "#17A2B8"),
            ("Самая доходная услуга:", "-", "#28A745"),
            ("Услуг с низкой маржинальностью:", "0", "#DC3545"),
            ("Неактивных услуг:", "0", "#FF6B6B")
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
            value_widget.setObjectName("metric_value")
            container_layout.addWidget(value_widget)

            metrics_layout.addWidget(container, row, col)

        layout.addWidget(metrics_group)

        # Группа с топ услугами
        top_services_group = QGroupBox("🏆 Топ-10 популярных услуг")
        top_services_layout = QVBoxLayout(top_services_group)

        self.top_services_table = QTableWidget()
        self.top_services_table.setColumnCount(5)
        self.top_services_table.setHorizontalHeaderLabels([
            "Услуга", "Категория", "Кол-во использований", "Выручка", "Маржинальность"
        ])
        self.top_services_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        top_services_layout.addWidget(self.top_services_table)
        layout.addWidget(top_services_group)

        # Группа с динамикой
        trends_group = QGroupBox("📈 Динамика использования")
        trends_layout = QVBoxLayout(trends_group)

        self.trends_table = QTableWidget()
        self.trends_table.setColumnCount(3)
        self.trends_table.setHorizontalHeaderLabels([
            "Период", "Количество услуг", "Выручка"
        ])
        self.trends_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        trends_layout.addWidget(self.trends_table)
        layout.addWidget(trends_group)

    def show_context_menu(self, position):
        """Показывает контекстное меню для таблицы"""
        menu = QMenu()

        edit_action = QAction("✏️ Редактировать", self)
        edit_action.triggered.connect(self.edit_selected_service)
        menu.addAction(edit_action)

        details_action = QAction("📋 Подробнее", self)
        details_action.triggered.connect(self.show_selected_details)
        menu.addAction(details_action)

        menu.addSeparator()

        copy_action = QAction("📋 Копировать название", self)
        copy_action.triggered.connect(self.copy_service_name)
        menu.addAction(copy_action)

        menu.addSeparator()

        delete_action = QAction("🗑️ Удалить", self)
        delete_action.triggered.connect(self.delete_service)
        delete_action.setIcon(QIcon())
        menu.addAction(delete_action)

        menu.exec_(self.table.viewport().mapToGlobal(position))

    def edit_selected_service(self):
        """Редактирует выбранную услугу"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            service_id = self.table.item(current_row, 0).text()
            for service in self.all_services:
                if str(service.get('ServiceTypeID')) == service_id:
                    self.current_service_id = service.get('ServiceTypeID')
                    self.populate_form(service)
                    self.load_service_stats(service)
                    break
            # Переключаемся на вкладку услуг
            self.tab_widget.setCurrentIndex(0)

    def show_selected_details(self):
        """Показывает детали выбранной услуги"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            service_id = self.table.item(current_row, 0).text()
            for service in self.all_services:
                if str(service.get('ServiceTypeID')) == service_id:
                    self.show_service_details(service)
                    break

    def copy_service_name(self):
        """Копирует название услуги в буфер обмена"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            name = self.table.item(current_row, 1).text()
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(name)
            QMessageBox.information(self, "Успех", f"✅ Название скопировано в буфер обмена")

    def update_statistics(self):
        """Обновляет панель статистики"""
        try:
            total_services = len(self.all_services)
            active_services = sum(1 for s in self.all_services if s.get('IsActive', True))
            categories = set(s.get('Category', '') for s in self.all_services if s.get('Category'))
            popular_services = sum(1 for s in self.all_services if s.get('usage_count', 0) > 10)

            # Обновляем значения
            self.stats_widgets[0].findChild(QLabel, "stat_value").setText(str(total_services))
            self.stats_widgets[1].findChild(QLabel, "stat_value").setText(str(len(categories)))
            self.stats_widgets[2].findChild(QLabel, "stat_value").setText(str(active_services))
            self.stats_widgets[4].findChild(QLabel, "stat_value").setText(str(popular_services))

            # Получаем общую выручку
            total_revenue = 0
            for service in self.all_services:
                total_revenue += service.get('total_revenue', 0)
            self.stats_widgets[3].findChild(QLabel, "stat_value").setText(
                f"{total_revenue:,.2f} ₽".replace(',', ' ')
            )

        except Exception as e:
            print(f"Ошибка обновления статистики: {e}")

    def update_categories_table(self):
        """Обновляет таблицу категорий"""
        try:
            # Группируем услуги по категориям
            categories_data = {}
            for service in self.all_services:
                category = service.get('Category', 'Без категории')
                if category not in categories_data:
                    categories_data[category] = {
                        'count': 0,
                        'total_revenue': 0,
                        'total_price': 0,
                        'popularity': 0
                    }
                categories_data[category]['count'] += 1
                categories_data[category]['total_price'] += service.get('BasePrice', 0)
                categories_data[category]['total_revenue'] += service.get('total_revenue', 0)
                categories_data[category]['popularity'] += service.get('usage_count', 0)

            self.categories_table.setRowCount(len(categories_data))

            for row, (category, data) in enumerate(sorted(categories_data.items())):
                avg_price = data['total_price'] / data['count'] if data['count'] > 0 else 0
                self.categories_table.setItem(row, 0, self.create_centered_item(category))
                self.categories_table.setItem(row, 1, self.create_centered_item(str(data['count'])))
                self.categories_table.setItem(row, 2, self.create_centered_item(
                    f"{avg_price:,.2f} ₽".replace(',', ' ')
                ))
                self.categories_table.setItem(row, 3, self.create_centered_item(
                    f"{data['total_revenue']:,.2f} ₽".replace(',', ' ')
                ))

                # Популярность (процент от общего количества)
                total_usage = sum(cat['popularity'] for cat in categories_data.values())
                if total_usage > 0:
                    popularity_pct = (data['popularity'] / total_usage) * 100
                    popularity_text = f"{popularity_pct:.1f}%"
                else:
                    popularity_text = "0%"

                pop_item = self.create_centered_item(popularity_text)
                if popularity_pct > 50:
                    pop_item.setForeground(QColor(76, 175, 80))
                elif popularity_pct > 20:
                    pop_item.setForeground(QColor(255, 193, 7))
                else:
                    pop_item.setForeground(QColor(220, 53, 69))
                self.categories_table.setItem(row, 4, pop_item)

        except Exception as e:
            print(f"Ошибка обновления таблицы категорий: {e}")

    def update_analytics(self):
        """Обновляет вкладку аналитики"""
        try:
            # 1. Обновляем ключевые метрики
            active_services = [s for s in self.all_services if s.get('IsActive', True)]
            if active_services:
                avg_price = sum(s.get('BasePrice', 0) for s in active_services) / len(active_services)
                avg_margin = sum(
                    ((s.get('BasePrice', 0) - s.get('CostPrice', 0)) / s.get('BasePrice', 1) * 100)
                    for s in active_services if s.get('BasePrice', 0) > 0
                ) / len(active_services)

                # Самая популярная услуга
                most_popular = max(active_services, key=lambda s: s.get('usage_count', 0))
                most_popular_name = most_popular.get('ServiceDescription', '-')[:30]

                # Самая доходная услуга
                most_profitable = max(active_services, key=lambda s: s.get('total_revenue', 0))
                most_profitable_name = most_profitable.get('ServiceDescription', '-')[:30]

                # Услуги с низкой маржинальностью (< 20%)
                low_margin = sum(
                    1 for s in active_services
                    if s.get('BasePrice', 0) > 0 and
                    ((s.get('BasePrice', 0) - s.get('CostPrice', 0)) / s.get('BasePrice', 1) * 100) < 20
                )

                # Неактивные услуги
                inactive_services = len([s for s in self.all_services if not s.get('IsActive', True)])

                # Получаем виджеты метрик
                for widget in self.analytics_tab.findChildren(QLabel, "metric_value"):
                    text = widget.text()
                    if "Средняя цена" in widget.parent().findChild(QLabel).text():
                        widget.setText(f"{avg_price:,.2f} ₽".replace(',', ' '))
                    elif "Средняя маржинальность" in widget.parent().findChild(QLabel).text():
                        widget.setText(f"{avg_margin:.1f}%")
                    elif "Самая популярная" in widget.parent().findChild(QLabel).text():
                        widget.setText(most_popular_name)
                    elif "Самая доходная" in widget.parent().findChild(QLabel).text():
                        widget.setText(most_profitable_name)
                    elif "низкой маржинальностью" in widget.parent().findChild(QLabel).text():
                        widget.setText(str(low_margin))
                    elif "Неактивных" in widget.parent().findChild(QLabel).text():
                        widget.setText(str(inactive_services))

            # 2. Обновляем топ-10 популярных услуг
            sorted_by_usage = sorted(
                [s for s in self.all_services if s.get('usage_count', 0) > 0],
                key=lambda s: s.get('usage_count', 0),
                reverse=True
            )[:10]

            self.top_services_table.setRowCount(len(sorted_by_usage))

            for row, service in enumerate(sorted_by_usage):
                name = service.get('ServiceDescription', '')[:40]
                category = service.get('Category', '-')
                usage_count = service.get('usage_count', 0)
                revenue = service.get('total_revenue', 0)
                price = service.get('BasePrice', 0)
                cost = service.get('CostPrice', 0)
                margin = ((price - cost) / price * 100) if price > 0 else 0

                self.top_services_table.setItem(row, 0, QTableWidgetItem(name))
                self.top_services_table.setItem(row, 1, self.create_centered_item(category))
                self.top_services_table.setItem(row, 2, self.create_centered_item(str(usage_count)))
                self.top_services_table.setItem(row, 3, self.create_centered_item(
                    f"{revenue:,.2f} ₽".replace(',', ' ')
                ))

                margin_item = self.create_centered_item(f"{margin:.1f}%")
                if margin >= 50:
                    margin_item.setForeground(QColor(76, 175, 80))
                elif margin >= 20:
                    margin_item.setForeground(QColor(255, 193, 7))
                else:
                    margin_item.setForeground(QColor(220, 53, 69))
                self.top_services_table.setItem(row, 4, margin_item)

            # 3. Обновляем динамику (пример - агрегация по месяцам)
            # В реальном проекте здесь нужно получать данные из БД
            trends_data = self.get_usage_trends()
            self.trends_table.setRowCount(len(trends_data))

            for row, trend in enumerate(trends_data):
                self.trends_table.setItem(row, 0, self.create_centered_item(trend['period']))
                self.trends_table.setItem(row, 1, self.create_centered_item(str(trend['count'])))
                self.trends_table.setItem(row, 2, self.create_centered_item(
                    f"{trend['revenue']:,.2f} ₽".replace(',', ' ')
                ))

        except Exception as e:
            print(f"Ошибка обновления аналитики: {e}")

    def get_usage_trends(self):
        """Получает данные о динамике использования услуг"""
        # Здесь должна быть реальная логика получения данных из БД
        # Пока возвращаем примерные данные
        return [
            {'period': 'Январь 2024', 'count': 45, 'revenue': 125000},
            {'period': 'Февраль 2024', 'count': 52, 'revenue': 148000},
            {'period': 'Март 2024', 'count': 68, 'revenue': 189000},
            {'period': 'Апрель 2024', 'count': 71, 'revenue': 212000},
            {'period': 'Май 2024', 'count': 84, 'revenue': 245000},
            {'period': 'Июнь 2024', 'count': 92, 'revenue': 278000},
        ]

    def create_centered_item(self, text):
        """Создает ячейку с центрированным текстом"""
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def reset_filters(self):
        """
        Сбрасывает фильтры к значениям по умолчанию.
        """
        self.category_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.search_input.clear()
        self.current_category = None
        self.current_status = None
        self.search_text = ""
        self.display_services(self.all_services)

    def apply_filters(self):
        """
        Применяет все фильтры.
        """
        self.search_text = self.search_input.text().strip().lower()
        self.current_category = self.category_filter.currentData()
        status_value = self.status_filter.currentData()
        self.current_status = status_value if status_value else None

        filtered = []
        for service in self.all_services:
            # Фильтр по категории
            if self.current_category and service.get('Category') != self.current_category:
                continue

            # Фильтр по статусу
            if self.current_status:
                is_active = service.get('IsActive', True)
                if self.current_status == 'active' and not is_active:
                    continue
                if self.current_status == 'inactive' and is_active:
                    continue

            # Фильтр по поиску
            if self.search_text:
                name = service.get('ServiceDescription', '').lower()
                category = service.get('Category', '').lower()
                if self.search_text not in name and self.search_text not in category:
                    continue

            filtered.append(service)

        self.display_services(filtered)

    def export_services(self):
        """
        Экспортирует список услуг в CSV файл.
        """
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Сохранить список услуг",
            f"services_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Название", "Категория", "Цена", "Себестоимость",
                                 "Время (мин)", "Гарантия (дн)", "Активна", "Описание",
                                 "Кол-во использований", "Общая выручка"])

                for service in self.all_services:
                    row = [
                        service.get('ServiceTypeID', ''),
                        service.get('ServiceDescription', ''),
                        service.get('Category', ''),
                        service.get('BasePrice', 0),
                        service.get('CostPrice', 0),
                        service.get('EstimatedTime', 60),
                        service.get('WarrantyPeriod', 30),
                        "Да" if service.get('IsActive', True) else "Нет",
                        service.get('Description', ''),
                        service.get('usage_count', 0),
                        service.get('total_revenue', 0)
                    ]
                    writer.writerow(row)

            QMessageBox.information(self, "Успех", f"✅ Список услуг сохранен в:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"❌ Не удалось сохранить файл: {e}")

    def refresh_data(self):
        """
        Обновляет все данные.
        """
        self.load_services()

    def load_services(self):
        """
        Загружает список услуг из базы данных с дополнительной статистикой.
        """
        try:
            # Получаем базовый список услуг
            self.all_services = db_crm.get_all_service_types()

            # Загружаем статистику для каждой услуги
            for service in self.all_services:
                service_id = service.get('ServiceTypeID')
                if service_id:
                    stats = self.get_service_stats_from_db(service_id)
                    service['usage_count'] = stats.get('usage_count', 0)
                    service['total_revenue'] = stats.get('total_revenue', 0)

            self.update_category_filter()
            self.display_services(self.all_services)
            self.update_statistics()
            self.update_categories_table()
            self.update_analytics()
            self.records_label.setText(f"Записей: {len(self.all_services)}")

        except Exception as e:
            print(f"Ошибка загрузки услуг: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить услуги: {e}")

    def get_service_stats_from_db(self, service_id):
        """
        Получает статистику использования услуги из БД.
        """
        try:
            connection = db_crm.get_crm_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                try:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as usage_count,
                            COALESCE(SUM(TotalPrice), 0) as total_revenue
                        FROM OrderServices 
                        WHERE ServiceTypeID = %s
                    """, (service_id,))
                    return cursor.fetchone() or {'usage_count': 0, 'total_revenue': 0}
                finally:
                    cursor.close()
                    connection.close()
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
        return {'usage_count': 0, 'total_revenue': 0}

    def update_category_filter(self):
        """
        Обновляет список категорий в фильтре.
        """
        categories = set()
        for service in self.all_services:
            cat = service.get('Category', '')
            if cat:
                categories.add(cat)

        current_category = self.category_filter.currentData()
        self.category_filter.clear()
        self.category_filter.addItem("📁 Все категории", "")
        for cat in sorted(categories):
            self.category_filter.addItem(cat, cat)

        if current_category:
            index = self.category_filter.findData(current_category)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)

        self.category_combo.clear()
        for cat in sorted(categories):
            self.category_combo.addItem(cat)

        default_cats = ["💻 Ремонт", "🔍 Диагностика", "🔄 Восстановление", "⚙️ Настройка", "🛡️ Обслуживание"]
        for cat in default_cats:
            if cat not in categories:
                self.category_combo.addItem(cat)

    def display_services(self, services):
        """
        Отображает список услуг в таблице.
        """
        self.table.setRowCount(len(services))

        for row, service in enumerate(services):
            service_id = service.get('ServiceTypeID', '')
            name = service.get('ServiceDescription', '')
            category = service.get('Category', '')
            price = service.get('BasePrice', 0)
            time_min = service.get('EstimatedTime', 60)
            is_active = service.get('IsActive', True)
            usage_count = service.get('usage_count', 0)

            self.table.setItem(row, 0, QTableWidgetItem(str(service_id)))

            name_item = QTableWidgetItem(name)
            name_item.setToolTip(name)
            if not is_active:
                name_item.setForeground(QColor(100, 100, 100))
            self.table.setItem(row, 1, name_item)

            category_item = QTableWidgetItem(category)
            if not is_active:
                category_item.setForeground(QColor(100, 100, 100))
            self.table.setItem(row, 2, category_item)

            price_item = QTableWidgetItem(f"{price:,.2f} ₽".replace(",", " "))
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if not is_active:
                price_item.setForeground(QColor(100, 100, 100))
            self.table.setItem(row, 3, price_item)

            time_item = QTableWidgetItem(f"{time_min} мин")
            time_item.setTextAlignment(Qt.AlignCenter)
            if not is_active:
                time_item.setForeground(QColor(100, 100, 100))
            self.table.setItem(row, 4, time_item)

            usage_item = QTableWidgetItem(str(usage_count))
            usage_item.setTextAlignment(Qt.AlignCenter)
            if usage_count > 10:
                usage_item.setForeground(QColor(76, 175, 80))
            elif usage_count > 0:
                usage_item.setForeground(QColor(255, 193, 7))
            self.table.setItem(row, 5, usage_item)

            status_text = "✅ Активна" if is_active else "❌ Неактивна"
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignCenter)
            if is_active:
                status_item.setForeground(QColor(76, 175, 80))
            else:
                status_item.setForeground(QColor(220, 53, 69))
            self.table.setItem(row, 6, status_item)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(1, 400)
        self.records_label.setText(f"Записей: {len(services)}")

    def on_category_filter_changed(self, index):
        """
        Обработчик изменения фильтра по категории.
        """
        self.apply_filters()

    def on_service_selected(self):
        """
        Обработчик выбора услуги в таблице.
        """
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        service_id = self.table.item(row, 0).text()
        if not service_id:
            return

        self.current_service_id = int(service_id)

        selected_service = None
        for service in self.all_services:
            if service.get('ServiceTypeID') == self.current_service_id:
                selected_service = service
                break

        if selected_service:
            self.populate_form(selected_service)
            self.load_service_stats(selected_service)

    def on_service_double_clicked(self, row, column):
        """
        Обработка двойного клика по услуге.
        """
        service_id = self.table.item(row, 0).text()
        for service in self.all_services:
            if service.get('ServiceTypeID') == int(service_id):
                self.show_service_details(service)
                break

    def show_service_details(self, service):
        """
        Показывает детальную информацию об услуге.
        """
        is_active = "✅ Активна" if service.get('IsActive', True) else "❌ Неактивна"
        usage_count = service.get('usage_count', 0)
        total_revenue = service.get('total_revenue', 0)

        details = (
            f"<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b><br><br>"
            f"<b>📋 ИНФОРМАЦИЯ ОБ УСЛУГЕ</b><br><br>"
            f"<b>ID услуги:</b> {service.get('ServiceTypeID', '')}<br>"
            f"<b>Название:</b> {service.get('ServiceDescription', '')}<br>"
            f"<b>Категория:</b> {service.get('Category', '-')}<br><br>"
            f"<b>💰 ФИНАНСОВЫЕ ПОКАЗАТЕЛИ</b><br>"
            f"<b>Цена:</b> {service.get('BasePrice', 0):,.2f} ₽<br>"
            f"<b>Себестоимость:</b> {service.get('CostPrice', 0):,.2f} ₽<br>"
            f"<b>Маржинальность:</b> "
            f"{((service.get('BasePrice', 0) - service.get('CostPrice', 0)) / service.get('BasePrice', 1) * 100):.1f}%<br><br>"
            f"<b>⏱️ ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ</b><br>"
            f"<b>Время выполнения:</b> {service.get('EstimatedTime', 60)} мин<br>"
            f"<b>Гарантия:</b> {service.get('WarrantyPeriod', 0)} дн<br>"
            f"<b>Статус:</b> {is_active}<br><br>"
            f"<b>📊 СТАТИСТИКА ИСПОЛЬЗОВАНИЯ</b><br>"
            f"<b>Использовано раз:</b> {usage_count}<br>"
            f"<b>Общая выручка:</b> {total_revenue:,.2f} ₽<br><br>"
            f"<b>📄 ОПИСАНИЕ</b><br>{service.get('Description', '-')}<br>"
        )

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("📋 Детали услуги")
        msg_box.setText(details)
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()

    def populate_form(self, service):
        """
        Заполняет форму данными выбранной услуги.
        """
        self.name_input.setText(service.get('ServiceDescription', ''))

        category = service.get('Category', '')
        idx = self.category_combo.findText(category)
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)

        self.price_input.setValue(float(service.get('BasePrice', 0)))
        self.cost_price_input.setValue(float(service.get('CostPrice', 0)))
        self.time_input.setValue(service.get('EstimatedTime', 60))
        self.warranty_input.setValue(service.get('WarrantyPeriod', 30))
        self.description_input.setText(service.get('Description', ''))
        self.active_check.setChecked(service.get('IsActive', True))

    def load_service_stats(self, service):
        """
        Загружает статистику использования услуги.
        """
        try:
            service_id = service.get('ServiceTypeID')
            if not service_id:
                return

            usage_count = service.get('usage_count', 0)
            total_revenue = service.get('total_revenue', 0)

            self.usage_label.setText(f"{usage_count} раз")
            self.revenue_label.setText(f"{total_revenue:,.2f} ₽".replace(",", " "))

            # Получаем дату последнего использования
            connection = db_crm.get_crm_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                try:
                    cursor.execute("""
                        SELECT MAX(StartDate) as last_used
                        FROM OrderServices 
                        WHERE ServiceTypeID = %s
                    """, (service_id,))
                    result = cursor.fetchone()
                    if result and result.get('last_used'):
                        last_used = result['last_used']
                        if hasattr(last_used, 'strftime'):
                            self.last_used_label.setText(last_used.strftime("%d.%m.%Y %H:%M"))
                        else:
                            self.last_used_label.setText(str(last_used)[:16])
                    else:
                        self.last_used_label.setText("Не использовалась")
                finally:
                    cursor.close()
                    connection.close()

            price = service.get('BasePrice', 0)
            cost = service.get('CostPrice', 0)
            if price > 0:
                margin = ((price - cost) / price) * 100
                if margin >= 50:
                    color = "#4CAF50"
                elif margin >= 20:
                    color = "#FF9800"
                else:
                    color = "#f44336"
                self.margin_label.setText(f"{margin:.1f}%")
                self.margin_label.setStyleSheet(
                    f"color: {color}; font-weight: bold; font-size: 18px; padding: 5px;")
            else:
                self.margin_label.setText("0%")
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")

    def clear_form(self):
        """
        Очищает форму редактирования.
        """
        self.current_service_id = None
        self.name_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.price_input.setValue(0)
        self.cost_price_input.setValue(0)
        self.time_input.setValue(60)
        self.warranty_input.setValue(30)
        self.description_input.clear()
        self.active_check.setChecked(True)
        self.usage_label.setText("0 раз")
        self.revenue_label.setText("0 ₽")
        self.last_used_label.setText("Не использовалась")
        self.margin_label.setText("0%")
        self.table.clearSelection()

    def add_service(self):
        """
        Создает новую услугу.
        """
        self.clear_form()
        self.name_input.setFocus()

    def save_service(self):
        """
        Сохраняет услугу (создает или обновляет).
        """
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "⚠️ Введите название услуги")
            self.name_input.setFocus()
            return

        price = self.price_input.value()
        if price <= 0:
            result = QMessageBox.question(
                self,
                "Подтверждение",
                "⚠️ Цена услуги 0 ₽. Продолжить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if result != QMessageBox.Yes:
                return

        service_data = {
            'ServiceDescription': name,
            'BasePrice': price,
            'CostPrice': self.cost_price_input.value(),
            'Category': self.category_combo.currentText(),
            'EstimatedTime': self.time_input.value(),
            'WarrantyPeriod': self.warranty_input.value(),
            'Description': self.description_input.toPlainText(),
            'IsActive': self.active_check.isChecked()
        }

        try:
            if self.current_service_id:
                success = self.update_service_in_db(self.current_service_id, service_data)
                if success:
                    QMessageBox.information(self, "Успех", f"✅ Услуга «{name}» успешно обновлена")
                    self.load_services()
            else:
                new_id = self.create_service_in_db(service_data)
                if new_id:
                    QMessageBox.information(self, "Успех", f"✅ Услуга «{name}» успешно создана")
                    self.load_services()
                    self.current_service_id = new_id

        except Exception as e:
            print(f"Ошибка сохранения услуги: {e}")
            QMessageBox.critical(self, "Ошибка", f"❌ Не удалось сохранить услугу: {e}")

    def create_service_in_db(self, service_data):
        """
        Создает новую услугу в базе данных.
        """
        connection = db_crm.get_crm_connection()
        if connection is None:
            return None

        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO ServiceTypes 
                (ServiceDescription, BasePrice, CostPrice, Category, EstimatedTime, 
                 WarrantyPeriod, Description, IsActive)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                service_data['ServiceDescription'],
                service_data['BasePrice'],
                service_data.get('CostPrice', 0),
                service_data['Category'],
                service_data['EstimatedTime'],
                service_data.get('WarrantyPeriod', 30),
                service_data.get('Description', ''),
                service_data['IsActive']
            ))
            connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Ошибка создания услуги: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()

    def update_service_in_db(self, service_id, service_data):
        """
        Обновляет услугу в базе данных.
        """
        connection = db_crm.get_crm_connection()
        if connection is None:
            return False

        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE ServiceTypes SET
                    ServiceDescription = %s,
                    BasePrice = %s,
                    CostPrice = %s,
                    Category = %s,
                    EstimatedTime = %s,
                    WarrantyPeriod = %s,
                    Description = %s,
                    IsActive = %s
                WHERE ServiceTypeID = %s
            """, (
                service_data['ServiceDescription'],
                service_data['BasePrice'],
                service_data.get('CostPrice', 0),
                service_data['Category'],
                service_data['EstimatedTime'],
                service_data.get('WarrantyPeriod', 30),
                service_data.get('Description', ''),
                service_data['IsActive'],
                service_id
            ))
            connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка обновления услуги: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()

    def delete_service(self):
        """
        Удаляет выбранную услугу.
        """
        if not self.current_service_id:
            QMessageBox.warning(self, "Ошибка", "⚠️ Выберите услугу для удаления")
            return

        name = self.name_input.text().strip() or "эту услугу"

        connection = db_crm.get_crm_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM OrderServices WHERE ServiceTypeID = %s
                """, (self.current_service_id,))
                count = cursor.fetchone()[0]

                if count > 0:
                    QMessageBox.warning(
                        self,
                        "Невозможно удалить",
                        f"⚠️ Услуга «{name}» используется в {count} заказах.\n\n"
                        "Вы можете деактивировать услугу вместо удаления."
                    )
                    reply = QMessageBox.question(
                        self,
                        "Деактивировать?",
                        f"Деактивировать услугу «{name}»?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        service_data = {
                            'ServiceDescription': name,
                            'BasePrice': self.price_input.value(),
                            'CostPrice': self.cost_price_input.value(),
                            'Category': self.category_combo.currentText(),
                            'EstimatedTime': self.time_input.value(),
                            'WarrantyPeriod': self.warranty_input.value(),
                            'Description': self.description_input.toPlainText(),
                            'IsActive': False
                        }
                        self.update_service_in_db(self.current_service_id, service_data)
                        self.load_services()
                        self.clear_form()
                        QMessageBox.information(self, "Успех", f"✅ Услуга «{name}» деактивирована")
                    return
            except Exception as e:
                print(f"Ошибка проверки использования: {e}")
            finally:
                cursor.close()
                connection.close()

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"⚠️ Вы действительно хотите удалить услугу «{name}»?\n\n"
            "Это действие необратимо!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                connection = db_crm.get_crm_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM ServiceTypes WHERE ServiceTypeID = %s", (self.current_service_id,))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    self.load_services()
                    self.clear_form()
                    QMessageBox.information(self, "Успех", f"✅ Услуга «{name}» удалена")
            except Exception as e:
                print(f"Ошибка удаления услуги: {e}")
                QMessageBox.critical(self, "Ошибка", f"❌ Не удалось удалить услугу: {e}")