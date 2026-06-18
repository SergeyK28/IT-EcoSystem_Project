# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QComboBox, QDateEdit, QSpinBox
from Server import db_crm
from datetime import datetime
import re


class Ui_AddOrderDialog(object):
    def __init__(self):
        self.dialog = None
        self.client_id = None

    def setupUi(self, AddOrderDialog):
        self.dialog = AddOrderDialog

        AddOrderDialog.setObjectName("AddOrderDialog")
        AddOrderDialog.resize(1400, 900)  # Увеличим размер для новых секций

        # Темный стиль
        AddOrderDialog.setStyleSheet("""
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

        self.verticalLayout = QtWidgets.QVBoxLayout(AddOrderDialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)

        # Создаем ScrollArea для прокрутки
        self.scrollArea = QtWidgets.QScrollArea(AddOrderDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.scrollAreaWidgetContents = QtWidgets.QWidget()

        self.mainLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.mainLayout.setSpacing(15)

        # 1. ЗАГОЛОВОК
        title_label = QtWidgets.QLabel("ДОБАВЛЕНИЕ НОВОГО ЗАКАЗА")
        title_label.setStyleSheet("""
            QLabel {
                color: rgb(103, 155, 118);
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                padding: 10px;
                border-bottom: 2px solid rgb(103, 155, 118);
            }
        """)
        self.mainLayout.addWidget(title_label)

        # 2. ИНФОРМАЦИЯ О КЛИЕНТЕ
        self.create_client_section()

        # 3. ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ
        self.create_device_section()

        # 4. ИНФОРМАЦИЯ О ЗАКАЗЕ
        self.create_order_section()

        # 5. СЕКЦИЯ УСЛУГ
        self.create_services_section()

        # 6. СЕКЦИЯ ЗАПЧАСТЕЙ
        self.create_parts_section()

        # 7. СЕКЦИЯ ИТОГО
        self.create_total_section()

        # 8. КНОПКИ ДЕЙСТВИЙ
        self.create_action_buttons()

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        # Загружаем данные в комбобоксы
        self.load_combobox_data()

        self.retranslateUi(AddOrderDialog)
        QtCore.QMetaObject.connectSlotsByName(AddOrderDialog)

    def create_client_section(self):
        """Создает секцию информации о клиенте"""
        client_group = QtWidgets.QGroupBox("ИНФОРМАЦИЯ О КЛИЕНТЕ")
        client_layout = QtWidgets.QVBoxLayout()

        # Кнопка выбора существующего клиента
        search_layout = QtWidgets.QHBoxLayout()
        self.searchClientBtn = QtWidgets.QPushButton("🔍 Найти существующего клиента")
        self.searchClientBtn.setStyleSheet("background-color: rgb(28, 113, 216);")
        self.searchClientBtn.clicked.connect(self.search_client)
        search_layout.addWidget(self.searchClientBtn)
        search_layout.addStretch()
        client_layout.addLayout(search_layout)

        # Или создать нового
        new_client_label = QtWidgets.QLabel("Или создайте нового клиента:")
        new_client_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px; margin-top: 10px;")
        client_layout.addWidget(new_client_label)

        # ФИО
        name_layout = QtWidgets.QHBoxLayout()
        first_name_label = QtWidgets.QLabel("Имя:")
        self.firstNameInput = QtWidgets.QLineEdit()
        self.firstNameInput.setPlaceholderText("Введите имя")
        last_name_label = QtWidgets.QLabel("Фамилия:")
        self.lastNameInput = QtWidgets.QLineEdit()
        self.lastNameInput.setPlaceholderText("Введите фамилию")

        name_layout.addWidget(first_name_label)
        name_layout.addWidget(self.firstNameInput)
        name_layout.addWidget(last_name_label)
        name_layout.addWidget(self.lastNameInput)
        client_layout.addLayout(name_layout)

        # Контакты
        contacts_layout = QtWidgets.QHBoxLayout()
        phone_label = QtWidgets.QLabel("Телефон:")
        self.phoneInput = QtWidgets.QLineEdit()
        self.phoneInput.setPlaceholderText("+7XXXXXXXXXX")
        email_label = QtWidgets.QLabel("Email:")
        self.emailInput = QtWidgets.QLineEdit()
        self.emailInput.setPlaceholderText("email@example.com")

        contacts_layout.addWidget(phone_label)
        contacts_layout.addWidget(self.phoneInput)
        contacts_layout.addWidget(email_label)
        contacts_layout.addWidget(self.emailInput)
        client_layout.addLayout(contacts_layout)

        # Дата рождения
        birth_layout = QtWidgets.QHBoxLayout()
        birth_label = QtWidgets.QLabel("Дата рождения:")
        self.birthdateInput = QDateEdit()
        self.birthdateInput.setCalendarPopup(True)
        self.birthdateInput.setDisplayFormat("dd.MM.yyyy")
        self.birthdateInput.setDate(QtCore.QDate(1990, 1, 1))

        birth_layout.addWidget(birth_label)
        birth_layout.addWidget(self.birthdateInput)
        birth_layout.addStretch()
        client_layout.addLayout(birth_layout)

        client_group.setLayout(client_layout)
        self.mainLayout.addWidget(client_group)

    def create_device_section(self):
        """Создает секцию информации об устройстве"""
        device_group = QtWidgets.QGroupBox("ИНФОРМАЦИЯ ОБ УСТРОЙСТВЕ")
        device_layout = QtWidgets.QVBoxLayout()

        # Тип устройства
        type_layout = QtWidgets.QHBoxLayout()
        type_label = QtWidgets.QLabel("Тип устройства:")
        self.deviceTypeCombo = QComboBox()
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.deviceTypeCombo)
        type_layout.addStretch()
        device_layout.addLayout(type_layout)

        # Бренд и модель
        brand_model_layout = QtWidgets.QHBoxLayout()
        brand_label = QtWidgets.QLabel("Бренд:")
        self.brandInput = QtWidgets.QLineEdit()
        self.brandInput.setPlaceholderText("Например: Apple, Samsung")
        model_label = QtWidgets.QLabel("Модель:")
        self.modelInput = QtWidgets.QLineEdit()
        self.modelInput.setPlaceholderText("Например: iPhone 12, Galaxy S21")

        brand_model_layout.addWidget(brand_label)
        brand_model_layout.addWidget(self.brandInput)
        brand_model_layout.addWidget(model_label)
        brand_model_layout.addWidget(self.modelInput)
        device_layout.addLayout(brand_model_layout)

        # IMEI/SN
        imei_layout = QtWidgets.QHBoxLayout()
        imei_label = QtWidgets.QLabel("IMEI/Серийный номер:")
        self.imeiInput = QtWidgets.QLineEdit()
        self.imeiInput.setPlaceholderText("Введите IMEI или серийный номер")
        imei_layout.addWidget(imei_label)
        imei_layout.addWidget(self.imeiInput)
        device_layout.addLayout(imei_layout)

        # Внешний вид
        appearance_layout = QtWidgets.QVBoxLayout()
        appearance_label = QtWidgets.QLabel("Внешний вид/Состояние:")
        self.appearanceInput = QtWidgets.QTextEdit()
        self.appearanceInput.setMaximumHeight(60)
        self.appearanceInput.setPlaceholderText("Опишите внешний вид устройства, повреждения, царапины и т.д.")
        appearance_layout.addWidget(appearance_label)
        appearance_layout.addWidget(self.appearanceInput)
        device_layout.addLayout(appearance_layout)

        # Комплектация
        completeness_layout = QtWidgets.QVBoxLayout()
        completeness_label = QtWidgets.QLabel("Комплектация:")
        self.completenessInput = QtWidgets.QTextEdit()
        self.completenessInput.setMaximumHeight(50)
        self.completenessInput.setPlaceholderText("Что входит в комплект: зарядка, наушники, коробка и т.д.")
        completeness_layout.addWidget(completeness_label)
        completeness_layout.addWidget(self.completenessInput)
        device_layout.addLayout(completeness_layout)

        # Причина обращения
        reason_layout = QtWidgets.QHBoxLayout()
        reason_label = QtWidgets.QLabel("Причина обращения:")
        self.reasonCombo = QComboBox()
        reason_layout.addWidget(reason_label)
        reason_layout.addWidget(self.reasonCombo)
        reason_layout.addStretch()
        device_layout.addLayout(reason_layout)

        # Описание проблемы
        problem_layout = QtWidgets.QVBoxLayout()
        problem_label = QtWidgets.QLabel("Описание проблемы:")
        self.problemInput = QtWidgets.QTextEdit()
        self.problemInput.setMaximumHeight(80)
        self.problemInput.setPlaceholderText("Подробно опишите проблему, симптомы, когда появилась и т.д.")
        problem_layout.addWidget(problem_label)
        problem_layout.addWidget(self.problemInput)
        device_layout.addLayout(problem_layout)

        device_group.setLayout(device_layout)
        self.mainLayout.addWidget(device_group)

    def create_order_section(self):
        """Создает секцию информации о заказе"""
        order_group = QtWidgets.QGroupBox("ИНФОРМАЦИЯ О ЗАКАЗЕ")
        order_layout = QtWidgets.QGridLayout()
        order_layout.setHorizontalSpacing(15)
        order_layout.setVerticalSpacing(10)

        # Тип заказа
        type_label = QtWidgets.QLabel("Тип заказа:")
        self.orderTypeCombo = QComboBox()
        order_layout.addWidget(type_label, 0, 0)
        order_layout.addWidget(self.orderTypeCombo, 0, 1)

        # Приоритет
        priority_label = QtWidgets.QLabel("Приоритет:")
        self.priorityCombo = QComboBox()
        order_layout.addWidget(priority_label, 0, 2)
        order_layout.addWidget(self.priorityCombo, 0, 3)

        # Менеджер
        manager_label = QtWidgets.QLabel("Менеджер:")
        self.managerCombo = QComboBox()
        order_layout.addWidget(manager_label, 1, 0)
        order_layout.addWidget(self.managerCombo, 1, 1)

        # Исполнитель
        executor_label = QtWidgets.QLabel("Исполнитель:")
        self.executorCombo = QComboBox()
        order_layout.addWidget(executor_label, 1, 2)
        order_layout.addWidget(self.executorCombo, 1, 3)

        # Срок выполнения
        deadline_label = QtWidgets.QLabel("Срок выполнения:")
        self.deadlineInput = QDateEdit()
        self.deadlineInput.setCalendarPopup(True)
        self.deadlineInput.setDisplayFormat("dd.MM.yyyy")
        self.deadlineInput.setDate(QtCore.QDate.currentDate().addDays(3))
        order_layout.addWidget(deadline_label, 2, 0)
        order_layout.addWidget(self.deadlineInput, 2, 1)

        # Предоплата
        prepayment_label = QtWidgets.QLabel("Предоплата (₽):")
        self.prepaymentInput = QtWidgets.QLineEdit()
        self.prepaymentInput.setText("0")
        order_layout.addWidget(prepayment_label, 2, 2)
        order_layout.addWidget(self.prepaymentInput, 2, 3)

        order_group.setLayout(order_layout)
        self.mainLayout.addWidget(order_group)

    def create_services_section(self):
        """Создает секцию для добавления услуг"""
        services_group = QtWidgets.QGroupBox("УСЛУГИ")
        services_layout = QtWidgets.QVBoxLayout()

        # Верхняя панель для добавления услуги
        add_service_layout = QtWidgets.QHBoxLayout()

        # Выбор услуги
        service_label = QtWidgets.QLabel("Услуга:")
        self.serviceCombo = QComboBox()
        self.serviceCombo.setMinimumWidth(350)

        # Количество
        qty_label = QtWidgets.QLabel("Кол-во:")
        self.serviceQtySpin = QSpinBox()
        self.serviceQtySpin.setMinimum(1)
        self.serviceQtySpin.setMaximum(999)
        self.serviceQtySpin.setValue(1)
        self.serviceQtySpin.setMaximumWidth(70)

        # Цена
        price_label = QtWidgets.QLabel("Цена (₽):")
        self.servicePriceInput = QtWidgets.QLineEdit()
        self.servicePriceInput.setMaximumWidth(100)

        # Кнопка добавления
        self.addServiceBtn = QtWidgets.QPushButton("➕ Добавить услугу")
        self.addServiceBtn.setStyleSheet("background-color: rgb(40, 167, 69);")
        self.addServiceBtn.clicked.connect(self.add_service_to_list)

        add_service_layout.addWidget(service_label)
        add_service_layout.addWidget(self.serviceCombo)
        add_service_layout.addWidget(qty_label)
        add_service_layout.addWidget(self.serviceQtySpin)
        add_service_layout.addWidget(price_label)
        add_service_layout.addWidget(self.servicePriceInput)
        add_service_layout.addWidget(self.addServiceBtn)
        add_service_layout.addStretch()

        services_layout.addLayout(add_service_layout)

        # Таблица добавленных услуг
        self.servicesTable = QtWidgets.QTableWidget()
        self.servicesTable.setColumnCount(6)
        self.servicesTable.setHorizontalHeaderLabels(["Услуга", "Кол-во", "Цена", "Сумма", "Гарантия", "Действия"])
        self.servicesTable.setMinimumHeight(150)
        self.servicesTable.horizontalHeader().setStretchLastSection(False)
        self.servicesTable.setColumnWidth(0, 300)  # Услуга
        self.servicesTable.setColumnWidth(1, 80)  # Кол-во
        self.servicesTable.setColumnWidth(2, 100)  # Цена
        self.servicesTable.setColumnWidth(3, 100)  # Сумма
        self.servicesTable.setColumnWidth(4, 100)  # Гарантия
        self.servicesTable.setColumnWidth(5, 100)  # Действия
        services_layout.addWidget(self.servicesTable)

        services_group.setLayout(services_layout)
        self.mainLayout.addWidget(services_group)

    def create_parts_section(self):
        """Создает секцию для добавления запчастей"""
        parts_group = QtWidgets.QGroupBox("ЗАПЧАСТИ")
        parts_layout = QtWidgets.QVBoxLayout()

        # Верхняя панель для добавления запчасти
        add_part_layout = QtWidgets.QHBoxLayout()

        # Выбор запчасти
        part_label = QtWidgets.QLabel("Запчасть:")
        self.partCombo = QComboBox()
        self.partCombo.setMinimumWidth(350)

        # Количество
        part_qty_label = QtWidgets.QLabel("Кол-во:")
        self.partQtySpin = QSpinBox()
        self.partQtySpin.setMinimum(1)
        self.partQtySpin.setMaximum(999)
        self.partQtySpin.setValue(1)
        self.partQtySpin.setMaximumWidth(70)

        # Цена
        part_price_label = QtWidgets.QLabel("Цена (₽):")
        self.partPriceInput = QtWidgets.QLineEdit()
        self.partPriceInput.setMaximumWidth(100)

        # Гарантия (дни)
        warranty_label = QtWidgets.QLabel("Гарантия (дней):")
        self.partWarrantyInput = QtWidgets.QLineEdit()
        self.partWarrantyInput.setText("90")
        self.partWarrantyInput.setMaximumWidth(80)

        # Кнопка добавления
        self.addPartBtn = QtWidgets.QPushButton("➕ Добавить запчасть")
        self.addPartBtn.setStyleSheet("background-color: rgb(40, 167, 69);")
        self.addPartBtn.clicked.connect(self.add_part_to_list)

        add_part_layout.addWidget(part_label)
        add_part_layout.addWidget(self.partCombo)
        add_part_layout.addWidget(part_qty_label)
        add_part_layout.addWidget(self.partQtySpin)
        add_part_layout.addWidget(part_price_label)
        add_part_layout.addWidget(self.partPriceInput)
        add_part_layout.addWidget(warranty_label)
        add_part_layout.addWidget(self.partWarrantyInput)
        add_part_layout.addWidget(self.addPartBtn)
        add_part_layout.addStretch()

        parts_layout.addLayout(add_part_layout)

        # Таблица добавленных запчастей
        self.partsTable = QtWidgets.QTableWidget()
        self.partsTable.setColumnCount(6)
        self.partsTable.setHorizontalHeaderLabels(["Запчасть", "Кол-во", "Цена", "Сумма", "Гарантия", "Действия"])
        self.partsTable.setMinimumHeight(150)
        self.partsTable.horizontalHeader().setStretchLastSection(False)
        self.partsTable.setColumnWidth(0, 300)  # Запчасть
        self.partsTable.setColumnWidth(1, 80)  # Кол-во
        self.partsTable.setColumnWidth(2, 100)  # Цена
        self.partsTable.setColumnWidth(3, 100)  # Сумма
        self.partsTable.setColumnWidth(4, 100)  # Гарантия
        self.partsTable.setColumnWidth(5, 100)  # Действия
        parts_layout.addWidget(self.partsTable)

        parts_group.setLayout(parts_layout)
        self.mainLayout.addWidget(parts_group)

    def create_total_section(self):
        """Создает секцию с итоговой суммой"""
        total_group = QtWidgets.QGroupBox("ИТОГО")
        total_layout = QtWidgets.QVBoxLayout()

        # Основная информация
        info_layout = QtWidgets.QHBoxLayout()

        # Количество услуг и запчастей
        self.servicesCountLabel = QtWidgets.QLabel("Услуг: 0")
        self.servicesCountLabel.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px;")

        self.partsCountLabel = QtWidgets.QLabel("Запчастей: 0")
        self.partsCountLabel.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px;")

        info_layout.addWidget(self.servicesCountLabel)
        info_layout.addWidget(self.partsCountLabel)
        info_layout.addStretch()

        total_layout.addLayout(info_layout)

        # Суммы
        sums_layout = QtWidgets.QHBoxLayout()

        self.servicesTotalLabel = QtWidgets.QLabel("Сумма услуг: 0.00 ₽")
        self.servicesTotalLabel.setStyleSheet("color: rgb(103, 155, 118); font-size: 14px;")

        self.partsTotalLabel = QtWidgets.QLabel("Сумма запчастей: 0.00 ₽")
        self.partsTotalLabel.setStyleSheet("color: rgb(103, 155, 118); font-size: 14px;")

        self.totalAmountLabel = QtWidgets.QLabel("ИТОГО: 0.00 ₽")
        self.totalAmountLabel.setStyleSheet("color: rgb(40, 167, 69); font-size: 16px; font-weight: bold;")

        sums_layout.addWidget(self.servicesTotalLabel)
        sums_layout.addWidget(self.partsTotalLabel)
        sums_layout.addStretch()
        sums_layout.addWidget(self.totalAmountLabel)

        total_layout.addLayout(sums_layout)

        total_group.setLayout(total_layout)
        self.mainLayout.addWidget(total_group)

    def create_action_buttons(self):
        """Создает кнопки действий"""
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Кнопка создания заказа
        self.createBtn = QtWidgets.QPushButton("✅ Создать заказ")
        self.createBtn.setStyleSheet("""
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
        self.createBtn.clicked.connect(self.create_order)

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

        # Кнопка очистки
        self.clearBtn = QtWidgets.QPushButton("🗑 Очистить форму")
        self.clearBtn.setStyleSheet("""
            QPushButton {
                background-color: rgb(220, 53, 69);
                color: white;
                font-size: 14px;
                padding: 12px 25px;
                border-radius: 5px;
            }
        """)
        self.clearBtn.clicked.connect(self.clear_form)

        buttons_layout.addWidget(self.createBtn)
        buttons_layout.addWidget(self.cancelBtn)
        buttons_layout.addWidget(self.clearBtn)
        buttons_layout.addStretch()

        self.mainLayout.addLayout(buttons_layout)

    def load_combobox_data(self):
        """Загружает данные в комбобоксы"""
        try:
            # Причины обращения
            reasons = db_crm.get_all_appeal_reasons()
            self.reasonCombo.clear()
            self.reasonCombo.addItem("Выберите причину", 0)
            for reason in reasons:
                self.reasonCombo.addItem(reason['ReasonName'], reason['ReasonID'])

            # Тип устройства
            self.deviceTypeCombo.clear()
            self.deviceTypeCombo.addItem("Выберите тип устройства", 0)
            self.deviceTypeCombo.addItems([
                "Смартфон", "Ноутбук", "Планшет", "Телевизор",
                "Игровая приставка", "Фотоаппарат", "Пылесос",
                "Кофемашина", "Другое"
            ])

            # Тип заказа
            self.orderTypeCombo.clear()
            self.orderTypeCombo.addItems(["Платный", "Гарантийный"])

            # Приоритет
            self.priorityCombo.clear()
            self.priorityCombo.addItems(["Низкий", "Средний", "Высокий", "Критичный"])

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

            # Загружаем услуги и запчасти
            self.load_services()
            self.load_parts()

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка загрузки данных: {e}")

    def load_services(self):
        """Загружает услуги в комбобокс"""
        try:
            services = db_crm.get_all_service_types()
            self.serviceCombo.clear()
            self.serviceCombo.addItem("Выберите услугу", 0)

            for service in services:
                service_text = f"{service['ServiceDescription']} - {service['BasePrice']:.2f} ₽"
                self.serviceCombo.addItem(service_text, service['ServiceTypeID'])

        except Exception as e:
            print(f"Ошибка загрузки услуг: {e}")

    def load_parts(self):
        """Загружает запчасти в комбобокс"""
        try:
            parts = db_crm.get_all_stock_items()
            self.partCombo.clear()
            self.partCombo.addItem("Выберите запчасть", 0)

            for part in parts:
                part_text = f"{part['DetailName']} ({part['CountInStock']} шт.) - {part['Price']:.2f} ₽"
                self.partCombo.addItem(part_text, part['StockID'])

        except Exception as e:
            print(f"Ошибка загрузки запчастей: {e}")

    def search_client(self):
        """Открывает диалог поиска клиента"""
        dialog = QtWidgets.QDialog(self.dialog)
        dialog.setWindowTitle("Поиск клиента")
        dialog.resize(700, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: rgb(23, 23, 23);
                color: rgb(255, 255, 255);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QLineEdit {
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
            }
            QPushButton:hover {
                background-color: rgb(80, 80, 80);
            }
            QTableWidget {
                background-color: rgb(40, 40, 40);
                color: rgb(255, 255, 255);
                gridline-color: rgb(80, 80, 80);
            }
            QHeaderView::section {
                background-color: rgb(103, 155, 118);
                color: white;
                padding: 5px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Поле поиска
        search_layout = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel("Поиск (ФИО/телефон/email):")
        search_input = QtWidgets.QLineEdit()
        search_input.setPlaceholderText("Введите текст для поиска...")
        search_btn = QtWidgets.QPushButton("🔍 Искать")
        search_btn.setStyleSheet("background-color: rgb(103, 155, 118);")

        show_all_btn = QtWidgets.QPushButton("Показать всех")
        show_all_btn.setStyleSheet("background-color: rgb(28, 113, 216);")

        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(show_all_btn)
        layout.addLayout(search_layout)

        # Таблица результатов
        results_table = QtWidgets.QTableWidget()
        results_table.setColumnCount(6)
        results_table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Email", "Дата рождения", "Дата регистрации"])
        results_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        results_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        layout.addWidget(results_table)

        # Кнопки
        buttons_layout = QtWidgets.QHBoxLayout()
        select_btn = QtWidgets.QPushButton("✅ Выбрать")
        select_btn.setStyleSheet("background-color: rgb(40, 167, 69);")
        cancel_btn = QtWidgets.QPushButton("❌ Отмена")
        cancel_btn.setStyleSheet("background-color: rgb(108, 117, 125);")

        buttons_layout.addWidget(select_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        def perform_search(search_text=""):
            """Выполняет поиск клиента"""
            try:
                if not search_text:
                    # Загружаем всех клиентов
                    connection = db_crm.get_crm_connection()
                    if connection:
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute("""
                            SELECT ID, FirstName, LastName, PhoneNumber, Email, 
                                   Birthdate, RegistrationDate
                            FROM Client 
                            ORDER BY RegistrationDate DESC 
                            LIMIT 50
                        """)
                        results = cursor.fetchall()
                        cursor.close()
                        connection.close()
                    else:
                        results = []
                else:
                    # Ищем клиентов
                    results = db_crm.search_clients(search_text)

                results_table.setRowCount(len(results))

                for row, client in enumerate(results):
                    # ID клиента
                    results_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(client.get('ID', ''))))
                    # ФИО
                    full_name = f"{client.get('FirstName', '')} {client.get('LastName', '')}"
                    results_table.setItem(row, 1, QtWidgets.QTableWidgetItem(full_name.strip()))
                    # Телефон
                    results_table.setItem(row, 2, QtWidgets.QTableWidgetItem(client.get('PhoneNumber', '')))
                    # Email
                    results_table.setItem(row, 3, QtWidgets.QTableWidgetItem(client.get('Email', '')))
                    # Дата рождения
                    birthdate = client.get('Birthdate')
                    results_table.setItem(row, 4, QtWidgets.QTableWidgetItem(
                        str(birthdate) if birthdate else ''))
                    # Дата регистрации
                    reg_date = client.get('RegistrationDate')
                    results_table.setItem(row, 5, QtWidgets.QTableWidgetItem(
                        str(reg_date)[:10] if reg_date else ''))

                results_table.resizeColumnsToContents()
                results_table.setColumnHidden(0, True)  # Скрываем ID

            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка поиска: {e}")

        def on_search():
            """Обработчик нажатия кнопки поиска"""
            search_text = search_input.text().strip()
            perform_search(search_text)

        def on_show_all():
            """Обработчик кнопки показа всех"""
            search_input.clear()
            perform_search()

        def select_client():
            """Выбирает клиента из таблицы"""
            current_row = results_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(dialog, "Ошибка", "Выберите клиента из списка")
                return

            try:
                # Получаем ID клиента
                client_id_item = results_table.item(current_row, 0)
                if not client_id_item:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось получить ID клиента")
                    return

                client_id = int(client_id_item.text())

                # Получаем данные клиента
                full_name_item = results_table.item(current_row, 1)
                phone_item = results_table.item(current_row, 2)
                email_item = results_table.item(current_row, 3)
                birthdate_item = results_table.item(current_row, 4)

                if full_name_item:
                    full_name = full_name_item.text().strip()
                    name_parts = full_name.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else ""
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                else:
                    first_name = ""
                    last_name = ""

                phone = phone_item.text() if phone_item else ""
                email = email_item.text() if email_item else ""

                # Заполняем поля формы
                self.firstNameInput.setText(first_name)
                self.lastNameInput.setText(last_name)
                self.phoneInput.setText(phone)
                self.emailInput.setText(email)

                # Устанавливаем дату рождения, если есть
                if birthdate_item and birthdate_item.text().strip():
                    try:
                        birthdate_str = birthdate_item.text().strip()
                        if birthdate_str:
                            birthdate = QtCore.QDate.fromString(birthdate_str, "yyyy-MM-dd")
                            if birthdate.isValid():
                                self.birthdateInput.setDate(birthdate)
                    except:
                        pass

                # Сохраняем ID клиента
                self.client_id = client_id

                dialog.accept()

            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка выбора клиента: {e}")

        def on_double_click(row, column):
            """Обработчик двойного клика по строке таблицы"""
            select_client()

        # Подключаем обработчики
        search_btn.clicked.connect(on_search)
        show_all_btn.clicked.connect(on_show_all)
        search_input.returnPressed.connect(on_search)
        select_btn.clicked.connect(select_client)
        cancel_btn.clicked.connect(dialog.reject)
        results_table.doubleClicked.connect(on_double_click)

        # Загружаем всех клиентов при открытии
        perform_search()

        dialog.exec_()

    def add_service_to_list(self):
        """Добавляет услугу в таблицу"""
        try:
            service_id = self.serviceCombo.currentData()
            if service_id == 0:
                QMessageBox.warning(self.dialog, "Ошибка", "Выберите услугу")
                return

            service_text = self.serviceCombo.currentText()
            qty = self.serviceQtySpin.value()
            price_text = self.servicePriceInput.text().strip()

            # Если цена не указана, берем из названия услуги
            if not price_text:
                # Пытаемся извлечь цену из текста услуги
                price_match = re.search(r'(\d+\.?\d*) ₽', service_text)
                if price_match:
                    price = float(price_match.group(1))
                else:
                    price = 0.0
                    QMessageBox.warning(self.dialog, "Внимание", "Цена услуги не указана. Установлена 0.00 ₽")
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

            # Услуга
            service_item = QtWidgets.QTableWidgetItem(service_text.split(' - ')[0])
            service_item.setData(QtCore.Qt.UserRole, {
                'service_id': service_id,
                'service_name': service_text.split(' - ')[0],
                'quantity': qty,
                'price': price,
                'total': total
            })
            self.servicesTable.setItem(row, 0, service_item)

            # Количество
            qty_item = QtWidgets.QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.servicesTable.setItem(row, 1, qty_item)

            # Цена
            price_item = QtWidgets.QTableWidgetItem(f"{price:.2f}")
            price_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.servicesTable.setItem(row, 2, price_item)

            # Сумма
            total_item = QtWidgets.QTableWidgetItem(f"{total:.2f}")
            total_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.servicesTable.setItem(row, 3, total_item)

            # Гарантия (для услуг обычно нет)
            warranty_item = QtWidgets.QTableWidgetItem("-")
            warranty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.servicesTable.setItem(row, 4, warranty_item)

            # Кнопка удаления
            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgb(220, 53, 69);
                    color: white;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: rgb(230, 63, 79);
                }
            """)
            delete_btn.clicked.connect(lambda: self.remove_service_row(row))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.servicesTable.setCellWidget(row, 5, cell_widget)

            # Обновляем итоги
            self.update_totals()

            # Очищаем поля
            self.serviceQtySpin.setValue(1)
            self.servicePriceInput.clear()

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления услуги: {e}")

    def add_part_to_list(self):
        """Добавляет запчасть в таблицу"""
        try:
            part_id = self.partCombo.currentData()
            if part_id == 0:
                QMessageBox.warning(self.dialog, "Ошибка", "Выберите запчасть")
                return

            part_text = self.partCombo.currentText()
            qty = self.partQtySpin.value()
            price_text = self.partPriceInput.text().strip()
            warranty_text = self.partWarrantyInput.text().strip()

            # Проверяем наличие на складе
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
                # Пытаемся извлечь цену из текста запчасти
                price_match = re.search(r'(\d+\.?\d*) ₽', part_text)
                if price_match:
                    price = float(price_match.group(1))
                else:
                    price = 0.0
                    QMessageBox.warning(self.dialog, "Внимание", "Цена запчасти не указана. Установлена 0.00 ₽")
            else:
                try:
                    price = float(price_text)
                except ValueError:
                    QMessageBox.warning(self.dialog, "Ошибка", "Введите корректную цену")
                    return

            # Гарантия
            warranty_days = 90  # значение по умолчанию
            if warranty_text:
                try:
                    warranty_days = int(warranty_text)
                except ValueError:
                    warranty_days = 90

            total = qty * price

            # Добавляем строку в таблицу
            row = self.partsTable.rowCount()
            self.partsTable.insertRow(row)

            # Запчасть
            part_item = QtWidgets.QTableWidgetItem(part_text.split(' (')[0])  # Убираем количество из названия
            part_item.setData(QtCore.Qt.UserRole, {
                'part_id': part_id,
                'part_name': part_text.split(' (')[0],
                'quantity': qty,
                'price': price,
                'total': total,
                'warranty_days': warranty_days,
                'stock_qty': stock_qty
            })
            self.partsTable.setItem(row, 0, part_item)

            # Количество
            qty_item = QtWidgets.QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.partsTable.setItem(row, 1, qty_item)

            # Цена
            price_item = QtWidgets.QTableWidgetItem(f"{price:.2f}")
            price_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.partsTable.setItem(row, 2, price_item)

            # Сумма
            total_item = QtWidgets.QTableWidgetItem(f"{total:.2f}")
            total_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.partsTable.setItem(row, 3, total_item)

            # Гарантия
            warranty_item = QtWidgets.QTableWidgetItem(f"{warranty_days} дней")
            warranty_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.partsTable.setItem(row, 4, warranty_item)

            # Кнопка удаления
            delete_btn = QtWidgets.QPushButton("🗑 Удалить")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgb(220, 53, 69);
                    color: white;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: rgb(230, 63, 79);
                }
            """)
            delete_btn.clicked.connect(lambda: self.remove_part_row(row))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(QtCore.Qt.AlignCenter)

            self.partsTable.setCellWidget(row, 5, cell_widget)

            # Обновляем итоги
            self.update_totals()

            # Очищаем поля
            self.partQtySpin.setValue(1)
            self.partPriceInput.clear()
            self.partWarrantyInput.setText("90")

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка добавления запчасти: {e}")

    def remove_service_row(self, row):
        """Удаляет услугу из таблицы"""
        try:
            self.servicesTable.removeRow(row)
            # Обновляем индексы для оставшихся кнопок удаления
            for i in range(self.servicesTable.rowCount()):
                widget = self.servicesTable.cellWidget(i, 5)
                if widget:
                    btn = widget.findChild(QtWidgets.QPushButton)
                    if btn:
                        try:
                            btn.clicked.disconnect()
                        except:
                            pass
                        btn.clicked.connect(lambda checked, r=i: self.remove_service_row(r))
            self.update_totals()
        except Exception as e:
            print(f"Ошибка удаления строки услуги: {e}")

    def remove_part_row(self, row):
        """Удаляет запчасть из таблицы"""
        try:
            self.partsTable.removeRow(row)
            # Обновляем индексы для оставшихся кнопок удаления
            for i in range(self.partsTable.rowCount()):
                widget = self.partsTable.cellWidget(i, 5)
                if widget:
                    btn = widget.findChild(QtWidgets.QPushButton)
                    if btn:
                        try:
                            btn.clicked.disconnect()
                        except:
                            pass
                        btn.clicked.connect(lambda checked, r=i: self.remove_part_row(r))
            self.update_totals()
        except Exception as e:
            print(f"Ошибка удаления строки запчасти: {e}")

    def update_totals(self):
        """Обновляет итоговые суммы"""
        try:
            services_total = 0.0
            services_count = 0

            for row in range(self.servicesTable.rowCount()):
                total_item = self.servicesTable.item(row, 3)
                if total_item:
                    try:
                        services_total += float(total_item.text())
                        services_count += 1
                    except ValueError:
                        pass

            parts_total = 0.0
            parts_count = 0

            for row in range(self.partsTable.rowCount()):
                total_item = self.partsTable.item(row, 3)
                if total_item:
                    try:
                        parts_total += float(total_item.text())
                        parts_count += 1
                    except ValueError:
                        pass

            total = services_total + parts_total

            self.servicesCountLabel.setText(f"Услуг: {services_count}")
            self.partsCountLabel.setText(f"Запчастей: {parts_count}")
            self.servicesTotalLabel.setText(f"Сумма услуг: {services_total:.2f} ₽")
            self.partsTotalLabel.setText(f"Сумма запчастей: {parts_total:.2f} ₽")
            self.totalAmountLabel.setText(f"ИТОГО: {total:.2f} ₽")

        except Exception as e:
            print(f"Ошибка обновления итогов: {e}")

    def clear_form(self):
        """Очищает форму"""
        try:
            # Клиент
            self.firstNameInput.clear()
            self.lastNameInput.clear()
            self.phoneInput.clear()
            self.emailInput.clear()
            self.birthdateInput.setDate(QtCore.QDate(1990, 1, 1))
            self.client_id = None

            # Устройство
            self.deviceTypeCombo.setCurrentIndex(0)
            self.brandInput.clear()
            self.modelInput.clear()
            self.imeiInput.clear()
            self.appearanceInput.clear()
            self.completenessInput.clear()
            self.reasonCombo.setCurrentIndex(0)
            self.problemInput.clear()

            # Заказ
            self.orderTypeCombo.setCurrentIndex(0)
            self.priorityCombo.setCurrentIndex(1)  # Средний
            self.managerCombo.setCurrentIndex(0)
            self.executorCombo.setCurrentIndex(0)
            self.deadlineInput.setDate(QtCore.QDate.currentDate().addDays(3))
            self.prepaymentInput.setText("0")

            # Услуги и запчасти
            self.servicesTable.setRowCount(0)
            self.partsTable.setRowCount(0)
            self.serviceCombo.setCurrentIndex(0)
            self.serviceQtySpin.setValue(1)
            self.servicePriceInput.clear()
            self.partCombo.setCurrentIndex(0)
            self.partQtySpin.setValue(1)
            self.partPriceInput.clear()
            self.partWarrantyInput.setText("90")

            # Итоги
            self.update_totals()

            QMessageBox.information(self.dialog, "Успех", "Форма очищена")

        except Exception as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка очистки формы: {e}")

    def validate_form(self):
        """Проверяет корректность заполнения формы"""
        errors = []

        # Проверка клиента
        if not self.firstNameInput.text().strip():
            errors.append("Введите имя клиента")
        if not self.lastNameInput.text().strip():
            errors.append("Введите фамилию клиента")
        if not self.phoneInput.text().strip():
            errors.append("Введите телефон клиента")

        # Проверка устройства
        if self.deviceTypeCombo.currentData() == 0:
            errors.append("Выберите тип устройства")
        if not self.brandInput.text().strip():
            errors.append("Введите бренд устройства")
        if not self.modelInput.text().strip():
            errors.append("Введите модель устройства")

        # Проверка проблемы
        if not self.problemInput.toPlainText().strip():
            errors.append("Опишите проблему")

        # Проверка причины обращения
        if self.reasonCombo.currentData() == 0:
            errors.append("Выберите причину обращения")

        if errors:
            QMessageBox.warning(self.dialog, "Ошибки в форме", "\n".join(errors))
            return False

        return True

    def create_order(self):
        """Создает новый заказ"""
        if not self.validate_form():
            return

        try:
            # Проверяем существование клиента перед созданием
            email = self.emailInput.text().strip()
            phone = self.phoneInput.text().strip()
            first_name = self.firstNameInput.text().strip()
            last_name = self.lastNameInput.text().strip()

            client_id = None

            # Если клиент уже выбран через поиск, используем его ID
            if self.client_id:
                client_id = self.client_id
            else:
                # Проверяем существование клиента по email или телефону
                connection = db_crm.get_crm_connection()
                if connection:
                    cursor = connection.cursor(dictionary=True)

                    if email:
                        cursor.execute("SELECT ID FROM Client WHERE Email = %s", (email,))
                        result = cursor.fetchone()
                        if result:
                            client_id = result['ID']

                    # Если не нашли по email, проверяем по телефону
                    if not client_id and phone:
                        cursor.execute("SELECT ID FROM Client WHERE PhoneNumber = %s", (phone,))
                        result = cursor.fetchone()
                        if result:
                            client_id = result['ID']

                    cursor.close()
                    connection.close()

            # Если клиент не найден, создаем нового
            if not client_id:
                # 1. Создаем клиента
                client_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': phone,
                    'email': email,
                    'birthdate': self.birthdateInput.date().toString("yyyy-MM-dd")
                }

                client_id = db_crm.create_new_client(client_data)
                if not client_id:
                    QMessageBox.critical(self.dialog, "Ошибка", "Не удалось создать клиента")
                    return
            else:
                # Если клиент уже существует, обновляем его данные
                connection = db_crm.get_crm_connection()
                if connection:
                    cursor = connection.cursor()
                    try:
                        cursor.execute("""
                            UPDATE Client SET 
                                FirstName = %s,
                                LastName = %s,
                                PhoneNumber = %s,
                                Birthdate = %s
                            WHERE ID = %s
                        """, (
                            first_name,
                            last_name,
                            phone,
                            self.birthdateInput.date().toString("yyyy-MM-dd"),
                            client_id
                        ))
                        connection.commit()
                    except Exception as e:
                        print(f"Ошибка обновления клиента: {e}")
                    finally:
                        cursor.close()
                        connection.close()

            # 2. Подготавливаем данные заказа
            deadline_date = self.deadlineInput.date()
            estimated_completion = deadline_date.toString("yyyy-MM-dd") + " 18:00:00"

            # Собираем услуги
            services_list = []
            for row in range(self.servicesTable.rowCount()):
                service_item = self.servicesTable.item(row, 0)
                qty_item = self.servicesTable.item(row, 1)
                price_item = self.servicesTable.item(row, 2)

                if service_item and qty_item and price_item:
                    service_data = service_item.data(QtCore.Qt.UserRole)
                    if service_data:
                        services_list.append({
                            'service_type_id': service_data['service_id'],
                            'quantity': int(qty_item.text()),
                            'unit_price': float(price_item.text())
                        })

            # Собираем запчасти
            parts_list = []
            for row in range(self.partsTable.rowCount()):
                part_item = self.partsTable.item(row, 0)
                qty_item = self.partsTable.item(row, 1)
                price_item = self.partsTable.item(row, 2)
                warranty_item = self.partsTable.item(row, 4)

                if part_item and qty_item and price_item:
                    part_data = part_item.data(QtCore.Qt.UserRole)
                    if part_data:
                        warranty_days = 90  # по умолчанию
                        if warranty_item:
                            warranty_text = warranty_item.text()
                            warranty_match = re.search(r'(\d+)', warranty_text)
                            if warranty_match:
                                warranty_days = int(warranty_match.group(1))

                        parts_list.append({
                            'stock_id': part_data['part_id'],
                            'quantity': int(qty_item.text()),
                            'unit_price': float(price_item.text()),
                            'warranty_days': warranty_days
                        })

            # Рассчитываем итоговые суммы
            services_total = sum(service['quantity'] * service['unit_price'] for service in services_list)
            parts_total = sum(part['quantity'] * part['unit_price'] for part in parts_list)
            total_amount = services_total + parts_total

            # Применяем скидку
            discount = 0.0
            final_amount = total_amount * (1 - discount / 100)

            order_data = {
                'status': 'Новая',
                'order_type': self.orderTypeCombo.currentText(),
                'priority': self.priorityCombo.currentText(),
                'device_type': self.deviceTypeCombo.currentText(),
                'device_brand': self.brandInput.text().strip(),
                'device_model': self.modelInput.text().strip(),
                'device_imei': self.imeiInput.text().strip(),
                'device_appearance': self.appearanceInput.toPlainText(),
                'problem_description': self.problemInput.toPlainText(),
                'client_id': client_id,
                'manager_id': self.managerCombo.currentData() if self.managerCombo.currentData() > 0 else None,
                'executor_id': self.executorCombo.currentData() if self.executorCombo.currentData() > 0 else None,
                'appeal_reason_id': self.reasonCombo.currentData() if self.reasonCombo.currentData() > 0 else None,
                'prepayment': float(self.prepaymentInput.text() or 0),
                'discount': discount,
                'total_amount': total_amount,
                'final_amount': final_amount,
                'estimated_completion': estimated_completion,
                'notes': self.completenessInput.toPlainText(),
                'created_by': 1,  # ID текущего пользователя
                'services_list': services_list,
                'parts_list': parts_list
            }

            # 3. Создаем заказ в БД
            new_order_id = db_crm.create_new_order_with_services_parts(order_data)

            if new_order_id:
                QMessageBox.information(self.dialog, "Успех",
                                        f"Заказ успешно создан!\n\n"
                                        f"Номер заказа: {new_order_id}\n"
                                        f"Клиент: {first_name} {last_name}\n"
                                        f"Устройство: {order_data['device_brand']} {order_data['device_model']}\n"
                                        f"Сумма заказа: {final_amount:.2f} ₽\n"
                                        f"Услуг: {len(services_list)}, Запчастей: {len(parts_list)}")

                # Закрываем диалог с успехом
                self.dialog.accept()
            else:
                QMessageBox.critical(self.dialog, "Ошибка", "Не удалось создать заказ")

        except ValueError as e:
            QMessageBox.critical(self.dialog, "Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            print(f"Ошибка создания заказа: {e}")
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка при создании заказа: {e}")

    def retranslateUi(self, AddOrderDialog):
        _translate = QtCore.QCoreApplication.translate
        AddOrderDialog.setWindowTitle(_translate("AddOrderDialog", "Добавление нового заказа"))


# Класс для удобного использования
class AddOrderDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AddOrderDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Добавление нового заказа")
        self.resize(1400, 900)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = AddOrderDialog()
    dialog.show()
    sys.exit(app.exec_())