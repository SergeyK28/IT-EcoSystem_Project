# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox

from Client.favorites_window import FavoritesWindow
from Client.search_widget import SearchResultsWidget
from session_manager import session
from authorization_window import AuthDialog
from Client.Remont_windows.remont_telefonov import Ui_Ui_Remont_Telefonov_Dialog
from Client.Remont_windows.remont_laptop import Ui_Ui_Remont_Laptop_Dialog
from shop_window import ShopWindow
from profil_window import Ui_profil
from cart_window import CartWindow
from Server import db
from Server import db_crm



class Ui_main_window_Dialog(object):
    def setupUi(self, main_window_Dialog):
        main_window_Dialog.setObjectName("main_window_Dialog")
        main_window_Dialog.resize(1200, 950)

        # Настройка иконки
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Pictures/Screenshot from 2025-09-15 14-30-16.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        main_window_Dialog.setWindowIcon(icon)

        # Главный градиентный фон
        main_window_Dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #232323, stop:1 #1a1a1a);
            }
        """)

        self.gridLayout_2 = QtWidgets.QGridLayout(main_window_Dialog)
        self.gridLayout_2.setContentsMargins(20, 20, 20, 20)
        self.gridLayout_2.setSpacing(15)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # ========== ВЕРХНЯЯ ПАНЕЛЬ (АДРЕС И РАБОТА) ==========
        self.top_info_frame = QtWidgets.QFrame(main_window_Dialog)
        self.top_info_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 5px;
            }
        """)

        # Добавляем тень для верхней панели
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.top_info_frame.setGraphicsEffect(shadow)

        top_layout = QtWidgets.QHBoxLayout(self.top_info_frame)
        top_layout.setContentsMargins(15, 8, 15, 8)

        self.Adres = QtWidgets.QLabel("🗺️ Красноярск, Улица Микуцкого, 12")
        self.Adres.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
                font-weight: 400;
                padding: 5px;
            }
        """)

        self.Work = QtWidgets.QLabel("📅 Пн-Пт: 10:00-20:00 | Сб-Вс: 12:00-19:00")
        self.Work.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
                font-weight: 400;
                padding: 5px;
            }
        """)

        top_layout.addWidget(self.Adres)
        top_layout.addStretch()
        top_layout.addWidget(self.Work)

        self.gridLayout_2.addWidget(self.top_info_frame, 0, 0, 1, 1)

        # ========== ХЕДЕР С ЛОГОТИПОМ И ПОИСКОМ ==========
        self.header_frame = QtWidgets.QFrame(main_window_Dialog)
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 10px;
            }
        """)

        # Тень для хедера
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(20)
        header_shadow.setColor(QColor(0, 0, 0, 100))
        header_shadow.setOffset(0, 4)
        self.header_frame.setGraphicsEffect(header_shadow)

        header_layout = QtWidgets.QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(20)

        # Логотип
        self.Logo_PushButton = QtWidgets.QPushButton("IT-EcoSystem")
        self.Logo_PushButton.setMinimumSize(180, 60)
        self.Logo_PushButton.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 20px;
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

        # Поиск
        self.Search = QtWidgets.QLineEdit()
        self.Search.setPlaceholderText("🔍 Поиск услуг, товаров...")
        self.Search.setMinimumHeight(45)
        self.Search.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border: 2px solid #4a4a4a;
                border-radius: 22px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #404040;
            }
            QLineEdit:hover {
                background-color: #424242;
            }
        """)

        # Кнопки действий
        button_style = """
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #404040;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """

        self.Shop_PushButton = QtWidgets.QPushButton("🏪 Магазины")
        self.Shop_PushButton.setStyleSheet(button_style)
        self.Shop_PushButton.clicked.connect(self.open_shop_window)

        self.Favourites_PushButton = QtWidgets.QPushButton("❤️ Избранное")
        self.Favourites_PushButton.setStyleSheet(button_style)

        self.Favourites_PushButton.clicked.connect(self.open_favorites_window)

        self.Basket_PushButton = QtWidgets.QPushButton("🛒 Корзина")
        self.Basket_PushButton.setStyleSheet(button_style)
        self.Basket_PushButton.clicked.connect(self.open_cart_window)

        self.auth_container = QtWidgets.QWidget()
        auth_layout = QtWidgets.QHBoxLayout(self.auth_container)
        auth_layout.setContentsMargins(0, 0, 0, 0)

        self.Enter_PushButton = QtWidgets.QPushButton("👤 Войти")
        self.Enter_PushButton.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #4CAF50, stop:1 #45a049);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 25px;
                        font-size: 14px;
                        font-weight: bold;
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

        # Кнопка профиля (изначально скрыта)
        self.Profile_PushButton = QtWidgets.QPushButton("👤 Профиль")
        self.Profile_PushButton.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #4CAF50, stop:1 #45a049);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 25px;
                        font-size: 14px;
                        font-weight: bold;
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
        self.Profile_PushButton.hide()
        session.set_main_window(main_window_Dialog)

        auth_layout.addWidget(self.Enter_PushButton)
        auth_layout.addWidget(self.Profile_PushButton)

        header_layout.addWidget(self.Logo_PushButton)
        header_layout.addWidget(self.Search, 1)
        header_layout.addWidget(self.Shop_PushButton)
        header_layout.addWidget(self.Favourites_PushButton)
        header_layout.addWidget(self.Basket_PushButton)
        header_layout.addWidget(self.auth_container)
        self.Enter_PushButton.clicked.connect(self.open_auth_window)
        self.Profile_PushButton.clicked.connect(self.open_profile_window)
        if session.is_authenticated():
            self.update_login_button()

        self.gridLayout_2.addWidget(self.header_frame, 1, 0, 1, 1)

        # ========== НАВИГАЦИОННОЕ МЕНЮ ==========
        self.nav_frame = QtWidgets.QFrame(main_window_Dialog)
        self.nav_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 5px;
            }
        """)

        nav_layout = QtWidgets.QHBoxLayout(self.nav_frame)
        nav_layout.setContentsMargins(10, 5, 10, 5)
        nav_layout.setSpacing(5)

        nav_button_style = """
            QPushButton {
                background-color: transparent;
                color: #d0d0d0;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #404040;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """

        nav_buttons = [
            ("🔧 Услуги", "Service_pushButton"),
            ("О нас!", "About_pushButton"),
            ("⭐ Отзывы", "Reviews_pushButton"),
            ("📞 Контакты", "Contacts_pushButton")
        ]

        for text, attr_name in nav_buttons:
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet(nav_button_style)
            setattr(self, attr_name, btn)
            nav_layout.addWidget(btn)

        self.gridLayout_2.addWidget(self.nav_frame, 2, 0, 1, 1)

        # ========== ОСНОВНОЙ КОНТЕНТ ==========
        self.scrollArea = QtWidgets.QScrollArea(main_window_Dialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("""
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
            QScrollBar::handle:vertical:hover {
                background-color: #45a049;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setStyleSheet("background-color: transparent;")
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)
        self.gridLayout.setSpacing(30)

        # ========== НАШИ УСЛУГИ ==========
        self.Our_services = QtWidgets.QLabel("Наши услуги")
        self.Our_services.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        self.gridLayout.addWidget(self.Our_services, 0, 0, 1, 1, Qt.AlignLeft)

        # Создаем сетку для услуг
        services_grid = QtWidgets.QGridLayout()
        services_grid.setSpacing(25)

        # ===== РЕМОНТ ЦИФРОВОЙ ТЕХНИКИ =====
        digital_frame = self.create_service_category(
            "💻 Ремонт цифровой техники",
            [
                ("📱 Телефон", "Smartphone_pushButton", self.open_remont_telefonov),
                ("💻 Ноутбук", "Laptop_pushButton", self.open_remont_laptop),
                ("📟 Планшет", "Tablet_pushButton", None),
                ("📖 Эл. книги", "Ebook_pushButton", None),
                ("📸 Фотоаппарат", "PhotoCamera_pushButton", None),
                ("📺 Телевизор", "TV_pushButton", None),
                ("🎮 Игр. приставка", "GameConsole_pushButton", None),
                ("📽️ Проектор", "Projector_pushButton", None)
            ]
        )
        services_grid.addWidget(digital_frame, 0, 0)

        # ===== РЕМОНТ БЫТОВОЙ ТЕХНИКИ =====
        household_frame = self.create_service_category(
            "🏠 Ремонт бытовой техники",
            [
                ("🧹 Пылесосы", "Vacuum_Cleaner_pushButton", None),
                ("☕ Кофемашины", "Coffee_Machine_pushButton", None),
                ("🌀 Вентиляторы", "Fan_pushButton", None)
            ]
        )
        services_grid.addWidget(household_frame, 0, 1)

        # ===== РЕМОНТ ВИДЕОТЕХНИКИ =====
        video_frame = self.create_service_category(
            "🎥 Ремонт видеотехники",
            [
                ("📹 Видеонаблюдение", "Security_Camera_pushButton", None),
                ("👶 Видеоняня", "Video_Babysitter_pushButton", None),
                ("📼 Видеорегистратор", "DVR_pushButton", None)
            ]
        )
        services_grid.addWidget(video_frame, 1, 0)

        # ===== РЕМОНТ АУДИОТЕХНИКИ =====
        audio_frame = self.create_service_category(
            "🎵 Ремонт аудиотехники",
            [
                ("🔊 Сабвуферы", "Subwoofer_pushButton", None),
                ("🎵 Колонки", "Columns_pushButton", None),
                ("🎚️ Усилители", "Sound_amplifier_pushButton", None)
            ]
        )
        services_grid.addWidget(audio_frame, 1, 1)

        self.gridLayout.addLayout(services_grid, 1, 0)

        # ========== БЛОК "О НАС" ==========
        about_frame = QtWidgets.QFrame()
        about_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #323232);
                border-radius: 20px;
                padding: 30px;
            }
        """)

        about_layout = QtWidgets.QVBoxLayout(about_frame)

        about_title = QtWidgets.QLabel("Ремонт техники любых видов")
        about_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        about_text = QtWidgets.QLabel(
            "Жизнь современного человека невозможно представить без электроники, "
            "и ее выход из строя очень часто чреват не только личными неудобствами, "
            "но и материальными потерями. Сервисный центр «IT-EcoSystem» гарантирует "
            "выполнение услуг на высоком профессиональном уровне и точно в оговоренные сроки."
        )
        about_text.setWordWrap(True)
        about_text.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 16px;
                line-height: 1.6;
                padding: 10px 0;
            }
        """)

        about_layout.addWidget(about_title)
        about_layout.addWidget(about_text)

        self.gridLayout.addWidget(about_frame, 2, 0)

        # ========== НАШИ ПРЕИМУЩЕСТВА ==========
        advantages_title = QtWidgets.QLabel("Наши преимущества")
        advantages_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                padding: 20px 0 10px 0;
            }
        """)
        self.gridLayout.addWidget(advantages_title, 3, 0)

        advantages_grid = QtWidgets.QGridLayout()
        advantages_grid.setSpacing(20)

        advantages = [
            ("👨‍🔧 Профессионализм",
             "Опытные мастера с многолетним стажем",
             "Professional_pushButton"),
            ("⚡ Любая сложность",
             "Ремонтируем технику любой сложности",
             "Complexity_pushButton"),
            ("🔧 Оборудование",
             "Современное диагностическое оборудование",
             "Equipment_pushButton"),
            ("🚀 Быстро",
             "Срочный ремонт за 1 час",
             "Quickly_pushButton"),
            ("💰 Доступно",
             "Адекватные цены и скидки",
             "Available_pushButton"),
            ("✅ Гарантия",
             "Гарантия на все виды работ",
             "pushButton_34")
        ]

        for i, (title, desc, attr) in enumerate(advantages):
            row, col = divmod(i, 3)
            adv_card = self.create_advantage_card(title, desc)
            setattr(self, attr, adv_card.findChild(QtWidgets.QPushButton))
            advantages_grid.addWidget(adv_card, row, col)

        self.gridLayout.addLayout(advantages_grid, 4, 0)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea, 3, 0, 1, 1)

        # Подключаем сигналы
        self.Enter_PushButton.clicked.connect(self.open_auth_window)
        if hasattr(self, 'Laptop_pushButton'):
            self.Laptop_pushButton.clicked.connect(self.open_remont_laptop)
        if hasattr(self, 'Smartphone_pushButton'):
            self.Smartphone_pushButton.clicked.connect(self.open_remont_telefonov)

        # Настраиваем поиск
        self.setup_search()

        QtCore.QMetaObject.connectSlotsByName(main_window_Dialog)

        self.setup_navigation_buttons()
        self.setup_advantages_buttons()

    def create_service_category(self, title, buttons_data):
        """Создает карточку категории услуг"""
        frame = QtWidgets.QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 15px;
                padding: 20px;
            }
            QFrame:hover {
                background-color: #333333;
                border: 1px solid #4CAF50;
            }
        """)

        # Тень для карточки
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        frame.setGraphicsEffect(shadow)

        layout = QtWidgets.QVBoxLayout(frame)

        # Заголовок
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 20px;
                font-weight: bold;
                padding-bottom: 15px;
            }
        """)
        layout.addWidget(title_label)

        # Сетка кнопок
        buttons_layout = QtWidgets.QGridLayout()
        buttons_layout.setSpacing(10)

        for i, (text, attr_name, callback) in enumerate(buttons_data):
            row, col = divmod(i, 4)
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 15px;
                    font-size: 13px;
                    font-weight: 500;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #4CAF50;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: #45a049;
                }
            """)
            setattr(self, attr_name, btn)
            if callback:
                btn.clicked.connect(callback)
            buttons_layout.addWidget(btn, row, col)

        layout.addLayout(buttons_layout)
        layout.addStretch()

        return frame

    def create_advantage_card(self, title, description):
        """Создает карточку преимущества"""
        card = QtWidgets.QFrame()
        card.setMinimumSize(250, 150)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d2d, stop:1 #262626);
                border-radius: 12px;
                padding: 20px;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #333333, stop:1 #2d2d2d);
                border: 1px solid #4CAF50;
            }
        """)

        # Тень для карточки
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        layout = QtWidgets.QVBoxLayout(card)

        btn = QtWidgets.QPushButton(title)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        desc_label = QtWidgets.QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
                padding: 5px 0;
            }
        """)

        layout.addWidget(btn)
        layout.addWidget(desc_label)
        layout.addStretch()

        return card

    def update_login_button(self):
        """Обновляет отображение кнопки входа/профиля"""
        if session.is_authenticated():
            # Пользователь авторизован - показываем кнопку профиля
            self.Enter_PushButton.hide()
            user_name = session.get_user_name()
            if user_name:
                # Показываем только первое слово (имя)
                short_name = user_name.split()[0] if user_name else "Профиль"
                self.Profile_PushButton.setText(f"👤 {short_name}")
            else:
                self.Profile_PushButton.setText("👤 Профиль")
            self.Profile_PushButton.show()
        else:
            # Пользователь не авторизован - показываем кнопку входа
            self.Profile_PushButton.hide()
            self.Enter_PushButton.show()

    def open_auth_window(self):
        """Открывает окно авторизации"""
        self.Dialog = QtWidgets.QDialog()
        self.ui = AuthDialog()
        self.ui.setupUi(self.Dialog)
        # Подключаем сигнал закрытия для обновления кнопки
        self.Dialog.finished.connect(self.check_auth_result)
        self.Dialog.show()

    def check_auth_result(self, result):
        """Проверяет результат авторизации"""
        if session.is_authenticated():
            self.update_login_button()

    def open_profile_window(self):
        """Открывает окно профиля"""
        if session.is_authenticated():
            self.Dialog = QtWidgets.QDialog()
            self.ui = Ui_profil(session.get_user_id(), session.get_user_name())
            # Передаем ссылку на главное окно
            self.ui.main_window = self
            self.ui.setupUi(self.Dialog)
            # Подключаем сигнал закрытия для обновления кнопки при выходе
            self.Dialog.finished.connect(self.update_login_button)
            self.Dialog.show()

    def open_remont_telefonov(self):
        self.Dialog = QtWidgets.QDialog()
        self.ui = Ui_Ui_Remont_Telefonov_Dialog()
        self.ui.setupUi(self.Dialog)
        self.Dialog.show()

    def open_remont_laptop(self):
        self.Dialog = QtWidgets.QDialog()
        self.ui = Ui_Ui_Remont_Laptop_Dialog()
        self.ui.setupUi(self.Dialog)
        self.Dialog.show()

    def open_shop_window(self):
        self.shop_dialog = QtWidgets.QDialog()
        self.shop_ui = ShopWindow()
        self.shop_ui.setupUi(self.shop_dialog)
        self.shop_dialog.exec_()

    def open_cart_window(self):
        """Открывает окно корзины"""
        if not session.is_authenticated():
            # Если пользователь не авторизован, показываем сообщение
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Требуется авторизация")
            msg_box.setText("🔐 Войдите в аккаунт для просмотра корзины")
            msg_box.setIcon(QMessageBox.Information)

            login_btn = msg_box.addButton("Войти", QMessageBox.AcceptRole)
            cancel_btn = msg_box.addButton("Отмена", QMessageBox.RejectRole)

            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: rgb(47, 47, 47);
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: rgb(103, 155, 118);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
            """)

            result = msg_box.exec_()

            if msg_box.clickedButton() == login_btn:
                self.open_auth_window()
            return

        # Если авторизован - открываем корзину
        try:
            self.cart_dialog = CartWindow()
            self.cart_dialog.exec_()
        except Exception as e:
            print(f"Ошибка открытия корзины: {e}")
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Не удалось открыть корзину: {e}"
            )

    def setup_search(self):
        """Настраивает функционал поиска"""
        # Создаем виджет результатов поиска
        self.search_results = SearchResultsWidget(self.header_frame)
        self.search_results.hide()
        self.search_results.result_selected.connect(self.on_search_result_clicked)

        # Поднимаем виджет на передний план
        self.search_results.raise_()

        # Устанавливаем атрибуты для правильного отображения
        self.search_results.setAttribute(Qt.WA_ShowWithoutActivating)

        # Таймер для debounce
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(500)
        self.search_timer.timeout.connect(self.perform_search)

        # Подключаем сигналы
        self.Search.textChanged.connect(self.on_search_text_changed)
        self.Search.returnPressed.connect(self.perform_search)

    def on_search_text_changed(self, text):
        """Обработчик изменения текста поиска"""
        if len(text) >= 2:  # Начинаем поиск при 2+ символах
            self.search_timer.start()
        else:
            self.search_results.hide()

    def perform_search(self):
        """Выполняет поиск"""
        search_text = self.Search.text().strip()

        if len(search_text) < 2:
            return

        # Показываем индикатор загрузки
        self.search_results.show_loading()
        self.update_search_results_position()
        self.search_results.show()

        # Выполняем поиск в БД
        import threading
        def search_thread():
            try:
                # Используем db.search_products_and_services
                results = db.search_products_and_services(search_text)

                # Сохраняем запрос если авторизован
                if session.is_authenticated():
                    db.save_search_query(search_text, session.get_user_id())

                # Используем сигнал вместо invokeMethod
                self.search_results.show_results_signal.emit(results)

            except Exception as e:
                print(f"Ошибка в потоке поиска: {e}")
                # В случае ошибки показываем пустые результаты
                self.search_results.show_results_signal.emit({'services': [], 'parts': [], 'categories': []})

        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()

    def update_search_results_position(self):
        """Обновляет позицию виджета результатов"""
        if not hasattr(self, 'search_results'):
            return

        # Получаем глобальные координаты поля поиска
        search_rect = self.Search.rect()
        global_pos = self.Search.mapToGlobal(search_rect.topLeft())

        # Конвертируем в координаты относительно header_frame
        local_pos = self.header_frame.mapFromGlobal(global_pos)

        # Устанавливаем геометрию виджета
        self.search_results.setGeometry(
            local_pos.x(),
            self.Search.height() + 5,
            self.Search.width(),
            0
        )

        # Поднимаем на передний план при каждом обновлении позиции
        self.search_results.raise_()
        self.search_results.show()  # Убеждаемся, что виджет показан

    def on_search_focus_out(self, event):
        """Обработчик потери фокуса полем поиска"""
        # Вызываем оригинальный обработчик
        if hasattr(self, 'original_focus_out') and self.original_focus_out:
            self.original_focus_out(event)

        # Проверяем, не кликнули ли по результатам поиска
        if hasattr(self, 'search_results') and self.search_results.isVisible():
            # Проверяем, находится ли мышь над результатами
            if not self.search_results.underMouse():
                # Задержка перед скрытием
                QTimer.singleShot(200, self.search_results.hide)

    def on_search_result_clicked(self, result):
        """Обработчик клика по результату поиска"""
        # Скрываем результаты
        self.search_results.hide()

        # Очищаем поле поиска (опционально)
        # self.Search.clear()

        result_type = result.get('type')

        if result_type == 'service':
            # Открываем окно услуги
            self.open_service_window(result)
        elif result_type == 'part':
            # Открываем окно товара
            self.open_part_window(result)
        elif result_type == 'category':
            # Показываем все услуги категории
            self.show_category_results(result.get('name'))

    def open_service_window(self, service_data):
        """Открывает окно услуги"""
        # Здесь можно открыть окно с деталями услуги
        # Например, окно ремонта телефона с предзаполненными данными
        if "телефон" in service_data.get('name', '').lower():
            self.open_remont_telefonov()
        elif "ноутбук" in service_data.get('name', '').lower():
            self.open_remont_laptop()
        else:
            # Для других услуг можно показать сообщение
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "Услуга",
                f"Вы выбрали: {service_data.get('name')}\n"
                f"Стоимость: {service_data.get('price', 0)} ₽"
            )

    def open_part_window(self, part_data):
        """Открывает окно товара"""
        if session.is_authenticated():
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                None,
                "Добавление в корзину",
                f"Добавить '{part_data.get('name')}' в корзину?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Добавляем в корзину
                cart_item = {
                    'device_type': part_data.get('category', 'Запчасть'),
                    'device_brand': part_data.get('brand', ''),
                    'device_model': part_data.get('name', ''),
                    'reason': 'Покупка запчасти',
                    'price': float(part_data.get('price', 0))
                }

                # Используем db_crm для корзины (это специфично для CRM)
                from Server import db_crm
                if db_crm.add_to_cart_db(session.get_user_id(), cart_item):
                    QMessageBox.information(None, "Успех", "✅ Товар добавлен в корзину")
                else:
                    QMessageBox.warning(None, "Ошибка", "❌ Не удалось добавить товар в корзину")
        else:
            # Предлагаем авторизоваться
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Требуется авторизация")
            msg.setText("Для добавления товаров в корзину необходимо войти в аккаунт")
            msg.setIcon(QMessageBox.Information)
            msg.addButton("Войти", QMessageBox.AcceptRole)
            msg.addButton("Отмена", QMessageBox.RejectRole)

            if msg.exec_() == 0:  # Нажали "Войти"
                self.open_auth_window()

    def open_favorites_window(self):
        """Открывает окно избранного"""
        if not session.is_authenticated():
            # Если пользователь не авторизован, показываем сообщение
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Требуется авторизация")
            msg_box.setText("🔐 Войдите в аккаунт для просмотра избранного")
            msg_box.setIcon(QMessageBox.Information)

            login_btn = msg_box.addButton("Войти", QMessageBox.AcceptRole)
            cancel_btn = msg_box.addButton("Отмена", QMessageBox.RejectRole)

            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                    color: white;
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

            result = msg_box.exec_()

            if msg_box.clickedButton() == login_btn:
                self.open_auth_window()
            return

        # Если авторизован - открываем окно избранного
        try:
            self.favorites_dialog = FavoritesWindow(self)
            self.favorites_dialog.exec_()
        except Exception as e:
            print(f"Ошибка открытия избранного: {e}")
            QMessageBox.critical(
                None,
                "Ошибка",
                f"Не удалось открыть избранное: {e}"
            )

    def show_category_results(self, category_name):
        """Показывает все услуги категории"""
        # Здесь можно открыть окно со всеми услугами категории
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Категория",
            f"Категория: {category_name}\n"
            f"Здесь будут отображены все услуги этой категории"
        )

    def enable_search_field(self):
        """Разблокирует поле поиска"""
        self.Search.setEnabled(True)
        self.Search.setPlaceholderText("🔍 Поиск услуг, товаров...")

    def setup_navigation_buttons(self):
        """Настраивает кнопки навигации для прокрутки к разделам"""

        # Словарь с соответствием кнопок и виджетов разделов
        self.navigation_sections = {
            'Service_pushButton': self.Our_services,  # Раздел "Наши услуги"
            'About_pushButton': self.get_about_section(),  # Раздел "О нас" (текстовый блок)
            'Reviews_pushButton': None,  # Пока нет раздела отзывов
            'Contacts_pushButton': None,  # Пока нет раздела контактов
        }

        # Подключаем обработчики для кнопок навигации
        if hasattr(self, 'Service_pushButton'):
            self.Service_pushButton.clicked.connect(
                lambda: self.scroll_to_section('Service_pushButton')
            )

        if hasattr(self, 'About_pushButton'):
            self.About_pushButton.clicked.connect(
                lambda: self.scroll_to_section('About_pushButton')
            )

        if hasattr(self, 'Reviews_pushButton'):
            self.Reviews_pushButton.clicked.connect(
                lambda: self.scroll_to_section('Reviews_pushButton')
            )

        if hasattr(self, 'Contacts_pushButton'):
            self.Contacts_pushButton.clicked.connect(
                lambda: self.scroll_to_section('Contacts_pushButton')
            )

    def get_about_section(self):
        """Возвращает виджет раздела 'О нас'"""
        # Ищем виджет с текстом о компании
        # В вашем коде это about_frame, который содержит about_title и about_text
        for i in range(self.gridLayout.count()):
            item = self.gridLayout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                # Проверяем, содержит ли виджет текст о компании
                if hasattr(widget, 'findChild'):
                    # Ищем QLabel с текстом о компании
                    labels = widget.findChildren(QtWidgets.QLabel)
                    for label in labels:
                        if label.text() and "Ремонт техники любых видов" in label.text():
                            return widget
        return None

    def scroll_to_section(self, button_name):
        """Прокручивает к указанному разделу"""
        target_widget = self.navigation_sections.get(button_name)

        if not target_widget:
            # Если раздел еще не создан, показываем сообщение
            QtWidgets.QMessageBox.information(
                self.scrollArea,
                "Информация",
                f"Раздел '{button_name.replace('_pushButton', '')} находится в разработке'"
            )
            return

        # Получаем позицию целевого виджета
        target_pos = target_widget.mapTo(self.scrollAreaWidgetContents, QtCore.QPoint(0, 0))

        # Создаем анимацию прокрутки
        self.animate_scroll(target_pos.y())

    def animate_scroll(self, target_y):
        """Анимированная прокрутка к целевой позиции"""
        current_scrollbar = self.scrollArea.verticalScrollBar()
        current_value = current_scrollbar.value()

        # Разница в позиции
        delta = target_y - current_value

        # Количество шагов анимации
        steps = 30
        # Время одного шага (мс)
        step_time = 10

        # Если разница небольшая, прокручиваем сразу
        if abs(delta) < 50:
            current_scrollbar.setValue(target_y)
            return

        # Создаем таймер для анимации
        self.scroll_timer = QtCore.QTimer()
        self.scroll_step = 0
        self.scroll_delta = delta

        def scroll_step_func():
            nonlocal current_value
            self.scroll_step += 1

            # Используем easing function для плавности
            progress = self.scroll_step / steps
            # Простое easing: замедление в конце
            eased_progress = 1 - (1 - progress) ** 3

            new_value = int(current_value + self.scroll_delta * eased_progress)
            current_scrollbar.setValue(new_value)

            if self.scroll_step >= steps:
                self.scroll_timer.stop()
                # Убеждаемся, что достигли точной позиции
                current_scrollbar.setValue(target_y)

        self.scroll_timer.timeout.connect(scroll_step_func)
        self.scroll_timer.start(step_time)

    # Добавьте этот метод для обработки кликов по кнопкам преимуществ
    def setup_advantages_buttons(self):
        """Настраивает кнопки в разделе преимуществ"""
        advantage_buttons = [
            ('Professional_pushButton', "👨‍🔧 Профессионализм",
             "Наши мастера имеют сертификаты и многолетний опыт работы"),
            ('Complexity_pushButton', "⚡ Любая сложность",
             "Мы беремся за ремонт любой сложности, от замены экрана до восстановления после залития"),
            ('Equipment_pushButton', "🔧 Оборудование",
             "Используем профессиональное диагностическое и ремонтное оборудование"),
            ('Quickly_pushButton', "🚀 Быстро",
             "Срочный ремонт большинства устройств за 1 час"),
            ('Available_pushButton', "💰 Доступно",
             "Гибкая система скидок и доступные цены на все виды работ"),
            ('pushButton_34', "✅ Гарантия",
             "Даем гарантию до 1 года на все виды работ и запчасти")
        ]

        for btn_name, title, description in advantage_buttons:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                # При клике показываем подробную информацию
                btn.clicked.connect(
                    lambda checked, t=title, d=description:
                    self.show_advantage_details(t, d)
                )

    def show_advantage_details(self, title, description):
        """Показывает подробную информацию о преимуществе"""
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(description)
        msg_box.setIcon(QtWidgets.QMessageBox.Information)

        # Добавляем дополнительную информацию в зависимости от выбранного преимущества
        if "Профессионализм" in title:
            msg_box.setDetailedText(
                "• Сертифицированные специалисты\n"
                "• Регулярное обучение новым технологиям\n"
                "• Опыт работы от 5 лет\n"
                "• Специализация на конкретных типах устройств"
            )
        elif "Любая сложность" in title:
            msg_box.setDetailedText(
                "• Замена экранов и матриц\n"
                "• Восстановление после залития\n"
                "• Ремонт материнских плат\n"
                "• Замена разъемов и шлейфов\n"
                "• Восстановление данных"
            )
        elif "Оборудование" in title:
            msg_box.setDetailedText(
                "• Профессиональная паяльная станция\n"
                "• Термовоздушная пайка\n"
                "• Осциллографы и мультиметры\n"
                "• Программаторы для всех типов устройств\n"
                "• Диагностическое ПО"
            )

        msg_box.exec_()