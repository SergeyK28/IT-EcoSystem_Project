# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
                             QScrollArea, QWidget, QTextEdit, QDateEdit, QComboBox,
                             QCheckBox, QLineEdit, QGridLayout)
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Handlers.Employees.employee_session import employee_session
from Server import db_crm, db_objectives


class ObjectivesDialog(QDialog):
    """Окно задач сотрудника (упрощённый дизайн)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_objective_id = None
        self.setup_ui()
        self.load_objectives()

    def setup_ui(self):
        self.setObjectName("ObjectivesDialog")
        self.setWindowTitle("IT-EcoSystem CRM - Задачи")
        self.resize(1000, 700)

        # Базовый стиль – тёмный, но без излишеств
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 11pt;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#addBtn {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#addBtn:hover {
                background-color: #3a9a4a;
            }
            QPushButton#closeBtn {
                background-color: #6c6c6c;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                font-size: 14px;
                padding: 0px;
                border: none;
            }
            QPushButton#closeBtn:hover {
                background-color: #8c8c8c;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2a2a2a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #ddd;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2d7d3a;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#taskCard {
                background-color: #3a3a3a;
                border-radius: 4px;
                border-left: 3px solid #2d7d3a;
            }
            QWidget#taskCard:hover {
                background-color: #444;
            }
            QCheckBox {
                color: #f0f0f0;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 2px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #2d7d3a;
                background-color: #3a3a3a;
            }
            QCheckBox::indicator:checked {
                background-color: #2d7d3a;
                border: 2px solid #2d7d3a;
            }
            QLineEdit, QTextEdit, QDateEdit, QComboBox {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
        """)

        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Верхняя панель
        header_layout = QHBoxLayout()

        title_label = QLabel("📋 ЗАДАЧИ")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.add_btn = QPushButton("➕ Новая задача")
        self.add_btn.setObjectName("addBtn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.show_add_objective_dialog)
        header_layout.addWidget(self.add_btn)

        layout.addLayout(header_layout)

        # Табы
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::tab-bar { alignment: center; }")

        self.active_tab = QWidget()
        self.setup_active_tab()
        self.tab_widget.addTab(self.active_tab, "Активные")

        self.completed_tab = QWidget()
        self.setup_completed_tab()
        self.tab_widget.addTab(self.completed_tab, "Завершено")

        layout.addWidget(self.tab_widget)

    def setup_active_tab(self):
        layout = QVBoxLayout(self.active_tab)
        layout.setContentsMargins(5, 5, 5, 5)

        # Фильтры
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Фильтр:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все задачи", "Мои задачи", "Назначенные мне", "По заказам", "Просроченные"])
        self.filter_combo.currentTextChanged.connect(self.load_objectives)
        filters_layout.addWidget(self.filter_combo)
        filters_layout.addStretch()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск задач...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self.load_objectives)
        filters_layout.addWidget(self.search_input)
        layout.addLayout(filters_layout)

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.active_tasks_widget = QWidget()
        self.active_tasks_layout = QVBoxLayout(self.active_tasks_widget)
        self.active_tasks_layout.setSpacing(8)
        self.active_tasks_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.active_tasks_widget)
        layout.addWidget(scroll_area)

    def setup_completed_tab(self):
        layout = QVBoxLayout(self.completed_tab)
        layout.setContentsMargins(5, 5, 5, 5)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.completed_tasks_widget = QWidget()
        self.completed_tasks_layout = QVBoxLayout(self.completed_tasks_widget)
        self.completed_tasks_layout.setSpacing(8)
        self.completed_tasks_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.completed_tasks_widget)
        layout.addWidget(scroll_area)

    def create_task_card(self, task_data, is_completed=False):
        card = QWidget()
        card.setObjectName("taskCard")
        card.setFixedHeight(110)
        card.setCursor(Qt.PointingHandCursor)
        card.task_id = task_data.get('ObjectiveID')
        card.task_data = task_data

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        checkbox = QCheckBox()
        checkbox.setChecked(is_completed)
        checkbox.stateChanged.connect(lambda state, t=card.task_id: self.toggle_task_completion(t, state == Qt.Checked))
        layout.addWidget(checkbox)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        title_layout = QHBoxLayout()
        title_label = QLabel(task_data.get('Title', 'Без названия'))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #fff;")
        title_layout.addWidget(title_label)

        priority = task_data.get('Priority', 'medium')
        priority_colors = {'low': '#6c757d', 'medium': '#ffc107', 'high': '#dc3545', 'critical': '#990000'}
        priority_texts = {'low': 'Низкий', 'medium': 'Средний', 'high': 'Высокий', 'critical': 'Критичный'}
        priority_label = QLabel(priority_texts.get(priority, 'Средний'))
        priority_label.setStyleSheet(f"""
            background-color: {priority_colors.get(priority, '#6c757d')};
            color: white;
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: bold;
        """)
        title_layout.addWidget(priority_label)
        title_layout.addStretch()

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
                due_label.setStyleSheet("color: #bbb; font-size: 11px;")
                if not is_completed and due_date < datetime.now():
                    due_label.setStyleSheet("color: #ff6666; font-size: 11px; font-weight: bold;")
                    due_label.setText(f"⚠️ ПРОСРОЧЕНО! {due_text}")
                title_layout.addWidget(due_label)

        content_layout.addLayout(title_layout)

        description = task_data.get('Description', '')
        if description:
            if len(description) > 100:
                description = description[:100] + "..."
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #ccc; font-size: 11px;")
            desc_label.setWordWrap(True)
            content_layout.addWidget(desc_label)

        info_layout = QHBoxLayout()
        created_by = task_data.get('CreatedByName', 'Система')
        info_layout.addWidget(QLabel(f"👤 {created_by}"))
        assigned_to = task_data.get('AssignedToName', 'Все')
        info_layout.addWidget(QLabel(f"➡️ {assigned_to}"))
        order_info = task_data.get('OrderInfo', '')
        if order_info:
            info_layout.addWidget(QLabel(f"📦 {order_info}"))
        info_layout.addStretch()
        content_layout.addLayout(info_layout)

        layout.addLayout(content_layout)

        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 12px;
                font-size: 14px;
                padding: 0px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e65a6a;
            }
        """)
        delete_btn.clicked.connect(lambda checked, t=card.task_id: self.delete_task(t))
        layout.addWidget(delete_btn)

        card.mousePressEvent = lambda event, t=task_data: self.open_task_notes(t)
        return card

    def load_objectives(self):
        try:
            filter_type = self.filter_combo.currentText()
            search_text = self.search_input.text().strip()

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

            self.clear_layout(self.active_tasks_layout)
            for task in active_tasks:
                card = self.create_task_card(task, is_completed=False)
                self.active_tasks_layout.addWidget(card)
            if not active_tasks:
                no_tasks_label = QLabel("✨ Нет активных задач")
                no_tasks_label.setAlignment(Qt.AlignCenter)
                no_tasks_label.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
                self.active_tasks_layout.addWidget(no_tasks_label)
            self.active_tasks_layout.addStretch()

            self.clear_layout(self.completed_tasks_layout)
            for task in completed_tasks:
                card = self.create_task_card(task, is_completed=True)
                self.completed_tasks_layout.addWidget(card)
            if not completed_tasks:
                no_tasks_label = QLabel("📌 Нет завершенных задач")
                no_tasks_label.setAlignment(Qt.AlignCenter)
                no_tasks_label.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
                self.completed_tasks_layout.addWidget(no_tasks_label)
            self.completed_tasks_layout.addStretch()

        except Exception as e:
            print(f"Ошибка загрузки задач: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить задачи: {e}")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def toggle_task_completion(self, task_id, completed):
        try:
            if completed:
                db_objectives.update_objective_status(task_id, 'completed')
            else:
                db_objectives.update_objective_status(task_id, 'active')
            self.load_objectives()
        except Exception as e:
            print(f"Ошибка изменения статуса задачи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось изменить статус задачи: {e}")

    def delete_task(self, task_id):
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
        dialog = TaskNotesDialog(task_data, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_objectives()

    def show_add_objective_dialog(self):
        dialog = AddObjectiveDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_objectives()

    # Убраны методы mousePressEvent/mouseMoveEvent, т.к. теперь стандартное окно


class TaskNotesDialog(QDialog):
    """Окно заметок к задаче (упрощённый дизайн)"""

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.task_id = task_data.get('ObjectiveID')
        self.setup_ui()
        self.load_comments()

    def setup_ui(self):
        self.setObjectName("TaskNotesDialog")
        self.setWindowTitle("Заметки к задаче")
        self.resize(600, 700)

        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#closeBtn {
                background-color: #6c6c6c;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                font-size: 14px;
                padding: 0px;
                border: none;
            }
            QPushButton#closeBtn:hover {
                background-color: #8c8c8c;
            }
            QPushButton#saveBtn {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#saveBtn:hover {
                background-color: #3a9a4a;
            }
            QTextEdit, QLineEdit, QDateEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
            QFrame#commentFrame {
                background-color: #3a3a3a;
                border-radius: 3px;
                border-left: 3px solid #2d7d3a;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel(f"📝 {self.task_data.get('Title', 'Задача')}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Информация о задаче
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #333; border-radius: 3px;")
        info_layout = QGridLayout(info_frame)
        info_layout.setHorizontalSpacing(15)
        info_layout.setVerticalSpacing(6)

        status_text = '✅ Выполнено' if self.task_data.get('Status') == 'completed' else '🔄 Активно'
        info_layout.addWidget(QLabel("Статус:"), 0, 0)
        info_layout.addWidget(QLabel(status_text), 0, 1)

        priority = self.task_data.get('Priority', 'medium')
        priority_texts = {'low': 'Низкий', 'medium': 'Средний', 'high': 'Высокий', 'critical': 'Критичный'}
        info_layout.addWidget(QLabel("Приоритет:"), 0, 2)
        info_layout.addWidget(QLabel(priority_texts.get(priority, 'Средний')), 0, 3)

        due_date = self.task_data.get('DueDate')
        if due_date:
            if isinstance(due_date, str):
                try:
                    due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S')
                except:
                    due_date = None
            if due_date:
                due_str = due_date.strftime('%d.%m.%Y %H:%M')
                info_layout.addWidget(QLabel("Срок:"), 1, 0)
                info_layout.addWidget(QLabel(due_str), 1, 1)

        created_by = self.task_data.get('CreatedByName', 'Система')
        info_layout.addWidget(QLabel("Автор:"), 1, 2)
        info_layout.addWidget(QLabel(created_by), 1, 3)

        assigned_to = self.task_data.get('AssignedToName', 'Все')
        info_layout.addWidget(QLabel("Назначено:"), 2, 0)
        info_layout.addWidget(QLabel(assigned_to), 2, 1, 1, 3)

        layout.addWidget(info_frame)

        # Описание
        desc_label = QLabel("Описание задачи:")
        desc_label.setStyleSheet("font-weight: bold; color: #ccc; margin-top: 6px;")
        layout.addWidget(desc_label)

        self.description_edit = QTextEdit()
        self.description_edit.setText(self.task_data.get('Description', ''))
        self.description_edit.setMaximumHeight(120)
        layout.addWidget(self.description_edit)

        # Чек-лист (если есть)
        checklist = self.task_data.get('Checklist', [])
        if checklist:
            checklist_label = QLabel("Чек-лист:")
            checklist_label.setStyleSheet("font-weight: bold; color: #ccc; margin-top: 6px;")
            layout.addWidget(checklist_label)

            self.checklist_widget = QWidget()
            checklist_layout = QVBoxLayout(self.checklist_widget)
            checklist_layout.setSpacing(4)
            for item in checklist:
                item_check = QCheckBox(item.get('ItemText', ''))
                item_check.setChecked(item.get('IsCompleted', False))
                checklist_layout.addWidget(item_check)
            layout.addWidget(self.checklist_widget)

        # Комментарии
        comments_label = QLabel("Комментарии:")
        comments_label.setStyleSheet("font-weight: bold; color: #ccc; margin-top: 6px;")
        layout.addWidget(comments_label)

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
        add_comment_btn.setFixedSize(36, 36)
        add_comment_btn.setStyleSheet("background-color: #2d7d3a; border: none;")
        add_comment_btn.clicked.connect(self.add_comment)
        comment_input_layout.addWidget(add_comment_btn)
        layout.addLayout(comment_input_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить изменения")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.save_changes)
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setStyleSheet("background-color: #6c6c6c; border: none;")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def load_comments(self):
        try:
            comments = db_objectives.get_objective_comments(self.task_id)
            self.clear_layout(self.comments_layout)

            for comment in comments:
                comment_frame = QFrame()
                comment_frame.setObjectName("commentFrame")
                comment_layout = QVBoxLayout(comment_frame)
                comment_layout.setSpacing(3)

                header_layout = QHBoxLayout()
                author = comment.get('EmployeeName', 'Система')
                author_label = QLabel(f"👤 {author}")
                author_label.setStyleSheet("font-weight: bold; color: #2d7d3a;")
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
                        date_label.setStyleSheet("color: #999; font-size: 10px;")
                        header_layout.addWidget(date_label)
                header_layout.addStretch()
                comment_layout.addLayout(header_layout)

                text_label = QLabel(comment.get('CommentText', ''))
                text_label.setWordWrap(True)
                comment_layout.addWidget(text_label)

                self.comments_layout.addWidget(comment_frame)

            if not comments:
                no_comments = QLabel("💬 Нет комментариев")
                no_comments.setAlignment(Qt.AlignCenter)
                no_comments.setStyleSheet("color: #999; padding: 15px;")
                self.comments_layout.addWidget(no_comments)

        except Exception as e:
            print(f"Ошибка загрузки комментариев: {e}")

    def add_comment(self):
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
        try:
            new_description = self.description_edit.toPlainText()
            db_objectives.update_objective_description(self.task_id, new_description)
            self.accept()
        except Exception as e:
            print(f"Ошибка сохранения изменений: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {e}")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class AddObjectiveDialog(QDialog):
    """Диалог добавления новой задачи (упрощённый дизайн)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_employees()
        self.load_orders()

    def setup_ui(self):
        self.setObjectName("AddObjectiveDialog")
        self.setWindowTitle("Новая задача")
        self.resize(500, 580)

        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 3px;
                font-weight: bold;
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #5a5a5a;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#createBtn {
                background-color: #2d7d3a;
                border: none;
            }
            QPushButton#createBtn:hover {
                background-color: #3a9a4a;
            }
            QPushButton#cancelBtn {
                background-color: #6c6c6c;
                border: none;
            }
            QPushButton#cancelBtn:hover {
                background-color: #8c8c8c;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("➕ НОВАЯ ЗАДАЧА")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2d7d3a;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Поля
        layout.addWidget(QLabel("Название задачи:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название задачи")
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Описание:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Подробное описание задачи...")
        layout.addWidget(self.description_input)

        layout.addWidget(QLabel("Приоритет:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Низкий", "Средний", "Высокий", "Критичный"])
        layout.addWidget(self.priority_combo)

        layout.addWidget(QLabel("Назначить:"))
        self.assigned_combo = QComboBox()
        layout.addWidget(self.assigned_combo)

        layout.addWidget(QLabel("Связать с заказом (опционально):"))
        self.order_combo = QComboBox()
        layout.addWidget(self.order_combo)

        layout.addWidget(QLabel("Срок выполнения:"))
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDateTime(QDateTime.currentDateTime().addDays(3))
        self.due_date.setDisplayFormat("dd.MM.yyyy hh:mm")
        layout.addWidget(self.due_date)

        layout.addStretch()

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
        try:
            employees = db_crm.get_all_employees()
            self.assigned_combo.addItem("Не назначено (для всех)", 0)
            for emp in employees:
                name = f"{emp['FirstName']} {emp['LastName']}"
                self.assigned_combo.addItem(name, emp['EmployeeID'])
        except Exception as e:
            print(f"Ошибка загрузки сотрудников: {e}")

    def load_orders(self):
        try:
            orders = db_crm.get_orders_for_crm_table()
            self.order_combo.addItem("Без привязки к заказу", 0)
            for order in orders:
                order_text = f"#{order.get('OrderID')} - {order.get('Бренд', '')} {order.get('Модель', '')}"
                self.order_combo.addItem(order_text, order.get('OrderID'))
        except Exception as e:
            print(f"Ошибка загрузки заказов: {e}")

    def create_objective(self):
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