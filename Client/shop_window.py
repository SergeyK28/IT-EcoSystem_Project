# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QColor, QPalette
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox, QDialog, QStackedWidget
from session_manager import session
from authorization_window import AuthDialog
from Server import db_crm  # Добавляем импорт для работы с БД


class ShopWindow(QDialog):
    def __init__(self, parent=None):
        super(ShopWindow, self).__init__(parent)
        self.setupUi(self)

        # Словарь для хранения цен в зависимости от комбинаций
        self.price_matrix = self.init_price_matrix()

        # Текущая цена
        self.current_price = 0

        # Для хранения данных заказа при повторной попытке после авторизации
        self.pending_order_item = None

    def init_price_matrix(self):
        """Инициализация матрицы цен (Тип устройства x Бренд x Причина)"""
        return {
            ("Смартфон", "Apple", "Разбитый экран"): 3500,
            ("Смартфон", "Samsung", "Разбитый экран"): 2800,
            ("Смартфон", "Xiaomi", "Разбитый экран"): 2000,
            ("Смартфон", "Huawei", "Разбитый экран"): 2200,
            ("Смартфон", "Honor", "Разбитый экран"): 2000,
            ("Смартфон", "Google", "Разбитый экран"): 3000,
            ("Смартфон", "OnePlus", "Разбитый экран"): 2500,
            ("Смартфон", "Sony", "Разбитый экран"): 2700,
            ("Смартфон", "Nokia", "Разбитый экран"): 1000,
            ("Смартфон", "Realme", "Разбитый экран"): 1800,

            ("Смартфон", "Apple", "Не включается"): 2500,
            ("Смартфон", "Samsung", "Не включается"): 2000,
            ("Смартфон", "Xiaomi", "Не включается"): 1500,
            ("Смартфон", "Nokia", "Не включается"): 800,

            ("Смартфон", "Apple", "Не заряжается"): 2000,
            ("Смартфон", "Samsung", "Не заряжается"): 1500,
            ("Смартфон", "Xiaomi", "Не заряжается"): 1200,
            ("Смартфон", "Nokia", "Не заряжается"): 700,

            ("Смартфон", "Apple", "Попала вода"): 4000,
            ("Смартфон", "Samsung", "Попала вода"): 3500,
            ("Смартфон", "Xiaomi", "Попала вода"): 2800,
            ("Смартфон", "Nokia", "Попала вода"): 1500,

            ("Ноутбук", "Apple", "Разбитый экран"): 15000,
            ("Ноутбук", "Lenovo", "Разбитый экран"): 8000,
            ("Ноутбук", "HP", "Разбитый экран"): 7000,
            ("Ноутбук", "Dell", "Разбитый экран"): 7500,
            ("Ноутбук", "Asus", "Разбитый экран"): 6500,
            ("Ноутбук", "Acer", "Разбитый экран"): 6000,
            ("Ноутбук", "MSI", "Разбитый экран"): 9000,

            ("Ноутбук", "Apple", "Не включается"): 5000,
            ("Ноутбук", "Lenovo", "Не включается"): 3500,
            ("Ноутбук", "HP", "Не включается"): 3000,

            ("Планшет", "Apple", "Разбитый экран"): 8000,
            ("Планшет", "Samsung", "Разбитый экран"): 6000,
            ("Планшет", "Lenovo", "Разбитый экран"): 4000,
            ("Планшет", "Xiaomi", "Разбитый экран"): 4500,

            ("Планшет", "Apple", "Не заряжается"): 3000,
            ("Планшет", "Samsung", "Не заряжается"): 2500,
        }

    def setupUi(self, Dialog):
        self.Dialog = Dialog
        Dialog.setObjectName("ShopWindow")
        Dialog.resize(1000, 1000)
        Dialog.setWindowTitle("IT-EcoSystem - Подбор услуги")

        Dialog.setWindowFlags(Dialog.windowFlags() | Qt.WindowMaximizeButtonHint)
        Dialog.setSizeGripEnabled(True)  # Добавляет "ручку" для изменения размера в правом нижнем углу

        # Устанавливаем минимальный размер окна
        Dialog.setMinimumSize(800, 600)

        # Устанавливаем иконку
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Pictures/Screenshot from 2025-09-15 14-30-16.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)

        # Градиентный фон
        Dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #232323, stop:1 #1a1a1a);
            }
        """)

        self.main_layout = QtWidgets.QVBoxLayout(Dialog)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # Заголовок
        self.create_header()

        # Создаем стек виджетов
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: transparent;
            }
        """)

        # Страница 1: Выбор параметров
        self.page_selection = QtWidgets.QWidget()
        self.create_selection_page()
        self.stacked_widget.addWidget(self.page_selection)

        # Страница 2: Итоговая стоимость
        self.page_result = QtWidgets.QWidget()
        self.create_result_page()
        self.stacked_widget.addWidget(self.page_result)

        self.main_layout.addWidget(self.stacked_widget)

        # Кнопки действий
        self.create_buttons()

    def create_header(self):
        """Создание заголовка окна"""
        header_frame = QtWidgets.QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        header_frame.setGraphicsEffect(shadow)

        header_layout = QtWidgets.QHBoxLayout(header_frame)

        title = QtWidgets.QLabel("🛒 Подбор услуги по ремонту")
        title.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 24px;
                font-weight: bold;
            }
        """)

        self.close_btn = QtWidgets.QPushButton("✕")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4CAF50;
            }
        """)
        self.close_btn.clicked.connect(self.Dialog.close)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)

        self.main_layout.addWidget(header_frame)

    def create_selection_page(self):
        """Создание страницы выбора параметров"""
        layout = QtWidgets.QVBoxLayout(self.page_selection)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Стиль для всех комбобоксов и полей
        style_input = """
            QComboBox, QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                min-width: 250px;
            }
            QComboBox:hover, QLineEdit:hover {
                background-color: #404040;
                border: 2px solid #4CAF50;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #b0b0b0;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: white;
                selection-background-color: #4CAF50;
                border: 1px solid #4a4a4a;
            }
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 5px;
            }
        """

        # ===== ТИП УСТРОЙСТВА =====
        type_layout = QtWidgets.QHBoxLayout()
        type_label = QtWidgets.QLabel("📱 Тип устройства:")
        type_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; min-width: 150px;")

        self.device_type = QtWidgets.QComboBox()
        self.device_type.addItems([
            "Смартфон", "Ноутбук", "Планшет", "Электронная книга",
            "Фотоаппарат", "Телевизор", "Игровая приставка", "Проектор",
            "Пылесос", "Кофемашина", "Вентилятор", "Видеонаблюдение",
            "Видеоняня", "Видеорегистратор", "Сабвуфер", "Колонки", "Усилитель"
        ])
        self.device_type.setStyleSheet(style_input)
        self.device_type.currentTextChanged.connect(self.update_brands)

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.device_type)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # ===== БРЕНД =====
        brand_layout = QtWidgets.QHBoxLayout()
        brand_label = QtWidgets.QLabel("🏷️ Бренд:")
        brand_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; min-width: 150px;")

        self.device_brand = QtWidgets.QComboBox()
        self.device_brand.setStyleSheet(style_input)
        self.device_brand.currentTextChanged.connect(self.update_models)

        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.device_brand)
        brand_layout.addStretch()
        layout.addLayout(brand_layout)

        # ===== МОДЕЛЬ =====
        model_layout = QtWidgets.QHBoxLayout()
        model_label = QtWidgets.QLabel("📟 Модель:")
        model_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; min-width: 150px;")

        self.device_model = QtWidgets.QComboBox()
        self.device_model.setEditable(True)
        self.device_model.setStyleSheet(style_input)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.device_model)
        model_layout.addStretch()
        layout.addLayout(model_layout)

        # ===== ПРИЧИНА ОБРАЩЕНИЯ =====
        reason_layout = QtWidgets.QHBoxLayout()
        reason_label = QtWidgets.QLabel("⚠️ Причина обращения:")
        reason_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; min-width: 150px;")

        self.reason = QtWidgets.QComboBox()
        self.reason.addItems([
            "Разбитый экран", "Не включается", "Не заряжается", "Залипают клавиши",
            "Не работает динамик", "Не работает камера", "Перегревается", "Медленно работает",
            "Попала вода", "Не работает звук", "Проблемы с Wi-Fi", "Не работает кнопка",
            "Не работает тачскрин", "Села батарея", "Проблемы с микрофоном",
            "Не видит SIM-карту", "Глючит система", "Не работает Bluetooth",
            "Треснул корпус", "Не работает разъем", "Другая причина"
        ])
        self.reason.setStyleSheet(style_input)
        self.reason.currentTextChanged.connect(self.calculate_price)

        reason_layout.addWidget(reason_label)
        reason_layout.addWidget(self.reason)
        reason_layout.addStretch()
        layout.addLayout(reason_layout)

        # ===== ИНФОРМАЦИЯ О ЦЕНЕ (ТОЛЬКО ДЛЯ ПРОСМОТРА) =====
        price_info_layout = QtWidgets.QHBoxLayout()
        price_info_label = QtWidgets.QLabel("💰 Стоимость услуги:")
        price_info_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; min-width: 150px;")

        self.price_display = QtWidgets.QLabel("—")
        self.price_display.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 24px;
                font-weight: bold;
                background-color: #3a3a3a;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 200px;
            }
        """)

        price_info_layout.addWidget(price_info_label)
        price_info_layout.addWidget(self.price_display)
        price_info_layout.addStretch()
        layout.addLayout(price_info_layout)

        # Информационная карточка
        info_frame = QtWidgets.QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2a2a2a, stop:1 #323232);
                border-radius: 10px;
                padding: 20px;
                margin-top: 30px;
            }
        """)

        info_layout = QtWidgets.QVBoxLayout(info_frame)

        info_title = QtWidgets.QLabel("Информация о ценах!")
        info_title.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold;")

        info_text = QtWidgets.QLabel(
            "• Стоимость ремонта зависит от типа устройства, бренда и причины обращения\n"
            "• Цены фиксированы для каждой комбинации параметров\n"
            "• Например: ремонт экрана Nokia может стоить от 1000₽, а Apple — от 3500₽\n"
            "• Точная стоимость будет рассчитана после диагностики от специалиста"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
                line-height: 1.6;
            }
        """)

        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)

        layout.addWidget(info_frame)
        layout.addStretch()

    def create_result_page(self):
        """Создание страницы с итоговой стоимостью"""
        layout = QtWidgets.QVBoxLayout(self.page_result)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        result_frame = QtWidgets.QFrame()
        result_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #323232);
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 10)
        result_frame.setGraphicsEffect(shadow)

        result_layout = QtWidgets.QVBoxLayout(result_frame)
        result_layout.setSpacing(20)

        # Иконка успеха
        success_icon = QtWidgets.QLabel("✅")
        success_icon.setStyleSheet("font-size: 64px;")
        success_icon.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(success_icon)

        # Заголовок
        result_title = QtWidgets.QLabel("Стоимость услуги рассчитана!")
        result_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        result_title.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(result_title)

        # Выбранные параметры
        self.result_params = QtWidgets.QLabel()
        self.result_params.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 18px;
                padding: 20px;
                background-color: #3a3a3a;
                border-radius: 10px;
            }
        """)
        self.result_params.setAlignment(Qt.AlignCenter)
        self.result_params.setWordWrap(True)
        result_layout.addWidget(self.result_params)

        # Разделитель
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setStyleSheet("background-color: #4a4a4a; max-height: 2px;")
        result_layout.addWidget(separator)

        # Итоговая стоимость
        self.result_price = QtWidgets.QLabel()
        self.result_price.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        self.result_price.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.result_price)

        layout.addWidget(result_frame)

        # Кнопки навигации
        nav_layout = QtWidgets.QHBoxLayout()
        nav_layout.setAlignment(Qt.AlignCenter)
        nav_layout.setSpacing(20)

        self.back_btn = QtWidgets.QPushButton("◀ Назад к выбору")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        nav_layout.addWidget(self.back_btn)
        layout.addLayout(nav_layout)

    def create_buttons(self):
        """Создание кнопок действий"""
        buttons_frame = QtWidgets.QFrame()
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)

        buttons_layout = QtWidgets.QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(15)

        button_style = """
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """

        self.calculate_btn = QtWidgets.QPushButton("🧮 Рассчитать стоимость")
        self.calculate_btn.setStyleSheet(button_style.replace("#3a3a3a", "#4CAF50").replace("#4a4a4a", "#45a049"))
        self.calculate_btn.clicked.connect(self.show_result)

        self.add_to_cart_btn = QtWidgets.QPushButton("🛒 В корзину")
        self.add_to_cart_btn.setStyleSheet(button_style)
        self.add_to_cart_btn.clicked.connect(self.add_to_cart)

        self.clear_btn = QtWidgets.QPushButton("🔄 Сбросить")
        self.clear_btn.setStyleSheet(button_style)
        self.clear_btn.clicked.connect(self.clear_form)

        buttons_layout.addWidget(self.calculate_btn)
        buttons_layout.addWidget(self.add_to_cart_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()

        self.main_layout.addWidget(buttons_frame)

    def update_brands(self):
        """Обновление списка брендов в зависимости от типа устройства"""
        self.device_brand.clear()
        device_type = self.device_type.currentText()

        brands = {
            "Смартфон": ["Apple", "Samsung", "Xiaomi", "Huawei", "Honor", "Google", "OnePlus", "Sony", "Nokia",
                         "Realme"],
            "Ноутбук": ["Apple", "Lenovo", "HP", "Dell", "Asus", "Acer", "MSI", "Samsung", "Xiaomi", "Huawei"],
            "Планшет": ["Apple", "Samsung", "Lenovo", "Xiaomi", "Huawei", "Amazon", "Microsoft"],
            "Телевизор": ["Samsung", "LG", "Sony", "Panasonic", "Philips", "Xiaomi", "TCL", "Hisense"],
            "Фотоаппарат": ["Canon", "Nikon", "Sony", "Fujifilm", "Panasonic", "Olympus", "Leica"],
            "Игровая приставка": ["Sony", "Microsoft", "Nintendo", "Sega"],
            "Пылесос": ["Dyson", "Xiaomi", "Samsung", "LG", "Bosch", "Philips"],
            "Кофемашина": ["DeLonghi", "Jura", "Saeco", "Philips", "Nespresso", "Bosch"],
            "Колонки": ["JBL", "Sony", "Marshall", "Harman Kardon", "Bang & Olufsen", "Xiaomi"]
        }

        default_brands = ["Samsung", "LG", "Sony", "Panasonic", "Philips", "Bosch", "Xiaomi", "Apple"]

        self.device_brand.addItems(brands.get(device_type, default_brands))
        self.calculate_price()

    def update_models(self):
        """Обновление списка моделей в зависимости от бренда"""
        self.device_model.clear()
        brand = self.device_brand.currentText()

        if brand == "Apple":
            if self.device_type.currentText() == "Смартфон":
                self.device_model.addItems(
                    ["iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14", "iPhone 13 Pro Max", "iPhone 13", "iPhone SE"])
            elif self.device_type.currentText() == "Ноутбук":
                self.device_model.addItems(["MacBook Pro 16", "MacBook Pro 14", "MacBook Air M2", "MacBook Air M1"])
            elif self.device_type.currentText() == "Планшет":
                self.device_model.addItems(["iPad Pro 12.9", "iPad Pro 11", "iPad Air", "iPad", "iPad mini"])
        elif brand == "Samsung":
            if self.device_type.currentText() == "Смартфон":
                self.device_model.addItems(
                    ["Galaxy S23 Ultra", "Galaxy S23+", "Galaxy S23", "Galaxy Z Fold5", "Galaxy Z Flip5", "Galaxy A54"])
            elif self.device_type.currentText() == "Ноутбук":
                self.device_model.addItems(["Galaxy Book3 Ultra", "Galaxy Book3 Pro", "Galaxy Book3 360"])
            elif self.device_type.currentText() == "Телевизор":
                self.device_model.addItems(["Neo QLED 8K", "Neo QLED 4K", "OLED", "Crystal UHD", "The Frame"])
        elif brand == "Nokia" and self.device_type.currentText() == "Смартфон":
            self.device_model.addItems(["Nokia G60", "Nokia X30", "Nokia G21", "Nokia C32", "Nokia 3310"])
        else:
            self.device_model.addItems(["Модель 1", "Модель 2", "Модель 3", "Модель 4", "Другая модель"])

        self.calculate_price()

    def calculate_price(self):
        """Расчет стоимости на основе матрицы цен"""
        device = self.device_type.currentText()
        brand = self.device_brand.currentText()
        reason = self.reason.currentText()

        # Пытаемся найти точное совпадение в матрице
        price = self.price_matrix.get((device, brand, reason))

        # Если точного совпадения нет, ищем похожее
        if price is None:
            # Пробуем найти по бренду и причине для любого типа устройства
            for (d, b, r), p in self.price_matrix.items():
                if b == brand and r == reason:
                    price = p
                    break

            # Если все еще не нашли, используем базовые цены
            if price is None:
                base_prices = {
                    "Разбитый экран": 2000,
                    "Не включается": 1500,
                    "Не заряжается": 1200,
                    "Попала вода": 2500,
                }
                price = base_prices.get(reason, 1500)

                # Корректировка по бренду
                if brand in ["Apple", "Samsung", "Google", "Sony"]:
                    price = int(price * 1.5)
                elif brand in ["Nokia", "Xiaomi", "Honor", "Realme"]:
                    price = int(price * 0.8)

        self.current_price = price
        self.price_display.setText(f"{price:,} ₽".replace(",", " "))

        return price

    def show_result(self):
        """Показать страницу с результатом"""
        if not self.validate_form():
            return

        # Обновляем информацию на странице результата
        device = self.device_type.currentText()
        brand = self.device_brand.currentText()
        model = self.device_model.currentText()
        reason = self.reason.currentText()
        price = self.calculate_price()

        params_text = f"{device} {brand} {model}\nПричина: {reason}"
        self.result_params.setText(params_text)
        self.result_price.setText(f"{price:,} ₽".replace(",", " "))

        # Переключаемся на страницу результата
        self.stacked_widget.setCurrentIndex(1)

    def add_to_cart(self):
        """Добавление в корзину с проверкой авторизации"""
        if not self.validate_form():
            return

        # Проверяем, авторизован ли пользователь
        if not session.is_authenticated():
            # Сохраняем данные заказа для повторной попытки после авторизации
            self.pending_order_item = {
                'device_type': self.device_type.currentText(),
                'device_brand': self.device_brand.currentText(),
                'device_model': self.device_model.currentText(),
                'reason': self.reason.currentText(),
                'price': self.calculate_price()
            }
            # Пользователь не авторизован - показываем диалог
            self.show_login_required_dialog()
            return

        # Пользователь авторизован - добавляем в корзину
        self.add_to_cart_authenticated()

    def add_to_cart_authenticated(self):
        """Добавляет в корзину уже авторизованного пользователя"""
        device = self.device_type.currentText()
        brand = self.device_brand.currentText()
        model = self.device_model.currentText()
        reason = self.reason.currentText()
        price = self.calculate_price()

        # Создаем объект заказа
        order_item = {
            'device_type': device,
            'device_brand': brand,
            'device_model': model,
            'reason': reason,
            'price': price
        }

        # Сохраняем в базу данных
        if db_crm.add_to_cart_db(session.get_user_id(), order_item):
            msg = QMessageBox(self.Dialog)
            msg.setWindowTitle("✅ Добавлено в корзину")
            msg.setTextFormat(Qt.RichText)  # разрешаем HTML
            msg.setText(
                f'<span style="color: white;">'
                f'Услуга добавлена в корзину!<br><br>'
                f'📱 {device} {brand} {model}<br>'
                f'⚠️ Причина: {reason}<br>'
                f'💰 Стоимость: {price:,.0f} ₽'
                f'</span>'.replace(",", " ")
            )
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        else:
            QMessageBox.warning(
                self.Dialog,
                "Ошибка",
                "Не удалось добавить товар в корзину"
            )

    def show_login_required_dialog(self):
        """Показывает диалог с требованием авторизации"""
        msg_box = QMessageBox(self.Dialog)
        msg_box.setWindowTitle("Требуется авторизация")
        msg_box.setText("🔐 Войдите в ваш аккаунт для добавления товара или услуги в корзину")
        msg_box.setIcon(QMessageBox.Information)

        # Создаем кнопки
        login_btn = msg_box.addButton("Войти в аккаунт", QMessageBox.AcceptRole)
        cancel_btn = msg_box.addButton("Отмена", QMessageBox.RejectRole)

        # Настраиваем стиль
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: rgb(47, 47, 47);
                color: white;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 12px;
                padding: 10px;
            }
            QPushButton {
                background-color: rgb(103, 155, 118);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgb(93, 145, 108);
            }
            QPushButton[text="Отмена"] {
                background-color: rgb(80, 80, 80);
            }
            QPushButton[text="Отмена"]:hover {
                background-color: rgb(100, 100, 100);
            }
        """)

        # Показываем диалог и обрабатываем результат
        result = msg_box.exec_()

        if msg_box.clickedButton() == login_btn:
            self.open_auth_window()

    def open_auth_window(self):
        """Открывает окно авторизации"""
        self.auth_dialog = QtWidgets.QDialog()
        self.auth_ui = AuthDialog()
        self.auth_ui.setupUi(self.auth_dialog)

        # Подключаем сигнал закрытия для обработки результата авторизации
        self.auth_dialog.finished.connect(self.on_auth_finished)
        self.auth_dialog.show()

    def on_auth_finished(self, result):
        """Обработчик закрытия окна авторизации"""
        if session.is_authenticated() and self.pending_order_item:
            # Если пользователь авторизовался и есть отложенный заказ, добавляем его
            if db_crm.add_to_cart_db(session.get_user_id(), self.pending_order_item):
                QMessageBox.information(
                    self.Dialog,
                    "✅ Добавлено в корзину",
                    f"Услуга добавлена в корзину!\n\n"
                    f"📱 {self.pending_order_item['device_type']} "
                    f"{self.pending_order_item['device_brand']} "
                    f"{self.pending_order_item['device_model']}\n"
                    f"⚠️ Причина: {self.pending_order_item['reason']}\n"
                    f"💰 Стоимость: {self.pending_order_item['price']:,.0f} ₽".replace(",", " ")
                )
            # Очищаем отложенный заказ
            self.pending_order_item = None

    def validate_form(self):
        """Валидация формы"""
        if not self.device_type.currentText():
            QMessageBox.warning(self.Dialog, "Ошибка", "Выберите тип устройства")
            return False

        if not self.device_brand.currentText():
            QMessageBox.warning(self.Dialog, "Ошибка", "Выберите бренд")
            return False

        if not self.device_model.currentText():
            QMessageBox.warning(self.Dialog, "Ошибка", "Укажите модель устройства")
            return False

        if not self.reason.currentText():
            QMessageBox.warning(self.Dialog, "Ошибка", "Выберите причину обращения")
            return False

        return True

    def clear_form(self):
        """Очистка формы"""
        self.device_type.setCurrentIndex(0)
        self.update_brands()
        self.update_models()
        self.reason.setCurrentIndex(0)
        self.price_display.setText("—")
        self.stacked_widget.setCurrentIndex(0)
        self.pending_order_item = None  # Очищаем отложенный заказ