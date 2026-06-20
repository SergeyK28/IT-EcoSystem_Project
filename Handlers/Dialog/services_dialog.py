# -*- coding: utf-8 -*-
"""
Модуль для управления услугами (упрощённый дизайн)
Аналог дизайна warehouse_dialog.py
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm


class ServicesDialog(QDialog):
    """
    Диалог управления услугами (упрощённый дизайн).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("IT-EcoSystem - Услуги")
        self.setMinimumSize(1600, 950)
        self.resize(1600, 950)
        self.setModal(False)

        self.current_service_id = None
        self.all_services = []
        self.current_category = None
        self.current_status = None
        self.search_text = ""
        self.categories = []

        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                 "Pictures", "Screenshot from 2025-09-15 14-30-16.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setup_ui()
        self.load_services()
        self.setStyleSheet(self.get_simple_style())

    def get_simple_style(self):
        """Возвращает простой тёмный стиль (без излишеств)"""
        return """
            QDialog {
                background-color: #2e2e2e;
            }
            QGroupBox {
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 3px;
                margin-top: 8px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #f0f0f0;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#successButton {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#successButton:hover {
                background-color: #3a9a4a;
            }
            QPushButton#dangerButton {
                background-color: #b33c3c;
                border: none;
            }
            QPushButton#dangerButton:hover {
                background-color: #cc4c4c;
            }
            QPushButton#warningButton {
                background-color: #d48c00;
                border: none;
            }
            QPushButton#warningButton:hover {
                background-color: #e8a000;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
            QTextEdit:focus, QDateEdit:focus {
                border-color: #2d7d3a;
            }
            QTextEdit {
                padding: 4px;
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
                alternate-background-color: #404040;
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
                padding: 6px;
                border: 1px solid #555;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #2a2a2a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #ddd;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #2d7d3a;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #4a4a4a;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 2px;
                text-align: center;
                color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #2d7d3a;
                border-radius: 2px;
            }
            QCheckBox {
                color: #f0f0f0;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 2px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #555;
                background-color: #3a3a3a;
            }
            QCheckBox::indicator:checked {
                background-color: #2d7d3a;
                border: 2px solid #2d7d3a;
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
            QFrame[frameType="card"] {
                background-color: #2a2a2a;
                border-radius: 3px;
                padding: 10px;
            }
        """

    def setup_ui(self):
        """Настройка пользовательского интерфейса (упрощённый)"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # ===== Верхняя панель =====
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #333; border-radius: 3px; padding: 8px;")
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel("📋 Управление услугами")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(header_frame)

        # ===== Статистика =====
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("background-color: #333; border-radius: 3px; padding: 10px;")
        stats_layout = QHBoxLayout(self.stats_frame)

        self.stats_widgets = []
        stats_config = [
            ("📊 Всего услуг", "0", "#2d7d3a"),
            ("🏷️ Категорий", "0", "#e0a800"),
            ("✅ Активных", "0", "#1a7a8a"),
            ("💰 Общая выручка", "0 ₽", "#28a745"),
            ("📈 Популярных", "0", "#dc3545")
        ]

        for title, value, color in stats_config:
            stat_widget = self.create_stat_widget(title, value, color)
            stats_layout.addWidget(stat_widget)
            self.stats_widgets.append(stat_widget)

        main_layout.addWidget(self.stats_frame)

        # ===== Фильтры =====
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #333; border-radius: 3px; padding: 10px;")
        filter_layout = QHBoxLayout(filter_frame)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по названию или категории...")
        self.search_input.setMinimumWidth(250)
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("Категория:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("📁 Все категории", "")
        self.category_filter.setMinimumWidth(160)
        self.category_filter.currentIndexChanged.connect(self.on_category_filter_changed)
        filter_layout.addWidget(self.category_filter)

        filter_layout.addWidget(QLabel("Статус:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("📌 Все", "")
        self.status_filter.addItem("✅ Активные", "active")
        self.status_filter.addItem("❌ Неактивные", "inactive")
        self.status_filter.setMinimumWidth(120)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.status_filter)

        filter_layout.addStretch()

        self.reset_btn = QPushButton("🔄 Сбросить")
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)

        self.export_btn = QPushButton("📊 Экспорт")
        self.export_btn.clicked.connect(self.export_services)
        filter_layout.addWidget(self.export_btn)

        main_layout.addWidget(filter_frame)

        # ===== Вкладки =====
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: 1px solid #555; border-radius: 3px; background-color: #2a2a2a; }")

        self.services_tab = QWidget()
        self.setup_services_tab()
        self.tab_widget.addTab(self.services_tab, "📋 Список услуг")

        self.categories_tab = QWidget()
        self.setup_categories_tab()
        self.tab_widget.addTab(self.categories_tab, "🏷️ Категории")

        self.analytics_tab = QWidget()
        self.setup_analytics_tab()
        self.tab_widget.addTab(self.analytics_tab, "📊 Аналитика")

        main_layout.addWidget(self.tab_widget)

        # ===== Нижняя панель =====
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("background-color: #333; border-radius: 3px; padding: 8px;")
        bottom_layout = QHBoxLayout(bottom_frame)

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

        self.records_label = QLabel("Записей: 0")
        self.records_label.setStyleSheet("color: #b0b0b0;")
        bottom_layout.addWidget(self.records_label)

        main_layout.addWidget(bottom_frame)

    def create_stat_widget(self, title, value, color):
        """Создаёт виджет статистики"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #3a3a3a;
                border-radius: 3px;
                padding: 6px 10px;
                border-left: 3px solid {color};
            }}
        """)
        layout = QVBoxLayout(frame)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        value_label.setObjectName("stat_value")
        layout.addWidget(value_label)

        return frame

    def setup_services_tab(self):
        """Настройка вкладки со списком услуг"""
        layout = QVBoxLayout(self.services_tab)
        layout.setContentsMargins(5, 5, 5, 5)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizes([850, 700])

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

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

        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnHidden(0, True)
        self.table.setColumnWidth(1, 400)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 100)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.on_service_double_clicked)
        self.table.itemSelectionChanged.connect(self.on_service_selected)

        left_layout.addWidget(self.table)
        splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)

        info_group = QGroupBox("📝 Информация об услуге")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите полное название услуги...")
        info_layout.addRow("Название *:", self.name_input)

        self.category_combo = QComboBox()
        info_layout.addRow("Категория:", self.category_combo)

        price_layout = QHBoxLayout()
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000)
        self.price_input.setPrefix("₽ ")
        self.price_input.setDecimals(2)
        price_layout.addWidget(self.price_input)

        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 1000000)
        self.cost_price_input.setPrefix("₽ ")
        self.cost_price_input.setDecimals(2)
        price_layout.addWidget(self.cost_price_input)
        price_layout.addStretch()
        info_layout.addRow("Цена / Себестоимость:", price_layout)

        time_layout = QHBoxLayout()
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 1440)
        self.time_input.setSuffix(" мин")
        time_layout.addWidget(self.time_input)

        self.warranty_input = QSpinBox()
        self.warranty_input.setRange(0, 3650)
        self.warranty_input.setSuffix(" дн")
        time_layout.addWidget(self.warranty_input)
        time_layout.addStretch()
        info_layout.addRow("Время / Гарантия:", time_layout)

        self.active_check = QCheckBox("Услуга активна и доступна для заказов")
        self.active_check.setChecked(True)
        info_layout.addRow("", self.active_check)

        right_layout.addWidget(info_group)

        desc_group = QGroupBox("📄 Описание услуги")
        desc_layout = QVBoxLayout(desc_group)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Введите подробное описание услуги..."
        )
        self.description_input.setMinimumHeight(100)
        self.description_input.setMaximumHeight(120)
        desc_layout.addWidget(self.description_input)
        right_layout.addWidget(desc_group)

        stats_group = QGroupBox("📊 Статистика использования")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(8)

        stats_layout.addWidget(QLabel("📈 Использовано:"), 0, 0)
        self.usage_label = QLabel("0 раз")
        self.usage_label.setStyleSheet("color: #2d7d3a; font-weight: bold; font-size: 16px;")
        stats_layout.addWidget(self.usage_label, 0, 1)

        stats_layout.addWidget(QLabel("💰 Выручка:"), 1, 0)
        self.revenue_label = QLabel("0 ₽")
        self.revenue_label.setStyleSheet("color: #e0a800; font-weight: bold; font-size: 16px;")
        stats_layout.addWidget(self.revenue_label, 1, 1)

        stats_layout.addWidget(QLabel("📊 Маржинальность:"), 2, 0)
        self.margin_label = QLabel("0%")
        self.margin_label.setStyleSheet("color: #1a7a8a; font-weight: bold; font-size: 16px;")
        stats_layout.addWidget(self.margin_label, 2, 1)

        stats_layout.addWidget(QLabel("🕐 Последнее использование:"), 3, 0)
        self.last_used_label = QLabel("Не использовалась")
        self.last_used_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        stats_layout.addWidget(self.last_used_label, 3, 1)

        right_layout.addWidget(stats_group)

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
        layout = QVBoxLayout(self.categories_tab)
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(5)
        self.categories_table.setHorizontalHeaderLabels([
            "Категория", "Кол-во услуг", "Средняя цена", "Общая выручка", "Популярность"
        ])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.categories_table)

    def setup_analytics_tab(self):
        layout = QVBoxLayout(self.analytics_tab)

        metrics_group = QGroupBox("Ключевые показатели")
        metrics_layout = QGridLayout(metrics_group)

        metrics = [
            ("Средняя цена услуги:", "0 ₽", "#2d7d3a"),
            ("Средняя маржинальность:", "0%", "#e0a800"),
            ("Самая популярная услуга:", "-", "#1a7a8a"),
            ("Самая доходная услуга:", "-", "#28a745"),
            ("Услуг с низкой маржинальностью:", "0", "#dc3545"),
            ("Неактивных услуг:", "0", "#ff6b6b")
        ]

        for i, (label, value, color) in enumerate(metrics):
            row = i // 2
            col = i % 2

            container = QFrame()
            container.setStyleSheet(f"""
                QFrame {{
                    background-color: #3a3a3a;
                    border-radius: 3px;
                    padding: 8px;
                    border-left: 3px solid {color};
                }}
            """)
            container_layout = QVBoxLayout(container)

            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #b0b0b0; font-size: 11px;")
            container_layout.addWidget(label_widget)

            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
            value_widget.setObjectName("metric_value")
            container_layout.addWidget(value_widget)

            metrics_layout.addWidget(container, row, col)

        layout.addWidget(metrics_group)

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

    # ----- Вспомогательные методы (без изменений) -----
    def show_context_menu(self, position):
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
        menu.addAction(delete_action)
        menu.exec_(self.table.viewport().mapToGlobal(position))

    def edit_selected_service(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            service_id = self.table.item(current_row, 0).text()
            for service in self.all_services:
                if str(service.get('ServiceTypeID')) == service_id:
                    self.current_service_id = service.get('ServiceTypeID')
                    self.populate_form(service)
                    self.load_service_stats(service)
                    break
            self.tab_widget.setCurrentIndex(0)

    def show_selected_details(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            service_id = self.table.item(current_row, 0).text()
            for service in self.all_services:
                if str(service.get('ServiceTypeID')) == service_id:
                    self.show_service_details(service)
                    break

    def copy_service_name(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            name = self.table.item(current_row, 1).text()
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(name)
            QMessageBox.information(self, "Успех", f"✅ Название скопировано в буфер обмена")

    def update_statistics(self):
        try:
            total_services = len(self.all_services)
            active_services = sum(1 for s in self.all_services if s.get('IsActive', True))
            categories = set(s.get('Category', '') for s in self.all_services if s.get('Category'))
            popular_services = sum(1 for s in self.all_services if s.get('usage_count', 0) > 10)

            self.stats_widgets[0].findChild(QLabel, "stat_value").setText(str(total_services))
            self.stats_widgets[1].findChild(QLabel, "stat_value").setText(str(len(categories)))
            self.stats_widgets[2].findChild(QLabel, "stat_value").setText(str(active_services))
            self.stats_widgets[4].findChild(QLabel, "stat_value").setText(str(popular_services))

            total_revenue = sum(s.get('total_revenue', 0) for s in self.all_services)
            self.stats_widgets[3].findChild(QLabel, "stat_value").setText(
                f"{total_revenue:,.2f} ₽".replace(',', ' ')
            )
        except Exception as e:
            print(f"Ошибка обновления статистики: {e}")

    def update_categories_table(self):
        try:
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
            total_usage = sum(cat['popularity'] for cat in categories_data.values())

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
        try:
            active_services = [s for s in self.all_services if s.get('IsActive', True)]
            if active_services:
                avg_price = sum(s.get('BasePrice', 0) for s in active_services) / len(active_services)
                avg_margin = sum(
                    ((s.get('BasePrice', 0) - s.get('CostPrice', 0)) / s.get('BasePrice', 1) * 100)
                    for s in active_services if s.get('BasePrice', 0) > 0
                ) / len(active_services)

                most_popular = max(active_services, key=lambda s: s.get('usage_count', 0))
                most_popular_name = most_popular.get('ServiceDescription', '-')[:30]
                most_profitable = max(active_services, key=lambda s: s.get('total_revenue', 0))
                most_profitable_name = most_profitable.get('ServiceDescription', '-')[:30]

                low_margin = sum(
                    1 for s in active_services
                    if s.get('BasePrice', 0) > 0 and
                    ((s.get('BasePrice', 0) - s.get('CostPrice', 0)) / s.get('BasePrice', 1) * 100) < 20
                )
                inactive_services = len([s for s in self.all_services if not s.get('IsActive', True)])

                for widget in self.analytics_tab.findChildren(QLabel, "metric_value"):
                    text = widget.parent().findChild(QLabel).text()
                    if "Средняя цена" in text:
                        widget.setText(f"{avg_price:,.2f} ₽".replace(',', ' '))
                    elif "Средняя маржинальность" in text:
                        widget.setText(f"{avg_margin:.1f}%")
                    elif "Самая популярная" in text:
                        widget.setText(most_popular_name)
                    elif "Самая доходная" in text:
                        widget.setText(most_profitable_name)
                    elif "низкой маржинальностью" in text:
                        widget.setText(str(low_margin))
                    elif "Неактивных" in text:
                        widget.setText(str(inactive_services))

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
        return [
            {'period': 'Январь 2024', 'count': 45, 'revenue': 125000},
            {'period': 'Февраль 2024', 'count': 52, 'revenue': 148000},
            {'period': 'Март 2024', 'count': 68, 'revenue': 189000},
            {'period': 'Апрель 2024', 'count': 71, 'revenue': 212000},
            {'period': 'Май 2024', 'count': 84, 'revenue': 245000},
            {'period': 'Июнь 2024', 'count': 92, 'revenue': 278000},
        ]

    def create_centered_item(self, text):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def reset_filters(self):
        self.category_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.search_input.clear()
        self.current_category = None
        self.current_status = None
        self.search_text = ""
        self.display_services(self.all_services)

    def apply_filters(self):
        self.search_text = self.search_input.text().strip().lower()
        self.current_category = self.category_filter.currentData()
        status_value = self.status_filter.currentData()
        self.current_status = status_value if status_value else None

        filtered = []
        for service in self.all_services:
            if self.current_category and service.get('Category') != self.current_category:
                continue
            if self.current_status:
                is_active = service.get('IsActive', True)
                if self.current_status == 'active' and not is_active:
                    continue
                if self.current_status == 'inactive' and is_active:
                    continue
            if self.search_text:
                name = service.get('ServiceDescription', '').lower()
                category = service.get('Category', '').lower()
                if self.search_text not in name and self.search_text not in category:
                    continue
            filtered.append(service)

        self.display_services(filtered)

    def export_services(self):
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
                    writer.writerow([
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
                    ])
            QMessageBox.information(self, "Успех", f"✅ Список услуг сохранен в:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"❌ Не удалось сохранить файл: {e}")

    def refresh_data(self):
        self.load_services()

    def load_services(self):
        try:
            self.all_services = db_crm.get_all_service_types()
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
        self.apply_filters()

    def on_service_selected(self):
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
        service_id = self.table.item(row, 0).text()
        for service in self.all_services:
            if service.get('ServiceTypeID') == int(service_id):
                self.show_service_details(service)
                break

    def show_service_details(self, service):
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
        try:
            service_id = service.get('ServiceTypeID')
            if not service_id:
                return

            usage_count = service.get('usage_count', 0)
            total_revenue = service.get('total_revenue', 0)

            self.usage_label.setText(f"{usage_count} раз")
            self.revenue_label.setText(f"{total_revenue:,.2f} ₽".replace(",", " "))

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
                    color = "#2d7d3a"
                elif margin >= 20:
                    color = "#e0a800"
                else:
                    color = "#dc3545"
                self.margin_label.setText(f"{margin:.1f}%")
                self.margin_label.setStyleSheet(
                    f"color: {color}; font-weight: bold; font-size: 16px; padding: 2px;")
            else:
                self.margin_label.setText("0%")
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")

    def clear_form(self):
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
        self.clear_form()
        self.name_input.setFocus()

    def save_service(self):
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