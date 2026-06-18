# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QColor, QFont, QPalette, QBrush
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QFrame, QPushButton, QLabel, QWidget
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from Server import db
import Server.globals as globals
from session_manager import session


class ModernButton(QPushButton):
    """Современная кнопка с анимацией при наведении"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self._opacity = 1.0

    def enterEvent(self, event):
        self.animate_opacity(0.8)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_opacity(1.0)
        super().leaveEvent(event)

    def animate_opacity(self, value):
        self.anim = QPropertyAnimation(self, b"opacity")
        self.anim.setDuration(200)
        self.anim.setStartValue(self._opacity)
        self.anim.setEndValue(value)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.update()

    opacity = pyqtProperty(float, get_opacity, set_opacity)


class Ui_Ui_Remont_Laptop_Dialog(object):
    def setupUi(self, Ui_Remont_Laptop_Dialog):
        self.dialog = Ui_Remont_Laptop_Dialog  # Сохраняем ссылку на диалог

        Ui_Remont_Laptop_Dialog.setObjectName("Ui_Remont_Laptop_Dialog")
        Ui_Remont_Laptop_Dialog.resize(1100, 1100)
        Ui_Remont_Laptop_Dialog.setMinimumSize(1000, 900)

        # Устанавливаем современный шрифт по умолчанию
        font = QFont("Segoe UI", 10)
        Ui_Remont_Laptop_Dialog.setFont(font)

        # Иконка
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Pictures/Screenshot from 2025-09-15 14-30-16.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Ui_Remont_Laptop_Dialog.setWindowIcon(icon)

        # Главный градиентный фон
        Ui_Remont_Laptop_Dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #232323, stop:1 #1a1a1a);
            }
        """)

        # Основной вертикальный layout с отступами
        self.main_layout = QtWidgets.QVBoxLayout(Ui_Remont_Laptop_Dialog)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(20)

        # ========== ВЕРХНЯЯ ПАНЕЛЬ С НАВИГАЦИЕЙ ==========
        self.top_frame = QFrame()
        self.top_frame.setObjectName("top_frame")
        self.top_frame.setStyleSheet("""
            QFrame#top_frame {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #3d3d3d;
            }
        """)

        # Тень для верхней панели
        top_shadow = QGraphicsDropShadowEffect()
        top_shadow.setBlurRadius(25)
        top_shadow.setColor(QColor(0, 0, 0, 90))
        top_shadow.setOffset(0, 5)
        self.top_frame.setGraphicsEffect(top_shadow)

        top_layout = QtWidgets.QHBoxLayout(self.top_frame)
        top_layout.setContentsMargins(20, 15, 20, 15)
        top_layout.setSpacing(15)

        # Кнопка назад с иконкой
        self.back_button = ModernButton("← Назад")
        self.back_button.setMinimumSize(100, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:pressed {
                background-color: #45a049;
            }
        """)

        # Логотип/название компании
        self.logo_label = QLabel("IT-EcoSystem")
        self.logo_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 20px;
                font-weight: bold;
                padding: 0 20px;
            }
        """)

        # Кнопки действий
        self.favourites_button = ModernButton("❤️")
        self.favourites_button.setMinimumSize(45, 40)
        self.favourites_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 8px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)

        self.cart_button = ModernButton("🛒")
        self.cart_button.setMinimumSize(45, 40)
        self.cart_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 8px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)

        self.contact_button = ModernButton("📞 Контакты")
        self.contact_button.setMinimumSize(110, 40)
        self.contact_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)

        top_layout.addWidget(self.back_button)
        top_layout.addWidget(self.logo_label)
        top_layout.addStretch()
        top_layout.addWidget(self.favourites_button)
        top_layout.addWidget(self.cart_button)
        top_layout.addWidget(self.contact_button)

        self.main_layout.addWidget(self.top_frame)

        # ========== ЗАГОЛОВОК СТРАНИЦЫ ==========
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d2d2d, stop:1 #252525);
                border-radius: 20px;
                padding: 5px;
            }
        """)

        header_layout = QtWidgets.QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(25, 15, 25, 15)

        self.page_title = QLabel("💻 Ремонт ноутбуков")
        self.page_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        self.page_subtitle = QLabel("Профессиональный ремонт любой сложности")
        self.page_subtitle.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 16px;
                padding-left: 20px;
            }
        """)

        header_layout.addWidget(self.page_title)
        header_layout.addWidget(self.page_subtitle)
        header_layout.addStretch()

        self.main_layout.addWidget(self.header_frame)

        # ========== ОСНОВНОЙ КОНТЕНТ С ПРОКРУТКОЙ ==========
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 6px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #45a049;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self.QW_Remont_laptop = QWidget()
        self.QW_Remont_laptop.setStyleSheet("background-color: transparent;")
        self.gridLayout = QtWidgets.QGridLayout(self.QW_Remont_laptop)
        self.gridLayout.setContentsMargins(0, 20, 0, 20)
        self.gridLayout.setSpacing(25)

        # ========== ИНФОРМАЦИОННАЯ КАРТОЧКА ==========
        self.info_card = QFrame()
        self.info_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #222222);
                border-radius: 25px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Тень для карточки
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(30)
        card_shadow.setColor(QColor(0, 0, 0, 120))
        card_shadow.setOffset(0, 8)
        self.info_card.setGraphicsEffect(card_shadow)

        info_layout = QtWidgets.QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(30, 30, 30, 30)
        info_layout.setSpacing(20)

        # Текст LB1
        self.LB1_Remont_laptop = QLabel()
        self.LB1_Remont_laptop.setWordWrap(True)
        self.LB1_Remont_laptop.setOpenExternalLinks(True)
        self.LB1_Remont_laptop.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                background: transparent;
                font-size: 15px;
                line-height: 1.7;
            }
        """)
        info_layout.addWidget(self.LB1_Remont_laptop)

        self.gridLayout.addWidget(self.info_card, 0, 0, 1, 1)

        # ========== ТАБЛИЦА ЦЕН (УПРОЩЕННАЯ) ==========
        self.price_card = QFrame()
        self.price_card.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 25px;
                border: 1px solid #353535;
            }
        """)

        price_shadow = QGraphicsDropShadowEffect()
        price_shadow.setBlurRadius(30)
        price_shadow.setColor(QColor(0, 0, 0, 120))
        price_shadow.setOffset(0, 8)
        self.price_card.setGraphicsEffect(price_shadow)

        price_layout = QtWidgets.QVBoxLayout(self.price_card)
        price_layout.setContentsMargins(30, 30, 30, 30)
        price_layout.setSpacing(20)

        # Заголовок таблицы
        table_header = QLabel("💰 Стоимость ремонта ноутбуков")
        table_header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        price_layout.addWidget(table_header)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                max-height: 1px;
                min-height: 1px;
                margin: 5px 0 15px 0;
            }
        """)
        price_layout.addWidget(separator)

        # Простая таблица услуг и цен (без QTableWidget)
        self.services_widget = QWidget()
        services_layout = QtWidgets.QVBoxLayout(self.services_widget)
        services_layout.setContentsMargins(0, 0, 0, 0)
        services_layout.setSpacing(10)

        # Список услуг с ценами
        services_list = [
            {"name": "Техническое обслуживание с заменой термопасты", "price": "от 1600 ₽"},
            {"name": "Техническое обслуживание без замены термопасты", "price": "от 1300 ₽"},
            {"name": "Замена матрицы", "price": "от 1000 ₽"},
            {"name": "Ремонт платы", "price": "от 1100 ₽"},
            {"name": "Восстановление разъема", "price": "от 800 ₽"},
            {"name": "Переустановка Windows", "price": "от 1000 ₽"},
            {"name": "Установка программ", "price": "от 600 ₽"},
            {"name": "Ремонт кнопок", "price": "от 800 ₽"}
        ]

        for service in services_list:
            # Создаем строку для услуги
            service_row = QFrame()
            service_row.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border-radius: 10px;
                }
                QFrame:hover {
                    background-color: #333333;
                    border-left: 3px solid #4CAF50;
                }
            """)

            row_layout = QtWidgets.QHBoxLayout(service_row)
            row_layout.setContentsMargins(15, 12, 15, 12)

            # Название услуги
            name_label = QLabel(service["name"])
            name_label.setStyleSheet("""
                QLabel {
                    color: #e0e0e0;
                    font-size: 15px;
                    font-weight: 500;
                }
            """)

            # Цена
            price_label = QLabel(service["price"])
            price_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 16px;
                    font-weight: bold;
                    background-color: #1a3a1a;
                    padding: 5px 15px;
                    border-radius: 15px;
                }
            """)

            row_layout.addWidget(name_label)
            row_layout.addStretch()
            row_layout.addWidget(price_label)

            services_layout.addWidget(service_row)

        price_layout.addWidget(self.services_widget)

        # Кнопка заказа
        self.order_button = ModernButton("💻 Заказать ремонт ноутбука")
        self.order_button.setMinimumHeight(55)
        self.order_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                margin-top: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3d8b40, stop:1 #357a38);
            }
        """)
        price_layout.addWidget(self.order_button)

        self.gridLayout.addWidget(self.price_card, 1, 0, 1, 1)

        # ========== ДЕТАЛЬНОЕ ОПИСАНИЕ ==========
        self.detail_card = QFrame()
        self.detail_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #262626, stop:1 #222222);
                border-radius: 25px;
                border: 1px solid #353535;
            }
        """)

        detail_shadow = QGraphicsDropShadowEffect()
        detail_shadow.setBlurRadius(30)
        detail_shadow.setColor(QColor(0, 0, 0, 120))
        detail_shadow.setOffset(0, 8)
        self.detail_card.setGraphicsEffect(detail_shadow)

        detail_layout = QtWidgets.QVBoxLayout(self.detail_card)
        detail_layout.setContentsMargins(30, 30, 30, 30)
        detail_layout.setSpacing(20)

        # Заголовок детального описания
        detail_header = QLabel("🔧 Подробнее об услугах")
        detail_header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        detail_layout.addWidget(detail_header)

        # Разделитель
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                max-height: 1px;
                min-height: 1px;
                margin: 5px 0 15px 0;
            }
        """)
        detail_layout.addWidget(separator2)

        self.LB2_Remont_laptop = QLabel()
        self.LB2_Remont_laptop.setWordWrap(True)
        self.LB2_Remont_laptop.setOpenExternalLinks(True)
        self.LB2_Remont_laptop.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                background: transparent;
                font-size: 15px;
                line-height: 1.8;
            }
            QLabel a {
                color: #4CAF50;
                text-decoration: none;
            }
            QLabel a:hover {
                text-decoration: underline;
            }
        """)
        detail_layout.addWidget(self.LB2_Remont_laptop)

        self.gridLayout.addWidget(self.detail_card, 2, 0, 1, 1)

        # ========== НИЖНЯЯ ПАНЕЛЬ С КОНТАКТАМИ ==========
        self.bottom_frame = QFrame()
        self.bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #3d3d3d;
            }
        """)

        bottom_layout = QtWidgets.QHBoxLayout(self.bottom_frame)
        bottom_layout.setContentsMargins(20, 15, 20, 15)

        # Контактная информация
        contact_info = QLabel("📞 +7 (929) 356-23-78  |  ✉️ info@it-ecosystem.ru  |  🏢 Красноярск, ул. Микуцкого, 12")
        contact_info.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
            }
        """)

        work_time = QLabel("🕒 Пн-Пт: 10:00-20:00 | Сб-Вс: 12:00-19:00")
        work_time.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 13px;
                font-weight: 500;
            }
        """)

        bottom_layout.addWidget(contact_info)
        bottom_layout.addStretch()
        bottom_layout.addWidget(work_time)

        self.gridLayout.addWidget(self.bottom_frame, 3, 0, 1, 1)

        self.scrollArea.setWidget(self.QW_Remont_laptop)
        self.main_layout.addWidget(self.scrollArea)

        # Подключаем кнопку назад
        self.back_button.clicked.connect(Ui_Remont_Laptop_Dialog.close)

        # Настраиваем кнопку избранного
        self.setup_favorites_button()
        self.check_favorite_status()

        self.retranslateUi(Ui_Remont_Laptop_Dialog)
        QtCore.QMetaObject.connectSlotsByName(Ui_Remont_Laptop_Dialog)

    def retranslateUi(self, Ui_Remont_Laptop_Dialog):
        _translate = QtCore.QCoreApplication.translate
        Ui_Remont_Laptop_Dialog.setWindowTitle(_translate("Ui_Remont_Laptop_Dialog", "IT-EcoSystem - Ремонт ноутбуков"))

        # Форматируем текст для LB1
        lb1_text = """
        <div style='text-align: left;'>
            <h1 style='color: #4CAF50; font-size: 32px; margin: 0 0 20px 0;'>💻 Ремонт ноутбуков любой сложности</h1>

            <p style='font-size: 16px; margin-bottom: 20px; color: #e0e0e0;'>
                Сервисный центр <b style='color: #4CAF50;'>«IT-EcoSystem»</b> предлагает профессиональный ремонт 
                ноутбуков всех марок и моделей.
            </p>

            <div style='background-color: rgba(76, 175, 80, 0.1); border-left: 4px solid #4CAF50; padding: 15px; margin: 20px 0; border-radius: 0 10px 10px 0;'>
                <p style='margin: 0; font-size: 15px;'>
                    <span style='color: #4CAF50; font-weight: bold;'>✓ Опытные мастера</span><br>
                    <span style='color: #b0b0b0;'>Специалисты с многолетним опытом работы с техникой ASUS, HP, Lenovo, Dell, Acer и других брендов</span>
                </p>
            </div>

            <p style='font-size: 15px; margin: 15px 0; color: #d0d0d0;'>
                <b style='color: #4CAF50;'>Мы ремонтируем:</b> ASUS, HP, Lenovo, Dell, Acer, MSI, Apple MacBook и другие бренды
            </p>

            <p style='font-size: 15px; color: #b0b0b0; margin-top: 15px;'>
                Ноутбуки чаще другой компьютерной техники требуют ремонта, что обычно связано с экстремальными условиями их эксплуатации. 
                Среди владельцев ноутбуков наиболее частыми поводами для обращения в сервис являются залитая клавиатура и механические 
                повреждения корпуса, что не характерно при ремонте стационарных ПК.
            </p>
        </div>
        """
        self.LB1_Remont_laptop.setText(_translate("Ui_Remont_Laptop_Dialog", lb1_text))

        # Форматируем текст для LB2
        lb2_text = """
        <div>
            <h2 style='color: #4CAF50; font-size: 26px; margin-bottom: 25px; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;'>
                🔧 Особенности ремонта ноутбуков
            </h2>

            <p style='margin-bottom: 25px; font-size: 16px; color: #e0e0e0;'>
                Есть несколько факторов, которые усложняют диагностику и ремонт любого ноутбука:
            </p>

            <div style='margin: 20px 0;'>
                <div style='margin-bottom: 15px; padding: 20px; background-color: #2d2d2d; border-radius: 15px; border-left: 4px solid #4CAF50;'>
                    <h3 style='color: #4CAF50; margin: 0 0 10px 0; font-size: 18px;'>1️⃣ Миниатюризация компонентов</h3>
                    <p style='color: #b0b0b0; margin: 0; font-size: 14px; line-height: 1.6;'>
                        Маленький размер деталей: ноутбук только кажется простым устройством, однако именно благодаря 
                        «мелкокалиберным» комплектующим он приобретает компактность.
                    </p>
                </div>

                <div style='margin-bottom: 15px; padding: 20px; background-color: #2d2d2d; border-radius: 15px; border-left: 4px solid #4CAF50;'>
                    <h3 style='color: #4CAF50; margin: 0 0 10px 0; font-size: 18px;'>2️⃣ Уникальная компоновка</h3>
                    <p style='color: #b0b0b0; margin: 0; font-size: 14px; line-height: 1.6;'>
                        Свойственна каждой модели, поэтому для ремонта ноутбуков можно использовать только оригинальные 
                        комплектующие – это же обстоятельство затрудняет поиск необходимой детали.
                    </p>
                </div>

                <div style='margin-bottom: 15px; padding: 20px; background-color: #2d2d2d; border-radius: 15px; border-left: 4px solid #4CAF50;'>
                    <h3 style='color: #4CAF50; margin: 0 0 10px 0; font-size: 18px;'>3️⃣ Комплексная диагностика</h3>
                    <p style='color: #b0b0b0; margin: 0; font-size: 14px; line-height: 1.6;'>
                        Диагностические мероприятия предшествуют ремонту ноутбука и обязательны как для всей системы 
                        в целом, так и для отдельных ее компонентов.
                    </p>
                </div>
            </div>

            <div style='background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a3a1a, stop:1 #2a4a2a); padding: 20px; border-radius: 15px; margin: 30px 0;'>
                <h3 style='color: white; margin-bottom: 15px; font-size: 20px;'>⚠️ Когда нужно обратиться в сервис:</h3>
                <table width='100%' style='color: #e0e0e0;'>
                    <tr>
                        <td style='padding: 8px;'>🔸 Ноутбук не включается</td>
                        <td style='padding: 8px;'>🔸 Сильный нагрев и шум</td>
                    </tr>
                    <tr>
                        <td style='padding: 8px;'>🔸 Не заряжается</td>
                        <td style='padding: 8px;'>🔸 Проблемы с изображением</td>
                    </tr>
                    <tr>
                        <td style='padding: 8px;'>🔸 Не работает клавиатура</td>
                        <td style='padding: 8px;'>🔸 Медленная работа</td>
                    </tr>
                </table>
            </div>

            <div style='background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a3a1a, stop:1 #2a4a2a); padding: 20px; border-radius: 15px; margin: 30px 0;'>
                <h3 style='color: white; margin-bottom: 15px; font-size: 20px;'>✨ Почему выбирают нас:</h3>
                <table width='100%' style='color: #e0e0e0;'>
                    <tr>
                        <td style='padding: 5px;'>✓ <b style='color: #4CAF50;'>Гарантия</b> на все виды работ</td>
                        <td style='padding: 5px;'>✓ <b style='color: #4CAF50;'>Срочный ремонт</b> от 1 часа</td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'>✓ <b style='color: #4CAF50;'>Оригинальные запчасти</b></td>
                        <td style='padding: 5px;'>✓ <b style='color: #4CAF50;'>Бесплатная диагностика</b></td>
                    </tr>
                    <tr>
                        <td style='padding: 5px;'>✓ <b style='color: #4CAF50;'>Опытные мастера</b></td>
                        <td style='padding: 5px;'>✓ <b style='color: #4CAF50;'>Современное оборудование</b></td>
                    </tr>
                </table>
            </div>

            <div style='background-color: #2d2d2d; border-radius: 15px; padding: 25px; margin-top: 25px;'>
                <h3 style='color: #4CAF50; margin-bottom: 15px; font-size: 20px;'>📞 Свяжитесь с нами</h3>
                <p style='font-size: 18px; margin-bottom: 10px; color: #e0e0e0;'>📍 Красноярск, Улица Микуцкого, 12</p>
                <p style='font-size: 24px; margin: 15px 0; color: #4CAF50; font-weight: bold;'>📱 +7 (929) 356-23-78</p>
                <p style='font-size: 16px; color: #b0b0b0;'>✉️ info@it-ecosystem.ru</p>
                <p style='font-size: 16px; color: #b0b0b0; margin-top: 10px;'>🕒 Пн-Пт: 10:00-20:00 | Сб-Вс: 12:00-19:00</p>
            </div>

            <p style='margin-top: 25px; color: #888; text-align: center; font-size: 14px;'>
                Чтобы узнать точные цены на услуги по ремонту, позвоните в мастерскую или оставьте заявку на сайте.
            </p>
        </div>
        """
        self.LB2_Remont_laptop.setText(_translate("Ui_Remont_Laptop_Dialog", lb2_text))

    def setup_favorites_button(self):
        """Настройка кнопки избранного"""
        # Проверяем, что кнопка существует
        if not hasattr(self, 'favourites_button'):
            print("Ошибка: favourites_button не создан!")
            return

        # Отключаем существующие соединения, чтобы избежать дублирования
        try:
            self.favourites_button.clicked.disconnect()
        except:
            pass  # Если не было соединений, игнорируем

        # Проверяем, авторизован ли пользователь
        if globals.current_user_id:
            # Получаем количество элементов в избранном
            count = db.get_favorites_count(globals.current_user_id)
            if count > 0:
                self.favourites_button.setText(f"❤️ {count}")

            # Подключаем обработчик
            self.favourites_button.clicked.connect(self.toggle_favorite)

            # При наведении показываем подсказку
            self.favourites_button.setToolTip("Добавить/удалить из избранного")
        else:
            self.favourites_button.setEnabled(False)
            self.favourites_button.setToolTip("Войдите в систему, чтобы добавлять в избранное")

    def toggle_favorite(self):
        """Добавление/удаление текущей страницы в избранное"""
        print("toggle_favorite вызван")  # Для отладки

        if not globals.current_user_id:
            QtWidgets.QMessageBox.warning(
                self.dialog,  # Используем сохраненную ссылку на диалог
                "Требуется авторизация",
                "Пожалуйста, войдите в систему, чтобы добавлять в избранное"
            )
            return

        # Получаем информацию о текущей странице
        item_name = self.page_title.text()
        item_id = self.get_page_id()

        # Проверяем, есть ли уже в избранном
        is_fav = db.is_in_favorites(globals.current_user_id, 'service', item_id)

        if is_fav:
            # Удаляем из избранного
            reply = QtWidgets.QMessageBox.question(
                self.dialog,  # Используем сохраненную ссылку на диалог
                "Удаление из избранного",
                f"Удалить '{item_name}' из избранного?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if reply == QtWidgets.QMessageBox.Yes:
                if db.remove_from_favorites_by_item(globals.current_user_id, 'service', item_id):
                    self.favourites_button.setText("❤️")
                    self.favourites_button.setStyleSheet("""
                        QPushButton {
                            background-color: #3a3a3a;
                            color: #e0e0e0;
                            border: none;
                            border-radius: 8px;
                            font-size: 18px;
                        }
                        QPushButton:hover {
                            background-color: #4CAF50;
                            color: white;
                        }
                    """)
                    QtWidgets.QMessageBox.information(
                        self.dialog,  # Используем сохраненную ссылку на диалог
                        "Успешно",
                        "Элемент удален из избранного"
                    )

                    # Обновляем счетчик в главном окне
                    self.update_main_window_favorites_count()
        else:
            # Добавляем в избранное
            if db.add_to_favorites(
                    user_id=globals.current_user_id,
                    item_type='service',
                    item_id=item_id,
                    item_name=item_name,
                    item_price=0,
                    item_category='Ремонт'
            ):
                self.favourites_button.setText("❤️")
                self.favourites_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                QtWidgets.QMessageBox.information(
                    self.dialog,  # Используем сохраненную ссылку на диалог
                    "Успешно",
                    "Элемент добавлен в избранное"
                )

                # Обновляем счетчик в главном окне
                self.update_main_window_favorites_count()

        # Обновляем счетчик на кнопке
        count = db.get_favorites_count(globals.current_user_id)
        if count > 0:
            self.favourites_button.setText(f"❤️ {count}")
        else:
            self.favourites_button.setText("❤️")

    def update_main_window_favorites_count(self):
        """Обновляет счетчик избранного в главном окне"""
        try:
            if hasattr(session, '_main_window') and session._main_window:
                main_window = session._main_window
                if hasattr(main_window, 'Favourites_PushButton'):
                    count = db.get_favorites_count(globals.current_user_id)
                    if count > 0:
                        main_window.Favourites_PushButton.setText(f"❤️ Избранное ({count})")
                    else:
                        main_window.Favourites_PushButton.setText("❤️ Избранное")
        except Exception as e:
            print(f"Ошибка обновления счетчика в главном окне: {e}")

    def get_page_id(self):
        """Возвращает ID текущей страницы"""
        if "ноутбук" in self.page_title.text().lower():
            return 1  # ID для ремонта ноутбуков
        return 0

    def check_favorite_status(self):
        """Проверяет статус избранного при загрузке страницы"""
        if not hasattr(self, 'favourites_button'):
            return

        if globals.current_user_id:
            item_id = self.get_page_id()
            if db.is_in_favorites(globals.current_user_id, 'service', item_id):
                self.favourites_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                self.favourites_button.setText("❤️")
            else:
                self.favourites_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a3a;
                        color: #e0e0e0;
                        border: none;
                        border-radius: 8px;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #4CAF50;
                        color: white;
                    }
                """)
        else:
            self.favourites_button.setEnabled(False)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # Устанавливаем современную цветовую схему
    app.setStyle('Fusion')

    # Настройка палитры приложения
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(35, 35, 35))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(55, 55, 55))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(55, 55, 55))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    # Устанавливаем шрифт по умолчанию
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    Ui_Remont_Laptop_Dialog = QtWidgets.QDialog()
    ui = Ui_Ui_Remont_Laptop_Dialog()
    ui.setupUi(Ui_Remont_Laptop_Dialog)
    Ui_Remont_Laptop_Dialog.show()
    sys.exit(app.exec_())