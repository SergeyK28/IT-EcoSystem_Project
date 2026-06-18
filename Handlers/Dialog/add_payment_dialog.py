# -*- coding: utf-8 -*-
"""
Диалог для добавления нового платежа.
Поддерживает три типа операций:
1. Оплата заказа - привязывается к существующему заказу
2. Доход (прочий) - не привязанный к заказу доход (консультации, продажа запчастей и т.д.)
3. Расход - не привязанный к заказу расход (зарплата, аренда, закупка запчастей и т.д.)
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QFormLayout, QButtonGroup,
    QRadioButton, QFrame
)
from PyQt5.QtCore import Qt

import sys
import os

# Добавляем путь к корневой директории для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Server import db_crm
from Handlers.Employees.employee_session import employee_session


class AddPaymentDialog(QDialog):
    """
    Диалог добавления нового платежа.
    Позволяет выбрать тип операции (заказ/доход/расход) и ввести соответствующие данные.
    """

    # Константы для режимов работы
    MODE_ORDER = 'order'  # Оплата заказа
    MODE_INCOME = 'income'  # Прочий доход
    MODE_EXPENSE = 'expense'  # Расход

    def __init__(self, parent=None):
        """
        Инициализация диалога добавления платежа.

        Аргументы:
            parent: Родительский виджет
        """
        super().__init__(parent)

        # Настройка окна
        self.setWindowTitle("Добавить операцию")
        self.setMinimumWidth(550)
        self.setModal(True)  # Модальное окно - блокирует родительское окно

        # Переменные состояния
        self.selected_order_id = None  # ID выбранного заказа
        self.current_mode = self.MODE_ORDER  # Текущий режим (по умолчанию - заказ)

        # Настройка интерфейса
        self.setup_ui()

    def setup_ui(self):
        """
        Настройка пользовательского интерфейса.
        Создает все виджеты и размещает их на форме.
        """
        # ==================== СТИЛИ ====================
        self.setStyleSheet("""
            QDialog {
                background: #2a2a2a;
            }
            QLabel {
                color: #d0d0d0;
                font-size: 13px;
            }
            QRadioButton {
                color: #d0d0d0;
                font-size: 13px;
                spacing: 8px;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 1px solid #4CAF50;
                border-radius: 9px;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #4CAF50;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton[secondary="true"] {
                background: #3a3a3a;
            }
            QPushButton[secondary="true"]:hover {
                background: #4a4a4a;
            }
            QFrame {
                background-color: #323232;
                border-radius: 8px;
                padding: 10px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
        """)

        # ==================== ГЛАВНЫЙ LAYOUT ====================
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ==================== ЗАГОЛОВОК ====================
        title = QLabel("Новая операция")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # ==================== ПЕРЕКЛЮЧАТЕЛЬ ТИПА ОПЕРАЦИИ ====================
        # Создаем рамку для переключателей
        mode_frame = QFrame()
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setSpacing(20)

        # Создаем радио-кнопки для выбора типа операции
        self.order_radio = QRadioButton("📦 Оплата заказа")
        self.order_radio.setChecked(True)  # По умолчанию выбран заказ
        self.income_radio = QRadioButton("💰 Доход (прочий)")
        self.expense_radio = QRadioButton("💸 Расход")

        # Группируем кнопки (чтобы можно было выбрать только одну)
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.order_radio, 0)
        self.mode_group.addButton(self.income_radio, 1)
        self.mode_group.addButton(self.expense_radio, 2)

        # Подключаем сигналы для переключения режимов
        self.order_radio.toggled.connect(lambda checked: self.switch_mode(self.MODE_ORDER) if checked else None)
        self.income_radio.toggled.connect(lambda checked: self.switch_mode(self.MODE_INCOME) if checked else None)
        self.expense_radio.toggled.connect(lambda checked: self.switch_mode(self.MODE_EXPENSE) if checked else None)

        # Добавляем кнопки в layout
        mode_layout.addWidget(self.order_radio)
        mode_layout.addWidget(self.income_radio)
        mode_layout.addWidget(self.expense_radio)
        mode_layout.addStretch()  # Растягивает пустое пространство справа

        main_layout.addWidget(mode_frame)

        # ==================== ФОРМА ДЛЯ ЗАКАЗА ====================
        # Создаем рамку для полей, связанных с заказом
        self.order_frame = QFrame()
        order_layout = QVBoxLayout(self.order_frame)
        order_layout.setSpacing(10)

        # Поле для ввода номера заказа
        order_layout.addWidget(QLabel("Номер заказа:"))
        self.order_input = QLineEdit()
        self.order_input.setPlaceholderText("Введите номер заказа (например: ORD-20260323-0001)")
        self.order_input.textChanged.connect(self.search_order)  # Поиск при вводе
        order_layout.addWidget(self.order_input)

        # Информационная панель с данными о заказе (появляется после поиска)
        self.order_info = QLabel()
        self.order_info.setStyleSheet("""
            color: #b0b0b0; 
            font-size: 12px; 
            background-color: #3a3a3a; 
            padding: 8px; 
            border-radius: 6px;
        """)
        self.order_info.setWordWrap(True)  # Перенос текста
        self.order_info.hide()  # Изначально скрыта
        order_layout.addWidget(self.order_info)

        main_layout.addWidget(self.order_frame)

        # ==================== ФОРМА ДЛЯ ДОХОДА/РАСХОДА ====================
        # Создаем рамку для полей доходов и расходов
        self.income_expense_frame = QFrame()
        ie_layout = QVBoxLayout(self.income_expense_frame)
        ie_layout.setSpacing(10)

        # Поле выбора категории
        ie_layout.addWidget(QLabel("Статья:"))
        self.category_combo = QComboBox()
        ie_layout.addWidget(self.category_combo)

        # Поле для описания
        ie_layout.addWidget(QLabel("Описание:"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Краткое описание операции")
        ie_layout.addWidget(self.description_input)

        # Скрываем форму доходов/расходов по умолчанию
        self.income_expense_frame.hide()

        main_layout.addWidget(self.income_expense_frame)

        # ==================== ОБЩИЕ ПОЛЯ ====================
        # Создаем рамку для полей, общих для всех типов операций
        common_frame = QFrame()
        common_layout = QFormLayout(common_frame)
        common_layout.setSpacing(12)
        common_layout.setLabelAlignment(Qt.AlignRight)  # Выравнивание меток по правому краю

        # Поле для суммы
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.setFocus()  # Устанавливаем фокус на поле суммы
        common_layout.addRow("Сумма (₽):", self.amount_input)

        # Поле для выбора метода оплаты
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Наличные", "Карта", "Перевод", "Онлайн"])
        common_layout.addRow("Метод оплаты:", self.method_combo)

        # Поле для номера чека (опционально)
        self.receipt_input = QLineEdit()
        self.receipt_input.setPlaceholderText("Необязательно")
        common_layout.addRow("Номер чека:", self.receipt_input)

        # Поле для комментария (опционально)
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Необязательно")
        common_layout.addRow("Комментарий:", self.notes_input)

        main_layout.addWidget(common_frame)

        # ==================== КНОПКИ ====================
        # Создаем горизонтальный layout для кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()  # Растягивает пустое пространство слева

        # Кнопка "Отмена"
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setProperty("secondary", True)
        self.cancel_btn.clicked.connect(self.reject)  # reject() закрывает диалог без сохранения

        # Кнопка "Сохранить"
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_payment)

        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)

        main_layout.addLayout(buttons_layout)

        # Инициализируем категории для доходов/расходов
        self._update_categories()

    def _update_categories(self):
        """
        Обновляет список категорий в зависимости от выбранного режима.
        Доходы и расходы имеют разные наборы статей.
        """
        # Очищаем текущий список
        self.category_combo.clear()

        if self.current_mode == self.MODE_INCOME:
            # Для доходов - список источников дохода
            categories = [
                "Выручка от ремонта",
                "Продажа запчастей",
                "Консультации",
                "Диагностика",
                "Абонентское обслуживание",
                "Другое"
            ]
            self.category_combo.addItems(categories)

        elif self.current_mode == self.MODE_EXPENSE:
            # Для расходов - список статей расходов
            categories = [
                "Зарплата",
                "Аренда",
                "Коммунальные услуги",
                "Закупка запчастей",
                "Реклама",
                "Налоги",
                "Канцелярия",
                "Оборудование",
                "Транспорт",
                "Другое"
            ]
            self.category_combo.addItems(categories)

    def switch_mode(self, mode):
        """
        Переключает режим работы диалога.

        Аргументы:
            mode: Новый режим (MODE_ORDER, MODE_INCOME, MODE_EXPENSE)
        """
        self.current_mode = mode

        if mode == self.MODE_ORDER:
            # Режим заказа
            self.setWindowTitle("Добавить оплату заказа")
            self.order_frame.show()  # Показываем поля для заказа
            self.income_expense_frame.hide()  # Скрываем поля доходов/расходов
            self.selected_order_id = None  # Сбрасываем выбранный заказ
            self.order_info.hide()  # Скрываем информацию о заказе
            self.order_input.clear()  # Очищаем поле ввода
            self.order_input.setFocus()  # Устанавливаем фокус на поле заказа

        elif mode == self.MODE_INCOME:
            # Режим дохода
            self.setWindowTitle("Добавить доход")
            self.order_frame.hide()  # Скрываем поля заказа
            self.income_expense_frame.show()  # Показываем поля доходов/расходов
            self._update_categories()  # Обновляем категории
            self.category_combo.setFocus()  # Фокус на категорию

        else:  # MODE_EXPENSE
            # Режим расхода
            self.setWindowTitle("Добавить расход")
            self.order_frame.hide()  # Скрываем поля заказа
            self.income_expense_frame.show()  # Показываем поля доходов/расходов
            self._update_categories()  # Обновляем категории
            self.category_combo.setFocus()  # Фокус на категорию

        # Очищаем информацию о заказе
        self.order_info.setText("")
        self.order_info.hide()

    def search_order(self, text):
        """
        Поиск заказа по номеру.
        Вызывается при каждом изменении текста в поле ввода номера заказа.

        Аргументы:
            text: Текст для поиска (номер заказа)
        """
        # Проверяем, что мы в режиме заказа
        if self.current_mode != self.MODE_ORDER:
            return

        # Не ищем если текст слишком короткий
        if len(text) < 5:
            self.order_info.hide()
            self.selected_order_id = None
            return

        # Пытаемся найти заказ по номеру
        order_id = db_crm.get_order_id_by_number(text)

        if order_id:
            self.selected_order_id = order_id
            order_data = db_crm.get_order_for_edit_form(order_id)

            if order_data:
                # Формируем информацию о заказе
                client = order_data.get('ClientFullName', 'Неизвестно')
                if not client or client == 'Неизвестно':
                    client = f"{order_data.get('ClientFirstName', '')} {order_data.get('ClientLastName', '')}".strip()
                    if not client:
                        client = 'Неизвестно'

                # Устройство
                device = f"{order_data.get('DeviceBrand', '')} {order_data.get('DeviceModel', '')}".strip()
                if not device:
                    device = order_data.get('DeviceType', 'Не указано')

                # Финансовая информация
                total = float(order_data.get('FinalAmount', 0))
                paid = float(order_data.get('AllPaymentsTotal', 0))
                debt = total - paid

                # Формируем текст информации
                info_text = (
                    f"✓ Заказ найден\n"
                    f"Клиент: {client}\n"
                    f"Устройство: {device}\n"
                    f"Сумма заказа: {total:,.2f} ₽\n"
                    f"Оплачено: {paid:,.2f} ₽\n"
                    f"Остаток: {debt:,.2f} ₽"
                )

                # Устанавливаем стиль и текст
                self.order_info.setStyleSheet("""
                    color: #4CAF50; 
                    font-size: 12px; 
                    background-color: #3a3a3a; 
                    padding: 8px; 
                    border-radius: 6px;
                """)
                self.order_info.setText(info_text)
                self.order_info.show()

                # Если есть долг, предлагаем его сумму в поле ввода
                if debt > 0 and not self.amount_input.text():
                    self.amount_input.setText(f"{debt:.2f}")

                # Если заказ полностью оплачен, показываем предупреждение
                if debt <= 0:
                    self.order_info.setStyleSheet("""
                        color: #FF9800; 
                        font-size: 12px; 
                        background-color: #3a3a3a; 
                        padding: 8px; 
                        border-radius: 6px;
                    """)
                    self.order_info.setText(info_text + "\n⚠️ Внимание: Заказ полностью оплачен!")
            else:
                # Ошибка загрузки данных заказа
                self._show_order_error("Не удалось загрузить данные заказа")
        else:
            # Заказ не найден
            self._show_order_error("Заказ не найден. Проверьте номер заказа.")

    def _show_order_error(self, message):
        """
        Показывает сообщение об ошибке поиска заказа.

        Аргументы:
            message: Текст сообщения об ошибке
        """
        self.selected_order_id = None
        self.order_info.setStyleSheet("""
            color: #f44336; 
            font-size: 12px; 
            background-color: #3a3a3a; 
            padding: 8px; 
            border-radius: 6px;
        """)
        self.order_info.setText(message)
        self.order_info.show()

    def save_payment(self):
        """
        Сохраняет платеж в базу данных.
        Валидирует введенные данные и вызывает соответствующие функции БД.
        """
        # ==================== ВАЛИДАЦИЯ СУММЫ ====================
        try:
            amount_text = self.amount_input.text().strip()
            if not amount_text:
                QMessageBox.warning(self, "Ошибка", "Введите сумму")
                return

            # Заменяем запятую на точку для корректного преобразования
            amount = float(amount_text.replace(',', '.'))
            if amount <= 0:
                QMessageBox.warning(self, "Ошибка", "Сумма должна быть больше 0")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную сумму (например: 1000.00)")
            return

        # Получаем ID текущего сотрудника (если авторизован)
        employee_id = employee_session.get_employee_id() if employee_session.is_authenticated() else None

        # ==================== ОБРАБОТКА В ЗАВИСИМОСТИ ОТ РЕЖИМА ====================

        if self.current_mode == self.MODE_ORDER:
            # ----- Режим: Оплата заказа -----
            if not self.selected_order_id:
                QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите заказ")
                return

            # Формируем данные платежа
            payment_data = {
                'amount': amount,
                'payment_method': self.method_combo.currentText(),
                'payment_type': 'Оплата',
                'receipt_number': self.receipt_input.text().strip() or None,
                'notes': self.notes_input.text().strip() or None,
                'employee_id': employee_id
            }

            # Добавляем платеж
            success, message = db_crm.add_payment_with_validation(self.selected_order_id, payment_data)

        elif self.current_mode == self.MODE_INCOME:
            # ----- Режим: Доход (прочий) -----
            category = self.category_combo.currentText()
            description = self.description_input.text().strip()

            if not category:
                QMessageBox.warning(self, "Ошибка", "Выберите статью дохода")
                return

            # Формируем данные дохода
            transaction_data = {
                'transaction_type': 'income',
                'amount': amount,
                'method': self.method_combo.currentText(),
                'category': category,
                'description': description,
                'receipt_number': self.receipt_input.text().strip() or None,
                'employee_id': employee_id
            }

            # Добавляем доход
            success, message = db_crm.add_income_expense(transaction_data)

        else:  # self.MODE_EXPENSE
            # ----- Режим: Расход -----
            category = self.category_combo.currentText()
            description = self.description_input.text().strip()

            if not category:
                QMessageBox.warning(self, "Ошибка", "Выберите статью расхода")
                return

            # Формируем данные расхода
            transaction_data = {
                'transaction_type': 'expense',
                'amount': amount,
                'method': self.method_combo.currentText(),
                'category': category,
                'description': description,
                'receipt_number': self.receipt_input.text().strip() or None,
                'employee_id': employee_id
            }

            # Добавляем расход
            success, message = db_crm.add_income_expense(transaction_data)

        # ==================== ОБРАБОТКА РЕЗУЛЬТАТА ====================
        if success:
            QMessageBox.information(self, "Успех", message)
            self.accept()  # Закрываем диалог с кодом Accepted
        else:
            QMessageBox.critical(self, "Ошибка", message)