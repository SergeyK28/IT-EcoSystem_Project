# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QColor
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QTextEdit, QComboBox, QWidget,
                             QScrollArea, QGridLayout)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm
from Handlers.Employees.employee_session import employee_session


class ShopsDialog(QDialog):
    """Окно управления ссылками на магазины (упрощённый дизайн)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shops_data = []
        self.setup_ui()
        self.load_shops_from_db()

    def setup_ui(self):
        self.setObjectName("ShopsDialog")
        self.setWindowTitle("IT-EcoSystem CRM - Магазины")
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)

        # Простой тёмный стиль (без градиентов, теней и frameless)
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 2px;
                font-weight: bold;
                font-size: 12px;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#addBtn {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#addBtn:hover {
                background-color: #3a9a4a;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #2d7d3a;
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
            QFrame#card {
                background-color: #3a3a3a;
                border-radius: 2px;
                border: 1px solid #555;
            }
            QFrame#card:hover {
                border-color: #2d7d3a;
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
        """)

        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Верхняя панель
        header_layout = QHBoxLayout()

        title_label = QLabel("🛒 МАГАЗИНЫ")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.add_btn = QPushButton("➕ Добавить магазин")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.show_add_shop_dialog)
        header_layout.addWidget(self.add_btn)

        layout.addLayout(header_layout)

        # Панель поиска и фильтров
        filters_frame = QFrame()
        filters_frame.setStyleSheet("background-color: #333; border-radius: 2px; padding: 10px;")
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(10)

        search_icon = QLabel("🔍")
        filters_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Название магазина или категория...")
        self.search_input.textChanged.connect(self.filter_shops)
        filters_layout.addWidget(self.search_input, 1)

        category_icon = QLabel("📂")
        filters_layout.addWidget(category_icon)

        self.category_combo = QComboBox()
        self.category_combo.addItem("Все категории")
        self.category_combo.currentTextChanged.connect(self.filter_shops)
        filters_layout.addWidget(self.category_combo)

        reset_btn = QPushButton("⟲ Сброс")
        reset_btn.clicked.connect(self.reset_filters)
        filters_layout.addWidget(reset_btn)

        layout.addWidget(filters_frame)

        # Статистика
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #333; border-radius: 2px; padding: 8px 12px;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        self.total_shops_label = QLabel("0 магазинов")
        self.total_shops_label.setStyleSheet("color: #2d7d3a; font-size: 14px; font-weight: bold;")

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #555; max-width: 2px;")

        self.categories_count_label = QLabel("0 категорий")
        self.categories_count_label.setStyleSheet("color: #b0b0b0; font-size: 13px;")

        stats_layout.addWidget(self.total_shops_label)
        stats_layout.addWidget(separator)
        stats_layout.addWidget(self.categories_count_label)
        stats_layout.addStretch()

        layout.addWidget(stats_frame)

        # Карточки
        self.setup_cards_view()
        layout.addWidget(self.cards_scroll_area, 1)

    def setup_cards_view(self):
        self.cards_scroll_area = QScrollArea()
        self.cards_scroll_area.setWidgetResizable(True)
        self.cards_scroll_area.setFrameShape(QFrame.NoFrame)
        self.cards_scroll_area.setStyleSheet("border: none; background-color: transparent;")

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setAlignment(Qt.AlignTop)

        self.cards_scroll_area.setWidget(self.cards_container)

    def load_shops_from_db(self):
        try:
            self.shops_data = db_crm.get_all_shops(only_active=True)
            print(f"Загружено {len(self.shops_data)} магазинов из БД")
            self.update_categories()
            self.update_shops_display()
            self.update_statistics()
        except Exception as e:
            print(f"Ошибка загрузки магазинов из БД: {e}")
            self.shops_data = []
            self.update_shops_display()

    def update_categories(self):
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
        total = len(self.shops_data)
        categories = len(set(shop.get('category', '') for shop in self.shops_data if shop.get('category')))
        self.total_shops_label.setText(f"{total} магазин{self._plural(total)}")
        self.categories_count_label.setText(f"{categories} категори{self._category_plural(categories)}")

    def _plural(self, n):
        if n % 10 == 1 and n % 100 != 11:
            return ""
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return "а"
        return "ов"

    def _category_plural(self, n):
        if n % 10 == 1 and n % 100 != 11:
            return "я"
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return "и"
        return "й"

    def update_shops_display(self):
        filtered_data = self.get_filtered_data()
        self.update_cards_view(filtered_data)
        self.update_statistics()

    def update_cards_view(self, filtered_data):
        # Очищаем контейнер
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        cols = 3
        for i, shop in enumerate(filtered_data):
            card = self.create_shop_card(shop)
            row = i // cols
            col = i % cols
            self.cards_layout.addWidget(card, row, col)

        if not filtered_data:
            no_data_label = QLabel("✨ Магазины не найдены")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #666; font-size: 18px; padding: 50px;")
            self.cards_layout.addWidget(no_data_label, 0, 0, 1, cols)

    def create_shop_card(self, shop_data):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedSize(300, 200)
        card.setStyleSheet("""
            QFrame#card {
                background-color: #3a3a3a;
                border-radius: 2px;
                border: 1px solid #555;
            }
            QFrame#card:hover {
                border-color: #2d7d3a;
            }
            QLabel {
                color: #f0f0f0;
                background: transparent;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        icon_label = QLabel(self.get_category_icon(shop_data.get('category', '')))
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)

        name_label = QLabel(shop_data.get('name', ''))
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d7d3a;")
        name_label.setWordWrap(True)
        header_layout.addWidget(name_label, 1)

        layout.addLayout(header_layout)

        category_label = QLabel(shop_data.get('category', ''))
        category_label.setStyleSheet("background-color: #555; color: #ddd; padding: 2px 8px; border-radius: 2px; font-size: 11px;")
        category_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(category_label)

        description = shop_data.get('description', '')
        if len(description) > 80:
            description = description[:80] + "..."
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        open_btn = QPushButton("🔗 Открыть")
        open_btn.setFixedSize(90, 30)
        open_btn.setStyleSheet("background-color: #1a7a8a; color: white; border: none; border-radius: 2px; font-size: 12px;")
        open_btn.clicked.connect(lambda: self.open_url(shop_data.get('url', '')))
        buttons_layout.addWidget(open_btn)

        edit_btn = QPushButton("✏️ Ред.")
        edit_btn.setFixedSize(70, 30)
        edit_btn.setStyleSheet("background-color: #e0a800; color: #222; border: none; border-radius: 2px; font-size: 12px;")
        edit_btn.clicked.connect(lambda: self.edit_shop(shop_data))
        buttons_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ Удал.")
        delete_btn.setFixedSize(70, 30)
        delete_btn.setStyleSheet("background-color: #b33c3c; color: white; border: none; border-radius: 2px; font-size: 12px;")
        delete_btn.clicked.connect(lambda: self.delete_shop(shop_data))
        buttons_layout.addWidget(delete_btn)

        layout.addLayout(buttons_layout)

        return card

    def get_category_icon(self, category):
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
        self.update_shops_display()

    def reset_filters(self):
        self.search_input.clear()
        self.category_combo.setCurrentIndex(0)

    def open_url(self, url):
        try:
            if url:
                QDesktopServices.openUrl(QUrl(url))
            else:
                QMessageBox.warning(self, "Ошибка", "Ссылка не указана")
        except Exception as e:
            print(f"Ошибка открытия ссылки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть ссылку: {e}")

    def show_add_shop_dialog(self):
        dialog = AddEditShopDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            shop_data = dialog.get_shop_data()
            if shop_data:
                created_by = employee_session.get_employee_id()
                new_id = db_crm.create_shop(shop_data, created_by)
                if new_id:
                    self.load_shops_from_db()
                    QMessageBox.information(self, "Успех", "✅ Магазин успешно добавлен")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось добавить магазин")

    def edit_shop(self, shop):
        dialog = AddEditShopDialog(self, shop)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_shop_data()
            if new_data:
                if db_crm.update_shop(shop['id'], new_data):
                    self.load_shops_from_db()
                    QMessageBox.information(self, "Успех", "✅ Магазин успешно обновлен")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить магазин")

    def delete_shop(self, shop):
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение удаления")
        msg.setText(f"Удалить магазин '{shop.get('name')}'?")
        msg.setInformativeText("Это действие нельзя отменить")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2e2e2e;
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 2px;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton[text="&Yes"] {
                background-color: #b33c3c;
                border: none;
            }
            QPushButton[text="&No"] {
                background-color: #6c6c6c;
                border: none;
            }
        """)
        if msg.exec_() == QMessageBox.Yes:
            try:
                if db_crm.delete_shop(shop['id'], hard_delete=False):
                    self.load_shops_from_db()
                    QMessageBox.information(self, "Успех", "🗑️ Магазин удален")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить магазин")
            except Exception as e:
                print(f"Ошибка удаления: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить магазин: {e}")


