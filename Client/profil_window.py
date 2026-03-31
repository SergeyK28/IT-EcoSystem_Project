# -*- coding: utf-8 -*-
"""
Модуль окна профиля пользователя
================================
Отображает информацию о пользователе, статистику, позволяет изменять аватар,
просматривать уведомления и управлять аккаунтом.
"""

import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette, QPixmap, QPainter, QPen, QPainterPath, QIcon
from PyQt5.QtWidgets import (
    QGraphicsDropShadowEffect, QLabel, QPushButton, QFrame,
    QMessageBox, QDialog, QFileDialog, QVBoxLayout, QHBoxLayout,
    QScrollArea, QWidget, QSpacerItem, QSizePolicy, QGridLayout
)

# Импорты из модулей сервера
from Server.db import (
    update_avatar_in_db,  # Обновление аватара в БД
    get_avatar_path_by_user_id,  # Получение пути к аватару
    get_user_statistics,  # Получение статистики пользователя
    get_user_info,  # Получение информации о пользователе
    create_user_notification,  # Создание уведомления
    get_user_notifications,  # Получение списка уведомлений
    get_unread_notifications_count,  # Количество непрочитанных уведомлений
    mark_notification_as_read,  # Отметить уведомление как прочитанное
    mark_all_notifications_as_read  # Отметить все уведомления как прочитанные
)
from Setting_profil import Ui_Setting_Profil  # Окно настроек профиля
from session_manager import session  # Менеджер сессий
from client_orders_window import ClientOrdersWindow  # Окно заказов клиента


# ==================== ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ ====================

