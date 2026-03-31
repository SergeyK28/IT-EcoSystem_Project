# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox, \
    QGraphicsDropShadowEffect, QSizeGrip
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Handlers.Employees.employee_session import employee_session
from Server import db_crm


class EmployeeProfileDialog(QDialog):
    """Упрощенное окно профиля сотрудника"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragging = False
        self.resizing = False
        self.drag_position = None
        self.resize_direction = None
        self.resize_margin = 10

        self.setup_ui()
        self.load_employee_data()

    def setup_ui(self):
        self.setObjectName("EmployeeProfileDialog")
        self.setWindowTitle("Профиль сотрудника")
        self.setMinimumSize(450, 550)
        self.resize(500, 600)

        # Основной стиль - более минималистичный
        self.setStyleSheet("""
            QDialog {
                background-color: transparent;
            }
            QLabel {
                color: #ffffff;
                background: transparent;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                min-height: 25px;
            }
            QPushButton#closeBtn {
                background-color: #5a5a5a;
                color: white;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                font-size: 14px;
                padding: 0px;
                border-radius: 15px;
            }
            QPushButton#closeBtn:hover {
                background-color: #777777;
            }
            QPushButton#logoutBtn {
                background-color: #dc3545;
                color: white;
            }
            QPushButton#logoutBtn:hover {
                background-color: #c82333;
            }
            QFrame#mainContainer {
                background-color: #2d2d2d;
                border-radius: 15px;
                border: 1px solid #404040;
            }
            QFrame#infoFrame {
                background-color: #353535;
                border-radius: 10px;
                padding: 5px;
            }
            QFrame#statCard {
                background-color: #353535;
                border-radius: 8px;
                padding: 5px;
            }
            QSizeGrip {
                background-color: transparent;
                width: 15px;
                height: 15px;
            }
        """)

        # Настройки окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        self.main_container = QFrame(self)
        self.main_container.setObjectName("mainContainer")
        self.main_container.setGeometry(0, 0, self.width(), self.height())

        # Легкая тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.main_container.setGraphicsEffect(shadow)

        # SizeGrip для изменения размера
        self.size_grip = QSizeGrip(self.main_container)
        self.size_grip.setStyleSheet("""
            QSizeGrip {
                background-color: #4a4a4a;
                border-radius: 7px;
                width: 15px;
                height: 15px;
            }
            QSizeGrip:hover {
                background-color: #5a5a5a;
            }
        """)

        # Основной layout
        layout = QVBoxLayout(self.main_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок с кнопкой закрытия
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("ПРОФИЛЬ")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #4CAF50;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Аватар с инициалами
        avatar_layout = QHBoxLayout()
        avatar_layout.setContentsMargins(0, 5, 0, 5)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
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
        self.name_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-top: 5px;
        """)
        layout.addWidget(self.name_label)

        # Должность
        self.position_label = QLabel()
        self.position_label.setAlignment(Qt.AlignCenter)
        self.position_label.setStyleSheet("""
            font-size: 12px;
            color: #4CAF50;
            background-color: #353535;
            padding: 5px 15px;
            border-radius: 15px;
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

        # Статистика - компактная
        stats_title = QLabel("СТАТИСТИКА")
        stats_title.setAlignment(Qt.AlignCenter)
        stats_title.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #4CAF50;
            margin-top: 5px;
        """)
        layout.addWidget(stats_title)

        # Карточки статистики в ряд
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
        layout.addWidget(self.logout_btn)
        self.logout_btn.clicked.connect(self.logout)

        # Позиционируем SizeGrip
        self.size_grip.move(self.main_container.width() - 25, self.main_container.height() - 25)

    def resizeEvent(self, event):
        """Обновление позиции SizeGrip при изменении размера"""
        super().resizeEvent(event)
        self.main_container.resize(self.width(), self.height())
        self.size_grip.move(self.main_container.width() - 25, self.main_container.height() - 25)

    def create_stat_card(self, icon, value):
        """Упрощенная карточка статистики"""
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
        stat_value_label.setStyleSheet("""
            color: #4CAF50;
            font-size: 16px;
            font-weight: bold;
            background: none;
        """)

        layout.addWidget(icon_label)
        layout.addWidget(stat_value_label)

        card.stat_label = stat_value_label
        return card

    def load_employee_data(self):
        """Загрузка данных сотрудника"""
        if not employee_session.is_authenticated():
            return

        name = employee_session.get_employee_name()
        email = employee_session.get_employee_email()
        position = employee_session.get_employee_position()
        role = employee_session.get_employee_role()
        employee_id = employee_session.get_employee_id()

        self.name_label.setText(name if name else "Сотрудник")
        self.email_label.setText(email if email else "Email не указан")
        self.position_label.setText(position if position else "Сотрудник")

        # Упрощенное отображение роли
        role_text = {
            'admin': 'Админ',
            'manager': 'Менеджер',
            'tech': 'Техник'
        }.get(role, 'Сотрудник')

        self.role_label.setText(f"Роль: {role_text}")
        self.id_label.setText(f"ID: {employee_id}")

        # Инициалы для аватара
        if name:
            parts = name.split()
            initials = parts[0][0] + (parts[1][0] if len(parts) > 1 else '')
            self.avatar_label.setText(initials.upper())
        else:
            self.avatar_label.setText("👤")

        # Загрузка статистики
        self.load_employee_statistics(employee_id)

    def load_employee_statistics(self, employee_id):
        """Загрузка статистики сотрудника"""
        try:
            connection = db_crm.get_crm_connection()
            if not connection:
                return

            cursor = connection.cursor(dictionary=True)

            # Общее количество заказов
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM Orders 
                WHERE ManagerID = %s OR ExecutorID = %s
            """, (employee_id, employee_id))
            total_orders = cursor.fetchone()['total']

            # Активные заказы
            cursor.execute("""
                SELECT COUNT(*) as active 
                FROM Orders 
                WHERE (ManagerID = %s OR ExecutorID = %s)
                AND Status NOT IN ('Завершен', 'Готовое', 'Отменен')
            """, (employee_id, employee_id))
            active_orders = cursor.fetchone()['active']

            # Завершенные заказы
            cursor.execute("""
                SELECT COUNT(*) as completed 
                FROM Orders 
                WHERE (ManagerID = %s OR ExecutorID = %s)
                AND Status IN ('Завершен', 'Готовое')
            """, (employee_id, employee_id))
            completed_orders = cursor.fetchone()['completed']

            cursor.close()
            connection.close()

            # Обновление карточек
            self.update_stat_cards(total_orders, active_orders, completed_orders)

        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")

    def update_stat_cards(self, total, active, completed):
        """Обновление карточек статистики"""
        if hasattr(self.orders_card, 'stat_label'):
            self.orders_card.stat_label.setText(str(total))
        if hasattr(self.active_card, 'stat_label'):
            self.active_card.stat_label.setText(str(active))
        if hasattr(self.completed_card, 'stat_label'):
            self.completed_card.stat_label.setText(str(completed))

    def logout(self):
        """Выход из аккаунта"""
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

            # Открытие окна входа
            from Handlers.Employees.employee_login import EmployeeLoginDialog
            login_dialog = EmployeeLoginDialog()
            if login_dialog.exec_() == QDialog.Accepted:
                from Handlers.main_CRM import MainCRMWindow
                crm_window = MainCRMWindow()
                crm_window.show()

    # Методы для перетаскивания и изменения размера
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            margin = self.resize_margin

            # Определение направления изменения размера
            on_left = pos.x() <= margin
            on_right = pos.x() >= self.width() - margin
            on_top = pos.y() <= margin
            on_bottom = pos.y() >= self.height() - margin

            if on_left and on_top:
                self.resize_direction = 'topleft'
                self.resizing = True
            elif on_right and on_top:
                self.resize_direction = 'topright'
                self.resizing = True
            elif on_left and on_bottom:
                self.resize_direction = 'bottomleft'
                self.resizing = True
            elif on_right and on_bottom:
                self.resize_direction = 'bottomright'
                self.resizing = True
            elif on_left:
                self.resize_direction = 'left'
                self.resizing = True
            elif on_right:
                self.resize_direction = 'right'
                self.resizing = True
            elif on_top:
                self.resize_direction = 'top'
                self.resizing = True
            elif on_bottom:
                self.resize_direction = 'bottom'
                self.resizing = True
            else:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                self.resizing = False

            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.resizing and self.resize_direction:
                self.resize_window(event.globalPos())
            elif self.dragging:
                self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            self.update_cursor_shape(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_direction = None
            event.accept()

    def resize_window(self, global_pos):
        if not self.resize_direction:
            return

        rect = self.geometry()

        if 'right' in self.resize_direction:
            rect.setWidth(max(self.minimumWidth(), global_pos.x() - rect.x()))
        if 'left' in self.resize_direction:
            new_left = global_pos.x()
            if rect.right() - new_left >= self.minimumWidth():
                rect.setLeft(new_left)
        if 'bottom' in self.resize_direction:
            rect.setHeight(max(self.minimumHeight(), global_pos.y() - rect.y()))
        if 'top' in self.resize_direction:
            new_top = global_pos.y()
            if rect.bottom() - new_top >= self.minimumHeight():
                rect.setTop(new_top)

        self.setGeometry(rect)

    def update_cursor_shape(self, pos):
        margin = self.resize_margin
        on_left = pos.x() <= margin
        on_right = pos.x() >= self.width() - margin
        on_top = pos.y() <= margin
        on_bottom = pos.y() >= self.height() - margin

        if (on_left and on_top) or (on_right and on_bottom):
            cursor = Qt.SizeFDiagCursor
        elif (on_left and on_bottom) or (on_right and on_top):
            cursor = Qt.SizeBDiagCursor
        elif on_left or on_right:
            cursor = Qt.SizeHorCursor
        elif on_top or on_bottom:
            cursor = Qt.SizeVerCursor
        else:
            cursor = Qt.ArrowCursor

        self.setCursor(cursor)