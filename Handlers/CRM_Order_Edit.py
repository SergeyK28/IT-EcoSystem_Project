# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QComboBox, QDateEdit, QSpinBox, QTabWidget
from Server import db_crm
from datetime import datetime
import re


class Ui_OrderEditDialog(object):
    def __init__(self, order_id, order_data):
        self.dialog = None
        self.order_id = order_id
        self.order_data = order_data
        self.services_data = []
        self.parts_data = []

    def setupUi(self, OrderEditDialog):
        self.dialog = OrderEditDialog

        OrderEditDialog.setObjectName("OrderEditDialog")
        OrderEditDialog.resize(1400, 900)

        # Темный стиль
        OrderEditDialog.setStyleSheet("""
            QDialog, QWidget {
                background-color: rgb(23, 23, 23);
                color: rgb(255, 255, 255);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {
                background-color: rgb(40, 40, 40);
                color: rgb(255, 255, 255);
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: rgb(60, 60, 60);
                color: rgb(255, 255, 255);
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgb(80, 80, 80);
            }
            QPushButton:pressed {
                background-color: rgb(40, 40, 40);
            }
            QGroupBox {
                border: 1px solid rgb(103, 155, 118);
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: rgb(103, 155, 118);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid rgb(103, 155, 118);
                background-color: rgb(40, 40, 40);
            }
            QTabBar::tab {
                background-color: rgb(60, 60, 60);
                color: rgb(255, 255, 255);
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: rgb(103, 155, 118);
                color: white;
            }
            QTabBar::tab:hover {
                background-color: rgb(80, 80, 80);
            }
            QTableWidget {
                background-color: rgb(40, 40, 40);
                color: rgb(255, 255, 255);
                gridline-color: rgb(80, 80, 80);
                alternate-background-color: rgb(50, 50, 50);
            }
            QHeaderView::section {
                background-color: rgb(103, 155, 118);
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)

        self.verticalLayout = QtWidgets.QVBoxLayout(OrderEditDialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)

        # ЗАГОЛОВОК С ИНФОРМАЦИЕЙ О ЗАКАЗЕ
        self.create_header_section()

        # ТАБЫ ДЛЯ РАЗНЫХ РАЗДЕЛОВ
        self.tabWidget = QTabWidget(OrderEditDialog)

        # 1. ВКЛАДКА ОСНОВНОЙ ИНФОРМАЦИИ
        self.tab_main = QtWidgets.QWidget()
        self.setup_main_tab()
        self.tabWidget.addTab(self.tab_main, "Основная информация")

        # 2. ВКЛАДКА УСЛУГ И ЗАПЧАСТЕЙ
        self.tab_services_parts = QtWidgets.QWidget()
        self.setup_services_parts_tab()
        self.tabWidget.addTab(self.tab_services_parts, "Услуги и запчасти")

        # 3. ВКЛАДКА КОММЕНТАРИЕВ И ИСТОРИИ
        self.tab_comments_history = QtWidgets.QWidget()
        self.setup_comments_history_tab()
        self.tabWidget.addTab(self.tab_comments_history, "Комментарии и история")

        # 4. ВКЛАДКА ФИНАНСОВ
        self.tab_finance = QtWidgets.QWidget()
        self.setup_finance_tab()
        self.tabWidget.addTab(self.tab_finance, "Финансы")

        self.verticalLayout.addWidget(self.tabWidget)

        # КНОПКИ ДЕЙСТВИЙ
        self.create_action_buttons()

        # Загружаем данные
        self.load_order_data()

        self.retranslateUi(OrderEditDialog)
        QtCore.QMetaObject.connectSlotsByName(OrderEditDialog)

    def create_header_section(self):
        """Создает заголовок с информацией о заказе"""
        header_layout = QtWidgets.QHBoxLayout()

        # Номер заказа и статус
        order_info_layout = QtWidgets.QVBoxLayout()

        self.orderNumberLabel = QtWidgets.QLabel()
        self.orderNumberLabel.setStyleSheet("""
            QLabel {
                color: rgb(103, 155, 118);
                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.orderStatusLabel = QtWidgets.QLabel()
        self.orderStatusLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 3px 8px;
                border-radius: 3px;
            }
        """)

        order_info_layout.addWidget(self.orderNumberLabel)
        order_info_layout.addWidget(self.orderStatusLabel)
        header_layout.addLayout(order_info_layout)

        # Информация о клиенте
        client_info_layout = QtWidgets.QVBoxLayout()

        self.clientNameLabel = QtWidgets.QLabel()
        self.clientNameLabel.setStyleSheet("color: rgb(180, 180, 180); font-size: 14px;")

        self.clientContactsLabel = QtWidgets.QLabel()
        self.clientContactsLabel.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px;")

        client_info_layout.addWidget(self.clientNameLabel)
        client_info_layout.addWidget(self.clientContactsLabel)
        header_layout.addLayout(client_info_layout)

        header_layout.addStretch()

        # Информация об устройстве
        device_info_layout = QtWidgets.QVBoxLayout()

        self.deviceInfoLabel = QtWidgets.QLabel()
        self.deviceInfoLabel.setStyleSheet("color: rgb(180, 180, 180); font-size: 14px;")

        self.deviceProblemLabel = QtWidgets.QLabel()
        self.deviceProblemLabel.setStyleSheet("color: rgb(200, 200, 200); font-size: 12px;")
        self.deviceProblemLabel.setWordWrap(True)
        self.deviceProblemLabel.setMaximumWidth(400)

        device_info_layout.addWidget(self.deviceInfoLabel)
        device_info_layout.addWidget(self.deviceProblemLabel)
        header_layout.addLayout(device_info_layout)

        self.verticalLayout.addLayout(header_layout)

        # Разделительная линия
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("background-color: rgb(103, 155, 118);")
        self.verticalLayout.addWidget(line)

    def setup_main_tab(self):
        """Настраивает вкладку основной информации"""
        layout = QtWidgets.QVBoxLayout(self.tab_main)

        # Создаем ScrollArea для прокрутки
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # 1. ИНФОРМАЦИЯ О КЛИЕНТЕ
        client_group = QtWidgets.QGroupBox("ИНФОРМАЦИЯ О КЛИЕНТЕ")
        client_layout = QtWidgets.QGridLayout()
        client_layout.setHorizontalSpacing(15)
        client_layout.setVerticalSpacing(10)

        # ФИО клиента
        client_name_label = QtWidgets.QLabel("ФИО:")
        self.clientNameEdit = QtWidgets.QLineEdit()
        client_layout.addWidget(client_name_label, 0, 0)
        client_layout.addWidget(self.clientNameEdit, 0, 1)

        # Телефон
        phone_label = QtWidgets.QLabel("Телефон:")
        self.clientPhoneEdit = QtWidgets.QLineEdit()
        client_layout.addWidget(phone_label, 1, 0)
        client_layout.addWidget(self.clientPhoneEdit, 1, 1)

        # Email
        email_label = QtWidgets.QLabel("Email:")
        self.clientEmailEdit = QtWidgets.QLineEdit()
        client_layout.addWidget(email_label, 2, 0)
        client_layout.addWidget(self.clientEmailEdit, 2, 1)

        # Дата рождения
        birth_label = QtWidgets.QLabel("Дата рождения:")
        self.clientBirthEdit = QDateEdit()
        self.clientBirthEdit.setCalendarPopup(True)
        self.clientBirthEdit.setDisplayFormat("dd.MM.yyyy")
        client_layout.addWidget(birth_label, 3, 0)
        client_layout.addWidget(self.clientBirthEdit, 3, 1)

        client_group.setLayout(client_layout)
        scroll_layout.addWidget(client_group)

        # 2. ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ
        device_group = QtWidgets.QGroupBox("ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ")
        device_layout = QtWidgets.QGridLayout()
        device_layout.setHorizontalSpacing(15)
        device_layout.setVerticalSpacing(10)

        # Тип устройства
        type_label = QtWidgets.QLabel("Тип устройства:")
        self.deviceTypeCombo = QComboBox()
        self.deviceTypeCombo.addItems([
            "Смартфон", "Ноутбук", "Планшет", "Телевизор",
            "Игровая приставка", "Фотоаппарат", "Пылесос",
            "Кофемашина", "Другое"
        ])
        device_layout.addWidget(type_label, 0, 0)
        device_layout.addWidget(self.deviceTypeCombo, 0, 1)

        # Бренд
        brand_label = QtWidgets.QLabel("Бренд:")
        self.deviceBrandEdit = QtWidgets.QLineEdit()
        device_layout.addWidget(brand_label, 1, 0)
        device_layout.addWidget(self.deviceBrandEdit, 1, 1)

        # Модель
        model_label = QtWidgets.QLabel("Модель:")
        self.deviceModelEdit = QtWidgets.QLineEdit()
        device_layout.addWidget(model_label, 2, 0)
        device_layout.addWidget(self.deviceModelEdit, 2, 1)

        # IMEI/SN
        imei_label = QtWidgets.QLabel("IMEI/Серийный номер:")
        self.deviceImeiEdit = QtWidgets.QLineEdit()
        device_layout.addWidget(imei_label, 3, 0)
        device_layout.addWidget(self.deviceImeiEdit, 3, 1)

        device_group.setLayout(device_layout)
        scroll_layout.addWidget(device_group)

        # 3. ИНФОРМАЦИЯ О ЗАКАЗЕ
        order_group = QtWidgets.QGroupBox("ИНФОРМАЦИЯ О ЗАКАЗЕ")
        order_layout = QtWidgets.QGridLayout()
        order_layout.setHorizontalSpacing(15)
        order_layout.setVerticalSpacing(10)

        # Статус заказа
        status_label = QtWidgets.QLabel("Статус:")
        self.orderStatusCombo = QComboBox()
        self.orderStatusCombo.addItems([
            "Новая", "Активная", "Срочное", "Ждут запчасти",
            "В работе", "Готовое", "Закрыто неуспешно", "Завершен"
        ])
        order_layout.addWidget(status_label, 0, 0)
        order_layout.addWidget(self.orderStatusCombo, 0, 1)

        # Тип заказа
        type_label = QtWidgets.QLabel("Тип заказа:")
        self.orderTypeCombo = QComboBox()
        self.orderTypeCombo.addItems(["Платный", "Гарантийный"])
        order_layout.addWidget(type_label, 1, 0)
        order_layout.addWidget(self.orderTypeCombo, 1, 1)

        # Приоритет
        priority_label = QtWidgets.QLabel("Приоритет:")
        self.orderPriorityCombo = QComboBox()
        self.orderPriorityCombo.addItems(["Низкий", "Средний", "Высокий", "Критичный"])
        order_layout.addWidget(priority_label, 2, 0)
        order_layout.addWidget(self.orderPriorityCombo, 2, 1)

        # Причина обращения
        reason_label = QtWidgets.QLabel("Причина обращения:")
        self.reasonCombo = QComboBox()
        order_layout.addWidget(reason_label, 3, 0)
        order_layout.addWidget(self.reasonCombo, 3, 1)

        # Менеджер
        manager_label = QtWidgets.QLabel("Менеджер:")
        self.managerCombo = QComboBox()
        order_layout.addWidget(manager_label, 0, 2)
        order_layout.addWidget(self.managerCombo, 0, 3)

        # Исполнитель
        executor_label = QtWidgets.QLabel("Исполнитель:")
        self.executorCombo = QComboBox()
        order_layout.addWidget(executor_label, 1, 2)
        order_layout.addWidget(self.executorCombo, 1, 3)

        # Срок выполнения
        deadline_label = QtWidgets.QLabel("Срок выполнения:")
        self.deadlineEdit = QDateEdit()
        self.deadlineEdit.setCalendarPopup(True)
        self.deadlineEdit.setDisplayFormat("dd.MM.yyyy")
        order_layout.addWidget(deadline_label, 2, 2)
        order_layout.addWidget(self.deadlineEdit, 2, 3)

        order_group.setLayout(order_layout)
        scroll_layout.addWidget(order_group)

        # 4. ВНЕШНИЙ ВИД И КОМПЛЕКТАЦИЯ
        appearance_group = QtWidgets.QGroupBox("ВНЕШНИЙ ВИД И КОМПЛЕКТАЦИЯ")
        appearance_layout = QtWidgets.QVBoxLayout()

        # Внешний вид
        appearance_label = QtWidgets.QLabel("Внешний вид/Состояние:")
        self.appearanceEdit = QtWidgets.QTextEdit()
        self.appearanceEdit.setMaximumHeight(80)
        appearance_layout.addWidget(appearance_label)
        appearance_layout.addWidget(self.appearanceEdit)

        # Комплектация
        completeness_label = QtWidgets.QLabel("Комплектация:")
        self.completenessEdit = QtWidgets.QTextEdit()
        self.completenessEdit.setMaximumHeight(60)
        appearance_layout.addWidget(completeness_label)
        appearance_layout.addWidget(self.completenessEdit)

        appearance_group.setLayout(appearance_layout)
        scroll_layout.addWidget(appearance_group)

        # 5. ОПИСАНИЕ ПРОБЛЕМЫ И ДИАГНОСТИКА
        problem_group = QtWidgets.QGroupBox("ПРОБЛЕМА И ДИАГНОСТИКА")
        problem_layout = QtWidgets.QVBoxLayout()

        # Описание проблемы
        problem_label = QtWidgets.QLabel("Описание проблемы клиента:")
        self.problemEdit = QtWidgets.QTextEdit()
        self.problemEdit.setMaximumHeight(80)
        problem_layout.addWidget(problem_label)
        problem_layout.addWidget(self.problemEdit)

        # Диагностика мастера
        diagnosis_label = QtWidgets.QLabel("Диагностика мастера:")
        self.diagnosisEdit = QtWidgets.QTextEdit()
        self.diagnosisEdit.setMaximumHeight(80)
        problem_layout.addWidget(diagnosis_label)
        problem_layout.addWidget(self.diagnosisEdit)

        # Рекомендации
        recommendation_label = QtWidgets.QLabel("Рекомендации:")
        self.recommendationEdit = QtWidgets.QTextEdit()
        self.recommendationEdit.setMaximumHeight(60)
        problem_layout.addWidget(recommendation_label)
        problem_layout.addWidget(self.recommendationEdit)

        problem_group.setLayout(problem_layout)
        scroll_layout.addWidget(problem_group)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

    def setup_services_parts_tab(self):
        """Настраивает вкладку услуг и запчастей"""
        layout = QtWidgets.QVBoxLayout(self.tab_services_parts)

        # ТАБЫ для услуг и запчастей
        services_parts_tabs = QTabWidget()

        # 1. ВКЛАДКА УСЛУГ
        services_tab = QtWidgets.QWidget()
        services_layout = QtWidgets.QVBoxLayout(services_tab)

        # Панель для добавления услуг
        add_service_layout = QtWidgets.QHBoxLayout()

        service_label = QtWidgets.QLabel("Услуга:")
        self.newServiceCombo = QComboBox()
        self.newServiceCombo.setMinimumWidth(300)

        qty_label = QtWidgets.QLabel("Кол-во:")
        self.newServiceQtySpin = QSpinBox()
        self.newServiceQtySpin.setMinimum(1)
        self.newServiceQtySpin.setMaximum(999)
        self.newServiceQtySpin.setValue(1)
        self.newServiceQtySpin.setMaximumWidth(70)

        price_label = QtWidgets.QLabel("Цена (₽):")
        self.newServicePriceEdit = QtWidgets.QLineEdit()
        self.newServicePriceEdit.setMaximumWidth(100)

        self.addServiceBtn = QtWidgets.QPushButton("➕ Добавить услугу")
        self.addServiceBtn.setStyleSheet("background-color: rgb(40, 167, 69);")
        self.addServiceBtn.clicked.connect(self.add_new_service)

        add_service_layout.addWidget(service_label)
        add_service_layout.addWidget(self.newServiceCombo)
        add_service_layout.addWidget(qty_label)
        add_service_layout.addWidget(self.newServiceQtySpin)
        add_service_layout.addWidget(price_label)
        add_service_layout.addWidget(self.newServicePriceEdit)
        add_service_layout.addWidget(self.addServiceBtn)
        add_service_layout.addStretch()

        services_layout.addLayout(add_service_layout)

        # Таблица услуг
        self.servicesTable = QtWidgets.QTableWidget()
        self.servicesTable.setColumnCount(7)
        self.servicesTable.setHorizontalHeaderLabels(["ID", "Услуга", "Кол-во", "Цена", "Сумма", "Статус", "Действия"])
        self.servicesTable.setColumnHidden(0, True)  # Скрываем ID
        services_layout.addWidget(self.servicesTable)

        services_parts_tabs.addTab(services_tab, "Услуги")

        # 2. ВКЛАДКА ЗАПЧАСТЕЙ
        parts_tab = QtWidgets.QWidget()
        parts_layout = QtWidgets.QVBoxLayout(parts_tab)

        # Панель для добавления запчастей
        add_part_layout = QtWidgets.QHBoxLayout()

        part_label = QtWidgets.QLabel("Запчасть:")
        self.newPartCombo = QComboBox()
        self.newPartCombo.setMinimumWidth(300)

        part_qty_label = QtWidgets.QLabel("Кол-во:")
        self.newPartQtySpin = QSpinBox()
        self.newPartQtySpin.setMinimum(1)
        self.newPartQtySpin.setMaximum(999)
        self.newPartQtySpin.setValue(1)
        self.newPartQtySpin.setMaximumWidth(70)

        part_price_label = QtWidgets.QLabel("Цена (₽):")
        self.newPartPriceEdit = QtWidgets.QLineEdit()
        self.newPartPriceEdit.setMaximumWidth(100)

        warranty_label = QtWidgets.QLabel("Гарантия (дней):")
        self.newPartWarrantyEdit = QtWidgets.QLineEdit()
        self.newPartWarrantyEdit.setText("90")
        self.newPartWarrantyEdit.setMaximumWidth(80)

        self.addPartBtn = QtWidgets.QPushButton("➕ Добавить запчасть")
        self.addPartBtn.setStyleSheet("background-color: rgb(40, 167, 69);")
        self.addPartBtn.clicked.connect(self.add_new_part)

        add_part_layout.addWidget(part_label)
        add_part_layout.addWidget(self.newPartCombo)
        add_part_layout.addWidget(part_qty_label)
        add_part_layout.addWidget(self.newPartQtySpin)
        add_part_layout.addWidget(part_price_label)
        add_part_layout.addWidget(self.newPartPriceEdit)
        add_part_layout.addWidget(warranty_label)
        add_part_layout.addWidget(self.newPartWarrantyEdit)
        add_part_layout.addWidget(self.addPartBtn)
        add_part_layout.addStretch()

        parts_layout.addLayout(add_part_layout)

        # Таблица запчастей
        self.partsTable = QtWidgets.QTableWidget()
        self.partsTable.setColumnCount(8)
        self.partsTable.setHorizontalHeaderLabels(
            ["ID", "Запчасть", "Кол-во", "Цена", "Сумма", "Гарантия", "На складе", "Действия"])
        self.partsTable.setColumnHidden(0, True)  # Скрываем ID
        parts_layout.addWidget(self.partsTable)

        services_parts_tabs.addTab(parts_tab, "Запчасти")

        layout.addWidget(services_parts_tabs)

        # ИТОГОВАЯ СУММА
        total_group = QtWidgets.QGroupBox("ИТОГО")
        total_layout = QtWidgets.QHBoxLayout()

        self.servicesTotalLabel = QtWidgets.QLabel("Услуги: 0.00 ₽")
        self.servicesTotalLabel.setStyleSheet("color: rgb(103, 155, 118); font-size: 14px;")

        self.partsTotalLabel = QtWidgets.QLabel("Запчасти: 0.00 ₽")
        self.partsTotalLabel.setStyleSheet("color: rgb(103, 155, 118); font-size: 14px;")

        self.totalAmountLabel = QtWidgets.QLabel("ИТОГО: 0.00 ₽")
        self.totalAmountLabel.setStyleSheet("color: rgb(40, 167, 69); font-size: 16px; font-weight: bold;")

        total_layout.addWidget(self.servicesTotalLabel)
        total_layout.addWidget(self.partsTotalLabel)
        total_layout.addStretch()
        total_layout.addWidget(self.totalAmountLabel)

        total_group.setLayout(total_layout)
        layout.addWidget(total_group)

    def setup_comments_history_tab(self):
        """Настраивает вкладку комментариев и истории"""
        layout = QtWidgets.QVBoxLayout(self.tab_comments_history)

        # ТАБЫ для комментариев и истории
        comments_history_tabs = QTabWidget()

        # 1. ВКЛАДКА КОММЕНТАРИЕВ
        comments_tab = QtWidgets.QWidget()
        comments_layout = QtWidgets.QVBoxLayout(comments_tab)

        # Панель для добавления комментария
        add_comment_layout = QtWidgets.QVBoxLayout()

        comment_type_layout = QtWidgets.QHBoxLayout()
        comment_type_label = QtWidgets.QLabel("Тип комментария:")
        self.commentTypeCombo = QComboBox()
        self.commentTypeCombo.addItems(["Внутренний", "Для клиента"])
        comment_type_layout.addWidget(comment_type_label)
        comment_type_layout.addWidget(self.commentTypeCombo)
        comment_type_layout.addStretch()
        add_comment_layout.addLayout(comment_type_layout)

        comment_text_layout = QtWidgets.QHBoxLayout()
        self.newCommentEdit = QtWidgets.QTextEdit()
        self.newCommentEdit.setMaximumHeight(80)
        self.newCommentEdit.setPlaceholderText("Введите комментарий...")

        self.addCommentBtn = QtWidgets.QPushButton("➕ Добавить комментарий")
        self.addCommentBtn.setStyleSheet("background-color: rgb(40, 167, 69);")
        self.addCommentBtn.clicked.connect(self.add_new_comment)

        comment_text_layout.addWidget(self.newCommentEdit)
        comment_text_layout.addWidget(self.addCommentBtn)
        add_comment_layout.addLayout(comment_text_layout)

        comments_layout.addLayout(add_comment_layout)

        # Таблица комментариев
        self.commentsTable = QtWidgets.QTableWidget()
        self.commentsTable.setColumnCount(4)
        self.commentsTable.setHorizontalHeaderLabels(["Дата", "Автор", "Текст", "Тип"])
        comments_layout.addWidget(self.commentsTable)

        comments_history_tabs.addTab(comments_tab, "Комментарии")

        # 2. ВКЛАДКА ИСТОРИИ СТАТУСОВ
        history_tab = QtWidgets.QWidget()
        history_layout = QtWidgets.QVBoxLayout(history_tab)

        # Таблица истории статусов
        self.historyTable = QtWidgets.QTableWidget()
        self.historyTable.setColumnCount(5)
        self.historyTable.setHorizontalHeaderLabels(["Дата", "Старый статус", "Новый статус", "Кто изменил", "Причина"])
        history_layout.addWidget(self.historyTable)

        comments_history_tabs.addTab(history_tab, "История статусов")

        layout.addWidget(comments_history_tabs)

    def setup_finance_tab(self):
        """Настраивает вкладку финансов"""
        layout = QtWidgets.QVBoxLayout(self.tab_finance)

        # 1. ОСНОВНЫЕ ФИНАНСОВЫЕ ДАННЫЕ
        finance_group = QtWidgets.QGroupBox("ФИНАНСОВАЯ ИНФОРМАЦИЯ")
        finance_layout = QtWidgets.QGridLayout()
        finance_layout.setHorizontalSpacing(15)
        finance_layout.setVerticalSpacing(10)

        # Общая сумма
        total_label = QtWidgets.QLabel("Общая сумма:")
        self.totalAmountEdit = QtWidgets.QLineEdit()
        self.totalAmountEdit.setReadOnly(True)
        finance_layout.addWidget(total_label, 0, 0)
        finance_layout.addWidget(self.totalAmountEdit, 0, 1)

        # Скидка
        discount_label = QtWidgets.QLabel("Скидка (%):")
        self.discountEdit = QtWidgets.QLineEdit()
        self.discountEdit.setText("0")
        finance_layout.addWidget(discount_label, 1, 0)
        finance_layout.addWidget(self.discountEdit, 1, 1)

        # Итоговая сумма
        final_label = QtWidgets.QLabel("Итоговая сумма:")
        self.finalAmountEdit = QtWidgets.QLineEdit()
        self.finalAmountEdit.setReadOnly(True)
        finance_layout.addWidget(final_label, 2, 0)
        finance_layout.addWidget(self.finalAmountEdit, 2, 1)

        # Предоплата
        prepayment_label = QtWidgets.QLabel("Предоплата:")
        self.prepaymentEdit = QtWidgets.QLineEdit()
        finance_layout.addWidget(prepayment_label, 3, 0)
        finance_layout.addWidget(self.prepaymentEdit, 3, 1)

        # Оплачено всего
        paid_label = QtWidgets.QLabel("Оплачено всего:")
        self.paidAmountEdit = QtWidgets.QLineEdit()
        self.paidAmountEdit.setReadOnly(True)
        finance_layout.addWidget(paid_label, 0, 2)
        finance_layout.addWidget(self.paidAmountEdit, 0, 3)

        # Остаток
        balance_label = QtWidgets.QLabel("Остаток к оплате:")
        self.balanceAmountEdit = QtWidgets.QLineEdit()
        self.balanceAmountEdit.setReadOnly(True)
        finance_layout.addWidget(balance_label, 1, 2)
        finance_layout.addWidget(self.balanceAmountEdit, 1, 3)

        # Статус оплаты
        payment_status_label = QtWidgets.QLabel("Статус оплаты:")
        self.paymentStatusCombo = QComboBox()
        self.paymentStatusCombo.addItems(["Не оплачен", "Частично оплачен", "Полностью оплачен"])
        finance_layout.addWidget(payment_status_label, 2, 2)
        finance_layout.addWidget(self.paymentStatusCombo, 2, 3)

        finance_group.setLayout(finance_layout)
        layout.addWidget(finance_group)

        # 2. ИСТОРИЯ ПЛАТЕЖЕЙ
        payments_group = QtWidgets.QGroupBox("ИСТОРИЯ ПЛАТЕЖЕЙ")
        payments_layout = QtWidgets.QVBoxLayout()

        # Панель для добавления платежа
        add_payment_layout = QtWidgets.QHBoxLayout()

        payment_amount_label = QtWidgets.QLabel("Сумма (₽):")
        self.newPaymentAmountEdit = QtWidgets.QLineEdit()

        payment_method_label = QtWidgets.QLabel("Способ:")
        self.newPaymentMethodCombo = QComboBox()
        self.newPaymentMethodCombo.addItems(["Наличные", "Карта", "Перевод", "Онлайн"])

        payment_type_label = QtWidgets.QLabel("Тип:")
        self.newPaymentTypeCombo = QComboBox()
        self.newPaymentTypeCombo.addItems(["Предоплата", "Оплата", "Возврат"])

        self.addPaymentBtn = QtWidgets.QPushButton("➕ Добавить платеж")
        self.addPaymentBtn.setStyleSheet("background-color: rgb(40, 167, 69);")
        self.addPaymentBtn.clicked.connect(self.add_new_payment)

        add_payment_layout.addWidget(payment_amount_label)
        add_payment_layout.addWidget(self.newPaymentAmountEdit)
        add_payment_layout.addWidget(payment_method_label)
        add_payment_layout.addWidget(self.newPaymentMethodCombo)
        add_payment_layout.addWidget(payment_type_label)
        add_payment_layout.addWidget(self.newPaymentTypeCombo)
        add_payment_layout.addWidget(self.addPaymentBtn)
        add_payment_layout.addStretch()

        payments_layout.addLayout(add_payment_layout)

        # Таблица платежей
        self.paymentsTable = QtWidgets.QTableWidget()
        self.paymentsTable.setColumnCount(6)
        self.paymentsTable.setHorizontalHeaderLabels(["Дата", "Сумма", "Способ", "Тип", "Номер чека", "Примечание"])
        payments_layout.addWidget(self.paymentsTable)

        payments_group.setLayout(payments_layout)
        layout.addWidget(payments_group)

    def create_action_buttons(self):
        """Создает кнопки действий"""
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Кнопка сохранения
        self.saveBtn = QtWidgets.QPushButton("💾 Сохранить изменения")
        self.saveBtn.setStyleSheet("""
            QPushButton {
                background-color: rgb(40, 167, 69);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 25px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgb(50, 187, 79);
            }
            QPushButton:pressed {
                background-color: rgb(30, 147, 59);
            }
        """)
        self.saveBtn.clicked.connect(self.save_order)

        # Кнопка отмены
        self.cancelBtn = QtWidgets.QPushButton("❌ Отмена")
        self.cancelBtn.setStyleSheet("""
            QPushButton {
                background-color: rgb(108, 117, 125);
                color: white;
                font-size: 14px;
                padding: 12px 25px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgb(118, 127, 135);
            }
        """)
        self.cancelBtn.clicked.connect(self.dialog.reject)

        # Кнопка печати
        self.printBtn = QtWidgets.QPushButton("🖨️ Печать")
        self.printBtn.setStyleSheet("background-color: rgb(23, 162, 184);")
        self.printBtn.clicked.connect(self.print_order)

        # Кнопка закрытия заказа
        self.closeBtn = QtWidgets.QPushButton("✅ Завершить заказ")
        self.closeBtn.setStyleSheet("background-color: rgb(103, 155, 118);")
        self.closeBtn.clicked.connect(self.close_order)

        buttons_layout.addWidget(self.saveBtn)
        buttons_layout.addWidget(self.cancelBtn)
        buttons_layout.addWidget(self.printBtn)
        buttons_layout.addWidget(self.closeBtn)
        buttons_layout.addStretch()

        self.verticalLayout.addLayout(buttons_layout)

    def load_order_data(self):
        """Загружает данные заказа"""
        try:
            # Загружаем данные из переданного order_data
            if not self.order_data:
                QMessageBox.critical(self.dialog, "Ошибка", "Не удалось загрузить данные заказа")
                return

            # Устанавливаем заголовок
            self.orderNumberLabel.setText(f"Заказ #{self.order_data.get('OrderNumber', self.order_id)}")

            # Устанавливаем статус с цветом
            status = self.order_data.get('Status', 'Новая')
            self.orderStatusLabel.setText(f"Статус: {status}")
            self.set_status_color(status)

            # Информация о клиенте
            client_name = f"{self.order_data.get('ClientFirstName', '')} {self.order_data.get('ClientLastName', '')}"
            self.clientNameLabel.setText(f"Клиент: {client_name}")
            self.clientContactsLabel.setText(
                f"Тел: {self.order_data.get('ClientPhone', '')} | Email: {self.order_data.get('ClientEmail', '')}")

            # Информация об устройстве
            device_info = f"{self.order_data.get('DeviceType', '')} {self.order_data.get('DeviceBrand', '')} {self.order_data.get('DeviceModel', '')}"
            self.deviceInfoLabel.setText(f"Устройство: {device_info}")

            problem = self.order_data.get('ProblemDescription', '')
            if len(problem) > 100:
                problem = problem[:100] + "..."
            self.deviceProblemLabel.setText(f"Проблема: {problem}")

            # Заполняем основные поля
            self.fill_main_fields()

            # Заполняем услуги и запчасти
            self.fill_services_parts()

            # Заполняем комментарии и историю
            self.fill_comments_history()

            # Заполняем финансовую информацию
            self.fill_finance_info()

            # Загружаем комбобоксы
            self.load_combobox_data()

        except Exception as e:
            print(f"Ошибка загрузки данных заказа: {e}")
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка загрузки данных заказа: {e}")

    def fill_main_fields(self):
        """Заполняет основные поля формы"""
        # Клиент
        self.clientNameEdit.setText(
            f"{self.order_data.get('ClientFirstName', '')} {self.order_data.get('ClientLastName', '')}")
        self.clientPhoneEdit.setText(self.order_data.get('ClientPhone', ''))
        self.clientEmailEdit.setText(self.order_data.get('ClientEmail', ''))

        birthdate = self.order_data.get('ClientBirthdate')
        if birthdate:
            try:
                date = QtCore.QDate.fromString(str(birthdate), "yyyy-MM-dd")
                if date.isValid():
                    self.clientBirthEdit.setDate(date)
            except:
                pass

        # Устройство
        device_type = self.order_data.get('DeviceType', '')
        if device_type:
            index = self.deviceTypeCombo.findText(device_type)
            if index >= 0:
                self.deviceTypeCombo.setCurrentIndex(index)

        self.deviceBrandEdit.setText(self.order_data.get('DeviceBrand', ''))
        self.deviceModelEdit.setText(self.order_data.get('DeviceModel', ''))
        self.deviceImeiEdit.setText(self.order_data.get('DeviceIMEI_SN', ''))
        self.appearanceEdit.setText(self.order_data.get('DeviceAppearance', ''))
        self.completenessEdit.setText(self.order_data.get('Notes', ''))
        self.problemEdit.setText(self.order_data.get('ProblemDescription', ''))
        self.diagnosisEdit.setText(self.order_data.get('Diagnosis', ''))
        self.recommendationEdit.setText(self.order_data.get('Recommendation', ''))

        # Заказ
        status = self.order_data.get('Status', 'Новая')
        index = self.orderStatusCombo.findText(status)
        if index >= 0:
            self.orderStatusCombo.setCurrentIndex(index)

        order_type = self.order_data.get('OrderType', 'Платный')
        index = self.orderTypeCombo.findText(order_type)
        if index >= 0:
            self.orderTypeCombo.setCurrentIndex(index)

        priority = self.order_data.get('Priority', 'Средний')
        index = self.orderPriorityCombo.findText(priority)
        if index >= 0:
            self.orderPriorityCombo.setCurrentIndex(index)

        # Срок выполнения
        estimated_completion = self.order_data.get('EstimatedCompletion')
        if estimated_completion:
            try:
                date_str = str(estimated_completion)
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                date = QtCore.QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.deadlineEdit.setDate(date)
            except:
                pass

    def fill_services_parts(self):
        """Заполняет услуги и запчасти"""
        # Услуги
        services_list = self.order_data.get('services_list', [])
        self.servicesTable.setRowCount(len(services_list))

        for row, service in enumerate(services_list):
            # ID
            self.servicesTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(service.get('OrderServiceID', ''))))

            # Услуга
            service_desc = f"{service.get('ServiceDescription', '')}"
            self.servicesTable.setItem(row, 1, QtWidgets.QTableWidgetItem(service_desc))

            # Количество
            self.servicesTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(service.get('Quantity', 1))))

            # Цена
            price = service.get('UnitPrice', 0)
            self.servicesTable.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price:.2f}"))

            # Сумма
            total = service.get('TotalPrice', price)
            self.servicesTable.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))

            # Статус
            status = service.get('ServiceStatus', 'Запланировано')
            self.servicesTable.setItem(row, 5, QtWidgets.QTableWidgetItem(status))

            # Действия
            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("background-color: rgb(220, 53, 69); color: white; padding: 5px 10px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_service(r))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.servicesTable.setCellWidget(row, 6, cell_widget)

        # Запчасти
        parts_list = self.order_data.get('details_list', [])
        self.partsTable.setRowCount(len(parts_list))

        for row, part in enumerate(parts_list):
            # ID
            self.partsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(part.get('OrderDetailID', ''))))

            # Запчасть
            part_name = f"{part.get('DetailName', '')} ({part.get('DetailCode', '')})"
            self.partsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(part_name))

            # Количество
            self.partsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(part.get('Quantity', 1))))

            # Цена
            price = part.get('UnitPrice', 0)
            self.partsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price:.2f}"))

            # Сумма
            total = part.get('TotalPrice', price)
            self.partsTable.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))

            # Гарантия
            warranty = part.get('WarrantyDays', 90)
            self.partsTable.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{warranty} дней"))

            # На складе
            stock_qty = part.get('CountInStock', 0)
            self.partsTable.setItem(row, 6, QtWidgets.QTableWidgetItem(str(stock_qty)))

            # Действия
            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("background-color: rgb(220, 53, 69); color: white; padding: 5px 10px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_part(r))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.partsTable.setCellWidget(row, 7, cell_widget)

        # Обновляем итоги
        self.update_totals()

    def fill_comments_history(self):
        """Заполняет комментарии и историю"""
        # Комментарии
        comments_list = self.order_data.get('comments_list', [])
        self.commentsTable.setRowCount(len(comments_list))

        for row, comment in enumerate(comments_list):
            # Дата
            date = comment.get('CommentDate', '')
            if date:
                date_str = str(date)[:19]  # Берем только дату и время
            else:
                date_str = ''
            self.commentsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(date_str))

            # Автор
            author = comment.get('EmployeeName', 'Система')
            self.commentsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(author))

            # Текст
            self.commentsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(comment.get('CommentText', '')))

            # Тип
            is_internal = comment.get('IsInternal', False)
            comment_type = "Внутренний" if is_internal else "Для клиента"
            self.commentsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(comment_type))

        # История статусов
        history_list = self.order_data.get('status_history', [])
        self.historyTable.setRowCount(len(history_list))

        for row, history in enumerate(history_list):
            # Дата
            date = history.get('ChangeDate', '')
            if date:
                date_str = str(date)[:19]
            else:
                date_str = ''
            self.historyTable.setItem(row, 0, QtWidgets.QTableWidgetItem(date_str))

            # Старый статус
            self.historyTable.setItem(row, 1, QtWidgets.QTableWidgetItem(history.get('OldStatus', '')))

            # Новый статус
            self.historyTable.setItem(row, 2, QtWidgets.QTableWidgetItem(history.get('NewStatus', '')))

            # Кто изменил
            self.historyTable.setItem(row, 3, QtWidgets.QTableWidgetItem(history.get('ChangedByName', '')))

            # Причина
            self.historyTable.setItem(row, 4, QtWidgets.QTableWidgetItem(history.get('ChangeReason', '')))

    def fill_finance_info(self):
        """Заполняет финансовую информацию"""
        # Основные суммы
        total_amount = self.order_data.get('TotalAmount', 0)
        self.totalAmountEdit.setText(f"{total_amount:.2f}")

        discount = self.order_data.get('Discount', 0)
        self.discountEdit.setText(f"{discount:.2f}")

        final_amount = self.order_data.get('FinalAmount', 0)
        self.finalAmountEdit.setText(f"{final_amount:.2f}")

        prepayment = self.order_data.get('Prepayment', 0)
        self.prepaymentEdit.setText(f"{prepayment:.2f}")

        # Платежи
        paid_amount = self.order_data.get('AllPaymentsTotal', 0)
        self.paidAmountEdit.setText(f"{paid_amount:.2f}")

        # Остаток
        balance = final_amount - paid_amount
        self.balanceAmountEdit.setText(f"{balance:.2f}")

        # Статус оплаты
        if balance <= 0:
            self.paymentStatusCombo.setCurrentIndex(2)  # Полностью оплачен
        elif paid_amount > 0:
            self.paymentStatusCombo.setCurrentIndex(1)  # Частично оплачен
        else:
            self.paymentStatusCombo.setCurrentIndex(0)  # Не оплачен

        # История платежей будет загружена отдельно
        self.load_payments_history()

    def load_combobox_data(self):
        """Загружает данные в комбобоксы"""
        try:
            # Причины обращения
            reasons = db_crm.get_all_appeal_reasons()
            self.reasonCombo.clear()
            self.reasonCombo.addItem("Не выбрано", 0)
            for reason in reasons:
                self.reasonCombo.addItem(reason['ReasonName'], reason['ReasonID'])

            # Устанавливаем текущую причину
            appeal_reason_id = self.order_data.get('AppealReasonID')
            if appeal_reason_id:
                for i in range(self.reasonCombo.count()):
                    if self.reasonCombo.itemData(i) == appeal_reason_id:
                        self.reasonCombo.setCurrentIndex(i)
                        break

            # Сотрудники
            employees = db_crm.get_all_employees()
            self.managerCombo.clear()
            self.executorCombo.clear()

            self.managerCombo.addItem("Не назначен", 0)
            self.executorCombo.addItem("Не назначен", 0)

            for emp in employees:
                name = f"{emp['FirstName']} {emp['LastName']}"
                self.managerCombo.addItem(name, emp['EmployeeID'])
                self.executorCombo.addItem(name, emp['EmployeeID'])

            # Устанавливаем текущих сотрудников
            manager_id = self.order_data.get('ManagerID')
            if manager_id:
                for i in range(self.managerCombo.count()):
                    if self.managerCombo.itemData(i) == manager_id:
                        self.managerCombo.setCurrentIndex(i)
                        break

            executor_id = self.order_data.get('ExecutorID')
            if executor_id:
                for i in range(self.executorCombo.count()):
                    if self.executorCombo.itemData(i) == executor_id:
                        self.executorCombo.setCurrentIndex(i)
                        break

            # Услуги для добавления
            services = db_crm.get_all_service_types()
            self.newServiceCombo.clear()
            self.newServiceCombo.addItem("Выберите услугу", 0)
            for service in services:
                service_text = f"{service['ServiceDescription']} - {service['BasePrice']:.2f} ₽"
                self.newServiceCombo.addItem(service_text, service['ServiceTypeID'])

            # Запчасти для добавления
            parts = db_crm.get_all_stock_items()
            self.newPartCombo.clear()
            self.newPartCombo.addItem("Выберите запчасть", 0)
            for part in parts:
                part_text = f"{part['DetailName']} ({part['CountInStock']} шт.) - {part['Price']:.2f} ₽"
                self.newPartCombo.addItem(part_text, part['StockID'])

        except Exception as e:
            print(f"Ошибка загрузки данных в комбобоксы: {e}")

    def load_payments_history(self):
        """Загружает историю платежей"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT PaymentDate, Amount, PaymentMethod, PaymentType, 
                       ReceiptNumber, Notes
                FROM Payments 
                WHERE OrderID = %s
                ORDER BY PaymentDate DESC
            """, (self.order_id,))

            payments = cursor.fetchall()
            cursor.close()
            connection.close()

            self.paymentsTable.setRowCount(len(payments))

            for row, payment in enumerate(payments):
                # Дата
                date = payment.get('PaymentDate', '')
                if date:
                    date_str = str(date)[:19]
                else:
                    date_str = ''
                self.paymentsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(date_str))

                # Сумма
                amount = payment.get('Amount', 0)
                self.paymentsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{amount:.2f}"))

                # Способ
                self.paymentsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(payment.get('PaymentMethod', '')))

                # Тип
                self.paymentsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(payment.get('PaymentType', '')))

                # Номер чека
                self.paymentsTable.setItem(row, 4, QtWidgets.QTableWidgetItem(payment.get('ReceiptNumber', '')))

                # Примечание
                self.paymentsTable.setItem(row, 5, QtWidgets.QTableWidgetItem(payment.get('Notes', '')))

        except Exception as e:
            print(f"Ошибка загрузки истории платежей: {e}")

    def set_status_color(self, status):
        """Устанавливает цвет статуса"""
        colors = {
            'Новая': 'rgb(66, 135, 245)',  # Синий
            'Активная': 'rgb(255, 193, 7)',  # Желтый
            'Срочное': 'rgb(220, 53, 69)',  # Красный
            'В работе': 'rgb(25, 135, 84)',  # Зеленый
            'Ждут запчасти': 'rgb(255, 149, 0)',  # Оранжевый
            'Готовое': 'rgb(40, 167, 69)',  # Зеленый
            'Завершен': 'rgb(108, 117, 125)',  # Серый
            'Закрыто неуспешно': 'rgb(108, 117, 125)',  # Серый
        }

        color = colors.get(status, 'rgb(108, 117, 125)')
        self.orderStatusLabel.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                padding: 3px 8px;
                border-radius: 3px;
                background-color: {color};
                color: white;
            }}
        """)

    def update_totals(self):
        """Обновляет итоговые суммы"""
        try:
            services_total = 0.0
            for row in range(self.servicesTable.rowCount()):
                total_item = self.servicesTable.item(row, 4)
                if total_item:
                    try:
                        services_total += float(total_item.text())
                    except ValueError:
                        pass

            parts_total = 0.0
            for row in range(self.partsTable.rowCount()):
                total_item = self.partsTable.item(row, 4)
                if total_item:
                    try:
                        parts_total += float(total_item.text())
                    except ValueError:
                        pass

            total = services_total + parts_total

            self.servicesTotalLabel.setText(f"Услуги: {services_total:.2f} ₽")
            self.partsTotalLabel.setText(f"Запчасти: {parts_total:.2f} ₽")
            self.totalAmountLabel.setText(f"ИТОГО: {total:.2f} ₽")

            # Обновляем поля в финансовой вкладке
            self.totalAmountEdit.setText(f"{total:.2f}")

            # Пересчитываем итоговую сумму с учетом скидки
            try:
                discount = float(self.discountEdit.text() or 0)
                final_amount = total * (1 - discount / 100)
                self.finalAmountEdit.setText(f"{final_amount:.2f}")

                # Пересчитываем остаток
                paid_amount = float(self.paidAmountEdit.text() or 0)
                balance = final_amount - paid_amount
                self.balanceAmountEdit.setText(f"{balance:.2f}")
            except:
                pass

        except Exception as e:
            print(f"Ошибка обновления итогов: {e}")

    def add_new_service(self):
        """Добавляет новую услугу"""
        try:
            service_id = self.newServiceCombo.currentData()
            if service_id == 0:
                QMessageBox.warning(self.dialog, "Ошибка", "Выберите услугу")
                return

            service_text = self.newServiceCombo.currentText()
            qty = self.newServiceQtySpin.value()
            price_text = self.newServicePriceEdit.text().strip()

            # Если цена не указана, берем из названия услуги
            if not price_text:
                import re
                price_match = re.search(r'(\d+\.?\d*) ₽', service_text)
                if price_match:
                    price = float(price_match.group(1))
                else:
                    price = 0.0
            else:
                try:
                    price = float(price_text)
                except ValueError:
                    QMessageBox.warning(self.dialog, "Ошибка", "Введите корректную цену")
                    return

            total = qty * price

            # Добавляем строку в таблицу
            row = self.servicesTable.rowCount()
            self.servicesTable.insertRow(row)

            # ID (временный)
            self.servicesTable.setItem(row, 0, QtWidgets.QTableWidgetItem(f"new_{row}"))

            # Услуга
            self.servicesTable.setItem(row, 1, QtWidgets.QTableWidgetItem(service_text.split(' - ')[0]))

            # Количество
            self.servicesTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(qty)))

            # Цена
            self.servicesTable.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price:.2f}"))

            # Сумма
            self.servicesTable.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))

            # Статус
            self.servicesTable.setItem(row, 5, QtWidgets.QTableWidgetItem("Запланировано"))

            # Действия
            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("background-color: rgb(220, 53, 69); color: white; padding: 5px 10px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_service(r))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.servicesTable.setCellWidget(row, 6, cell_widget)

            # Обновляем итоги
            self.update_totals()

            # Очищаем поля
            self.newServiceQtySpin.setValue(1)
            self.newServicePriceEdit.clear()

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления услуги: {e}")

    def add_new_part(self):
        """Добавляет новую запчасть"""
        try:
            part_id = self.newPartCombo.currentData()
            if part_id == 0:
                QMessageBox.warning(self.dialog, "Ошибка", "Выберите запчасть")
                return

            part_text = self.newPartCombo.currentText()
            qty = self.newPartQtySpin.value()
            price_text = self.newPartPriceEdit.text().strip()
            warranty_text = self.newPartWarrantyEdit.text().strip()

            # Проверяем наличие на складе
            import re
            stock_match = re.search(r'\((\d+) шт\.\)', part_text)
            stock_qty = 0
            if stock_match:
                stock_qty = int(stock_match.group(1))
                if qty > stock_qty:
                    reply = QMessageBox.question(self.dialog, "Внимание",
                                                 f"На складе только {stock_qty} шт. этого товара.\n"
                                                 f"Добавить {qty} шт. все равно?",
                                                 QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.No:
                        return

            # Если цена не указана, берем из названия запчасти
            if not price_text:
                price_match = re.search(r'(\d+\.?\d*) ₽', part_text)
                if price_match:
                    price = float(price_match.group(1))
                else:
                    price = 0.0
            else:
                try:
                    price = float(price_text)
                except ValueError:
                    QMessageBox.warning(self.dialog, "Ошибка", "Введите корректную цену")
                    return

            # Гарантия
            warranty_days = 90
            if warranty_text:
                try:
                    warranty_days = int(warranty_text)
                except ValueError:
                    warranty_days = 90

            total = qty * price

            # Добавляем строку в таблицу
            row = self.partsTable.rowCount()
            self.partsTable.insertRow(row)

            # ID (временный)
            self.partsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(f"new_{row}"))

            # Запчасть
            self.partsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(part_text.split(' (')[0]))

            # Количество
            self.partsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(qty)))

            # Цена
            self.partsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price:.2f}"))

            # Сумма
            self.partsTable.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))

            # Гарантия
            self.partsTable.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{warranty_days} дней"))

            # На складе
            self.partsTable.setItem(row, 6, QtWidgets.QTableWidgetItem(str(stock_qty)))

            # Действия
            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("background-color: rgb(220, 53, 69); color: white; padding: 5px 10px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_part(r))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.partsTable.setCellWidget(row, 7, cell_widget)

            # Обновляем итоги
            self.update_totals()

            # Очищаем поля
            self.newPartQtySpin.setValue(1)
            self.newPartPriceEdit.clear()
            self.newPartWarrantyEdit.setText("90")

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления запчасти: {e}")

    def add_new_comment(self):
        """Добавляет новый комментарий"""
        try:
            comment_text = self.newCommentEdit.toPlainText().strip()
            if not comment_text:
                QMessageBox.warning(self.dialog, "Ошибка", "Введите текст комментария")
                return

            is_internal = self.commentTypeCombo.currentText() == "Внутренний"

            # Добавляем комментарий в базу данных
            connection = db_crm.get_crm_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO OrderComments (OrderID, EmployeeID, CommentText, IsInternal)
                    VALUES (%s, %s, %s, %s)
                """, (self.order_id, 1, comment_text, is_internal))  # EmployeeID = 1 (текущий пользователь)
                connection.commit()
                cursor.close()
                connection.close()

            # Добавляем комментарий в таблицу
            row = self.commentsTable.rowCount()
            self.commentsTable.insertRow(row)

            # Дата
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.commentsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(current_time))

            # Автор (текущий пользователь)
            self.commentsTable.setItem(row, 1, QtWidgets.QTableWidgetItem("Вы"))

            # Текст
            self.commentsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(comment_text))

            # Тип
            comment_type = "Внутренний" if is_internal else "Для клиента"
            self.commentsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(comment_type))

            # Очищаем поле ввода
            self.newCommentEdit.clear()

            QMessageBox.information(self.dialog, "Успех", "Комментарий добавлен")

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления комментария: {e}")

    def add_new_payment(self):
        """Добавляет новый платеж"""
        try:
            amount_text = self.newPaymentAmountEdit.text().strip()
            if not amount_text:
                QMessageBox.warning(self.dialog, "Ошибка", "Введите сумму платежа")
                return

            try:
                amount = float(amount_text)
                if amount <= 0:
                    QMessageBox.warning(self.dialog, "Ошибка", "Сумма должна быть больше 0")
                    return
            except ValueError:
                QMessageBox.warning(self.dialog, "Ошибка", "Введите корректную сумму")
                return

            payment_method = self.newPaymentMethodCombo.currentText()
            payment_type = self.newPaymentTypeCombo.currentText()

            # Добавляем платеж в базу данных
            connection = db_crm.get_crm_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO Payments (OrderID, Amount, PaymentMethod, PaymentType, EmployeeID)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.order_id, amount, payment_method, payment_type, 1))  # EmployeeID = 1
                connection.commit()
                cursor.close()
                connection.close()

            # Обновляем отображение платежей
            self.load_payments_history()

            # Пересчитываем финансовую информацию
            paid_amount = float(self.paidAmountEdit.text() or 0) + amount
            self.paidAmountEdit.setText(f"{paid_amount:.2f}")

            # Пересчитываем остаток
            final_amount = float(self.finalAmountEdit.text() or 0)
            balance = final_amount - paid_amount
            self.balanceAmountEdit.setText(f"{balance:.2f}")

            # Обновляем статус оплаты
            if balance <= 0:
                self.paymentStatusCombo.setCurrentIndex(2)  # Полностью оплачен
            else:
                self.paymentStatusCombo.setCurrentIndex(1)  # Частично оплачен

            # Очищаем поля
            self.newPaymentAmountEdit.clear()

            QMessageBox.information(self.dialog, "Успех", "Платеж добавлен")

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления платежа: {e}")

    def remove_service(self, row):
        """Удаляет услугу"""
        try:
            service_id_item = self.servicesTable.item(row, 0)
            if service_id_item:
                service_id = service_id_item.text()
                # Если это не новый элемент, удаляем из базы
                if not service_id.startswith('new_'):
                    connection = db_crm.get_crm_connection()
                    if connection:
                        cursor = connection.cursor()
                        cursor.execute("DELETE FROM OrderServices WHERE OrderServiceID = %s", (int(service_id),))
                        connection.commit()
                        cursor.close()
                        connection.close()

            self.servicesTable.removeRow(row)
            self.update_totals()

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка удаления услуги: {e}")

    def remove_part(self, row):
        """Удаляет запчасть"""
        try:
            part_id_item = self.partsTable.item(row, 0)
            if part_id_item:
                part_id = part_id_item.text()
                # Если это не новый элемент, удаляем из базы
                if not part_id.startswith('new_'):
                    # Сначала получаем количество для возврата на склад
                    qty_item = self.partsTable.item(row, 2)
                    if qty_item:
                        qty = int(qty_item.text())

                        # Получаем stock_id
                        connection = db_crm.get_crm_connection()
                        if connection:
                            cursor = connection.cursor(dictionary=True)
                            cursor.execute("SELECT StockID FROM OrderDetails WHERE OrderDetailID = %s", (int(part_id),))
                            result = cursor.fetchone()
                            if result:
                                stock_id = result['StockID']
                                # Возвращаем на склад
                                cursor.execute("""
                                    UPDATE DetailStock 
                                    SET CountInStock = CountInStock + %s
                                    WHERE StockID = %s
                                """, (qty, stock_id))

                            # Удаляем запись
                            cursor.execute("DELETE FROM OrderDetails WHERE OrderDetailID = %s", (int(part_id),))
                            connection.commit()
                            cursor.close()
                            connection.close()

            self.partsTable.removeRow(row)
            self.update_totals()

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка удаления запчасти: {e}")

    def save_order(self):
        """Сохраняет изменения заказа"""
        try:
            # Подготавливаем данные для сохранения
            order_data = {
                'order_id': self.order_id,
                'status': self.orderStatusCombo.currentText(),
                'order_type': self.orderTypeCombo.currentText(),
                'priority': self.orderPriorityCombo.currentText(),
                'device_type': self.deviceTypeCombo.currentText(),
                'device_brand': self.deviceBrandEdit.text().strip(),
                'device_model': self.deviceModelEdit.text().strip(),
                'device_imei': self.deviceImeiEdit.text().strip(),
                'device_appearance': self.appearanceEdit.toPlainText(),
                'problem_description': self.problemEdit.toPlainText(),
                'diagnosis': self.diagnosisEdit.toPlainText(),
                'recommendation': self.recommendationEdit.toPlainText(),
                'manager_id': self.managerCombo.currentData() if self.managerCombo.currentData() > 0 else None,
                'executor_id': self.executorCombo.currentData() if self.executorCombo.currentData() > 0 else None,
                'appeal_reason_id': self.reasonCombo.currentData() if self.reasonCombo.currentData() > 0 else None,
                'prepayment': float(self.prepaymentEdit.text() or 0),
                'discount': float(self.discountEdit.text() or 0),
                'total_amount': float(self.totalAmountEdit.text() or 0),
                'final_amount': float(self.finalAmountEdit.text() or 0),
                'estimated_completion': self.deadlineEdit.date().toString("yyyy-MM-dd") + " 18:00:00",
                'notes': self.completenessEdit.toPlainText(),
                'update_comment': "Изменения сохранены через форму редактирования",
                'updated_by': 1  # ID текущего пользователя
            }

            # Собираем услуги
            services_data = []
            for row in range(self.servicesTable.rowCount()):
                service_id_item = self.servicesTable.item(row, 0)
                service_name_item = self.servicesTable.item(row, 1)
                qty_item = self.servicesTable.item(row, 2)
                price_item = self.servicesTable.item(row, 3)
                status_item = self.servicesTable.item(row, 5)

                if all([service_id_item, service_name_item, qty_item, price_item, status_item]):
                    # Получаем ID типа услуги по названию
                    service_name = service_name_item.text()
                    service_type_id = None

                    # Ищем в комбобоксе
                    for i in range(self.newServiceCombo.count()):
                        if service_name in self.newServiceCombo.itemText(i):
                            service_type_id = self.newServiceCombo.itemData(i)
                            break

                    if service_type_id:
                        services_data.append({
                            'order_service_id': None if service_id_item.text().startswith('new_') else int(
                                service_id_item.text()),
                            'service_type_id': service_type_id,
                            'quantity': int(qty_item.text()),
                            'unit_price': float(price_item.text()),
                            'status': status_item.text()
                        })

            # Собираем запчасти
            parts_data = []
            for row in range(self.partsTable.rowCount()):
                part_id_item = self.partsTable.item(row, 0)
                part_name_item = self.partsTable.item(row, 1)
                qty_item = self.partsTable.item(row, 2)
                price_item = self.partsTable.item(row, 3)
                warranty_item = self.partsTable.item(row, 5)

                if all([part_id_item, part_name_item, qty_item, price_item, warranty_item]):
                    # Получаем ID запчасти по названию
                    part_name = part_name_item.text()
                    stock_id = None

                    # Ищем в комбобоксе
                    for i in range(self.newPartCombo.count()):
                        if part_name in self.newPartCombo.itemText(i):
                            stock_id = self.newPartCombo.itemData(i)
                            break

                    if stock_id:
                        warranty_match = re.search(r'(\d+)', warranty_item.text())
                        warranty_days = int(warranty_match.group(1)) if warranty_match else 90

                        parts_data.append({
                            'order_detail_id': None if part_id_item.text().startswith('new_') else int(
                                part_id_item.text()),
                            'stock_id': stock_id,
                            'quantity': int(qty_item.text()),
                            'unit_price': float(price_item.text()),
                            'warranty_days': warranty_days
                        })

            # Сохраняем изменения в базе данных
            success = db_crm.update_order_from_edit_form(
                self.order_id,
                order_data,
                parts_data,
                services_data
            )

            if success:
                QMessageBox.information(self.dialog, "Успех", "Изменения сохранены")
                self.dialog.accept()
            else:
                QMessageBox.critical(self.dialog, "Ошибка", "Не удалось сохранить изменения")

        except Exception as e:
            print(f"Ошибка сохранения заказа: {e}")
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка сохранения: {e}")

    def print_order(self):
        """Печатает информацию о заказе"""
        QMessageBox.information(self.dialog, "Печать", "Функция печати будет реализована позже")

    def close_order(self):
        """Завершает заказ"""
        try:
            reply = QMessageBox.question(
                self.dialog,
                "Завершение заказа",
                "Вы уверены, что хотите завершить этот заказ?\n"
                "После завершения изменить статус будет сложнее.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Устанавливаем статус "Завершен"
                self.orderStatusCombo.setCurrentText("Завершен")

                # Добавляем комментарий
                self.newCommentEdit.setText("Заказ завершен")
                self.commentTypeCombo.setCurrentText("Внутренний")
                self.add_new_comment()

                # Сохраняем изменения
                self.save_order()

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка завершения заказа: {e}")

    def retranslateUi(self, OrderEditDialog):
        _translate = QtCore.QCoreApplication.translate
        OrderEditDialog.setWindowTitle(_translate("OrderEditDialog", f"Редактирование заказа #{self.order_id}"))


# Класс для удобного использования
class OrderEditDialog(QtWidgets.QDialog):
    def __init__(self, order_id, order_data, parent=None):
        super().__init__(parent)
        self.ui = Ui_OrderEditDialog(order_id, order_data)
        self.ui.setupUi(self)
        self.setWindowTitle(f"Редактирование заказа #{order_id}")
        self.resize(1400, 900)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # Для тестирования
    dialog = QtWidgets.QDialog()
    ui = Ui_OrderEditDialog(1, {})
    ui.setupUi(dialog)
    dialog.show()

    sys.exit(app.exec_())