class AddEditShopDialog(QDialog):
    """Диалог добавления/редактирования магазина (упрощённый)"""

    def __init__(self, parent=None, shop_data=None):
        super().__init__(parent)
        self.shop_data = shop_data
        self.setup_ui()
        if shop_data:
            self.setWindowTitle("Редактирование магазина")
            self.fill_data()
        else:
            self.setWindowTitle("Добавление магазина")

    def setup_ui(self):
        self.setFixedSize(500, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 2px;
                font-weight: bold;
                font-size: 12px;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#saveBtn {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#saveBtn:hover {
                background-color: #3a9a4a;
            }
            QPushButton#cancelBtn {
                background-color: #6c6c6c;
                border: none;
            }
            QPushButton#cancelBtn:hover {
                background-color: #7c7c7c;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #2d7d3a;
            }
            QFrame#formFrame {
                background-color: #333;
                border-radius: 2px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        header_layout = QHBoxLayout()
        title_text = "✏️ РЕДАКТИРОВАНИЕ" if self.shop_data else "➕ ДОБАВЛЕНИЕ МАГАЗИНА"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Форма
        form_frame = QFrame()
        form_frame.setObjectName("formFrame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)

        name_label = QLabel("📝 Название магазина")
        form_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название магазина")
        form_layout.addWidget(self.name_input)

        category_label = QLabel("📂 Категория")
        form_layout.addWidget(category_label)
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Например: Электроника, Маркетплейс")
        form_layout.addWidget(self.category_input)

        # Подсказки категорий
        hints_layout = QHBoxLayout()
        for cat in ["Электроника", "Маркетплейс", "Одежда", "Книги", "Продукты"]:
            hint_btn = QPushButton(cat)
            hint_btn.setFixedHeight(25)
            hint_btn.setStyleSheet("background-color: #3a3a3a; color: #b0b0b0; border: 1px solid #555; border-radius: 2px; font-size: 10px; padding: 2px 6px;")
            hint_btn.clicked.connect(lambda checked, c=cat: self.category_input.setText(c))
            hints_layout.addWidget(hint_btn)
        hints_layout.addStretch()
        form_layout.addLayout(hints_layout)

        url_label = QLabel("🔗 Ссылка на магазин")
        form_layout.addWidget(url_label)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        form_layout.addWidget(self.url_input)

        desc_label = QLabel("📝 Описание (необязательно)")
        form_layout.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Краткое описание магазина...")
        self.description_input.setMaximumHeight(80)
        form_layout.addWidget(self.description_input)

        layout.addWidget(form_frame)
        layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setMinimumHeight(35)
        self.save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

    def fill_data(self):
        if self.shop_data:
            self.name_input.setText(self.shop_data.get('name', ''))
            self.category_input.setText(self.shop_data.get('category', ''))
            self.url_input.setText(self.shop_data.get('url', ''))
            self.description_input.setText(self.shop_data.get('description', ''))

    def get_shop_data(self):
        name = self.name_input.text().strip()
        category = self.category_input.text().strip()
        url = self.url_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название магазина")
            return None
        if not category:
            QMessageBox.warning(self, "Ошибка", "Введите категорию магазина")
            return None
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите ссылку на магазин")
            return None

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        return {
            'name': name,
            'category': category,
            'url': url,
            'description': description
        }