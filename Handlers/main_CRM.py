# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from Server import db_crm


class Ui_main_window_CRM(object):
    def setupUi(self, main_window_CRM):
        main_window_CRM.setObjectName("main_window_CRM")
        main_window_CRM.resize(1270, 952)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Pictures/Screenshot from 2025-09-15 14-30-16.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        main_window_CRM.setWindowIcon(icon)
        main_window_CRM.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.horizontalLayout = QtWidgets.QHBoxLayout(main_window_CRM)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scrollArea = QtWidgets.QScrollArea(main_window_CRM)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1250, 932))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.PB_Trends = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Trends.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Trends.setStyleSheet("color: rgb(255, 255, 255);\n"
                                     "background-color: rgb(103, 155, 118);")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/bar_chart_4_bars_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Trends.setIcon(icon1)
        self.PB_Trends.setObjectName("PB_Trends")
        self.verticalLayout.addWidget(self.PB_Trends)
        spacerItem = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.PB_Objectives = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Objectives.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Objectives.setStyleSheet("color: rgb(255, 255, 255);\n"
                                         "background-color: rgb(103, 155, 118);")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/check_circle_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Objectives.setIcon(icon2)
        self.PB_Objectives.setObjectName("PB_Objectives")
        self.verticalLayout.addWidget(self.PB_Objectives)
        spacerItem1 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.PB_Orders = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Orders.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Orders.setStyleSheet("color: rgb(255, 255, 255);\n"
                                     "background-color: rgb(103, 155, 118);")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/orders_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Orders.setIcon(icon3)
        self.PB_Orders.setObjectName("PB_Orders")
        self.verticalLayout.addWidget(self.PB_Orders)
        spacerItem2 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem2)
        self.PB_Pay = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Pay.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Pay.setStyleSheet("color: rgb(255, 255, 255);\n"
                                  "background-color: rgb(103, 155, 118);")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(
            "IT-EcoSystem/Client/Icons_PNG/account_balance_wallet_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Pay.setIcon(icon4)
        self.PB_Pay.setObjectName("PB_Pay")
        self.verticalLayout.addWidget(self.PB_Pay)
        spacerItem3 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem3)
        self.PB_Customers = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Customers.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Customers.setStyleSheet("color: rgb(255, 255, 255);\n"
                                        "background-color: rgb(103, 155, 118);")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/identity_platform_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Customers.setIcon(icon5)
        self.PB_Customers.setObjectName("PB_Customers")
        self.verticalLayout.addWidget(self.PB_Customers)
        spacerItem4 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem4)
        self.PB_Warehouses = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Warehouses.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Warehouses.setStyleSheet("color: rgb(255, 255, 255);\n"
                                         "background-color: rgb(103, 155, 118);")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/inventory_2_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Warehouses.setIcon(icon6)
        self.PB_Warehouses.setObjectName("PB_Warehouses")
        self.verticalLayout.addWidget(self.PB_Warehouses)
        spacerItem5 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem5)
        self.PB_Shops = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Shops.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Shops.setStyleSheet("color: rgb(255, 255, 255);\n"
                                    "background-color: rgb(103, 155, 118);")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/shopping_cart_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Shops.setIcon(icon7)
        self.PB_Shops.setObjectName("PB_Shops")
        self.verticalLayout.addWidget(self.PB_Shops)
        spacerItem6 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem6)
        self.PB_Reports = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Reports.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Reports.setStyleSheet("color: rgb(255, 255, 255);\n"
                                      "background-color: rgb(103, 155, 118);")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/monitoring_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Reports.setIcon(icon8)
        self.PB_Reports.setObjectName("PB_Reports")
        self.verticalLayout.addWidget(self.PB_Reports)
        spacerItem7 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem7)
        self.PB_Customization = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Customization.setMaximumSize(QtCore.QSize(200, 16777215))
        self.PB_Customization.setStyleSheet("color: rgb(255, 255, 255);\n"
                                            "background-color: rgb(103, 155, 118);")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/settings_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Customization.setIcon(icon9)
        self.PB_Customization.setObjectName("PB_Customization")
        self.verticalLayout.addWidget(self.PB_Customization)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem8)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.LBTEXT_Ordes = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.LBTEXT_Ordes.setStyleSheet("color: rgb(255, 255, 255);")
        self.LBTEXT_Ordes.setObjectName("LBTEXT_Ordes")
        self.horizontalLayout_3.addWidget(self.LBTEXT_Ordes)
        self.PB_Paid = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Paid.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_Paid.setObjectName("PB_Paid")
        self.horizontalLayout_3.addWidget(self.PB_Paid)
        self.PB_TWC = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_TWC.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_TWC.setObjectName("PB_TWC")
        self.horizontalLayout_3.addWidget(self.PB_TWC)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem9)
        self.PB_Notification = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(
            QtGui.QPixmap("../IT-EcoSystem/Client/Icons_PNG/notifications_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Notification.setIcon(icon10)
        self.PB_Notification.setObjectName("PB_Notification")
        self.horizontalLayout_3.addWidget(self.PB_Notification)
        self.PB_Profile = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Profile.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_Profile.setObjectName("PB_Profile")
        self.horizontalLayout_3.addWidget(self.PB_Profile)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.PB_All = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_All.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_All.setObjectName("PB_All")
        self.horizontalLayout_2.addWidget(self.PB_All)
        self.PB_CloUns = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_CloUns.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_CloUns.setObjectName("PB_CloUns")
        self.horizontalLayout_2.addWidget(self.PB_CloUns)
        self.PB_Work = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Work.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_Work.setObjectName("PB_Work")
        self.horizontalLayout_2.addWidget(self.PB_Work)
        self.PB_New = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_New.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_New.setObjectName("PB_New")
        self.horizontalLayout_2.addWidget(self.PB_New)
        self.PB_Active = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Active.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_Active.setObjectName("PB_Active")
        self.horizontalLayout_2.addWidget(self.PB_Active)
        self.PB_Urgent = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Urgent.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_Urgent.setObjectName("PB_Urgent")
        self.horizontalLayout_2.addWidget(self.PB_Urgent)
        self.PB_WFSP = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_WFSP.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_WFSP.setObjectName("PB_WFSP")
        self.horizontalLayout_2.addWidget(self.PB_WFSP)
        self.PB_Done = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Done.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_Done.setObjectName("PB_Done")
        self.horizontalLayout_2.addWidget(self.PB_Done)
        self.lineEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.lineEdit.setMaximumSize(QtCore.QSize(120, 16777215))
        self.lineEdit.setStyleSheet("color: rgb(255, 255, 255);")
        self.lineEdit.setInputMask("")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.PB_Filter = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Filter.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_Filter.setObjectName("PB_Filter")
        self.horizontalLayout_2.addWidget(self.PB_Filter)
        self.PB_Stil = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Stil.setStyleSheet("color: rgb(255, 255, 255);")
        self.PB_Stil.setObjectName("PB_Stil")
        self.horizontalLayout_2.addWidget(self.PB_Stil)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        # Таблица CRM
        self.tableCRM = QtWidgets.QTableWidget(self.scrollAreaWidgetContents)
        self.tableCRM.setMinimumSize(QtCore.QSize(0, 0))
        self.tableCRM.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tableCRM.setStyleSheet("""
            QTableWidget {
                color: rgb(255, 255, 255);
                background-color: rgb(40, 40, 40);
                gridline-color: rgb(80, 80, 80);
                alternate-background-color: rgb(50, 50, 50);
                selection-background-color: rgb(103, 155, 118);
            }
            QHeaderView::section {
                background-color: rgb(103, 155, 118);
                color: rgb(255, 255, 255);
                padding: 5px;
                border: 1px solid rgb(80, 80, 80);
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        self.tableCRM.setAlternatingRowColors(True)
        self.tableCRM.setObjectName("tableCRM")

        # Устанавливаем количество столбцов
        self.tableCRM.setColumnCount(10)

        # Устанавливаем заголовки столбцов
        headers = [
            "Заказы", "Статус", "Клиент", "Менеджер", "Исполнитель",
            "Причины обращения", "Бренд", "Модель", "Тип устройства", "Внешний вид"
        ]
        for i, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(header)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tableCRM.setHorizontalHeaderItem(i, item)

        self.tableCRM.setRowCount(0)  # Начинаем с 0 строк
        self.tableCRM.horizontalHeader().setStretchLastSection(True)
        self.tableCRM.horizontalHeader().setDefaultSectionSize(120)

        self.verticalLayout_2.addWidget(self.tableCRM)
        self.PB_Add_Order = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.PB_Add_Order.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.PB_Add_Order.setStyleSheet("color: rgb(255, 255, 255);\n"
                                        "background-color: rgb(26, 95, 180);")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(
            QtGui.QPixmap("IT-EcoSystem/Client/Icons_PNG/add_2_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.PB_Add_Order.setIcon(icon11)
        self.PB_Add_Order.setObjectName("PB_Add_Order")
        self.verticalLayout_2.addWidget(self.PB_Add_Order)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)

        # Подключаем кнопки фильтров
        self.PB_All.clicked.connect(lambda: self.load_orders_data())
        self.PB_New.clicked.connect(lambda: self.load_orders_data("Новая"))
        self.PB_Active.clicked.connect(lambda: self.load_orders_data("Активная"))
        self.PB_Urgent.clicked.connect(lambda: self.load_orders_data("Срочное"))
        self.PB_WFSP.clicked.connect(lambda: self.load_orders_data("Ждут запчасти"))
        self.PB_Work.clicked.connect(lambda: self.load_orders_data("В работе"))
        self.PB_Done.clicked.connect(lambda: self.load_orders_data("Готовое"))
        self.PB_CloUns.clicked.connect(lambda: self.load_orders_data("Закрыто неуспешно"))
        self.PB_Filter.clicked.connect(self.apply_search_filter)
        self.lineEdit.returnPressed.connect(self.apply_search_filter)

        self.retranslateUi(main_window_CRM)
        QtCore.QMetaObject.connectSlotsByName(main_window_CRM)

        # Загружаем данные при открытии окна
        self.load_orders_data()

    def load_orders_data(self, status_filter=None):
        """Загружает данные заказов из базы данных в таблицу"""
        try:
            # Используем функцию из db_crm модуля
            orders = db_crm.get_orders_for_crm_table(filter_status=status_filter)

            # Обновляем таблицу
            self.update_table_with_data(orders)

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Ошибка при загрузке данных: {e}")

    def apply_search_filter(self):
        """Применяет поисковый фильтр"""
        search_text = self.lineEdit.text().strip()
        if not search_text:
            self.load_orders_data()
            return

        try:
            # Используем функцию поиска из db_crm
            orders = db_crm.get_orders_for_crm_table(search_text=search_text)

            self.update_table_with_data(orders)

        except Exception as e:
            print(f"Ошибка поиска: {e}")
            QtWidgets.QMessageBox.critical(None, "Ошибка", f"Ошибка при поиске: {e}")

    def update_table_with_data(self, orders):
        """Обновляет таблицу с полученными данными"""
        # Устанавливаем количество строк
        self.tableCRM.setRowCount(len(orders))

        # Заполняем таблицу данными
        for row, order in enumerate(orders):
            for col, field in enumerate([
                'Заказы', 'Статус', 'Клиент', 'Менеджер', 'Исполнитель',
                'Причины обращения', 'Бренд', 'Модель', 'Тип устройства', 'Внешний вид'
            ]):
                value = order.get(field, '')
                if value is None:
                    value = ''

                item = QtWidgets.QTableWidgetItem(str(value))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

                # Настраиваем выравнивание текста
                if col == 0:  # Заказы
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                elif col == 1:  # Статус
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    # Добавляем цветовое выделение для статусов
                    self.color_status_item(item, str(value))

                self.tableCRM.setItem(row, col, item)

        # Автонастройка ширины столбцов
        self.tableCRM.resizeColumnsToContents()

        # Показываем количество загруженных заказов
        self.LBTEXT_Ordes.setText(f"Заказы ({len(orders)}) /")

    def color_status_item(self, item, status):
        """Добавляет цветовое оформление для ячеек статуса"""
        colors = {
            'Новая': QtGui.QColor(66, 135, 245),  # Синий
            'Активная': QtGui.QColor(255, 193, 7),  # Желтый
            'Срочное': QtGui.QColor(220, 53, 69),  # Красный
            'В работе': QtGui.QColor(25, 135, 84),  # Зеленый
            'Ждут запчасти': QtGui.QColor(255, 149, 0),  # Оранжевый
            'Готовое': QtGui.QColor(40, 167, 69),  # Зеленый
            'Завершен': QtGui.QColor(108, 117, 125),  # Серый
            'Закрыто неуспешно': QtGui.QColor(108, 117, 125),  # Серый
        }

        if status in colors:
            item.setBackground(colors[status])
            item.setForeground(QtGui.QColor(255, 255, 255))  # Белый текст

    def retranslateUi(self, main_window_CRM):
        _translate = QtCore.QCoreApplication.translate
        main_window_CRM.setWindowTitle(_translate("main_window_CRM", "IT-EcoSystem - CRM"))
        self.PB_Trends.setText(_translate("main_window_CRM", "Тренды"))
        self.PB_Objectives.setText(_translate("main_window_CRM", "Задачи"))
        self.PB_Orders.setText(_translate("main_window_CRM", "Заказы"))
        self.PB_Pay.setText(_translate("main_window_CRM", "Платежи"))
        self.PB_Customers.setText(_translate("main_window_CRM", "Клиенты"))
        self.PB_Warehouses.setText(_translate("main_window_CRM", "Склад"))
        self.PB_Shops.setText(_translate("main_window_CRM", "Магазин"))
        self.PB_Reports.setText(_translate("main_window_CRM", "Отчеты"))
        self.PB_Customization.setText(_translate("main_window_CRM", "Настройка"))
        self.LBTEXT_Ordes.setText(_translate("main_window_CRM", "Заказы /"))
        self.PB_Paid.setText(_translate("main_window_CRM", "Платные"))
        self.PB_TWC.setText(_translate("main_window_CRM", "Гарантийные"))
        self.PB_Profile.setText(_translate("main_window_CRM", "Профиль"))
        self.PB_All.setText(_translate("main_window_CRM", "Все"))
        self.PB_CloUns.setText(_translate("main_window_CRM", "Закрыто неуспешно"))
        self.PB_Work.setText(_translate("main_window_CRM", "В работе"))
        self.PB_New.setText(_translate("main_window_CRM", "Новое"))
        self.PB_Active.setText(_translate("main_window_CRM", "Активное"))
        self.PB_Urgent.setText(_translate("main_window_CRM", "Срочное"))
        self.PB_WFSP.setText(_translate("main_window_CRM", "Ждут запсасти"))
        self.PB_Done.setText(_translate("main_window_CRM", "Готовое"))
        self.lineEdit.setPlaceholderText(_translate("main_window_CRM", "Поиск"))
        self.PB_Filter.setText(_translate("main_window_CRM", "Фильтр"))
        self.PB_Stil.setText(_translate("main_window_CRM", "Еще :"))
        self.PB_Add_Order.setText(_translate("main_window_CRM", "Добавить заказ"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window_CRM = QtWidgets.QDialog()
    ui = Ui_main_window_CRM()
    ui.setupUi(main_window_CRM)
    main_window_CRM.show()
    sys.exit(app.exec_())