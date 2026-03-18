# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette, QPixmap, QPainter, QPen, QPainterPath, QIcon
from PyQt5.QtWidgets import (QGraphicsDropShadowEffect, QLabel, QPushButton, QFrame,
                             QMessageBox, QDialog, QFileDialog, QVBoxLayout, QHBoxLayout,
                             QScrollArea, QWidget, QSpacerItem, QSizePolicy, QGridLayout)

# Импорты ваших модулей
from Server.db import update_avatar_in_db, get_avatar_path_by_user_id, get_user_statistics, get_user_info
from Setting_profil import Ui_Setting_Profil
from session_manager import session
from client_orders_window import ClientOrdersWindow


class ModernLineEdit(QtWidgets.QLineEdit):
    """Современное поле ввода с анимацией (как в identification_window)"""

    def __init__(self, placeholder="", icon=None, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(45)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
                font-weight: 400;
                selection-background-color: #4CAF50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #333333;
            }
            QLineEdit:hover:not(:focus) {
                background-color: #353535;
                border: 2px solid #454545;
            }
            QLineEdit::placeholder {
                color: #808080;
                font-style: italic;
            }
        """)

        # Добавляем тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernButton(QPushButton):
    """Современная кнопка с анимацией (как в authorization_window)"""

    def __init__(self, text="", primary=True, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(45)
        self.setCursor(Qt.PointingHandCursor)

        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #45a049, stop:1 #3d8b40);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3d8b40, stop:1 #357a38);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: #b0b0b0;
                    border: 2px solid #4a4a4a;
                    border-radius: 10px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #454545;
                    color: white;
                    border: 2px solid #4CAF50;
                }
                QPushButton:pressed {
                    background-color: #353535;
                }
            """)


