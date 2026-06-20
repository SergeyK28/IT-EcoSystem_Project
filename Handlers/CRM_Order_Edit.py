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

        # Упрощённый тёмный стиль (без градиентов)
        OrderEditDialog.setStyleSheet("""
            QDialog, QWidget {
                background-color: #2e2e2e;
                color: #f0f0f0;
            }
            QLabel {
                color: #f0f0f0;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #f0f0f0;
                border: 1px solid #5a5a5a;
                border-radius: 2px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QGroupBox {
                border: 1px solid #2d7d3a;
                border-radius: 3px;
                margin-top: 8px;
                font-weight: bold;
                color: #2d7d3a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #2d7d3a;
                background-color: #3a3a3a;
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                color: #f0f0f0;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 2px;
                border-top-right-radius: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2d7d3a;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #5a5a5a;
            }
            QTableWidget {
                background-color: #3a3a3a;
                color: #f0f0f0;
                gridline-color: #555;
                alternate-background-color: #404040;
                border: none;
            }
            QHeaderView::section {
                background-color: #2d7d3a;
                color: white;
                padding: 4px;
                border: 1px solid #555;
                font-weight: bold;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
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

        order_info_layout = QtWidgets.QVBoxLayout()

        self.orderNumberLabel = QtWidgets.QLabel()
        self.orderNumberLabel.setStyleSheet("""
            QLabel {
                color: #2d7d3a;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        self.orderStatusLabel = QtWidgets.QLabel()
        self.orderStatusLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 2px 6px;
                border-radius: 2px;
            }
        """)

        order_info_layout.addWidget(self.orderNumberLabel)
        order_info_layout.addWidget(self.orderStatusLabel)
        header_layout.addLayout(order_info_layout)

        client_info_layout = QtWidgets.QVBoxLayout()

        self.clientNameLabel = QtWidgets.QLabel()
        self.clientNameLabel.setStyleSheet("color: #b0b0b0; font-size: 14px;")

        self.clientContactsLabel = QtWidgets.QLabel()
        self.clientContactsLabel.setStyleSheet("color: #b0b0b0; font-size: 12px;")

        client_info_layout.addWidget(self.clientNameLabel)
        client_info_layout.addWidget(self.clientContactsLabel)
        header_layout.addLayout(client_info_layout)

        header_layout.addStretch()

        device_info_layout = QtWidgets.QVBoxLayout()

        self.deviceInfoLabel = QtWidgets.QLabel()
        self.deviceInfoLabel.setStyleSheet("color: #b0b0b0; font-size: 14px;")

        self.deviceProblemLabel = QtWidgets.QLabel()
        self.deviceProblemLabel.setStyleSheet("color: #d0d0d0; font-size: 12px;")
        self.deviceProblemLabel.setWordWrap(True)
        self.deviceProblemLabel.setMaximumWidth(400)

        device_info_layout.addWidget(self.deviceInfoLabel)
        device_info_layout.addWidget(self.deviceProblemLabel)
        header_layout.addLayout(device_info_layout)

        self.verticalLayout.addLayout(header_layout)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("background-color: #2d7d3a;")
        self.verticalLayout.addWidget(line)

    def setup_main_tab(self):
        """Настраивает вкладку основной информации"""
        layout = QtWidgets.QVBoxLayout(self.tab_main)

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

        client_name_label = QtWidgets.QLabel("ФИО:")
        self.clientNameEdit = QtWidgets.QLineEdit()
        client_layout.addWidget(client_name_label, 0, 0)
        client_layout.addWidget(self.clientNameEdit, 0, 1)

        phone_label = QtWidgets.QLabel("Телефон:")
        self.clientPhoneEdit = QtWidgets.QLineEdit()
        client_layout.addWidget(phone_label, 1, 0)
        client_layout.addWidget(self.clientPhoneEdit, 1, 1)

        email_label = QtWidgets.QLabel("Email:")
        self.clientEmailEdit = QtWidgets.QLineEdit()
        client_layout.addWidget(email_label, 2, 0)
        client_layout.addWidget(self.clientEmailEdit, 2, 1)

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

        type_label = QtWidgets.QLabel("Тип устройства:")
        self.deviceTypeCombo = QComboBox()
        self.deviceTypeCombo.addItems([
            "Смартфон", "Ноутбук", "Планшет", "Телевизор",
            "Игровая приставка", "Фотоаппарат", "Пылесос",
            "Кофемашина", "Другое"
        ])
        device_layout.addWidget(type_label, 0, 0)
        device_layout.addWidget(self.deviceTypeCombo, 0, 1)

        brand_label = QtWidgets.QLabel("Бренд:")
        self.deviceBrandEdit = QtWidgets.QLineEdit()
        device_layout.addWidget(brand_label, 1, 0)
        device_layout.addWidget(self.deviceBrandEdit, 1, 1)

        model_label = QtWidgets.QLabel("Модель:")
        self.deviceModelEdit = QtWidgets.QLineEdit()
        device_layout.addWidget(model_label, 2, 0)
        device_layout.addWidget(self.deviceModelEdit, 2, 1)

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

        status_label = QtWidgets.QLabel("Статус:")
        self.orderStatusCombo = QComboBox()
        self.orderStatusCombo.addItems([
            "Новая", "Активная", "Срочное", "Ждут запчасти",
            "В работе", "Готовое", "Закрыто неуспешно", "Завершен"
        ])
        order_layout.addWidget(status_label, 0, 0)
        order_layout.addWidget(self.orderStatusCombo, 0, 1)

        type_label = QtWidgets.QLabel("Тип заказа:")
        self.orderTypeCombo = QComboBox()
        self.orderTypeCombo.addItems(["Платный", "Гарантийный"])
        order_layout.addWidget(type_label, 1, 0)
        order_layout.addWidget(self.orderTypeCombo, 1, 1)

        priority_label = QtWidgets.QLabel("Приоритет:")
        self.orderPriorityCombo = QComboBox()
        self.orderPriorityCombo.addItems(["Низкий", "Средний", "Высокий", "Критичный"])
        order_layout.addWidget(priority_label, 2, 0)
        order_layout.addWidget(self.orderPriorityCombo, 2, 1)

        reason_label = QtWidgets.QLabel("Причина обращения:")
        self.reasonCombo = QComboBox()
        order_layout.addWidget(reason_label, 3, 0)
        order_layout.addWidget(self.reasonCombo, 3, 1)

        manager_label = QtWidgets.QLabel("Менеджер:")
        self.managerCombo = QComboBox()
        order_layout.addWidget(manager_label, 0, 2)
        order_layout.addWidget(self.managerCombo, 0, 3)

        executor_label = QtWidgets.QLabel("Исполнитель:")
        self.executorCombo = QComboBox()
        order_layout.addWidget(executor_label, 1, 2)
        order_layout.addWidget(self.executorCombo, 1, 3)

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

        appearance_label = QtWidgets.QLabel("Внешний вид/Состояние:")
        self.appearanceEdit = QtWidgets.QTextEdit()
        self.appearanceEdit.setMaximumHeight(80)
        appearance_layout.addWidget(appearance_label)
        appearance_layout.addWidget(self.appearanceEdit)

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

        problem_label = QtWidgets.QLabel("Описание проблемы клиента:")
        self.problemEdit = QtWidgets.QTextEdit()
        self.problemEdit.setMaximumHeight(80)
        problem_layout.addWidget(problem_label)
        problem_layout.addWidget(self.problemEdit)

        diagnosis_label = QtWidgets.QLabel("Диагностика мастера:")
        self.diagnosisEdit = QtWidgets.QTextEdit()
        self.diagnosisEdit.setMaximumHeight(80)
        problem_layout.addWidget(diagnosis_label)
        problem_layout.addWidget(self.diagnosisEdit)

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

        services_parts_tabs = QTabWidget()

        # 1. ВКЛАДКА УСЛУГ
        services_tab = QtWidgets.QWidget()
        services_layout = QtWidgets.QVBoxLayout(services_tab)

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
        self.addServiceBtn.setStyleSheet("background-color: #2d7d3a; border: none;")
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

        self.servicesTable = QtWidgets.QTableWidget()
        self.servicesTable.setColumnCount(7)
        self.servicesTable.setHorizontalHeaderLabels(["ID", "Услуга", "Кол-во", "Цена", "Сумма", "Статус", "Действия"])
        self.servicesTable.setColumnHidden(0, True)
        services_layout.addWidget(self.servicesTable)

        services_parts_tabs.addTab(services_tab, "Услуги")

        # 2. ВКЛАДКА ЗАПЧАСТЕЙ
        parts_tab = QtWidgets.QWidget()
        parts_layout = QtWidgets.QVBoxLayout(parts_tab)

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
        self.addPartBtn.setStyleSheet("background-color: #2d7d3a; border: none;")
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

        self.partsTable = QtWidgets.QTableWidget()
        self.partsTable.setColumnCount(8)
        self.partsTable.setHorizontalHeaderLabels(
            ["ID", "Запчасть", "Кол-во", "Цена", "Сумма", "Гарантия", "На складе", "Действия"])
        self.partsTable.setColumnHidden(0, True)
        parts_layout.addWidget(self.partsTable)

        services_parts_tabs.addTab(parts_tab, "Запчасти")

        layout.addWidget(services_parts_tabs)

        total_group = QtWidgets.QGroupBox("ИТОГО")
        total_layout = QtWidgets.QHBoxLayout()

        self.servicesTotalLabel = QtWidgets.QLabel("Услуги: 0.00 ₽")
        self.servicesTotalLabel.setStyleSheet("color: #2d7d3a; font-size: 14px;")

        self.partsTotalLabel = QtWidgets.QLabel("Запчасти: 0.00 ₽")
        self.partsTotalLabel.setStyleSheet("color: #2d7d3a; font-size: 14px;")

        self.totalAmountLabel = QtWidgets.QLabel("ИТОГО: 0.00 ₽")
        self.totalAmountLabel.setStyleSheet("color: #2d7d3a; font-size: 16px; font-weight: bold;")

        total_layout.addWidget(self.servicesTotalLabel)
        total_layout.addWidget(self.partsTotalLabel)
        total_layout.addStretch()
        total_layout.addWidget(self.totalAmountLabel)

        total_group.setLayout(total_layout)
        layout.addWidget(total_group)

    def setup_comments_history_tab(self):
        """Настраивает вкладку комментариев и истории"""
        layout = QtWidgets.QVBoxLayout(self.tab_comments_history)

        comments_history_tabs = QTabWidget()

        # 1. ВКЛАДКА КОММЕНТАРИЕВ
        comments_tab = QtWidgets.QWidget()
        comments_layout = QtWidgets.QVBoxLayout(comments_tab)

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
        self.addCommentBtn.setStyleSheet("background-color: #2d7d3a; border: none;")
        self.addCommentBtn.clicked.connect(self.add_new_comment)

        comment_text_layout.addWidget(self.newCommentEdit)
        comment_text_layout.addWidget(self.addCommentBtn)
        add_comment_layout.addLayout(comment_text_layout)

        comments_layout.addLayout(add_comment_layout)

        self.commentsTable = QtWidgets.QTableWidget()
        self.commentsTable.setColumnCount(4)
        self.commentsTable.setHorizontalHeaderLabels(["Дата", "Автор", "Текст", "Тип"])
        comments_layout.addWidget(self.commentsTable)

        comments_history_tabs.addTab(comments_tab, "Комментарии")

        # 2. ВКЛАДКА ИСТОРИИ СТАТУСОВ
        history_tab = QtWidgets.QWidget()
        history_layout = QtWidgets.QVBoxLayout(history_tab)

        self.historyTable = QtWidgets.QTableWidget()
        self.historyTable.setColumnCount(5)
        self.historyTable.setHorizontalHeaderLabels(["Дата", "Старый статус", "Новый статус", "Кто изменил", "Причина"])
        history_layout.addWidget(self.historyTable)

        comments_history_tabs.addTab(history_tab, "История статусов")

        layout.addWidget(comments_history_tabs)

    def setup_finance_tab(self):
        """Настраивает вкладку финансов"""
        layout = QtWidgets.QVBoxLayout(self.tab_finance)

        finance_group = QtWidgets.QGroupBox("ФИНАНСОВАЯ ИНФОРМАЦИЯ")
        finance_layout = QtWidgets.QGridLayout()
        finance_layout.setHorizontalSpacing(15)
        finance_layout.setVerticalSpacing(10)

        total_label = QtWidgets.QLabel("Общая сумма:")
        self.totalAmountEdit = QtWidgets.QLineEdit()
        self.totalAmountEdit.setReadOnly(True)
        finance_layout.addWidget(total_label, 0, 0)
        finance_layout.addWidget(self.totalAmountEdit, 0, 1)

        discount_label = QtWidgets.QLabel("Скидка (%):")
        self.discountEdit = QtWidgets.QLineEdit()
        self.discountEdit.setText("0")
        finance_layout.addWidget(discount_label, 1, 0)
        finance_layout.addWidget(self.discountEdit, 1, 1)

        final_label = QtWidgets.QLabel("Итоговая сумма:")
        self.finalAmountEdit = QtWidgets.QLineEdit()
        self.finalAmountEdit.setReadOnly(True)
        finance_layout.addWidget(final_label, 2, 0)
        finance_layout.addWidget(self.finalAmountEdit, 2, 1)

        prepayment_label = QtWidgets.QLabel("Предоплата:")
        self.prepaymentEdit = QtWidgets.QLineEdit()
        finance_layout.addWidget(prepayment_label, 3, 0)
        finance_layout.addWidget(self.prepaymentEdit, 3, 1)

        paid_label = QtWidgets.QLabel("Оплачено всего:")
        self.paidAmountEdit = QtWidgets.QLineEdit()
        self.paidAmountEdit.setReadOnly(True)
        finance_layout.addWidget(paid_label, 0, 2)
        finance_layout.addWidget(self.paidAmountEdit, 0, 3)

        balance_label = QtWidgets.QLabel("Остаток к оплате:")
        self.balanceAmountEdit = QtWidgets.QLineEdit()
        self.balanceAmountEdit.setReadOnly(True)
        finance_layout.addWidget(balance_label, 1, 2)
        finance_layout.addWidget(self.balanceAmountEdit, 1, 3)

        payment_status_label = QtWidgets.QLabel("Статус оплаты:")
        self.paymentStatusCombo = QComboBox()
        self.paymentStatusCombo.addItems(["Не оплачен", "Частично оплачен", "Полностью оплачен"])
        finance_layout.addWidget(payment_status_label, 2, 2)
        finance_layout.addWidget(self.paymentStatusCombo, 2, 3)

        finance_group.setLayout(finance_layout)
        layout.addWidget(finance_group)

        payments_group = QtWidgets.QGroupBox("ИСТОРИЯ ПЛАТЕЖЕЙ")
        payments_layout = QtWidgets.QVBoxLayout()

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
        self.addPaymentBtn.setStyleSheet("background-color: #2d7d3a; border: none;")
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

        self.saveBtn = QtWidgets.QPushButton("💾 Сохранить изменения")
        self.saveBtn.setStyleSheet("""
            QPushButton {
                background-color: #2d7d3a;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #3a9a4a;
            }
        """)
        self.saveBtn.clicked.connect(self.save_order)

        self.cancelBtn = QtWidgets.QPushButton("❌ Отмена")
        self.cancelBtn.setStyleSheet("""
            QPushButton {
                background-color: #6c6c6c;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border: none;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #7c7c7c;
            }
        """)
        self.cancelBtn.clicked.connect(self.dialog.reject)

        self.printBtn = QtWidgets.QPushButton("🖨️ Печать")
        self.printBtn.setStyleSheet("background-color: #1a7a8a; border: none;")
        self.printBtn.clicked.connect(self.print_order)

        self.closeBtn = QtWidgets.QPushButton("✅ Завершить заказ")
        self.closeBtn.setStyleSheet("background-color: #2d7d3a; border: none;")
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
            if not self.order_data:
                QMessageBox.critical(self.dialog, "Ошибка", "Не удалось загрузить данные заказа")
                return

            self.orderNumberLabel.setText(f"Заказ #{self.order_data.get('OrderNumber', self.order_id)}")

            status = self.order_data.get('Status', 'Новая')
            self.orderStatusLabel.setText(f"Статус: {status}")
            self.set_status_color(status)

            client_name = f"{self.order_data.get('ClientFirstName', '')} {self.order_data.get('ClientLastName', '')}"
            self.clientNameLabel.setText(f"Клиент: {client_name}")
            self.clientContactsLabel.setText(
                f"Тел: {self.order_data.get('ClientPhone', '')} | Email: {self.order_data.get('ClientEmail', '')}")

            device_info = f"{self.order_data.get('DeviceType', '')} {self.order_data.get('DeviceBrand', '')} {self.order_data.get('DeviceModel', '')}"
            self.deviceInfoLabel.setText(f"Устройство: {device_info}")

            problem = self.order_data.get('ProblemDescription', '')
            if len(problem) > 100:
                problem = problem[:100] + "..."
            self.deviceProblemLabel.setText(f"Проблема: {problem}")

            self.fill_main_fields()
            self.fill_services_parts()
            self.fill_comments_history()
            self.fill_finance_info()
            self.load_combobox_data()

        except Exception as e:
            print(f"Ошибка загрузки данных заказа: {e}")
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка загрузки данных заказа: {e}")

    def fill_main_fields(self):
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
        services_list = self.order_data.get('services_list', [])
        self.servicesTable.setRowCount(len(services_list))

        for row, service in enumerate(services_list):
            self.servicesTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(service.get('OrderServiceID', ''))))
            self.servicesTable.setItem(row, 1, QtWidgets.QTableWidgetItem(service.get('ServiceDescription', '')))
            self.servicesTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(service.get('Quantity', 1))))
            price = service.get('UnitPrice', 0)
            self.servicesTable.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            total = service.get('TotalPrice', price)
            self.servicesTable.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))
            status = service.get('ServiceStatus', 'Запланировано')
            self.servicesTable.setItem(row, 5, QtWidgets.QTableWidgetItem(status))

            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("background-color: #b33c3c; color: white; padding: 4px 8px; border: none; border-radius: 2px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_service(r))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.servicesTable.setCellWidget(row, 6, cell_widget)

        parts_list = self.order_data.get('details_list', [])
        self.partsTable.setRowCount(len(parts_list))

        for row, part in enumerate(parts_list):
            self.partsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(part.get('OrderDetailID', ''))))
            part_name = f"{part.get('DetailName', '')} ({part.get('DetailCode', '')})"
            self.partsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(part_name))
            self.partsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(part.get('Quantity', 1))))
            price = part.get('UnitPrice', 0)
            self.partsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            total = part.get('TotalPrice', price)
            self.partsTable.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))
            warranty = part.get('WarrantyDays', 90)
            self.partsTable.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{warranty} дней"))
            stock_qty = part.get('CountInStock', 0)
            self.partsTable.setItem(row, 6, QtWidgets.QTableWidgetItem(str(stock_qty)))

            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("background-color: #b33c3c; color: white; padding: 4px 8px; border: none; border-radius: 2px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_part(r))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.partsTable.setCellWidget(row, 7, cell_widget)

        self.update_totals()

    def fill_comments_history(self):
        comments_list = self.order_data.get('comments_list', [])
        self.commentsTable.setRowCount(len(comments_list))

        for row, comment in enumerate(comments_list):
            date = comment.get('CommentDate', '')
            if date:
                date_str = str(date)[:19]
            else:
                date_str = ''
            self.commentsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(date_str))

            author = comment.get('EmployeeName', 'Система')
            self.commentsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(author))

            self.commentsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(comment.get('CommentText', '')))

            is_internal = comment.get('IsInternal', False)
            comment_type = "Внутренний" if is_internal else "Для клиента"
            self.commentsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(comment_type))

        history_list = self.order_data.get('status_history', [])
        self.historyTable.setRowCount(len(history_list))

        for row, history in enumerate(history_list):
            date = history.get('ChangeDate', '')
            if date:
                date_str = str(date)[:19]
            else:
                date_str = ''
            self.historyTable.setItem(row, 0, QtWidgets.QTableWidgetItem(date_str))

            self.historyTable.setItem(row, 1, QtWidgets.QTableWidgetItem(history.get('OldStatus', '')))
            self.historyTable.setItem(row, 2, QtWidgets.QTableWidgetItem(history.get('NewStatus', '')))
            self.historyTable.setItem(row, 3, QtWidgets.QTableWidgetItem(history.get('ChangedByName', '')))
            self.historyTable.setItem(row, 4, QtWidgets.QTableWidgetItem(history.get('ChangeReason', '')))

    def fill_finance_info(self):
        total_amount = self.order_data.get('TotalAmount', 0)
        self.totalAmountEdit.setText(f"{total_amount:.2f}")

        discount = self.order_data.get('Discount', 0)
        self.discountEdit.setText(f"{discount:.2f}")

        final_amount = self.order_data.get('FinalAmount', 0)
        self.finalAmountEdit.setText(f"{final_amount:.2f}")

        prepayment = self.order_data.get('Prepayment', 0)
        self.prepaymentEdit.setText(f"{prepayment:.2f}")

        paid_amount = self.order_data.get('AllPaymentsTotal', 0)
        self.paidAmountEdit.setText(f"{paid_amount:.2f}")

        balance = final_amount - paid_amount
        self.balanceAmountEdit.setText(f"{balance:.2f}")

        if balance <= 0:
            self.paymentStatusCombo.setCurrentIndex(2)
        elif paid_amount > 0:
            self.paymentStatusCombo.setCurrentIndex(1)
        else:
            self.paymentStatusCombo.setCurrentIndex(0)

        self.load_payments_history()

    def load_combobox_data(self):
        try:
            reasons = db_crm.get_all_appeal_reasons()
            self.reasonCombo.clear()
            self.reasonCombo.addItem("Не выбрано", 0)
            for reason in reasons:
                self.reasonCombo.addItem(reason['ReasonName'], reason['ReasonID'])

            appeal_reason_id = self.order_data.get('AppealReasonID')
            if appeal_reason_id:
                for i in range(self.reasonCombo.count()):
                    if self.reasonCombo.itemData(i) == appeal_reason_id:
                        self.reasonCombo.setCurrentIndex(i)
                        break

            employees = db_crm.get_all_employees()
            self.managerCombo.clear()
            self.executorCombo.clear()

            self.managerCombo.addItem("Не назначен", 0)
            self.executorCombo.addItem("Не назначен", 0)

            for emp in employees:
                name = f"{emp['FirstName']} {emp['LastName']}"
                self.managerCombo.addItem(name, emp['EmployeeID'])
                self.executorCombo.addItem(name, emp['EmployeeID'])

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

            services = db_crm.get_all_service_types()
            self.newServiceCombo.clear()
            self.newServiceCombo.addItem("Выберите услугу", 0)
            for service in services:
                service_text = f"{service['ServiceDescription']} - {service['BasePrice']:.2f} ₽"
                self.newServiceCombo.addItem(service_text, service['ServiceTypeID'])

            parts = db_crm.get_all_stock_items()
            self.newPartCombo.clear()
            self.newPartCombo.addItem("Выберите запчасть", 0)
            for part in parts:
                part_text = f"{part['DetailName']} ({part['CountInStock']} шт.) - {part['Price']:.2f} ₽"
                self.newPartCombo.addItem(part_text, part['StockID'])

        except Exception as e:
            print(f"Ошибка загрузки данных в комбобоксы: {e}")

    def load_payments_history(self):
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
                date = payment.get('PaymentDate', '')
                if date:
                    date_str = str(date)[:19]
                else:
                    date_str = ''
                self.paymentsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(date_str))

                amount = payment.get('Amount', 0)
                self.paymentsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{amount:.2f}"))

                self.paymentsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(payment.get('PaymentMethod', '')))
                self.paymentsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(payment.get('PaymentType', '')))
                self.paymentsTable.setItem(row, 4, QtWidgets.QTableWidgetItem(payment.get('ReceiptNumber', '')))
                self.paymentsTable.setItem(row, 5, QtWidgets.QTableWidgetItem(payment.get('Notes', '')))

        except Exception as e:
            print(f"Ошибка загрузки истории платежей: {e}")

    def set_status_color(self, status):
        colors = {
            'Новая': '#4287f5',
            'Активная': '#ffc107',
            'Срочное': '#dc3545',
            'В работе': '#198754',
            'Ждут запчасти': '#ff9500',
            'Готовое': '#28a745',
            'Завершен': '#6c757d',
            'Закрыто неуспешно': '#6c757d',
        }
        color = colors.get(status, '#6c757d')
        self.orderStatusLabel.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                padding: 2px 6px;
                border-radius: 2px;
                background-color: {color};
                color: white;
            }}
        """)

    def update_totals(self):
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

            self.totalAmountEdit.setText(f"{total:.2f}")

            try:
                discount = float(self.discountEdit.text() or 0)
                final_amount = total * (1 - discount / 100)
                self.finalAmountEdit.setText(f"{final_amount:.2f}")

                paid_amount = float(self.paidAmountEdit.text() or 0)
                balance = final_amount - paid_amount
                self.balanceAmountEdit.setText(f"{balance:.2f}")
            except:
                pass

        except Exception as e:
            print(f"Ошибка обновления итогов: {e}")

    def add_new_service(self):
        try:
            service_id = self.newServiceCombo.currentData()
            if service_id == 0:
                QMessageBox.warning(self.dialog, "Ошибка", "Выберите услугу")
                return

            service_text = self.newServiceCombo.currentText()
            qty = self.newServiceQtySpin.value()
            price_text = self.newServicePriceEdit.text().strip()

            if not price_text:
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

            row = self.servicesTable.rowCount()
            self.servicesTable.insertRow(row)

            self.servicesTable.setItem(row, 0, QtWidgets.QTableWidgetItem(f"new_{row}"))
            self.servicesTable.setItem(row, 1, QtWidgets.QTableWidgetItem(service_text.split(' - ')[0]))
            self.servicesTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(qty)))
            self.servicesTable.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            self.servicesTable.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))
            self.servicesTable.setItem(row, 5, QtWidgets.QTableWidgetItem("Запланировано"))

            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("background-color: #b33c3c; color: white; padding: 4px 8px; border: none; border-radius: 2px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_service(r))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.servicesTable.setCellWidget(row, 6, cell_widget)

            self.update_totals()

            self.newServiceQtySpin.setValue(1)
            self.newServicePriceEdit.clear()

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления услуги: {e}")

    def add_new_part(self):
        try:
            part_id = self.newPartCombo.currentData()
            if part_id == 0:
                QMessageBox.warning(self.dialog, "Ошибка", "Выберите запчасть")
                return

            part_text = self.newPartCombo.currentText()
            qty = self.newPartQtySpin.value()
            price_text = self.newPartPriceEdit.text().strip()
            warranty_text = self.newPartWarrantyEdit.text().strip()

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

            warranty_days = 90
            if warranty_text:
                try:
                    warranty_days = int(warranty_text)
                except ValueError:
                    warranty_days = 90

            total = qty * price

            row = self.partsTable.rowCount()
            self.partsTable.insertRow(row)

            self.partsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(f"new_{row}"))
            self.partsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(part_text.split(' (')[0]))
            self.partsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(qty)))
            self.partsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{price:.2f}"))
            self.partsTable.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{total:.2f}"))
            self.partsTable.setItem(row, 5, QtWidgets.QTableWidgetItem(f"{warranty_days} дней"))
            self.partsTable.setItem(row, 6, QtWidgets.QTableWidgetItem(str(stock_qty)))

            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("background-color: #b33c3c; color: white; padding: 4px 8px; border: none; border-radius: 2px;")
            delete_btn.clicked.connect(lambda checked, r=row: self.remove_part(r))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.partsTable.setCellWidget(row, 7, cell_widget)

            self.update_totals()

            self.newPartQtySpin.setValue(1)
            self.newPartPriceEdit.clear()
            self.newPartWarrantyEdit.setText("90")

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления запчасти: {e}")

    def add_new_comment(self):
        try:
            comment_text = self.newCommentEdit.toPlainText().strip()
            if not comment_text:
                QMessageBox.warning(self.dialog, "Ошибка", "Введите текст комментария")
                return

            is_internal = self.commentTypeCombo.currentText() == "Внутренний"

            connection = db_crm.get_crm_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO OrderComments (OrderID, EmployeeID, CommentText, IsInternal)
                    VALUES (%s, %s, %s, %s)
                """, (self.order_id, 1, comment_text, is_internal))
                connection.commit()
                cursor.close()
                connection.close()

            row = self.commentsTable.rowCount()
            self.commentsTable.insertRow(row)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.commentsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(current_time))
            self.commentsTable.setItem(row, 1, QtWidgets.QTableWidgetItem("Вы"))
            self.commentsTable.setItem(row, 2, QtWidgets.QTableWidgetItem(comment_text))
            comment_type = "Внутренний" if is_internal else "Для клиента"
            self.commentsTable.setItem(row, 3, QtWidgets.QTableWidgetItem(comment_type))

            self.newCommentEdit.clear()

            QMessageBox.information(self.dialog, "Успех", "Комментарий добавлен")

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления комментария: {e}")

    def add_new_payment(self):
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

            connection = db_crm.get_crm_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO Payments (OrderID, Amount, PaymentMethod, PaymentType, EmployeeID)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.order_id, amount, payment_method, payment_type, 1))
                connection.commit()
                cursor.close()
                connection.close()

            self.load_payments_history()

            paid_amount = float(self.paidAmountEdit.text() or 0) + amount
            self.paidAmountEdit.setText(f"{paid_amount:.2f}")

            final_amount = float(self.finalAmountEdit.text() or 0)
            balance = final_amount - paid_amount
            self.balanceAmountEdit.setText(f"{balance:.2f}")

            if balance <= 0:
                self.paymentStatusCombo.setCurrentIndex(2)
            else:
                self.paymentStatusCombo.setCurrentIndex(1)

            self.newPaymentAmountEdit.clear()

            QMessageBox.information(self.dialog, "Успех", "Платеж добавлен")

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления платежа: {e}")

    def remove_service(self, row):
        try:
            service_id_item = self.servicesTable.item(row, 0)
            if service_id_item:
                service_id = service_id_item.text()
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
        try:
            part_id_item = self.partsTable.item(row, 0)
            if part_id_item:
                part_id = part_id_item.text()
                if not part_id.startswith('new_'):
                    qty_item = self.partsTable.item(row, 2)
                    if qty_item:
                        qty = int(qty_item.text())

                        connection = db_crm.get_crm_connection()
                        if connection:
                            cursor = connection.cursor(dictionary=True)
                            cursor.execute("SELECT StockID FROM OrderDetails WHERE OrderDetailID = %s", (int(part_id),))
                            result = cursor.fetchone()
                            if result:
                                stock_id = result['StockID']
                                cursor.execute("""
                                    UPDATE DetailStock 
                                    SET CountInStock = CountInStock + %s
                                    WHERE StockID = %s
                                """, (qty, stock_id))

                            cursor.execute("DELETE FROM OrderDetails WHERE OrderDetailID = %s", (int(part_id),))
                            connection.commit()
                            cursor.close()
                            connection.close()

            self.partsTable.removeRow(row)
            self.update_totals()

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка удаления запчасти: {e}")

    def save_order(self):
        try:
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
                'updated_by': 1
            }

            services_data = []
            for row in range(self.servicesTable.rowCount()):
                service_id_item = self.servicesTable.item(row, 0)
                service_name_item = self.servicesTable.item(row, 1)
                qty_item = self.servicesTable.item(row, 2)
                price_item = self.servicesTable.item(row, 3)
                status_item = self.servicesTable.item(row, 5)

                if all([service_id_item, service_name_item, qty_item, price_item, status_item]):
                    service_name = service_name_item.text()
                    service_type_id = None

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

            parts_data = []
            for row in range(self.partsTable.rowCount()):
                part_id_item = self.partsTable.item(row, 0)
                part_name_item = self.partsTable.item(row, 1)
                qty_item = self.partsTable.item(row, 2)
                price_item = self.partsTable.item(row, 3)
                warranty_item = self.partsTable.item(row, 5)

                if all([part_id_item, part_name_item, qty_item, price_item, warranty_item]):
                    part_name = part_name_item.text()
                    stock_id = None

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
        QMessageBox.information(self.dialog, "Печать", "Функция печати будет реализована позже")

    def close_order(self):
        try:
            reply = QMessageBox.question(
                self.dialog,
                "Завершение заказа",
                "Вы уверены, что хотите завершить этот заказ?\n"
                "После завершения изменить статус будет сложнее.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.orderStatusCombo.setCurrentText("Завершен")
                self.newCommentEdit.setText("Заказ завершен")
                self.commentTypeCombo.setCurrentText("Внутренний")
                self.add_new_comment()
                self.save_order()

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка завершения заказа: {e}")

    def retranslateUi(self, OrderEditDialog):
        _translate = QtCore.QCoreApplication.translate
        OrderEditDialog.setWindowTitle(_translate("OrderEditDialog", f"Редактирование заказа #{self.order_id}"))


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
    dialog = QtWidgets.QDialog()
    ui = Ui_OrderEditDialog(1, {})
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())