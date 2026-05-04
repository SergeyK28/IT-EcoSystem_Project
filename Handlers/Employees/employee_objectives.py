# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
                             QGraphicsDropShadowEffect, QScrollArea, QWidget, QTextEdit, QDateEdit, QComboBox,
                             QCheckBox, QLineEdit, QGridLayout)  # Добавлен QGridLayout
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Handlers.Employees.employee_session import employee_session
from Server import db_crm, db_objectives


class ObjectivesDialog(QDialog):
    """Окно задач сотрудника"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_objective_id = None
        self.setup_ui()
        self.load_objectives()

    def setup_ui(self):
        self.setObjectName("ObjectivesDialog")
        self.setWindowTitle("IT-EcoSystem CRM - Задачи")
        self.setFixedSize(1000, 700)

        # Основной стиль
        self.setStyleSheet("""
            QDialog {
                background-color: rgb(47, 47, 47);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
                min-height: 25px;
            }
            QPushButton#closeBtn {
                background-color: rgb(119, 118, 123);
                color: rgb(255, 255, 255);
                min-width: 35px;
                max-width: 35px;
                min-height: 35px;
                max-height: 35px;
                font-size: 16px;
                padding: 0px;
            }
            QPushButton#closeBtn:hover {
                background-color: rgb(139, 138, 143);
            }
            QPushButton#addBtn {
                background-color: rgb(40, 167, 69);
                color: white;
                font-size: 12pt;
                padding: 10px;
            }
            QPushButton#addBtn:hover {
                background-color: rgb(50, 187, 79);
            }
            QTabWidget::pane {
                border: 1px solid rgb(103, 155, 118);
                background-color: rgb(30, 30, 30);
            }
            QTabBar::tab {
                background-color: rgb(45, 45, 45);
                color: rgb(255, 255, 255);
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: rgb(103, 155, 118);
                color: white;
            }
            QTabBar::tab:hover {
                background-color: rgb(60, 60, 60);
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#taskCard {
                background-color: rgb(40, 40, 40);
                border-radius: 8px;
                border-left: 4px solid rgb(103, 155, 118);
            }
            QWidget#taskCard:hover {
                background-color: rgb(50, 50, 50);
            }
            QCheckBox {
                color: rgb(255, 255, 255);
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid rgb(103, 155, 118);
                background-color: rgb(40, 40, 40);
            }
            QCheckBox::indicator:checked {
                background-color: rgb(103, 155, 118);
                border: 2px solid rgb(103, 155, 118);
                image: url(check.png);
            }
            QLineEdit, QTextEdit, QDateEdit, QComboBox, QSpinBox {
                background-color: rgb(45, 45, 45);
                color: rgb(255, 255, 255);
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 3px;
            }
        """)

        # Убираем стандартные рамки окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 1000, 700)
        main_container.setStyleSheet("""
            QFrame {
                background-color: rgb(47, 47, 47);
                border-radius: 15px;
                border: 2px solid rgb(103, 155, 118);
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(shadow)

        # Основной layout
        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Верхняя панель
        header_layout = QHBoxLayout()

        title_label = QLabel("📋 ЗАДАЧИ")
        title_label.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: rgb(103, 155, 118);
            padding: 5px;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Кнопка добавления задачи
        self.add_btn = QPushButton("➕ Новая задача")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.show_add_objective_dialog)
        header_layout.addWidget(self.add_btn)

        # Кнопка закрытия
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Табы для активных и завершенных задач
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::tab-bar {
                alignment: center;
            }
        """)

        # Вкладка активных задач
        self.active_tab = QWidget()
        self.setup_active_tab()
        self.tab_widget.addTab(self.active_tab, "Активные")

        # Вкладка завершенных задач
        self.completed_tab = QWidget()
        self.setup_completed_tab()
        self.tab_widget.addTab(self.completed_tab, "Завершено")

        layout.addWidget(self.tab_widget)

    def setup_active_tab(self):
        """Настраивает вкладку активных задач"""
        layout = QVBoxLayout(self.active_tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Фильтры
        filters_layout = QHBoxLayout()

        filters_layout.addWidget(QLabel("Фильтр:"))

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все задачи", "Мои задачи", "Назначенные мне", "По заказам", "Просроченные"])
        self.filter_combo.currentTextChanged.connect(self.load_objectives)
        filters_layout.addWidget(self.filter_combo)

        filters_layout.addStretch()

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск задач...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self.load_objectives)
        filters_layout.addWidget(self.search_input)

        layout.addLayout(filters_layout)

        # Область прокрутки для задач
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.active_tasks_widget = QWidget()
        self.active_tasks_layout = QVBoxLayout(self.active_tasks_widget)
        self.active_tasks_layout.setSpacing(10)
        self.active_tasks_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.active_tasks_widget)
        layout.addWidget(scroll_area)

    def setup_completed_tab(self):
        """Настраивает вкладку завершенных задач"""
        layout = QVBoxLayout(self.completed_tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Область прокрутки для завершенных задач
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.completed_tasks_widget = QWidget()
        self.completed_tasks_layout = QVBoxLayout(self.completed_tasks_widget)
        self.completed_tasks_layout.setSpacing(10)
        self.completed_tasks_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.completed_tasks_widget)
        layout.addWidget(scroll_area)

    def create_task_card(self, task_data, is_completed=False):
        """Создает карточку задачи"""
        card = QWidget()
        card.setObjectName("taskCard")
        card.setFixedHeight(120)
        card.setCursor(Qt.PointingHandCursor)

        # Сохраняем ID задачи
        card.task_id = task_data.get('ObjectiveID')
        card.task_data = task_data

        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)

        # Чекбокс выполнения
        checkbox = QCheckBox()
        checkbox.setChecked(is_completed)
        checkbox.stateChanged.connect(lambda state, t=card.task_id: self.toggle_task_completion(t, state == Qt.Checked))
        layout.addWidget(checkbox)

        # Основной контент
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)

        # Заголовок и приоритет
        title_layout = QHBoxLayout()

        title_label = QLabel(task_data.get('Title', 'Без названия'))
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: rgb(255, 255, 255);
        """)
        title_layout.addWidget(title_label)

        # Приоритет
        priority = task_data.get('Priority', 'medium')
        priority_colors = {
            'low': 'rgb(108, 117, 125)',
            'medium': 'rgb(255, 193, 7)',
            'high': 'rgb(220, 53, 69)',
            'critical': 'rgb(153, 0, 0)'
        }
        priority_texts = {
            'low': 'Низкий',
            'medium': 'Средний',
            'high': 'Высокий',
            'critical': 'Критичный'
        }

        priority_label = QLabel(priority_texts.get(priority, 'Средний'))
        priority_label.setStyleSheet(f"""
            background-color: {priority_colors.get(priority, 'rgb(108, 117, 125)')};
            color: white;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        title_layout.addWidget(priority_label)

        title_layout.addStretch()

        # Срок
        due_date = task_data.get('DueDate')
        if due_date:
            if isinstance(due_date, str):
                try:
                    due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                except:
                    due_date = None

            if due_date:
                due_text = f"📅 {due_date.strftime('%d.%m.%Y %H:%M')}"
                due_label = QLabel(due_text)
                due_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 11px;")

                # Проверка просрочки
                if not is_completed and due_date < datetime.now():
                    due_label.setStyleSheet("color: rgb(255, 100, 100); font-size: 11px; font-weight: bold;")
                    due_label.setText(f"⚠️ ПРОСРОЧЕНО! {due_text}")

                title_layout.addWidget(due_label)

        content_layout.addLayout(title_layout)

        # Описание (обрезанное)
        description = task_data.get('Description', '')
        if description:
            if len(description) > 100:
                description = description[:100] + "..."
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: rgb(200, 200, 200); font-size: 11px;")
            desc_label.setWordWrap(True)
            content_layout.addWidget(desc_label)

        # Нижняя строка с информацией
        info_layout = QHBoxLayout()

        # Автор
        created_by = task_data.get('CreatedByName', 'Система')
        info_layout.addWidget(QLabel(f"👤 {created_by}"))

        # Назначено
        assigned_to = task_data.get('AssignedToName', 'Все')
        info_layout.addWidget(QLabel(f"➡️ {assigned_to}"))

        # Связанный заказ
        order_info = task_data.get('OrderInfo', '')
        if order_info:
            info_layout.addWidget(QLabel(f"📦 {order_info}"))

        info_layout.addStretch()

        content_layout.addLayout(info_layout)

        layout.addLayout(content_layout)

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(220, 53, 69);
                color: white;
                border-radius: 15px;
                font-size: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgb(240, 73, 89);
            }
        """)
        delete_btn.clicked.connect(lambda checked, t=card.task_id: self.delete_task(t))
        layout.addWidget(delete_btn)

        # Клик по карточке открывает заметки
        card.mousePressEvent = lambda event, t=task_data: self.open_task_notes(t)

        return card

    def load_objectives(self):
        """Загружает задачи из БД"""
        try:
            filter_type = self.filter_combo.currentText()
            search_text = self.search_input.text().strip()

            # Получаем задачи
            active_tasks = db_objectives.get_objectives(
                status='active',
                filter_type=filter_type,
                search=search_text,
                employee_id=employee_session.get_employee_id()
            )

            completed_tasks = db_objectives.get_objectives(
                status='completed',
                filter_type=filter_type,
                search=search_text,
                employee_id=employee_session.get_employee_id()
            )

            # Очищаем и заполняем активные задачи
            self.clear_layout(self.active_tasks_layout)
            for task in active_tasks:
                card = self.create_task_card(task, is_completed=False)
                self.active_tasks_layout.addWidget(card)

            if not active_tasks:
                no_tasks_label = QLabel("✨ Нет активных задач")
                no_tasks_label.setAlignment(Qt.AlignCenter)
                no_tasks_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 14px; padding: 50px;")
                self.active_tasks_layout.addWidget(no_tasks_label)

            self.active_tasks_layout.addStretch()

            # Очищаем и заполняем завершенные задачи
            self.clear_layout(self.completed_tasks_layout)
            for task in completed_tasks:
                card = self.create_task_card(task, is_completed=True)
                self.completed_tasks_layout.addWidget(card)

            if not completed_tasks:
                no_tasks_label = QLabel("📌 Нет завершенных задач")
                no_tasks_label.setAlignment(Qt.AlignCenter)
                no_tasks_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 14px; padding: 50px;")
                self.completed_tasks_layout.addWidget(no_tasks_label)

            self.completed_tasks_layout.addStretch()

        except Exception as e:
            print(f"Ошибка загрузки задач: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить задачи: {e}")

    def clear_layout(self, layout):
        """Очищает layout от всех виджетов"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def toggle_task_completion(self, task_id, completed):
        """Переключает статус выполнения задачи"""
        try:
            if completed:
                # Отмечаем как выполненную
                db_objectives.update_objective_status(task_id, 'completed')
            else:
                # Возвращаем в активные
                db_objectives.update_objective_status(task_id, 'active')

            # Перезагружаем задачи
            self.load_objectives()

        except Exception as e:
            print(f"Ошибка изменения статуса задачи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус задачи: {e}")

    def delete_task(self, task_id):
        """Удаляет задачу"""
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы действительно хотите удалить эту задачу?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                db_objectives.delete_objective(task_id)
                self.load_objectives()
            except Exception as e:
                print(f"Ошибка удаления задачи: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить задачу: {e}")

    def open_task_notes(self, task_data):
        """Открывает окно с заметками к задаче"""
        dialog = TaskNotesDialog(task_data, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_objectives()  # Перезагружаем задачи после изменений

    def show_add_objective_dialog(self):
        """Показывает диалог добавления новой задачи"""
        dialog = AddObjectiveDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_objectives()

    def mousePressEvent(self, event):
        """Для перетаскивания окна"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Для перетаскивания окна"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class TaskNotesDialog(QDialog):
    """Окно заметок к задаче"""

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.task_id = task_data.get('ObjectiveID')
        self.setup_ui()
        self.load_comments()

    def setup_ui(self):
        self.setObjectName("TaskNotesDialog")
        self.setWindowTitle("Заметки к задаче")
        self.setFixedSize(600, 700)

        self.setStyleSheet("""
            QDialog {
                background-color: rgb(47, 47, 47);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#closeBtn {
                background-color: rgb(119, 118, 123);
                color: white;
                min-width: 35px;
                max-width: 35px;
                min-height: 35px;
                max-height: 35px;
                font-size: 16px;
            }
            QPushButton#saveBtn {
                background-color: rgb(40, 167, 69);
                color: white;
            }
            QTextEdit, QLineEdit, QDateEdit {
                background-color: rgb(45, 45, 45);
                color: white;
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 3px;
            }
            QFrame#commentFrame {
                background-color: rgb(40, 40, 40);
                border-radius: 5px;
                border-left: 3px solid rgb(103, 155, 118);
            }
        """)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 600, 700)
        main_container.setStyleSheet("""
            QFrame {
                background-color: rgb(47, 47, 47);
                border-radius: 15px;
                border: 2px solid rgb(103, 155, 118);
            }
        """)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        header_layout = QHBoxLayout()

        title_label = QLabel(f"📝 {self.task_data.get('Title', 'Задача')}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: rgb(103, 155, 118);")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.clicked.connect(self.reject)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Информация о задаче
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: rgb(35, 35, 35); border-radius: 5px;")
        info_layout = QGridLayout(info_frame)  # Здесь используется QGridLayout
        info_layout.setHorizontalSpacing(15)
        info_layout.setVerticalSpacing(10)

        # Статус
        status_text = '✅ Выполнено' if self.task_data.get('Status') == 'completed' else '🔄 Активно'
        info_layout.addWidget(QLabel(f"Статус:"), 0, 0)
        info_layout.addWidget(QLabel(status_text), 0, 1)

        # Приоритет
        priority = self.task_data.get('Priority', 'medium')
        priority_texts = {'low': 'Низкий', 'medium': 'Средний', 'high': 'Высокий', 'critical': 'Критичный'}
        info_layout.addWidget(QLabel(f"Приоритет:"), 0, 2)
        info_layout.addWidget(QLabel(priority_texts.get(priority, 'Средний')), 0, 3)

        # Срок
        due_date = self.task_data.get('DueDate')
        if due_date:
            if isinstance(due_date, str):
                try:
                    due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                except:
                    due_date = None

            if due_date:
                due_str = due_date.strftime('%d.%m.%Y %H:%M')
                info_layout.addWidget(QLabel(f"Срок:"), 1, 0)
                info_layout.addWidget(QLabel(due_str), 1, 1)

        # Автор
        created_by = self.task_data.get('CreatedByName', 'Система')
        info_layout.addWidget(QLabel(f"Автор:"), 1, 2)
        info_layout.addWidget(QLabel(created_by), 1, 3)

        # Назначено
        assigned_to = self.task_data.get('AssignedToName', 'Все')
        info_layout.addWidget(QLabel(f"Назначено:"), 2, 0)
        info_layout.addWidget(QLabel(assigned_to), 2, 1, 1, 3)

        layout.addWidget(info_frame)

        # Редактирование описания
        desc_label = QLabel("Описание задачи:")
        desc_label.setStyleSheet("font-weight: bold; color: rgb(180, 180, 180); margin-top: 10px;")
        layout.addWidget(desc_label)

        self.description_edit = QTextEdit()
        self.description_edit.setText(self.task_data.get('Description', ''))
        self.description_edit.setMaximumHeight(150)
        layout.addWidget(self.description_edit)

        # Чеклист (если есть)
        checklist = self.task_data.get('Checklist', [])
        if checklist:
            checklist_label = QLabel("Чек-лист:")
            checklist_label.setStyleSheet("font-weight: bold; color: rgb(180, 180, 180); margin-top: 10px;")
            layout.addWidget(checklist_label)

            self.checklist_widget = QWidget()
            checklist_layout = QVBoxLayout(self.checklist_widget)
            checklist_layout.setSpacing(5)

            for item in checklist:
                item_check = QCheckBox(item.get('ItemText', ''))
                item_check.setChecked(item.get('IsCompleted', False))
                checklist_layout.addWidget(item_check)

            layout.addWidget(self.checklist_widget)

        # Комментарии
        comments_label = QLabel("Комментарии:")
        comments_label.setStyleSheet("font-weight: bold; color: rgb(180, 180, 180); margin-top: 10px;")
        layout.addWidget(comments_label)

        # Область комментариев
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_area.setMaximumHeight(200)

        self.comments_widget = QWidget()
        self.comments_layout = QVBoxLayout(self.comments_widget)
        self.comments_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.comments_widget)
        layout.addWidget(scroll_area)

        # Добавление комментария
        comment_input_layout = QHBoxLayout()

        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Введите комментарий...")
        comment_input_layout.addWidget(self.comment_input)

        add_comment_btn = QPushButton("➕")
        add_comment_btn.setFixedSize(40, 40)
        add_comment_btn.setStyleSheet("background-color: rgb(40, 167, 69);")
        add_comment_btn.clicked.connect(self.add_comment)
        comment_input_layout.addWidget(add_comment_btn)

        layout.addLayout(comment_input_layout)

        # Кнопки сохранения
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Сохранить изменения")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.save_changes)
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setStyleSheet("background-color: rgb(108, 117, 125); color: white;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def load_comments(self):
        """Загружает комментарии к задаче"""
        try:
            comments = db_objectives.get_objective_comments(self.task_id)

            self.clear_layout(self.comments_layout)

            for comment in comments:
                comment_frame = QFrame()
                comment_frame.setObjectName("commentFrame")
                comment_layout = QVBoxLayout(comment_frame)

                # Верхняя строка с автором и датой
                header_layout = QHBoxLayout()

                author = comment.get('EmployeeName', 'Система')
                author_label = QLabel(f"👤 {author}")
                author_label.setStyleSheet("font-weight: bold; color: rgb(103, 155, 118);")
                header_layout.addWidget(author_label)

                date = comment.get('CommentDate', '')
                if date:
                    if isinstance(date, str):
                        try:
                            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                        except:
                            date = None

                    if date:
                        date_str = date.strftime('%d.%m.%Y %H:%M')
                        date_label = QLabel(date_str)
                        date_label.setStyleSheet("color: rgb(150, 150, 150); font-size: 10px;")
                        header_layout.addWidget(date_label)

                header_layout.addStretch()
                comment_layout.addLayout(header_layout)

                # Текст комментария
                text_label = QLabel(comment.get('CommentText', ''))
                text_label.setWordWrap(True)
                comment_layout.addWidget(text_label)

                self.comments_layout.addWidget(comment_frame)

            if not comments:
                no_comments = QLabel("💬 Нет комментариев")
                no_comments.setAlignment(Qt.AlignCenter)
                no_comments.setStyleSheet("color: rgb(150, 150, 150); padding: 20px;")
                self.comments_layout.addWidget(no_comments)

        except Exception as e:
            print(f"Ошибка загрузки комментариев: {e}")

    def add_comment(self):
        """Добавляет новый комментарий"""
        comment_text = self.comment_input.text().strip()
        if not comment_text:
            return

        try:
            db_objectives.add_objective_comment(
                self.task_id,
                employee_session.get_employee_id(),
                comment_text
            )
            self.comment_input.clear()
            self.load_comments()
        except Exception as e:
            print(f"Ошибка добавления комментария: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить комментарий: {e}")

    def save_changes(self):
        """Сохраняет изменения в задаче"""
        try:
            # Обновляем описание
            new_description = self.description_edit.toPlainText()
            db_objectives.update_objective_description(self.task_id, new_description)

            self.accept()
        except Exception as e:
            print(f"Ошибка сохранения изменений: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {e}")

    def clear_layout(self, layout):
        """Очищает layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class AddObjectiveDialog(QDialog):
    """Диалог добавления новой задачи"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_employees()
        self.load_orders()

    def setup_ui(self):
        self.setObjectName("AddObjectiveDialog")
        self.setWindowTitle("Новая задача")
        self.setFixedSize(500, 600)

        self.setStyleSheet("""
            QDialog {
                background-color: rgb(47, 47, 47);
            }
            QLabel {
                color: rgb(255, 255, 255);
            }
            QPushButton {
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#createBtn {
                background-color: rgb(40, 167, 69);
                color: white;
            }
            QPushButton#cancelBtn {
                background-color: rgb(108, 117, 125);
                color: white;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: rgb(45, 45, 45);
                color: white;
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 3px;
            }
        """)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 500, 600)
        main_container.setStyleSheet("""
            QFrame {
                background-color: rgb(47, 47, 47);
                border-radius: 15px;
                border: 2px solid rgb(103, 155, 118);
            }
        """)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        header_layout = QHBoxLayout()

        title_label = QLabel("➕ НОВАЯ ЗАДАЧА")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: rgb(103, 155, 118);")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(119, 118, 123);
                color: white;
                min-width: 35px;
                max-width: 35px;
                min-height: 35px;
                max-height: 35px;
                font-size: 16px;
                border-radius: 4px;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        header_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)

        # Название задачи
        layout.addWidget(QLabel("Название задачи:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название задачи")
        layout.addWidget(self.title_input)

        # Описание
        layout.addWidget(QLabel("Описание:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Подробное описание задачи...")
        layout.addWidget(self.description_input)

        # Приоритет
        layout.addWidget(QLabel("Приоритет:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкий", "Средний", "Высокий", "Критичный"])
        layout.addWidget(self.priority_combo)

        # Назначить сотруднику
        layout.addWidget(QLabel("Назначить:"))
        self.assigned_combo = QComboBox()
        layout.addWidget(self.assigned_combo)

        # Связать с заказом
        layout.addWidget(QLabel("Связать с заказом (опционально):"))
        self.order_combo = QComboBox()
        layout.addWidget(self.order_combo)

        # Срок выполнения
        layout.addWidget(QLabel("Срок выполнения:"))
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDateTime(QDateTime.currentDateTime().addDays(3))
        self.due_date.setDisplayFormat("dd.MM.yyyy hh:mm")
        layout.addWidget(self.due_date)

        layout.addStretch()

        # Кнопки
        buttons_layout = QHBoxLayout()

        create_btn = QPushButton("✅ Создать задачу")
        create_btn.setObjectName("createBtn")
        create_btn.clicked.connect(self.create_objective)
        buttons_layout.addWidget(create_btn)

        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def load_employees(self):
        """Загружает список сотрудников"""
        try:
            employees = db_crm.get_all_employees()
            self.assigned_combo.addItem("Не назначено (для всех)", 0)
            for emp in employees:
                name = f"{emp['FirstName']} {emp['LastName']}"
                self.assigned_combo.addItem(name, emp['EmployeeID'])
        except Exception as e:
            print(f"Ошибка загрузки сотрудников: {e}")

    def load_orders(self):
        """Загружает список активных заказов"""
        try:
            orders = db_crm.get_orders_for_crm_table()
            self.order_combo.addItem("Без привязки к заказу", 0)
            for order in orders:
                order_text = f"#{order.get('OrderID')} - {order.get('Бренд', '')} {order.get('Модель', '')}"
                self.order_combo.addItem(order_text, order.get('OrderID'))
        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")

    def create_objective(self):
        """Создает новую задачу"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите название задачи")
            return

        priority_map = {
            "Низкий": "low",
            "Средний": "medium",
            "Высокий": "high",
            "Критичный": "critical"
        }

        task_data = {
            'employee_id': employee_session.get_employee_id(),
            'assigned_to_id': self.assigned_combo.currentData() if self.assigned_combo.currentData() != 0 else None,
            'order_id': self.order_combo.currentData() if self.order_combo.currentData() != 0 else None,
            'title': title,
            'description': self.description_input.toPlainText(),
            'priority': priority_map.get(self.priority_combo.currentText(), 'medium'),
            'due_date': self.due_date.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        }

        try:
            objective_id = db_objectives.create_objective(task_data)
            if objective_id:
                QMessageBox.information(self, "Успех", "Задача успешно создана!")
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось создать задачу")
        except Exception as e:
            print(f"Ошибка создания задачи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()