class StatCard(QFrame):
    """Стильная карточка статистики с градиентом и тенью"""

    def __init__(self, icon="📊", title="0", subtitle="Заказов", parent=None):
        super().__init__(parent)
        self.title_label = None
        self.setup_ui(icon, title, subtitle)

    def setup_ui(self, icon, title, subtitle):
        self.setMinimumSize(120, 90)
        self.setMaximumHeight(90)

        # Стиль с градиентом
        self.setStyleSheet("""
            StatCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d2d, stop:1 #262626);
                border-radius: 15px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Добавляем тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Иконка с фоном
        icon_container = QFrame()
        icon_container.setFixedSize(45, 45)
        icon_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(76, 175, 80, 0.2), stop:1 rgba(76, 175, 80, 0.1));
                border-radius: 12px;
                border: 1px solid #4CAF50;
            }
        """)

        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 22px;
                background: none;
                border: none;
            }
        """)
        icon_layout.addWidget(icon_label)

        # Текстовая информация
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
                background: none;
                border: none;
            }
        """)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 11px;
                background: none;
                border: none;
            }
        """)

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(subtitle_label)

        layout.addWidget(icon_container)
        layout.addLayout(text_layout)
        layout.addStretch()

    def set_value(self, value):
        """Обновляет значение в карточке статистики"""
        if self.title_label:
            self.title_label.setText(str(value))


class AvatarWidget(QLabel):
    """Улучшенный виджет аватара с круглой обрезкой и анимацией"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(130, 130)
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def setPixmap(self, pixmap):
        """Устанавливает круглую обрезку изображения с красивой рамкой"""
        if pixmap.isNull():
            return

        # Создаем круглую маску
        size = min(pixmap.width(), pixmap.height())
        circular_pixmap = QPixmap(size, size)
        circular_pixmap.fill(Qt.transparent)

        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Рисуем круг
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        # Масштабируем и рисуем изображение
        scaled_pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (size - scaled_pixmap.width()) // 2
        y = (size - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()

        # Добавляем градиентную рамку
        bordered_pixmap = QPixmap(size + 8, size + 8)
        bordered_pixmap.fill(Qt.transparent)

        painter = QPainter(bordered_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Градиент для рамки
        gradient = QLinearGradient(0, 0, size + 8, size + 8)
        gradient.setColorAt(0, QColor(76, 175, 80))
        gradient.setColorAt(1, QColor(69, 160, 73))

        pen = QPen(QBrush(gradient), 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(2, 2, size + 4, size + 4)

        # Рисуем аватар
        painter.drawPixmap(4, 4, circular_pixmap)
        painter.end()

        super().setPixmap(bordered_pixmap.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        """Обработка клика для смены аватара с анимацией"""
        # Анимация нажатия
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(100)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(self.geometry())
        anim.setEndValue(self.geometry().adjusted(5, 5, -5, -5))
        anim.finished.connect(lambda: self.reset_avatar_size())
        anim.start()

        # Вызываем загрузку аватара
        QTimer.singleShot(100, lambda: self.parent().parent().load_avatar(event))

    def reset_avatar_size(self):
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(100)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(self.geometry())
        anim.setEndValue(self.geometry().adjusted(-5, -5, 5, 5))
        anim.start()


class Ui_profil(object):
    def __init__(self, user_id, full_name):
        self.user_id = user_id
        self.full_name = full_name
        self.dialog = None
        self.main_window = None
        self.user_data = None
        self.stat_orders = None
        self.stat_favorites = None
        self.stat_days = None
        self.stat_bonus = None
        self.contact_phone = None
        self.contact_email = None

    def setupUi(self, Dialog):
        self.dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 750)
        Dialog.setMinimumSize(450, 600)
        Dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        Dialog.setAttribute(Qt.WA_TranslucentBackground)

        # Загружаем данные пользователя
        self.load_user_data()

        # Главный контейнер с градиентом
        main_container = QFrame(Dialog)
        main_container.setObjectName("main_container")
        main_container.setGeometry(0, 0, Dialog.width(), Dialog.height())
        main_container.setStyleSheet("""
            QFrame#main_container {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 30px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Основная тень
        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(30)
        main_shadow.setColor(QColor(0, 0, 0, 150))
        main_shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(main_shadow)

        # Layout для контейнера
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Скролл-область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
                border-radius: 30px;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
                margin: 10px 0px 10px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 4px;
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
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        # Основной layout для контента
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

        # ===== ВЕРХНЯЯ ПАНЕЛЬ =====
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопка закрытия
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        self.btn_close.clicked.connect(Dialog.close)

        # Кнопка настроек
        self.btn_settings_quick = QPushButton("⚙️")
        self.btn_settings_quick.setFixedSize(40, 40)
        self.btn_settings_quick.setCursor(Qt.PointingHandCursor)
        self.btn_settings_quick.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 12px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:pressed {
                background-color: #45a049;
            }
        """)
        self.btn_settings_quick.clicked.connect(self.open_Ui_Setting_Profil)

        top_layout.addWidget(self.btn_close)
        top_layout.addStretch()

        # Заголовок профиля
        title_label = QLabel("Мой профиль")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        top_layout.addWidget(title_label)

        top_layout.addStretch()
        top_layout.addWidget(self.btn_settings_quick)

        layout.addLayout(top_layout)

        # ===== ПРОФИЛЬ КЛИЕНТА =====
        profile_layout = QVBoxLayout()
        profile_layout.setSpacing(15)
        profile_layout.setAlignment(Qt.AlignCenter)

        # Аватар
        self.Ava_Profile = AvatarWidget()
        self.load_user_avatar()

        # Имя пользователя
        self.Name_Profile = QLabel(self.full_name)
        self.Name_Profile.setAlignment(Qt.AlignCenter)
        self.Name_Profile.setWordWrap(True)
        self.Name_Profile.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: 600;
                margin-top: 10px;
            }
        """)

        # Статус с бейджем
        status_container = QFrame()
        status_container.setFixedHeight(30)
        status_container.setStyleSheet("""
            QFrame {
                background-color: rgba(76, 175, 80, 0.15);
                border-radius: 15px;
                border: 1px solid #4CAF50;
                padding: 0 15px;
            }
        """)

        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(10, 0, 10, 0)

        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #4CAF50; font-size: 14px;")

        status_label = QLabel("Активный клиент")
        status_label.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: 500;")

        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_label)

        profile_layout.addWidget(self.Ava_Profile, 0, Qt.AlignCenter)
        profile_layout.addWidget(self.Name_Profile)
        profile_layout.addWidget(status_container, 0, Qt.AlignCenter)

        layout.addLayout(profile_layout)

        # ===== СТАТИСТИКА КЛИЕНТА =====
        stats_title = QLabel("📊 Статистика")
        stats_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 600;
                margin-top: 10px;
            }
        """)
        layout.addWidget(stats_title)

        # Грид для статистики
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)

        # Получаем статистику
        stats = self.load_user_statistics()

        self.stat_orders = StatCard("📦", str(stats['orders_count']), "Заказов")
        self.stat_favorites = StatCard("❤️", str(stats['favorites_count']), "В избранном")
        self.stat_days = StatCard("📅", str(stats['days_with_us']), "Дней с нами")
        self.stat_bonus = StatCard("🎁", str(stats['bonus_points']), "Бонусов")

        stats_grid.addWidget(self.stat_orders, 0, 0)
        stats_grid.addWidget(self.stat_favorites, 0, 1)
        stats_grid.addWidget(self.stat_days, 1, 0)
        stats_grid.addWidget(self.stat_bonus, 1, 1)

        layout.addLayout(stats_grid)

        # ===== РАЗДЕЛИТЕЛЬ =====
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                max-height: 1px;
                min-height: 1px;
                margin: 5px 0;
            }
        """)
        layout.addWidget(separator)

        # ===== МОИ УСЛУГИ =====
        services_title = QLabel("🛠️ Мои услуги")
        services_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 600;
                margin-top: 5px;
            }
        """)
        layout.addWidget(services_title)

        # Кнопки с иконками
        self.btn_new_order = ModernButton("📋 Мои заказы", True)
        layout.addWidget(self.btn_new_order)
        self.btn_new_order.clicked.connect(self.open_my_orders)

        self.btn_favorites = ModernButton("❤️ Избранное", False)
        layout.addWidget(self.btn_favorites)

        self.btn_history = ModernButton("📜 История заказов", False)
        layout.addWidget(self.btn_history)

        # ===== КОНТАКТНАЯ ИНФОРМАЦИЯ =====
        contact_frame = QFrame()
        contact_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #222222);
                border-radius: 20px;
                border: 1px solid #3a3a3a;
                padding: 15px;
                margin-top: 5px;
            }
        """)

        # Тень для контактного фрейма
        contact_shadow = QGraphicsDropShadowEffect()
        contact_shadow.setBlurRadius(15)
        contact_shadow.setColor(QColor(0, 0, 0, 60))
        contact_shadow.setOffset(0, 3)
        contact_frame.setGraphicsEffect(contact_shadow)

        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setSpacing(12)

        contact_header = QLabel("📞 Контактная информация")
        contact_header.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 600;
                background: none;
            }
        """)
        contact_layout.addWidget(contact_header)

        # Телефон с иконкой
        phone_widget = QWidget()
        phone_layout = QHBoxLayout(phone_widget)
        phone_layout.setContentsMargins(0, 0, 0, 0)

        phone_icon = QLabel("📱")
        phone_icon.setStyleSheet("font-size: 16px;")

        phone_number = self.user_data.get('PhoneNumber',
                                          '+7 (___) ___-__-__') if self.user_data else '+7 (___) ___-__-__'
        self.contact_phone = QLabel(phone_number)
        self.contact_phone.setStyleSheet("color: white; font-size: 13px;")

        phone_layout.addWidget(phone_icon)
        phone_layout.addWidget(self.contact_phone)
        phone_layout.addStretch()

        contact_layout.addWidget(phone_widget)

        # Email с иконкой
        email_widget = QWidget()
        email_layout = QHBoxLayout(email_widget)
        email_layout.setContentsMargins(0, 0, 0, 0)

        email_icon = QLabel("📧")
        email_icon.setStyleSheet("font-size: 16px;")

        email = self.user_data.get('Email', 'email@example.com') if self.user_data else 'email@example.com'
        self.contact_email = QLabel(email)
        self.contact_email.setStyleSheet("color: white; font-size: 13px;")

        email_layout.addWidget(email_icon)
        email_layout.addWidget(self.contact_email)
        email_layout.addStretch()

        contact_layout.addWidget(email_widget)

        layout.addWidget(contact_frame)

        # ===== КНОПКА ВЫХОДА =====
        self.btn_logout = QPushButton("🚪 Выйти из аккаунта")
        self.btn_logout.setMinimumHeight(45)
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #ff6b6b;
                border: 2px solid #ff6b6b;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                color: white;
            }
            QPushButton:pressed {
                background-color: #ff5252;
            }
        """)
        self.btn_logout.clicked.connect(self.logout)
        layout.addWidget(self.btn_logout)

        # Добавляем растяжку в конце
        layout.addStretch()

        scroll_content.setLayout(layout)
        scroll_area.setWidget(scroll_content)

        # Добавляем scroll_area в контейнер
        container_layout.addWidget(scroll_area)

        # Подключаем сигналы
        self.Ava_Profile.mousePressEvent = self.load_avatar

        # Анимация появления окна
        self.fade_in_animation(Dialog)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def load_user_data(self):
        """Загружает данные пользователя из БД"""
        self.user_data = get_user_info(self.user_id)
        if self.user_data:
            # Обновляем полное имя, если оно отличается
            self.full_name = f"{self.user_data.get('FirstName', '')} {self.user_data.get('LastName', '')}".strip()
            if not self.full_name:
                self.full_name = self.user_data.get('Login', 'Пользователь')

    def load_user_statistics(self):
        """Загружает статистику пользователя из БД"""
        return get_user_statistics(self.user_id)

    def load_user_avatar(self):
        """Загружает аватар пользователя"""
        avatar_path = get_avatar_path_by_user_id(self.user_id)
        if avatar_path and os.path.exists(avatar_path):
            ava_pixmap = QPixmap(avatar_path)
            if not ava_pixmap.isNull():
                self.Ava_Profile.setPixmap(ava_pixmap)
                return
        self.load_standard_avatar()

    def fade_in_animation(self, widget):
        """Анимация появления окна"""
        self.animation = QPropertyAnimation(widget, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        if hasattr(self, 'dialog') and self.dialog:
            main_container = self.dialog.findChild(QFrame, "main_container")
            if main_container:
                main_container.setGeometry(0, 0, self.dialog.width(), self.dialog.height())

    def load_standard_avatar(self):
        """Загрузка стандартного аватара"""
        try:
            # Создаем аватар по умолчанию с градиентом
            placeholder = QPixmap(200, 200)
            placeholder.fill(Qt.transparent)

            painter = QPainter(placeholder)
            painter.setRenderHint(QPainter.Antialiasing)

            # Градиентный фон
            gradient = QLinearGradient(0, 0, 200, 200)
            gradient.setColorAt(0, QColor(76, 175, 80))
            gradient.setColorAt(1, QColor(56, 142, 60))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 200, 200)

            # Буква или иконка
            painter.setPen(Qt.white)
            painter.setFont(QFont("Segoe UI", 80, QFont.Bold))

            if self.full_name:
                initial = self.full_name[0].upper()
            else:
                initial = "👤"

            painter.drawText(placeholder.rect(), Qt.AlignCenter, initial)
            painter.end()

            self.Ava_Profile.setPixmap(placeholder)
        except Exception as e:
            print(f"Ошибка создания аватара: {e}")

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "IT-EcoSystem - Профиль"))

    def open_Ui_Setting_Profil(self):
        self.Dialog = QtWidgets.QDialog()
        self.Dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.Dialog.setAttribute(Qt.WA_TranslucentBackground)
        self.Dialog.setStyleSheet("background-color: transparent;")
        self.ui = Ui_Setting_Profil(self.user_id)
        self.ui.setupUi(self.Dialog)
        self.Dialog.show()

    def load_avatar(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.Ava_Profile.setPixmap(pixmap)
                if update_avatar_in_db(self.user_id, file_path):
                    self.show_message("Успех", "✅ Аватар успешно обновлен!")

                    # Обновляем статистику после изменения аватара
                    self.refresh_statistics()
                else:
                    self.show_message("Ошибка", "❌ Не удалось сохранить аватар", "error")
            else:
                self.show_message("Ошибка", "❌ Не удалось загрузить изображение", "error")

    def refresh_statistics(self):
        """Обновляет статистику на экране"""
        stats = self.load_user_statistics()

        if self.stat_orders:
            self.stat_orders.set_value(stats['orders_count'])
        if self.stat_favorites:
            self.stat_favorites.set_value(stats['favorites_count'])
        if self.stat_days:
            self.stat_days.set_value(stats['days_with_us'])
        if self.stat_bonus:
            self.stat_bonus.set_value(stats['bonus_points'])

    def show_message(self, title, text, msg_type="success"):
        """Уведомление в стиле authorization_window"""
        msg = QMessageBox(self.dialog)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
                border-radius: 15px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 20px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        if msg_type == "error":
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Information)

        msg.exec_()

    def logout(self):
        """Выход из аккаунта"""
        msg = QMessageBox(self.dialog)
        msg.setWindowTitle("Подтверждение")
        msg.setText("Вы действительно хотите выйти из аккаунта?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
                border-radius: 15px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 20px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        reply = msg.exec_()

        if reply == QMessageBox.Yes:
            session.logout()
            self.dialog.close()

    def open_my_orders(self):
        """Открывает окно с заказами клиента"""
        if not session.is_authenticated():
            return

        self.orders_window = ClientOrdersWindow(session.get_user_id(), self.dialog)
        self.orders_window.setModal(True)
        self.orders_window.show()


if __name__ == "__main__":
    import sys

    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    # Установка глобального шрифта
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Применяем темную палитру глобально
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(76, 175, 80))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    # Для теста используем user_id = 1
    dialog = QtWidgets.QDialog()
    ui = Ui_profil(1, "Анна Смирнова")
    ui.setupUi(dialog)
    dialog.show()

    sys.exit(app.exec_())