# -*- coding: utf-8 -*-
from delivery_datetime_dialog import DeliveryDateTimeDialog  # Новый импорт
from datetime import datetime
import random
import string
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDialog, QHeaderView
from session_manager import session
from Server import db_crm


class CartWindow(QDialog):
    def __init__(self, parent=None):
        super(CartWindow, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("CartWindow")
        self.resize(900, 600)
        self.setWindowTitle("Корзина - IT-EcoSystem")

        # Устанавливаем иконку
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Pictures/Screenshot from 2025-09-15 14-30-16.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # Темный стиль
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #232323, stop:1 #1a1a1a);
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: rgb(60, 60, 60);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgb(80, 80, 80);
            }
            QTableWidget {
                background-color: rgb(40, 40, 40);
                color: white;
                gridline-color: rgb(80, 80, 80);
                alternate-background-color: rgb(50, 50, 50);
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: rgb(103, 155, 118);
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        header_frame = QtWidgets.QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        header_layout = QtWidgets.QHBoxLayout(header_frame)

        title = QtWidgets.QLabel("🛒 Ваша корзина")
        title.setStyleSheet("color: #4CAF50; font-size: 20px; font-weight: bold;")

        self.close_btn = QtWidgets.QPushButton("✕")
        self.close_btn.setFixedSize(35, 35)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border-radius: 17px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4CAF50;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)

        layout.addWidget(header_frame)

        # Таблица корзины
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)  # Добавляем скрытую колонку для ID
        self.table.setHorizontalHeaderLabels([
            "Тип устройства", "Бренд", "Модель",
            "Причина", "Цена (₽)", "Дата добавления", "Действия"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(False)

        # Настраиваем ширину колонок
        self.table.setColumnWidth(0, 120)  # Тип устройства
        self.table.setColumnWidth(1, 100)  # Бренд
        self.table.setColumnWidth(2, 120)  # Модель
        self.table.setColumnWidth(3, 150)  # Причина
        self.table.setColumnWidth(4, 100)  # Цена
        self.table.setColumnWidth(5, 140)  # Дата
        self.table.setColumnWidth(6, 100)  # Действия

        layout.addWidget(self.table)

        # Нижняя панель с итогом
        bottom_frame = QtWidgets.QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        bottom_layout = QtWidgets.QHBoxLayout(bottom_frame)

        # Кнопка очистки корзины
        self.clear_btn = QtWidgets.QPushButton("🗑 Очистить корзину")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(220, 53, 69);
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgb(230, 63, 79);
            }
        """)
        self.clear_btn.clicked.connect(self.clear_cart)

        # Количество товаров
        self.count_label = QtWidgets.QLabel("Товаров: 0")
        self.count_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 13px;")

        # Итоговая сумма
        self.total_label = QtWidgets.QLabel("Итого: 0 ₽")
        self.total_label.setStyleSheet("color: #4CAF50; font-size: 18px; font-weight: bold;")

        # Кнопка оформления
        self.checkout_btn = QtWidgets.QPushButton("✅ Оформить заказ")
        self.checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(40, 167, 69);
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: rgb(50, 187, 79);
            }
        """)
        self.checkout_btn.clicked.connect(self.checkout)

        bottom_layout.addWidget(self.clear_btn)
        bottom_layout.addWidget(self.count_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addSpacing(20)
        bottom_layout.addWidget(self.checkout_btn)

        layout.addWidget(bottom_frame)

        # Загружаем данные корзины
        self.load_cart()

    def load_cart(self):
        """Загружает корзину текущего пользователя из БД"""
        if not session.is_authenticated():
            print("Пользователь не авторизован")
            return

        print(f"Загрузка корзины для пользователя ID: {session.get_user_id()}")
        cart_items = db_crm.get_user_cart_from_db(session.get_user_id())
        print(f"Получено элементов: {len(cart_items)}")

        self.table.setRowCount(len(cart_items))
        total = 0

        for row, item in enumerate(cart_items):
            # Тип устройства
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item.get('DeviceType', ''))))

            # Бренд
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item.get('DeviceBrand', ''))))

            # Модель
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(item.get('DeviceModel', ''))))

            # Причина
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(item.get('Reason', ''))))

            # Цена
            try:
                price = float(item.get('Price', 0))
                price_item = QtWidgets.QTableWidgetItem(f"{price:,.0f} ₽".replace(',', ' '))
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 4, price_item)
                total += price
            except (ValueError, TypeError) as e:
                print(f"Ошибка преобразования цены: {e}")
                self.table.setItem(row, 4, QtWidgets.QTableWidgetItem("0 ₽"))

            # Дата
            date_str = str(item.get('DateAdded', ''))
            date_item = QtWidgets.QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, date_item)

            # Сохраняем CartID в данных строки для последующего использования
            cart_id = item.get('CartID')

            # Кнопка удаления
            delete_btn = QtWidgets.QPushButton("🗑")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgb(220, 53, 69);
                    color: white;
                    border-radius: 15px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgb(230, 63, 79);
                }
            """)
            delete_btn.clicked.connect(lambda checked, r=row, cid=cart_id:
                                       self.remove_from_cart(r, cid))

            cell_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout(cell_widget)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setAlignment(Qt.AlignCenter)

            self.table.setCellWidget(row, 6, cell_widget)

        # Обновляем итоги
        self.total_label.setText(f"Итого: {total:,.0f} ₽".replace(',', ' '))
        self.count_label.setText(f"Товаров: {len(cart_items)}")

        # Выравнивание текста в ячейках
        for row in range(self.table.rowCount()):
            for col in range(6):  # Не включаем колонку с кнопками
                item = self.table.item(row, col)
                if item:
                    if col == 4:  # Цена - вправо
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    elif col == 5:  # Дата - по центру
                        item.setTextAlignment(Qt.AlignCenter)
                    else:
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.table.resizeColumnsToContents()

    def remove_from_cart(self, row, cart_id):
        """Удаляет товар из корзины"""
        if cart_id is None:
            print("Ошибка: cart_id is None")
            return

        reply = QMessageBox.question(
            self,
            "Удаление из корзины",
            "Убрать этот товар из корзины?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if db_crm.remove_from_cart_db(cart_id, session.get_user_id()):
                self.table.removeRow(row)
                self.load_cart()  # Перезагружаем для обновления итогов
                QMessageBox.information(self, "Успех", "Товар удален из корзины")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить товар")

    def clear_cart(self):
        """Очищает корзину текущего пользователя"""
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Корзина пуста", "В корзине нет товаров")
            return

        reply = QMessageBox.question(
            self,
            "Очистка корзины",
            "Вы уверены, что хотите очистить корзину?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if db_crm.clear_user_cart_db(session.get_user_id()):
                self.load_cart()  # Перезагружаем (таблица будет пустой)
                QMessageBox.information(self, "Успех", "Корзина очищена")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось очистить корзину")

    def checkout(self):
        """Оформление заказа с выбором даты и времени"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Корзина пуста", "Добавьте товары в корзину перед оформлением")
            return

        # Открываем диалог выбора даты и времени
        datetime_dialog = DeliveryDateTimeDialog(self)
        if datetime_dialog.exec_() != QDialog.Accepted:
            return  # Пользователь отменил выбор

        selected_datetime = datetime_dialog.get_selected_datetime()

        # Показываем подтверждение с выбранным временем
        reply = QMessageBox.question(
            self,
            "Подтверждение визита",
            f"Вы выбрали дату и время визита:\n\n"
            f"📅 {selected_datetime.replace('-', '.').replace(' ', ' в ')}\n\n"
            f"Пожалуйста, принесите технику в сервисный центр в это время.\n"
            f"Адрес: Красноярск, Улица Микуцкого, 12\n\n"
            f"Подтвердить оформление заказа?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            # Получаем товары из корзины
            cart_items = db_crm.get_user_cart_from_db(session.get_user_id())

            if not cart_items:
                QMessageBox.warning(self, "Ошибка", "Корзина пуста")
                return

            try:
                # Создаем новый заказ в CRM
                order_id = self.create_order_from_cart(cart_items, selected_datetime)

                if order_id:
                    # Очищаем корзину
                    db_crm.clear_user_cart_db(session.get_user_id())

                    QMessageBox.information(
                        self,
                        "Заказ оформлен",
                        f"✅ Ваш заказ успешно оформлен!\n\n"
                        f"📅 Дата визита: {selected_datetime.replace('-', '.').replace(' ', ' в ')}\n"
                        f"📍 Адрес: Красноярск, Улица Микуцкого, 12\n\n"
                        f"Наш менеджер свяжется с вами для подтверждения."
                    )
                    self.load_cart()  # Очищаем таблицу
                    self.accept()  # Закрываем окно корзины
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать заказ")

            except Exception as e:
                print(f"Ошибка при оформлении заказа: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось оформить заказ: {e}")

    def create_order_from_cart(self, cart_items, visit_datetime):
        """Создает заказ на основе товаров в корзине"""
        try:
            # Генерируем номер заказа
            import time
            current_date = time.strftime('%Y%m%d')

            connection = db_crm.get_crm_connection()
            if not connection:
                return None

            cursor = connection.cursor()

            # Получаем последний номер заказа за сегодня
            cursor.execute("""
                SELECT OrderNumber FROM Orders 
                WHERE OrderNumber LIKE %s 
                ORDER BY OrderNumber DESC 
                LIMIT 1
            """, (f'ORD-{current_date}-%',))

            last_order = cursor.fetchone()
            if last_order:
                last_number = int(last_order[0].split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            order_number = f"ORD-{current_date}-{new_number:04d}"

            # Берем первый товар для основной информации (можно объединить несколько)
            first_item = cart_items[0] if cart_items else {}

            # Определяем причину обращения
            appeal_reason_id = self.get_appeal_reason_id(first_item.get('Reason', ''))

            # Создаем заказ
            query = """
            INSERT INTO Orders (
                OrderNumber, OrderDate, Status, OrderType, Priority,
                DeviceType, DeviceBrand, DeviceModel, ProblemDescription,
                ClientID, AppealReasonID, EstimatedCompletion, Notes,
                TotalAmount, FinalAmount, IsPaid
            ) VALUES (
                %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            # Рассчитываем общую сумму
            total_amount = sum(float(item.get('Price', 0)) for item in cart_items)

            # Формируем описание из всех товаров
            if len(cart_items) > 1:
                problem_desc = f"Несколько услуг:\n"
                for item in cart_items:
                    problem_desc += f"- {item.get('DeviceType', '')} {item.get('DeviceBrand', '')} {item.get('DeviceModel', '')}: {item.get('Reason', '')}\n"
            else:
                problem_desc = first_item.get('Reason', '')

            cursor.execute(query, (
                order_number,
                'Клиент несет заказ',  # Новый статус
                'Платный',  # OrderType
                'Средний',  # Priority
                first_item.get('DeviceType', ''),
                first_item.get('DeviceBrand', ''),
                first_item.get('DeviceModel', ''),
                problem_desc,
                session.get_user_id(),  # ClientID
                appeal_reason_id,
                visit_datetime,  # EstimatedCompletion
                f"Клиент принесет технику {visit_datetime}",
                total_amount,
                total_amount,
                False  # IsPaid
            ))

            new_order_id = cursor.lastrowid

            # Добавляем комментарий о времени визита
            cursor.execute("""
                INSERT INTO OrderComments (OrderID, EmployeeID, CommentText, IsInternal)
                VALUES (%s, %s, %s, %s)
            """, (
                new_order_id,
                None,
                f"Клиент планирует принести технику {visit_datetime.replace('-', '.').replace(' ', ' в ')}",
                True
            ))

            # Записываем в историю статусов
            cursor.execute("""
                INSERT INTO OrderStatusHistory (OrderID, OldStatus, NewStatus, ChangedBy, ChangeReason)
                VALUES (%s, NULL, %s, %s, %s)
            """, (
                new_order_id,
                'Клиент несет заказ',
                None,
                'Оформление через корзину'
            ))

            connection.commit()
            cursor.close()
            connection.close()

            return new_order_id

        except Exception as e:
            print(f"Ошибка создания заказа из корзины: {e}")
            if connection:
                connection.rollback()
                connection.close()
            return None

    def get_appeal_reason_id(self, reason_name):
        """Получает ID причины обращения по названию"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return None

            cursor = connection.cursor(dictionary=True)

            # Пытаемся найти точное совпадение
            cursor.execute("SELECT ReasonID FROM AppealReasons WHERE ReasonName LIKE %s", (f'%{reason_name}%',))
            result = cursor.fetchone()

            cursor.close()
            connection.close()

            if result:
                return result['ReasonID']

            # Если не нашли, возвращаем ID "Другой причины" (обычно 20)
            return 20

        except Exception as e:
            print(f"Ошибка получения ID причины: {e}")
            return None