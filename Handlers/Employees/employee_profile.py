# -*- coding: utf-8 -*-
"""
Модуль окна профиля сотрудника CRM (упрощённый дизайн).
Использует методы employee_session напрямую.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Handlers.Employees.employee_session import employee_session
from Server import db_crm


class EmployeeProfileDialog(QDialog):
    """
    Упрощённое окно профиля сотрудника со стандартным заголовком.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_employee_data()

    def setup_ui(self):
        """Настройка интерфейса окна профиля."""
        self.setObjectName("EmployeeProfileDialog")
        self.setWindowTitle("Профиль сотрудника")
        self.setMinimumSize(450, 550)
        self.resize(500, 600)

        # Простой тёмный стиль (без излишеств)
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
                background: transparent;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#logoutBtn {
                background-color: #b33c3c;
                border: none;
            }
            QPushButton#logoutBtn:hover {
                background-color: #cc4c4c;
            }
            QFrame#infoFrame {
                background-color: #3a3a3a;
                border-radius: 3px;
                padding: 5px;
            }
            QFrame#statCard {
                background-color: #3a3a3a;
                border-radius: 3px;
                padding: 5px;
            }
        """)

        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок (без кнопки закрытия)
        title_label = QLabel("ПРОФИЛЬ")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d7d3a;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Аватар с инициалами
        avatar_layout = QHBoxLayout()
        avatar_layout.setContentsMargins(0, 5, 0, 5)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                background-color: #2d7d3a;
                border-radius: 40px;
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        avatar_layout.addStretch()
        avatar_layout.addWidget(self.avatar_label)
        avatar_layout.addStretch()
        layout.addLayout(avatar_layout)

        # Имя сотрудника
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 5px;")
        layout.addWidget(self.name_label)

        # Должность
        self.position_label = QLabel()
        self.position_label.setAlignment(Qt.AlignCenter)
        self.position_label.setStyleSheet("""
            font-size: 12px;
            color: #2d7d3a;
            background-color: #3a3a3a;
            padding: 4px 12px;
            border-radius: 12px;
            max-width: 200px;
            margin: 0 auto;
        """)
        layout.addWidget(self.position_label)

        layout.addSpacing(10)

        # Информационная карточка
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(15, 15, 15, 15)

        # Email
        email_layout = QHBoxLayout()
        email_icon = QLabel("📧")
        email_icon.setStyleSheet("font-size: 14px;")
        self.email_label = QLabel()
        self.email_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        email_layout.addWidget(email_icon)
        email_layout.addWidget(self.email_label)
        email_layout.addStretch()
        info_layout.addLayout(email_layout)

        # Роль
        role_layout = QHBoxLayout()
        role_icon = QLabel("🔑")
        role_icon.setStyleSheet("font-size: 14px;")
        self.role_label = QLabel()
        self.role_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        role_layout.addWidget(role_icon)
        role_layout.addWidget(self.role_label)
        role_layout.addStretch()
        info_layout.addLayout(role_layout)

        # ID сотрудника
        id_layout = QHBoxLayout()
        id_icon = QLabel("🆔")
        id_icon.setStyleSheet("font-size: 14px;")
        self.id_label = QLabel()
        self.id_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        id_layout.addWidget(id_icon)
        id_layout.addWidget(self.id_label)
        id_layout.addStretch()
        info_layout.addLayout(id_layout)

        layout.addWidget(info_frame)

        # Статистика
        stats_title = QLabel("СТАТИСТИКА")
        stats_title.setAlignment(Qt.AlignCenter)
        stats_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2d7d3a; margin-top: 5px;")
        layout.addWidget(stats_title)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)

        self.orders_card = self.create_stat_card("📦", "0")
        stats_layout.addWidget(self.orders_card)

        self.active_card = self.create_stat_card("⚡", "0")
        stats_layout.addWidget(self.active_card)

        self.completed_card = self.create_stat_card("✅", "0")
        stats_layout.addWidget(self.completed_card)

        layout.addLayout(stats_layout)

        layout.addStretch()

        # Кнопка выхода
        self.logout_btn = QPushButton("🚪 Выйти")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setMinimumHeight(35)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout)
        layout.addWidget(self.logout_btn)

    def create_stat_card(self, icon, value):
        """Создаёт упрощённую карточку статистики."""
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumSize(100, 60)

        layout = QVBoxLayout(card)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 8, 5, 8)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 18px; background: none;")

        stat_value_label = QLabel(value)
        stat_value_label.setAlignment(Qt.AlignCenter)
        stat_value_label.setStyleSheet("color: #2d7d3a; font-size: 16px; font-weight: bold; background: none;")

        layout.addWidget(icon_label)
        layout.addWidget(stat_value_label)

        card.stat_label = stat_value_label
        return card

    def load_employee_data(self):
        """Загружает данные сотрудника из сессии."""
        if not employee_session.is_authenticated():
            return

        data = employee_session.get_employee_data()
        if not data:
            return

        first_name = data.get('FirstName', '')
        last_name = data.get('LastName', '')
        full_name = f"{first_name} {last_name}".strip()
        email = data.get('Email', '')
        position = data.get('Position', 'Сотрудник')
        role = data.get('Role', 'technician')
        employee_id = data.get('EmployeeID')

        self.name_label.setText(full_name if full_name else "Сотрудник")
        self.email_label.setText(email if email else "Email не указан")
        self.position_label.setText(position)

        role_text = {
            'admin': 'Администратор',
            'manager': 'Менеджер',
            'technician': 'Техник',
            'consultant': 'Консультант'
        }.get(role, 'Сотрудник')
        self.role_label.setText(f"Роль: {role_text}")
        self.id_label.setText(f"ID: {employee_id}")

        if full_name:
            parts = full_name.split()
            if len(parts) >= 2:
                initials = parts[0][0] + parts[1][0]
            else:
                initials = parts[0][0]
            self.avatar_label.setText(initials.upper())
        else:
            self.avatar_label.setText("👤")

        if employee_id:
            self.load_employee_statistics(employee_id)

    def load_employee_statistics(self, employee_id):
        """Загружает статистику сотрудника из БД."""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM Orders 
                WHERE ManagerID = %s OR ExecutorID = %s
            """, (employee_id, employee_id))
            total_orders = cursor.fetchone()['total']

            cursor.execute("""
                SELECT COUNT(*) as active 
                FROM Orders 
                WHERE (ManagerID = %s OR ExecutorID = %s)
                AND Status NOT IN ('Завершен', 'Готовое', 'Отменен')
            """, (employee_id, employee_id))
            active_orders = cursor.fetchone()['active']

            cursor.execute("""
                SELECT COUNT(*) as completed 
                FROM Orders 
                WHERE (ManagerID = %s OR ExecutorID = %s)
                AND Status IN ('Завершен', 'Готовое')
            """, (employee_id, employee_id))
            completed_orders = cursor.fetchone()['completed']

            cursor.close()
            connection.close()

            self.update_stat_cards(total_orders, active_orders, completed_orders)

        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")

    def update_stat_cards(self, total, active, completed):
        """Обновление карточек статистики."""
        if hasattr(self.orders_card, 'stat_label'):
            self.orders_card.stat_label.setText(str(total))
        if hasattr(self.active_card, 'stat_label'):
            self.active_card.stat_label.setText(str(active))
        if hasattr(self.completed_card, 'stat_label'):
            self.completed_card.stat_label.setText(str(completed))

    def logout(self):
        """Выход из аккаунта."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Выйти из CRM?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            employee_session.logout()
            self.close()
            from Handlers.Employees.employee_login import EmployeeLoginDialog
            login_dialog = EmployeeLoginDialog()
            if login_dialog.exec_() == QDialog.Accepted:
                from Handlers.main_CRM import MainCRMWindow
                crm_window = MainCRMWindow()
                crm_window.show()