class ModernLineEdit(QtWidgets.QLineEdit):
    """
    Современное поле ввода с анимацией и стилизацией
    Используется для ввода текста с эффектом при фокусе
    """

    def __init__(self, placeholder: str = "", icon=None, parent=None):
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

        # Добавляем эффект тени
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernButton(QPushButton):
    """
    Современная кнопка с градиентом и анимацией
    primary=True - зеленая кнопка, primary=False - серая кнопка
    """

    def __init__(self, text: str = "", primary: bool = True, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(45)
        self.setCursor(Qt.PointingHandCursor)

        if primary:
            # Основная зеленая кнопка с градиентом
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
            # Вторичная серая кнопка
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
    """
    Карточка статистики с иконкой и значением
    Отображает один статистический показатель (заказы, бонусы и т.д.)
    """

    def __init__(self, icon: str = "📊", title: str = "0", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.title_label = None
        self._setup_ui(icon, title, subtitle)

    def _setup_ui(self, icon: str, title: str, subtitle: str):
        """Настройка интерфейса карточки статистики"""
        self.setMinimumSize(120, 90)
        self.setMaximumHeight(90)

        # Стиль карточки с градиентом
        self.setStyleSheet("""
            StatCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2d2d2d, stop:1 #262626);
                border-radius: 15px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Эффект тени для карточки
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        # Основной горизонтальный layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Контейнер для иконки с фоном
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

        # Иконка внутри контейнера
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
        """Обновляет отображаемое значение в карточке"""
        if self.title_label:
            self.title_label.setText(str(value))


class AvatarWidget(QLabel):
    """
    Виджет аватара пользователя с круглой обрезкой и анимацией при клике
    Поддерживает загрузку нового изображения
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(130, 130)
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)

        # Тень для аватара
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def setPixmap(self, pixmap: QPixmap):
        """
        Устанавливает изображение с круглой обрезкой и красивой рамкой
        """
        if pixmap.isNull():
            return

        # Создаем круглую маску для изображения
        size = min(pixmap.width(), pixmap.height())
        circular_pixmap = QPixmap(size, size)
        circular_pixmap.fill(Qt.transparent)

        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Рисуем круг и обрезаем изображение по кругу
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        # Масштабируем и размещаем изображение
        scaled_pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (size - scaled_pixmap.width()) // 2
        y = (size - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()

        # Добавляем градиентную рамку вокруг аватара
        bordered_pixmap = QPixmap(size + 8, size + 8)
        bordered_pixmap.fill(Qt.transparent)

        painter = QPainter(bordered_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Создаем градиент для рамки
        gradient = QLinearGradient(0, 0, size + 8, size + 8)
        gradient.setColorAt(0, QColor(76, 175, 80))
        gradient.setColorAt(1, QColor(69, 160, 73))

        pen = QPen(QBrush(gradient), 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(2, 2, size + 4, size + 4)

        # Рисуем аватар внутри рамки
        painter.drawPixmap(4, 4, circular_pixmap)
        painter.end()

        super().setPixmap(bordered_pixmap.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        """
        Обработчик клика - анимация сжатия и вызов загрузки аватара
        """
        # Анимация сжатия при нажатии
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(100)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(self.geometry())
        anim.setEndValue(self.geometry().adjusted(5, 5, -5, -5))
        anim.finished.connect(self._reset_avatar_size)
        anim.start()

        # Загружаем новое изображение через родительский виджет
        QTimer.singleShot(100, lambda: self.parent().parent().load_avatar(event))

    def _reset_avatar_size(self):
        """Анимация возврата к исходному размеру"""
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(100)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(self.geometry())
        anim.setEndValue(self.geometry().adjusted(-5, -5, 5, 5))
        anim.start()


# ==================== ОСНОВНОЙ КЛАСС ОКНА ПРОФИЛЯ ====================

class Ui_profil(object):
    """
    Главный класс окна профиля пользователя
    Отображает информацию о пользователе, статистику, уведомления
    Позволяет редактировать профиль и управлять аккаунтом
    """

    def __init__(self, user_id: int, full_name: str):
        """
        Инициализация окна профиля

        Args:
            user_id: ID пользователя в системе
            full_name: Полное имя пользователя
        """
        self.user_id = user_id  # ID текущего пользователя
        self.full_name = full_name  # Полное имя пользователя
        self.dialog = None  # Ссылка на диалоговое окно
        self.main_window = None  # Ссылка на главное окно
        self.user_data = None  # Данные пользователя из БД

        # Виджеты статистики
        self.stat_orders = None  # Карточка с количеством заказов
        self.stat_favorites = None  # Карточка с количеством избранного
        self.stat_days = None  # Карточка с днями активности
        self.stat_bonus = None  # Карточка с бонусными баллами

        # Виджеты контактной информации
        self.contact_phone = None  # Отображение телефона
        self.contact_email = None  # Отображение email

    # ==================== НАСТРОЙКА ИНТЕРФЕЙСА ====================

    def setupUi(self, Dialog):
        """
        Главный метод настройки интерфейса окна профиля
        Создает все виджеты, располагает их, настраивает стили
        """
        self.dialog = Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 750)
        Dialog.setMinimumSize(450, 600)
        Dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        Dialog.setAttribute(Qt.WA_TranslucentBackground)

        # Загружаем данные пользователя из базы данных
        self._load_user_data()

        # ========== ОСНОВНОЙ КОНТЕЙНЕР ==========
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

        # Тень для основного контейнера
        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(30)
        main_shadow.setColor(QColor(0, 0, 0, 150))
        main_shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(main_shadow)

        # Layout для контейнера
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # ========== ОБЛАСТЬ ПРОКРУТКИ ==========
        scroll_area = self._create_scroll_area()
        container_layout.addWidget(scroll_area)

        # ========== ЗАПОЛНЕНИЕ КОНТЕНТА ==========
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignTop)

        # Добавляем все секции в основной layout
        main_layout.addLayout(self._create_top_panel())  # Верхняя панель с кнопками
        main_layout.addLayout(self._create_profile_section())  # Секция профиля (аватар, имя)
        main_layout.addWidget(self._create_stats_section())  # Секция статистики
        main_layout.addWidget(self._create_separator())  # Разделитель
        main_layout.addWidget(self._create_services_section())  # Секция с кнопками услуг
        main_layout.addWidget(self._create_contact_section())  # Секция контактной информации
        main_layout.addWidget(self._create_logout_button())  # Кнопка выхода
        main_layout.addStretch()

        scroll_content.setLayout(main_layout)
        scroll_area.setWidget(scroll_content)

        # Анимация появления окна
        self._fade_in_animation(Dialog)

        # Подключаем обработчики событий
        self._connect_signals()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def _create_scroll_area(self) -> QScrollArea:
        """
        Создает область прокрутки для контента

        Returns:
            QScrollArea: Настроенная область прокрутки
        """
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
        return scroll_area

    def _create_top_panel(self) -> QHBoxLayout:
        """
        Создает верхнюю панель с кнопками закрытия и настроек

        Returns:
            QHBoxLayout: Layout с кнопками
        """
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Кнопка закрытия окна
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
        """)
        self.btn_close.clicked.connect(self.dialog.close)

        # Кнопка быстрых настроек
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
        """)
        self.btn_settings_quick.clicked.connect(self._open_settings_window)

        # Заголовок окна
        title_label = QLabel("Мой профиль")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        top_layout.addWidget(self.btn_close)
        top_layout.addStretch()
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_settings_quick)

        return top_layout

    def _create_profile_section(self) -> QVBoxLayout:
        """
        Создает секцию профиля с аватаром и именем пользователя

        Returns:
            QVBoxLayout: Layout с элементами профиля
        """
        profile_layout = QVBoxLayout()
        profile_layout.setSpacing(15)
        profile_layout.setAlignment(Qt.AlignCenter)

        # Виджет аватара
        self.Ava_Profile = AvatarWidget()
        self._load_user_avatar()  # Загружаем аватар пользователя

        # Метка с именем пользователя
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

        # Статус пользователя (активный клиент)
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

        return profile_layout

    def _create_stats_section(self) -> QWidget:
        """
        Создает секцию со статистикой пользователя

        Returns:
            QWidget: Виджет с карточками статистики
        """
        # Заголовок секции
        stats_title = QLabel("📊 Статистика")
        stats_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 600;
                margin-top: 10px;
            }
        """)

        # Сетка для карточек статистики
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)

        # Получаем статистику из базы данных
        stats = self._load_user_statistics()

        # Создаем карточки статистики
        self.stat_orders = StatCard("📦", str(stats['orders_count']), "Заказов")
        self.stat_favorites = StatCard("❤️", str(stats['favorites_count']), "В избранном")
        self.stat_days = StatCard("📅", str(stats['days_with_us']), "Дней с нами")
        self.stat_bonus = StatCard("🎁", str(stats['bonus_points']), "Бонусов")

        stats_grid.addWidget(self.stat_orders, 0, 0)
        stats_grid.addWidget(self.stat_favorites, 0, 1)
        stats_grid.addWidget(self.stat_days, 1, 0)
        stats_grid.addWidget(self.stat_bonus, 1, 1)

        # Контейнер для заголовка и сетки
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)
        container_layout.addWidget(stats_title)
        container_layout.addLayout(stats_grid)

        return container

    def _create_separator(self) -> QFrame:
        """
        Создает линию-разделитель между секциями

        Returns:
            QFrame: Горизонтальная линия
        """
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
        return separator

    def _create_services_section(self) -> QWidget:
        """
        Создает секцию с кнопками услуг (заказы, уведомления)

        Returns:
            QWidget: Виджет с кнопками
        """
        # Заголовок секции
        services_title = QLabel("🛠️ Мои услуги")
        services_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 600;
                margin-top: 5px;
            }
        """)

        # Кнопка "Мои заказы"
        self.btn_new_order = ModernButton("📋 Мои заказы", True)
        self.btn_new_order.clicked.connect(self._open_my_orders)

        # Кнопка уведомлений
        self.PB_Notification = QPushButton("🔔 Уведомления")
        self.PB_Notification.setMinimumHeight(45)
        self.PB_Notification.setCursor(Qt.PointingHandCursor)
        self.PB_Notification.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #454545;
                color: white;
                border: 2px solid #4CAF50;
            }
        """)

        # Контейнер для кнопок
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)
        container_layout.addWidget(services_title)
        container_layout.addWidget(self.btn_new_order)
        container_layout.addWidget(self.PB_Notification)

        # Настраиваем уведомления
        self._setup_notifications()

        return container

    def _create_contact_section(self) -> QFrame:
        """
        Создает секцию с контактной информацией пользователя

        Returns:
            QFrame: Фрейм с контактами
        """
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

        # Тень для фрейма контактов
        contact_shadow = QGraphicsDropShadowEffect()
        contact_shadow.setBlurRadius(15)
        contact_shadow.setColor(QColor(0, 0, 0, 60))
        contact_shadow.setOffset(0, 3)
        contact_frame.setGraphicsEffect(contact_shadow)

        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setSpacing(12)

        # Заголовок секции
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

        # Блок телефона
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

        # Блок email
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

        return contact_frame

    def _create_logout_button(self) -> QPushButton:
        """
        Создает кнопку выхода из аккаунта

        Returns:
            QPushButton: Кнопка выхода
        """
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
        """)
        self.btn_logout.clicked.connect(self._logout)

        return self.btn_logout

    def _connect_signals(self):
        """Подключает все сигналы к слотам"""
        # Аватар обрабатывает клик самостоятельно через mousePressEvent
        pass

    def retranslateUi(self, Dialog):
        """Устанавливает заголовок окна"""
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "IT-EcoSystem - Профиль"))

    # ==================== РАБОТА С ДАННЫМИ ====================

    def _load_user_data(self):
        """
        Загружает данные пользователя из базы данных
        Обновляет полное имя, если данные изменились
        """
        self.user_data = get_user_info(self.user_id)
        if self.user_data:
            # Обновляем полное имя, если оно отличается от сохраненного
            new_full_name = f"{self.user_data.get('FirstName', '')} {self.user_data.get('LastName', '')}".strip()
            if new_full_name and new_full_name != self.full_name:
                self.full_name = new_full_name

    def _load_user_statistics(self) -> Dict[str, Any]:
        """
        Загружает статистику пользователя из базы данных

        Returns:
            Dict[str, Any]: Словарь со статистикой (заказы, избранное, дни, бонусы)
        """
        return get_user_statistics(self.user_id)

    def _load_user_avatar(self):
        """
        Загружает аватар пользователя из базы данных
        Если аватар не найден, устанавливает стандартный
        """
        avatar_path = get_avatar_path_by_user_id(self.user_id)
        if avatar_path and os.path.exists(avatar_path):
            ava_pixmap = QPixmap(avatar_path)
            if not ava_pixmap.isNull():
                self.Ava_Profile.setPixmap(ava_pixmap)
                return
        self._set_standard_avatar()

    def _set_standard_avatar(self):
        """
        Создает и устанавливает стандартный аватар
        Генерирует круглый градиентный аватар с первой буквой имени
        """
        try:
            # Создаем пустое изображение
            placeholder = QPixmap(200, 200)
            placeholder.fill(Qt.transparent)

            painter = QPainter(placeholder)
            painter.setRenderHint(QPainter.Antialiasing)

            # Рисуем градиентный круг
            gradient = QLinearGradient(0, 0, 200, 200)
            gradient.setColorAt(0, QColor(76, 175, 80))
            gradient.setColorAt(1, QColor(56, 142, 60))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 200, 200)

            # Добавляем инициал пользователя
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
            print(f"Ошибка создания стандартного аватара: {e}")

    # ==================== УВЕДОМЛЕНИЯ ====================

    def _setup_notifications(self):
        """
        Настраивает систему уведомлений:
        - Подключает обработчик клика по кнопке
        - Обновляет счетчик непрочитанных уведомлений
        """
        if not hasattr(self, 'PB_Notification'):
            return

        self.PB_Notification.clicked.connect(self._open_notifications_window)
        self._update_notification_badge()

    def _update_notification_badge(self):
        """
        Обновляет бейдж с количеством непрочитанных уведомлений
        Меняет текст и стиль кнопки в зависимости от наличия новых уведомлений
        """
        if not hasattr(self, 'PB_Notification'):
            return

        try:
            count = get_unread_notifications_count(self.user_id)

            if count > 0:
                # Есть непрочитанные уведомления - показываем счетчик и зеленую кнопку
                self.PB_Notification.setText(f"🔔 Уведомления ({count})")
                self.PB_Notification.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
            else:
                # Нет новых уведомлений - стандартный вид
                self.PB_Notification.setText("🔔 Уведомления")
                self.PB_Notification.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a3a;
                        color: #b0b0b0;
                        border: 2px solid #4a4a4a;
                        border-radius: 8px;
                        padding: 12px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #454545;
                        color: white;
                        border: 2px solid #4CAF50;
                    }
                """)
        except Exception as e:
            print(f"Ошибка обновления бейджа уведомлений: {e}")

    def _open_notifications_window(self):
        """
        Открывает окно со списком всех уведомлений пользователя
        Содержит список уведомлений с возможностью отметить как прочитанные
        """
        dialog = QDialog(self.dialog)
        dialog.setWindowTitle("Мои уведомления")
        dialog.setMinimumSize(500, 600)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setStyleSheet("background-color: transparent;")

        # Основной контейнер с тенью
        container = QFrame(dialog)
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 20px;
                border: 1px solid #3a3a3a;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)

        # Основной layout контейнера
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        # Верхняя панель с заголовком и кнопками
        header_layout = QHBoxLayout()

        title_label = QLabel("📬 Уведомления")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")

        # Кнопка "Прочитать все"
        read_all_btn = QPushButton("✓ Прочитать все")
        read_all_btn.setCursor(Qt.PointingHandCursor)
        read_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        read_all_btn.clicked.connect(lambda: self._mark_all_notifications_read(dialog))

        # Кнопка закрытия
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        close_btn.clicked.connect(dialog.close)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(read_all_btn)
        header_layout.addWidget(close_btn)
        container_layout.addLayout(header_layout)

        # Область прокрутки для списка уведомлений
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
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

        notifications_widget = QWidget()
        notifications_widget.setStyleSheet("background-color: transparent;")
        notifications_layout = QVBoxLayout(notifications_widget)
        notifications_layout.setSpacing(10)
        notifications_layout.setAlignment(Qt.AlignTop)

        # Загружаем список уведомлений
        self._load_notifications_list(notifications_layout, dialog)

        scroll_area.setWidget(notifications_widget)
        container_layout.addWidget(scroll_area)

        # Размещаем контейнер в диалоге
        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(container)
        main_layout.setContentsMargins(10, 10, 10, 10)

        dialog.exec_()

        # После закрытия обновляем счетчик уведомлений
        self._update_notification_badge()

    def _load_notifications_list(self, layout: QVBoxLayout, dialog: QDialog):
        """
        Загружает список уведомлений из базы данных и отображает их

        Args:
            layout: Layout для размещения уведомлений
            dialog: Диалоговое окно (для контекста)
        """
        # Очищаем существующие элементы
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            notifications = get_user_notifications(self.user_id, limit=50, include_read=True)

            if not notifications:
                # Нет уведомлений - показываем пустое сообщение
                empty_label = QLabel("📭 У вас пока нет уведомлений")
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setStyleSheet("color: #808080; font-size: 16px; padding: 50px;")
                layout.addWidget(empty_label)
                return

            # Создаем виджет для каждого уведомления
            for notif in notifications:
                notif_widget = self._create_notification_widget(notif, dialog)
                layout.addWidget(notif_widget)

            layout.addStretch()

        except Exception as e:
            print(f"Ошибка загрузки уведомлений: {e}")
            error_label = QLabel(f"❌ Ошибка загрузки: {e}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #ff6b6b; padding: 20px;")
            layout.addWidget(error_label)

    def _create_notification_widget(self, notification: Dict[str, Any], dialog: QDialog) -> QFrame:
        """
        Создает виджет для отображения одного уведомления

        Args:
            notification: Словарь с данными уведомления
            dialog: Диалоговое окно (для контекста)

        Returns:
            QFrame: Виджет уведомления
        """
        widget = QFrame()
        widget.setCursor(Qt.PointingHandCursor)

        # Стиль зависит от того, прочитано уведомление или нет
        if notification.get('IsRead'):
            # Прочитанное уведомление - серый фон
            widget.setStyleSheet("""
                QFrame {
                    background-color: #2a2a2a;
                    border-radius: 12px;
                    border: 1px solid #3a3a3a;
                    padding: 12px;
                }
                QFrame:hover {
                    background-color: #323232;
                    border: 1px solid #4CAF50;
                }
            """)
        else:
            # Непрочитанное уведомление - выделено зеленой полосой слева
            widget.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border-radius: 12px;
                    border-left: 4px solid #4CAF50;
                    border-top: 1px solid #3a3a3a;
                    border-right: 1px solid #3a3a3a;
                    border-bottom: 1px solid #3a3a3a;
                    padding: 12px;
                }
                QFrame:hover {
                    background-color: #353535;
                    border-left: 4px solid #45a049;
                }
            """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # Верхняя строка: заголовок и дата
        header_layout = QHBoxLayout()

        # Иконка в зависимости от типа уведомления
        icon_map = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'order': '📦',
            'promo': '🎁'
        }
        icon = icon_map.get(notification.get('Type', 'info'), '🔔')

        title_label = QLabel(f"{icon} {notification.get('Title', 'Уведомление')}")
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")

        date_label = QLabel(notification.get('CreatedAtFormatted', ''))
        date_label.setStyleSheet("color: #808080; font-size: 11px;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(date_label)

        # Текст сообщения
        message_label = QLabel(notification.get('Message', ''))
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #c0c0c0; font-size: 13px; line-height: 1.4;")

        layout.addLayout(header_layout)
        layout.addWidget(message_label)

        # Индикатор "Новое" для непрочитанных уведомлений
        if not notification.get('IsRead'):
            unread_indicator = QLabel("● Новое")
            unread_indicator.setStyleSheet("color: #4CAF50; font-size: 10px; font-weight: bold;")
            layout.addWidget(unread_indicator, alignment=Qt.AlignRight)

        # Обработчик клика по уведомлению
        def on_click():
            if not notification.get('IsRead'):
                # Отмечаем уведомление как прочитанное
                mark_notification_as_read(notification['NotificationID'], self.user_id)
                # Обновляем стиль виджета
                widget.setStyleSheet("""
                    QFrame {
                        background-color: #2a2a2a;
                        border-radius: 12px;
                        border: 1px solid #3a3a3a;
                        padding: 12px;
                    }
                    QFrame:hover {
                        background-color: #323232;
                        border: 1px solid #4CAF50;
                    }
                """)
                # Удаляем индикатор "Новое"
                if 'unread_indicator' in locals() and unread_indicator.parent():
                    unread_indicator.deleteLater()
                # Обновляем счетчик уведомлений
                self._update_notification_badge()

        widget.mousePressEvent = lambda event: on_click()

        return widget

    def _mark_all_notifications_read(self, dialog: QDialog):
        """
        Отмечает все уведомления пользователя как прочитанные

        Args:
            dialog: Диалоговое окно для обновления списка
        """
        try:
            count = mark_all_notifications_as_read(self.user_id)
            if count > 0:
                # Обновляем список уведомлений в окне
                notifications_layout = dialog.findChild(QVBoxLayout)
                if notifications_layout:
                    self._load_notifications_list(notifications_layout, dialog)
                self._update_notification_badge()
        except Exception as e:
            print(f"Ошибка отметки всех уведомлений: {e}")

    # ==================== ДЕЙСТВИЯ ПОЛЬЗОВАТЕЛЯ ====================

    def load_avatar(self, event):
        """
        Загружает новый аватар через диалог выбора файла

        Args:
            event: Событие клика
        """
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
                    self._show_message("Успех", "✅ Аватар успешно обновлен!")
                    self._refresh_statistics()
                else:
                    self._show_message("Ошибка", "❌ Не удалось сохранить аватар", "error")
            else:
                self._show_message("Ошибка", "❌ Не удалось загрузить изображение", "error")

    def _refresh_statistics(self):
        """
        Обновляет отображаемую статистику после изменений в профиле
        """
        stats = self._load_user_statistics()

        if self.stat_orders:
            self.stat_orders.set_value(stats['orders_count'])
        if self.stat_favorites:
            self.stat_favorites.set_value(stats['favorites_count'])
        if self.stat_days:
            self.stat_days.set_value(stats['days_with_us'])
        if self.stat_bonus:
            self.stat_bonus.set_value(stats['bonus_points'])

    def _show_message(self, title: str, text: str, msg_type: str = "success"):
        """
        Показывает всплывающее сообщение в стиле приложения

        Args:
            title: Заголовок сообщения
            text: Текст сообщения
            msg_type: Тип сообщения ("success" или "error")
        """
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

    def _logout(self):
        """
        Выход из аккаунта с подтверждением
        Закрывает окно профиля и очищает сессию
        """
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

    def _open_my_orders(self):
        """
        Открывает окно с заказами текущего пользователя
        """
        if not session.is_authenticated():
            return

        self.orders_window = ClientOrdersWindow(session.get_user_id(), self.dialog)
        self.orders_window.setModal(True)
        self.orders_window.show()

    def _open_settings_window(self):
        """
        Открывает окно настроек профиля (изменение личных данных, пароля)
        """
        self.Dialog = QtWidgets.QDialog()
        self.Dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.Dialog.setAttribute(Qt.WA_TranslucentBackground)
        self.Dialog.setStyleSheet("background-color: transparent;")
        self.ui = Ui_Setting_Profil(self.user_id)
        self.ui.setupUi(self.Dialog)
        self.Dialog.show()

    # ==================== АНИМАЦИИ ====================

    def _fade_in_animation(self, widget):
        """
        Анимация плавного появления окна

        Args:
            widget: Виджет для анимации
        """
        self.animation = QPropertyAnimation(widget, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def resizeEvent(self, event):
        """
        Обработчик изменения размера окна
        Обновляет размер основного контейнера

        Args:
            event: Событие изменения размера
        """
        super().resizeEvent(event)
        if hasattr(self, 'dialog') and self.dialog:
            main_container = self.dialog.findChild(QFrame, "main_container")
            if main_container:
                main_container.setGeometry(0, 0, self.dialog.width(), self.dialog.height())


# ==================== ТОЧКА ВХОДА ДЛЯ ТЕСТИРОВАНИЯ ====================

if __name__ == "__main__":
    """
    Блок для автономного тестирования окна профиля
    Запускается только при прямом запуске файла
    """
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