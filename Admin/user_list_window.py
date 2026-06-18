# -*- coding: utf-8 -*-

import sys
import os
import secrets
import bcrypt
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QFormLayout, QMessageBox, QComboBox,
    QCheckBox, QDateEdit, QHeaderView, QAbstractItemView, QTabWidget,
    QWidget, QFrame, QGroupBox, QGridLayout, QTextEdit, QSpinBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QIcon

# Добавляем путь к корневой директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Server import db_crm
from Server.db import get_connection


class UnifiedUserManagementDialog(QDialog):
    """
    Диалоговое окно управления пользователями (клиенты + сотрудники).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Управление пользователями - IT-EcoSystem CRM")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 750)

        self.selected_user_id = None  # ID выбранного пользователя
        self.selected_user_type = None  # 'client' или 'employee'
        self.search_timer = None  # для debounce поиска

        self.setup_ui()
        self.load_clients()  # По умолчанию загружаем клиентов

        self.setStyleSheet(self.get_style())

    def get_style(self):
        """Стилизация окна в тёмной теме CRM."""
        return """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #232323, stop:1 #1a1a1a);
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 6px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4CAF50;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton#primaryBtn {
                background-color: #4CAF50;
            }
            QPushButton#primaryBtn:hover {
                background-color: #45a049;
            }
            QPushButton#dangerBtn {
                background-color: #f44336;
            }
            QPushButton#dangerBtn:hover {
                background-color: #d32f2f;
            }
            QPushButton#warningBtn {
                background-color: #FF9800;
            }
            QPushButton#warningBtn:hover {
                background-color: #e68900;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                gridline-color: #3a3a3a;
                alternate-background-color: #333333;
                selection-background-color: #4CAF50;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QTabWidget::pane {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #d0d0d0;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QGroupBox {
                color: #4CAF50;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """

    def setup_ui(self):
        """Создаёт интерфейс: вкладки клиенты/сотрудники, поиск, таблица, кнопки."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title = QLabel("👥 Управление пользователями")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Вкладки: Клиенты / Сотрудники
        self.tab_widget = QTabWidget()
        self.clients_tab = QWidget()
        self.employees_tab = QWidget()
        self.setup_clients_tab()
        self.setup_employees_tab()
        self.tab_widget.addTab(self.clients_tab, "👤 Клиенты")
        self.tab_widget.addTab(self.employees_tab, "👔 Сотрудники")
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)

    def setup_clients_tab(self):
        """Настройка вкладки клиентов."""
        layout = QVBoxLayout(self.clients_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Панель поиска
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)

        self.client_search_input = QLineEdit()
        self.client_search_input.setPlaceholderText("🔍 Поиск клиентов (логин, имя, email, телефон)...")
        self.client_search_input.textChanged.connect(lambda: self.on_search_changed('client'))
        search_layout.addWidget(self.client_search_input)

        self.client_search_btn = QPushButton("Найти")
        self.client_search_btn.clicked.connect(lambda: self.load_clients())
        search_layout.addWidget(self.client_search_btn)

        layout.addWidget(search_frame)

        # Таблица клиентов
        self.client_table = QTableWidget()
        self.client_table.setColumnCount(7)
        self.client_table.setHorizontalHeaderLabels([
            "ID", "Логин", "Имя", "Фамилия", "Email", "Телефон", "Статус"
        ])
        self.client_table.setAlternatingRowColors(True)
        self.client_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.client_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.client_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.client_table.setColumnHidden(0, True)
        self.client_table.itemSelectionChanged.connect(lambda: self.on_user_selected('client'))
        layout.addWidget(self.client_table)

        # Кнопки действий
        self.client_buttons = self.create_buttons_panel()
        layout.addLayout(self.client_buttons)

    def setup_employees_tab(self):
        """Настройка вкладки сотрудников."""
        layout = QVBoxLayout(self.employees_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Панель поиска
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)

        self.emp_search_input = QLineEdit()
        self.emp_search_input.setPlaceholderText("🔍 Поиск сотрудников (имя, email, должность)...")
        self.emp_search_input.textChanged.connect(lambda: self.on_search_changed('employee'))
        search_layout.addWidget(self.emp_search_input)

        self.emp_search_btn = QPushButton("Найти")
        self.emp_search_btn.clicked.connect(lambda: self.load_employees())
        search_layout.addWidget(self.emp_search_btn)

        layout.addWidget(search_frame)

        # Таблица сотрудников
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(8)
        self.employee_table.setHorizontalHeaderLabels([
            "ID", "Имя", "Фамилия", "Email", "Телефон", "Должность", "Роль", "Статус"
        ])
        self.employee_table.setAlternatingRowColors(True)
        self.employee_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.employee_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.employee_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employee_table.setColumnHidden(0, True)
        self.employee_table.itemSelectionChanged.connect(lambda: self.on_user_selected('employee'))
        layout.addWidget(self.employee_table)

        # Кнопки действий
        self.emp_buttons = self.create_buttons_panel()
        layout.addLayout(self.emp_buttons)

    def create_buttons_panel(self):
        """Создаёт горизонтальную панель с кнопками."""
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.add_btn = QPushButton("➕ Добавить")
        self.add_btn.setObjectName("primaryBtn")
        self.add_btn.clicked.connect(self.add_user)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setObjectName("warningBtn")
        self.edit_btn.clicked.connect(self.edit_user)
        btn_layout.addWidget(self.edit_btn)

        self.block_btn = QPushButton("🔒 Заблокировать / 🔓 Разблокировать")
        self.block_btn.setObjectName("dangerBtn")
        self.block_btn.clicked.connect(self.toggle_block)
        btn_layout.addWidget(self.block_btn)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.refresh_current_tab)
        btn_layout.addWidget(self.refresh_btn)

        btn_layout.addStretch()
        return btn_layout

    def on_search_changed(self, user_type: str):
        """Debounce поиска: задержка 500 мс после ввода."""
        if hasattr(self, '_search_timer'):
            self._search_timer.stop()
        from PyQt5.QtCore import QTimer
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(500)
        if user_type == 'client':
            self._search_timer.timeout.connect(self.load_clients)
        else:
            self._search_timer.timeout.connect(self.load_employees)
        self._search_timer.start()

    def on_tab_changed(self, index):
        """При переключении вкладки загружаем соответствующий список."""
        if index == 0:
            self.load_clients()
        else:
            self.load_employees()
        self.selected_user_id = None
        self.selected_user_type = None
        self.update_block_button_text()

    def refresh_current_tab(self):
        """Обновляет данные текущей вкладки."""
        if self.tab_widget.currentIndex() == 0:
            self.load_clients()
        else:
            self.load_employees()

    def on_user_selected(self, user_type: str):
        """Обработчик выбора строки в таблице."""
        if user_type == 'client':
            table = self.client_table
        else:
            table = self.employee_table

        selected = table.selectedItems()
        if selected:
            row = selected[0].row()
            id_item = table.item(row, 0)
            if id_item:
                self.selected_user_id = int(id_item.text())
                self.selected_user_type = user_type
            else:
                self.selected_user_id = None
        else:
            self.selected_user_id = None

        self.update_block_button_text()

    def update_block_button_text(self):
        """Меняет текст кнопки блокировки в зависимости от статуса выбранного пользователя."""
        if self.selected_user_id is None:
            self.block_btn.setText("🔒 Заблокировать")
            return

        # Получаем текущий статус из таблицы
        if self.selected_user_type == 'client':
            table = self.client_table
            row = self.get_selected_row(table)
            if row is not None:
                status_item = table.item(row, 6)
                if status_item:
                    is_active = status_item.text() == "Активен"
                    self.block_btn.setText("🔒 Заблокировать" if is_active else "🔓 Разблокировать")
        else:
            table = self.employee_table
            row = self.get_selected_row(table)
            if row is not None:
                status_item = table.item(row, 7)
                if status_item:
                    is_active = status_item.text() == "Активен"
                    self.block_btn.setText("🔒 Заблокировать" if is_active else "🔓 Разблокировать")

    def get_selected_row(self, table):
        """Возвращает индекс выбранной строки или None."""
        selected = table.selectedItems()
        if selected:
            return selected[0].row()
        return None

    # ================== ЗАГРУЗКА ДАННЫХ ==================

    def load_clients(self):
        """Загружает клиентов из БД с учётом поискового запроса."""
        try:
            conn = db_crm.get_crm_connection()
            if not conn:
                return
            cursor = conn.cursor(dictionary=True)

            search_text = self.client_search_input.text().strip()
            if search_text:
                search_pattern = f"%{search_text}%"
                cursor.execute("""
                               SELECT ID, Login, FirstName, LastName, Email, PhoneNumber, IsActive
                               FROM Client
                               WHERE Login LIKE %s
                                  OR FirstName LIKE %s
                                  OR LastName LIKE %s
                                  OR Email LIKE %s
                                  OR PhoneNumber LIKE %s
                               ORDER BY ID
                               """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            else:
                cursor.execute("""
                               SELECT ID, Login, FirstName, LastName, Email, PhoneNumber, IsActive
                               FROM Client
                               ORDER BY ID
                               """)
            clients = cursor.fetchall()
            cursor.close()
            conn.close()

            self.populate_client_table(clients)
        except Exception as e:
            print(f"Ошибка загрузки клиентов: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить клиентов: {e}")

    def populate_client_table(self, clients):
        """Заполняет таблицу клиентов."""
        self.client_table.setRowCount(len(clients))
        for row, c in enumerate(clients):
            self.client_table.setItem(row, 0, QTableWidgetItem(str(c['ID'])))
            self.client_table.setItem(row, 1, QTableWidgetItem(c['Login'] or ""))
            self.client_table.setItem(row, 2, QTableWidgetItem(c['FirstName'] or ""))
            self.client_table.setItem(row, 3, QTableWidgetItem(c['LastName'] or ""))
            self.client_table.setItem(row, 4, QTableWidgetItem(c['Email'] or ""))
            self.client_table.setItem(row, 5, QTableWidgetItem(c['PhoneNumber'] or ""))

            status_text = "Активен" if c['IsActive'] else "Заблокирован"
            status_item = QTableWidgetItem(status_text)
            if not c['IsActive']:
                status_item.setBackground(QColor(220, 53, 69))
            else:
                status_item.setBackground(QColor(40, 167, 69))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.client_table.setItem(row, 6, status_item)

        self.client_table.resizeColumnsToContents()
        self.selected_user_id = None
        self.selected_user_type = None

    def load_employees(self):
        """Загружает сотрудников из БД с учётом поиска."""
        try:
            conn = db_crm.get_crm_connection()
            if not conn:
                return
            cursor = conn.cursor(dictionary=True)

            search_text = self.emp_search_input.text().strip()
            if search_text:
                search_pattern = f"%{search_text}%"
                cursor.execute("""
                               SELECT EmployeeID,
                                      FirstName,
                                      LastName,
                                      Email,
                                      PhoneNumber,
                                      Position,
                                      Role,
                                      IsActive
                               FROM ListEmployee
                               WHERE FirstName LIKE %s
                                  OR LastName LIKE %s
                                  OR Email LIKE %s
                                  OR PhoneNumber LIKE %s
                                  OR Position LIKE %s
                               ORDER BY EmployeeID
                               """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            else:
                cursor.execute("""
                               SELECT EmployeeID,
                                      FirstName,
                                      LastName,
                                      Email,
                                      PhoneNumber,
                                      Position,
                                      Role,
                                      IsActive
                               FROM ListEmployee
                               ORDER BY EmployeeID
                               """)
            employees = cursor.fetchall()
            cursor.close()
            conn.close()

            self.populate_employee_table(employees)
        except Exception as e:
            print(f"Ошибка загрузки сотрудников: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить сотрудников: {e}")

    def populate_employee_table(self, employees):
        """Заполняет таблицу сотрудников."""
        self.employee_table.setRowCount(len(employees))
        for row, e in enumerate(employees):
            self.employee_table.setItem(row, 0, QTableWidgetItem(str(e['EmployeeID'])))
            self.employee_table.setItem(row, 1, QTableWidgetItem(e['FirstName'] or ""))
            self.employee_table.setItem(row, 2, QTableWidgetItem(e['LastName'] or ""))
            self.employee_table.setItem(row, 3, QTableWidgetItem(e['Email'] or ""))
            self.employee_table.setItem(row, 4, QTableWidgetItem(e['PhoneNumber'] or ""))
            self.employee_table.setItem(row, 5, QTableWidgetItem(e['Position'] or ""))
            self.employee_table.setItem(row, 6, QTableWidgetItem(e['Role'] or ""))

            status_text = "Активен" if e['IsActive'] else "Заблокирован"
            status_item = QTableWidgetItem(status_text)
            if not e['IsActive']:
                status_item.setBackground(QColor(220, 53, 69))
            else:
                status_item.setBackground(QColor(40, 167, 69))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.employee_table.setItem(row, 7, status_item)

        self.employee_table.resizeColumnsToContents()
        self.selected_user_id = None
        self.selected_user_type = None

    # ================== ДЕЙСТВИЯ С ПОЛЬЗОВАТЕЛЯМИ ==================

    def add_user(self):
        """Добавление нового пользователя в зависимости от текущей вкладки."""
        if self.tab_widget.currentIndex() == 0:
            self.open_client_dialog(mode='add')
        else:
            self.open_employee_dialog(mode='add')

    def edit_user(self):
        """Редактирование выбранного пользователя."""
        if self.selected_user_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите пользователя для редактирования")
            return
        if self.selected_user_type == 'client':
            self.open_client_dialog(mode='edit')
        else:
            self.open_employee_dialog(mode='edit')

    def toggle_block(self):
        """Блокировка/разблокировка выбранного пользователя (единая кнопка)."""
        if self.selected_user_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите пользователя")
            return

        # Определяем текущий статус
        if self.selected_user_type == 'client':
            table = self.client_table
            row = self.get_selected_row(table)
            if row is None:
                return
            status_item = table.item(row, 6)
            is_active = status_item.text() == "Активен"
            new_status = not is_active
            action = "разблокировать" if not is_active else "заблокировать"
            reply = QMessageBox.question(
                self, "Подтверждение",
                f"Вы уверены, что хотите {action} этого клиента?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            try:
                conn = db_crm.get_crm_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                cursor.execute("UPDATE Client SET IsActive = %s WHERE ID = %s", (new_status, self.selected_user_id))
                conn.commit()
                cursor.close()
                conn.close()
                self.load_clients()
                QMessageBox.information(self, "Успех", f"Клиент {action}.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось {action} клиента: {e}")
        else:
            table = self.employee_table
            row = self.get_selected_row(table)
            if row is None:
                return
            status_item = table.item(row, 7)
            is_active = status_item.text() == "Активен"
            new_status = not is_active
            action = "разблокировать" if not is_active else "заблокировать"
            reply = QMessageBox.question(
                self, "Подтверждение",
                f"Вы уверены, что хотите {action} этого сотрудника?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            try:
                conn = db_crm.get_crm_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                cursor.execute("UPDATE ListEmployee SET IsActive = %s WHERE EmployeeID = %s",
                               (new_status, self.selected_user_id))
                conn.commit()
                cursor.close()
                conn.close()
                self.load_employees()
                QMessageBox.information(self, "Успех", f"Сотрудник {action}.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось {action} сотрудника: {e}")

    # ================== ДИАЛОГИ ДЛЯ КЛИЕНТОВ ==================

    def open_client_dialog(self, mode='add'):
        """Открывает диалог добавления/редактирования клиента."""
        dialog = ClientUnifiedDialog(self, mode=mode, user_id=self.selected_user_id if mode == 'edit' else None)
        if dialog.exec_() == QDialog.Accepted:
            self.load_clients()

    # ================== ДИАЛОГИ ДЛЯ СОТРУДНИКОВ ==================

    def open_employee_dialog(self, mode='add'):
        """Открывает диалог добавления/редактирования сотрудника."""
        dialog = EmployeeUnifiedDialog(self, mode=mode, user_id=self.selected_user_id if mode == 'edit' else None)
        if dialog.exec_() == QDialog.Accepted:
            self.load_employees()


class ClientUnifiedDialog(QDialog):
    """Диалог добавления/редактирования клиента с возможностью смены пароля."""

    def __init__(self, parent=None, mode='add', user_id=None):
        super().__init__(parent)
        self.mode = mode
        self.user_id = user_id
        self.client_data = None

        self.setWindowTitle("Добавление клиента" if mode == 'add' else "Редактирование клиента")
        self.setMinimumSize(450, 550)
        self.setModal(True)

        self.setup_ui()
        if mode == 'edit' and user_id:
            self.load_client_data()

        self.apply_style()

    def apply_style(self):
        style = """
            QDialog { background-color: #2a2a2a; }
            QLabel { color: white; }
            QLineEdit, QDateEdit { background-color: #3a3a3a; color: white; border: 1px solid #4a4a4a; border-radius: 5px; padding: 6px; }
            QPushButton { background-color: #3a3a3a; color: white; border-radius: 5px; padding: 8px 16px; }
            QPushButton#saveBtn { background-color: #4CAF50; }
            QPushButton#saveBtn:hover { background-color: #45a049; }
            QPushButton#cancelBtn:hover { background-color: #5a5a5a; }
            QGroupBox { color: #4CAF50; border: 1px solid #4a4a4a; border-radius: 8px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """
        self.setStyleSheet(style)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(10)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин")
        form.addRow("Логин *:", self.login_edit)

        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Имя")
        form.addRow("Имя:", self.first_name_edit)

        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Фамилия")
        form.addRow("Фамилия:", self.last_name_edit)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        form.addRow("Email:", self.email_edit)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Телефон")
        form.addRow("Телефон:", self.phone_edit)

        self.birthdate_edit = QDateEdit()
        self.birthdate_edit.setCalendarPopup(True)
        self.birthdate_edit.setDisplayFormat("dd.MM.yyyy")
        self.birthdate_edit.setDate(QDate(1990, 1, 1))
        form.addRow("Дата рождения:", self.birthdate_edit)

        # Группа смены пароля (только для редактирования)
        self.password_group = QGroupBox("Смена пароля")
        self.password_group.setVisible(self.mode == 'edit')
        pwd_layout = QVBoxLayout(self.password_group)

        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        self.new_password_edit.setPlaceholderText("Новый пароль (оставьте пустым, чтобы не менять)")
        pwd_layout.addWidget(self.new_password_edit)

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("Подтвердите новый пароль")
        pwd_layout.addWidget(self.confirm_password_edit)

        layout.addLayout(form)
        layout.addWidget(self.password_group)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def load_client_data(self):
        """Загружает данные клиента для редактирования."""
        try:
            conn = db_crm.get_crm_connection()
            if not conn:
                return
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                           SELECT ID,
                                  Login,
                                  FirstName,
                                  LastName,
                                  Email,
                                  PhoneNumber,
                                  Birthdate,
                                  IsActive
                           FROM Client
                           WHERE ID = %s
                           """, (self.user_id,))
            self.client_data = cursor.fetchone()
            cursor.close()
            conn.close()

            if self.client_data:
                self.login_edit.setText(self.client_data['Login'] or "")
                self.first_name_edit.setText(self.client_data['FirstName'] or "")
                self.last_name_edit.setText(self.client_data['LastName'] or "")
                self.email_edit.setText(self.client_data['Email'] or "")
                self.phone_edit.setText(self.client_data['PhoneNumber'] or "")
                if self.client_data.get('Birthdate'):
                    qdate = QDate.fromString(str(self.client_data['Birthdate']), "yyyy-MM-dd")
                    if qdate.isValid():
                        self.birthdate_edit.setDate(qdate)
            else:
                QMessageBox.warning(self, "Ошибка", "Клиент не найден")
                self.reject()
        except Exception as e:
            print(f"Ошибка загрузки клиента: {e}")

    def save(self):
        login = self.login_edit.text().strip()
        if not login:
            QMessageBox.warning(self, "Ошибка", "Логин обязателен")
            return

        data = {
            'login': login,
            'first_name': self.first_name_edit.text().strip(),
            'last_name': self.last_name_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'birthdate': self.birthdate_edit.date().toString("yyyy-MM-dd")
        }

        try:
            conn = db_crm.get_crm_connection()
            if not conn:
                return
            cursor = conn.cursor()

            if self.mode == 'add':
                # Проверка уникальности логина/email
                cursor.execute("SELECT ID FROM Client WHERE Login = %s", (login,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Ошибка", "Логин уже существует")
                    return
                if data['email']:
                    cursor.execute("SELECT ID FROM Client WHERE Email = %s", (data['email'],))
                    if cursor.fetchone():
                        QMessageBox.warning(self, "Ошибка", "Email уже существует")
                        return

                # Генерация пароля
                temp_password = secrets.token_urlsafe(8)
                password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cursor.execute("""
                               INSERT INTO Client (Login, PasswordHash, FirstName, LastName, Email, PhoneNumber,
                                                   Birthdate, RegistrationDate, IsActive)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), TRUE)
                               """, (login, password_hash, data['first_name'], data['last_name'], data['email'],
                                     data['phone'],
                                     data['birthdate'] if data['birthdate'] != "1900-01-01" else None))
                conn.commit()
                QMessageBox.information(self, "Успех",
                                        f"Клиент добавлен!\nВременный пароль: {temp_password}\nСохраните его.")
            else:
                # Обновление
                updates = []
                params = []
                updates.append("Login = %s")
                params.append(login)
                updates.append("FirstName = %s")
                params.append(data['first_name'])
                updates.append("LastName = %s")
                params.append(data['last_name'])
                updates.append("Email = %s")
                params.append(data['email'])
                updates.append("PhoneNumber = %s")
                params.append(data['phone'])
                updates.append("Birthdate = %s")
                params.append(data['birthdate'] if data['birthdate'] != "1900-01-01" else None)

                # Смена пароля
                new_pass = self.new_password_edit.text().strip()
                if new_pass:
                    if new_pass != self.confirm_password_edit.text().strip():
                        QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
                        return
                    password_hash = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    updates.append("PasswordHash = %s")
                    params.append(password_hash)

                params.append(self.user_id)
                query = f"UPDATE Client SET {', '.join(updates)} WHERE ID = %s"
                cursor.execute(query, params)
                conn.commit()
                QMessageBox.information(self, "Успех", "Данные клиента обновлены")

            cursor.close()
            conn.close()
            self.accept()
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")


class EmployeeUnifiedDialog(QDialog):
    """Диалог добавления/редактирования сотрудника с возможностью смены пароля."""

    def __init__(self, parent=None, mode='add', user_id=None):
        super().__init__(parent)
        self.mode = mode
        self.user_id = user_id
        self.employee_data = None

        self.setWindowTitle("Добавление сотрудника" if mode == 'add' else "Редактирование сотрудника")
        self.setMinimumSize(500, 600)
        self.setModal(True)

        self.setup_ui()
        if mode == 'edit' and user_id:
            self.load_employee_data()

        self.apply_style()

    def apply_style(self):
        style = """
            QDialog { background-color: #2a2a2a; }
            QLabel { color: white; }
            QLineEdit, QDateEdit, QComboBox { background-color: #3a3a3a; color: white; border: 1px solid #4a4a4a; border-radius: 5px; padding: 6px; }
            QPushButton { background-color: #3a3a3a; color: white; border-radius: 5px; padding: 8px 16px; }
            QPushButton#saveBtn { background-color: #4CAF50; }
            QPushButton#saveBtn:hover { background-color: #45a049; }
            QPushButton#cancelBtn:hover { background-color: #5a5a5a; }
            QGroupBox { color: #4CAF50; border: 1px solid #4a4a4a; border-radius: 8px; margin-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """
        self.setStyleSheet(style)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(10)

        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Имя")
        form.addRow("Имя *:", self.first_name_edit)

        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Фамилия")
        form.addRow("Фамилия *:", self.last_name_edit)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email *")
        form.addRow("Email *:", self.email_edit)

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Телефон")
        form.addRow("Телефон:", self.phone_edit)

        self.position_edit = QLineEdit()
        self.position_edit.setPlaceholderText("Должность")
        form.addRow("Должность:", self.position_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["technician", "manager", "admin", "consultant"])
        self.role_combo.setEditable(True)
        form.addRow("Роль:", self.role_combo)

        # Группа смены пароля
        self.password_group = QGroupBox("Смена пароля")
        self.password_group.setVisible(self.mode == 'edit')
        pwd_layout = QVBoxLayout(self.password_group)

        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        self.new_password_edit.setPlaceholderText("Новый пароль (оставьте пустым, чтобы не менять)")
        pwd_layout.addWidget(self.new_password_edit)

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("Подтвердите новый пароль")
        pwd_layout.addWidget(self.confirm_password_edit)

        layout.addLayout(form)
        layout.addWidget(self.password_group)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def load_employee_data(self):
        try:
            conn = db_crm.get_crm_connection()
            if not conn:
                return
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                           SELECT EmployeeID,
                                  FirstName,
                                  LastName,
                                  Email,
                                  PhoneNumber,
                                  Position,
                                  Role,
                                  IsActive
                           FROM ListEmployee
                           WHERE EmployeeID = %s
                           """, (self.user_id,))
            self.employee_data = cursor.fetchone()
            cursor.close()
            conn.close()

            if self.employee_data:
                self.first_name_edit.setText(self.employee_data['FirstName'] or "")
                self.last_name_edit.setText(self.employee_data['LastName'] or "")
                self.email_edit.setText(self.employee_data['Email'] or "")
                self.phone_edit.setText(self.employee_data['PhoneNumber'] or "")
                self.position_edit.setText(self.employee_data['Position'] or "")
                role = self.employee_data.get('Role', 'technician')
                idx = self.role_combo.findText(role)
                if idx >= 0:
                    self.role_combo.setCurrentIndex(idx)
                else:
                    self.role_combo.setEditText(role)
            else:
                QMessageBox.warning(self, "Ошибка", "Сотрудник не найден")
                self.reject()
        except Exception as e:
            print(f"Ошибка загрузки сотрудника: {e}")

    def save(self):
        first_name = self.first_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        email = self.email_edit.text().strip()
        if not first_name or not last_name or not email:
            QMessageBox.warning(self, "Ошибка", "Имя, фамилия и email обязательны")
            return

        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': self.phone_edit.text().strip(),
            'position': self.position_edit.text().strip(),
            'role': self.role_combo.currentText().strip()
        }

        try:
            conn = db_crm.get_crm_connection()
            if not conn:
                return
            cursor = conn.cursor()

            if self.mode == 'add':
                cursor.execute("SELECT EmployeeID FROM ListEmployee WHERE Email = %s", (email,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Ошибка", "Сотрудник с таким email уже существует")
                    return

                temp_password = secrets.token_urlsafe(8)
                password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cursor.execute("""
                               INSERT INTO ListEmployee (FirstName, LastName, Email, PhoneNumber, Position, Role,
                                                         PasswordHash, IsActive, HireDate)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, CURDATE())
                               """,
                               (data['first_name'], data['last_name'], data['email'], data['phone'], data['position'],
                                data['role'], password_hash))
                conn.commit()
                QMessageBox.information(self, "Успех", f"Сотрудник добавлен!\nВременный пароль: {temp_password}")
            else:
                # Обновление
                updates = []
                params = []
                updates.append("FirstName = %s")
                params.append(data['first_name'])
                updates.append("LastName = %s")
                params.append(data['last_name'])
                updates.append("Email = %s")
                params.append(data['email'])
                updates.append("PhoneNumber = %s")
                params.append(data['phone'])
                updates.append("Position = %s")
                params.append(data['position'])
                updates.append("Role = %s")
                params.append(data['role'])

                new_pass = self.new_password_edit.text().strip()
                if new_pass:
                    if new_pass != self.confirm_password_edit.text().strip():
                        QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
                        return
                    password_hash = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    updates.append("PasswordHash = %s")
                    params.append(password_hash)

                params.append(self.user_id)
                query = f"UPDATE ListEmployee SET {', '.join(updates)} WHERE EmployeeID = %s"
                cursor.execute(query, params)
                conn.commit()
                QMessageBox.information(self, "Успех", "Данные сотрудника обновлены")

            cursor.close()
            conn.close()
            self.accept()
        except Exception as e:
            print(f"Ошибка сохранения сотрудника: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    win = UnifiedUserManagementDialog()
    win.show()
    sys.exit(app.exec_())