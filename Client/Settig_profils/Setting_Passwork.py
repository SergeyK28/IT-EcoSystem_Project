# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLabel, QPushButton, QFrame, \
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout

from Server.db import update_password_in_db


class ModernPasswordDialog(QDialog):
    """Современный диалог изменения пароля"""

    def __init__(self, user_id, parent=None):
        super(ModernPasswordDialog, self).__init__(parent)
        self.user_id = user_id
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(500, 700)  # Увеличил размер для лучшей видимости

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 500, 700)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 25px;
                border: 1px solid #3a3a3a;
            }
        """)

        # Тень
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # ===== ЗАГОЛОВОК =====
        header_layout = QHBoxLayout()

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        # Иконка и заголовок
        icon_label = QLabel("🔒")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                background: none;
                margin-left: 10px;
            }
        """)

        title_label = QLabel("Изменить пароль")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: 600;
                background: none;
            }
        """)

        header_layout.addWidget(self.btn_close)
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # ===== ОПИСАНИЕ =====
        desc_label = QLabel("Используйте надежный пароль для защиты вашей учетной записи")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 13px;
                background: none;
                padding: 10px 0;
            }
        """)
        layout.addWidget(desc_label)

        # ===== ТЕКУЩИЙ ПАРОЛЬ =====
        current_label = QLabel("Текущий пароль:")
        current_label.setStyleSheet("color: #808080; font-size: 13px; font-weight: 600; margin-top: 5px;")
        layout.addWidget(current_label)

        self.current_input = QtWidgets.QLineEdit()
        self.current_input.setPlaceholderText("Введите текущий пароль")
        self.current_input.setMinimumHeight(45)
        self.current_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.current_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        layout.addWidget(self.current_input)

        # ===== НОВЫЙ ПАРОЛЬ =====
        new_label = QLabel("Новый пароль:")
        new_label.setStyleSheet("color: #808080; font-size: 13px; font-weight: 600; margin-top: 15px;")
        layout.addWidget(new_label)

        self.new_input = QtWidgets.QLineEdit()
        self.new_input.setPlaceholderText("Введите новый пароль")
        self.new_input.setMinimumHeight(45)
        self.new_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        self.new_input.textChanged.connect(self.check_password_strength)
        layout.addWidget(self.new_input)

        # ===== ПОДТВЕРЖДЕНИЕ ПАРОЛЯ =====
        confirm_label = QLabel("Подтвердите пароль:")
        confirm_label.setStyleSheet("color: #808080; font-size: 13px; font-weight: 600; margin-top: 15px;")
        layout.addWidget(confirm_label)

        self.confirm_input = QtWidgets.QLineEdit()
        self.confirm_input.setPlaceholderText("Повторите новый пароль")
        self.confirm_input.setMinimumHeight(45)
        self.confirm_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        self.confirm_input.textChanged.connect(self.check_passwords_match)
        layout.addWidget(self.confirm_input)

        # ===== ИНДИКАТОР СЛОЖНОСТИ ПАРОЛЯ =====
        strength_frame = QFrame()
        strength_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 15px;
                padding: 15px;
                margin-top: 20px;
                border: 1px solid #3a3a3a;
            }
        """)

        strength_layout = QVBoxLayout(strength_frame)
        strength_layout.setContentsMargins(20, 20, 20, 20)
        strength_layout.setSpacing(15)

        # Заголовок
        strength_title = QLabel("📊 Требования к паролю:")
        strength_title.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 600;
                background: none;
            }
        """)
        strength_layout.addWidget(strength_title)

        # Создаем сетку для требований (2 колонки)
        requirements_grid = QGridLayout()
        requirements_grid.setSpacing(10)

        # Список требований с иконками
        self.requirements = {
            'length': {"text": "Минимум 8 символов", "met": False, "icon": "🔴"},
            'uppercase': {"text": "Заглавная буква (A-Z)", "met": False, "icon": "🔴"},
            'lowercase': {"text": "Строчная буква (a-z)", "met": False, "icon": "🔴"},
            'digit': {"text": "Цифра (0-9)", "met": False, "icon": "🔴"},
            'special': {"text": "Спецсимвол (!@#$%^&*)", "met": False, "icon": "🔴"}
        }

        self.req_labels = {}
        row = 0
        col = 0
        for i, (key, req) in enumerate(self.requirements.items()):
            # Контейнер для одного требования
            req_container = QFrame()
            req_container.setStyleSheet("background: transparent;")
            req_layout = QHBoxLayout(req_container)
            req_layout.setContentsMargins(0, 0, 0, 0)
            req_layout.setSpacing(8)

            # Иконка статуса
            icon_label = QLabel(req["icon"])
            icon_label.setFixedSize(20, 20)
            icon_label.setStyleSheet("""
                QLabel {
                    background: none;
                    font-size: 14px;
                }
            """)
            req_layout.addWidget(icon_label)

            # Текст требования
            text_label = QLabel(req["text"])
            text_label.setStyleSheet("""
                QLabel {
                    color: #808080;
                    font-size: 12px;
                    background: none;
                }
            """)
            req_layout.addWidget(text_label)
            req_layout.addStretch()

            # Добавляем в сетку
            requirements_grid.addWidget(req_container, row, col)

            # Сохраняем ссылки на элементы
            self.req_labels[key] = {
                'icon': icon_label,
                'text': text_label
            }

            # Переходим на следующую строку/колонку
            col += 1
            if col > 1:  # Максимум 2 колонки
                col = 0
                row += 1

        strength_layout.addLayout(requirements_grid)

        # Прогресс-бар сложности
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(5)

        # Текст сложности
        self.strength_text = QLabel("Сложность пароля: Не введен")
        self.strength_text.setStyleSheet("color: #808080; font-size: 12px;")
        progress_layout.addWidget(self.strength_text)

        # Прогресс-бар
        self.strength_bar = QtWidgets.QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(10)
        self.strength_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3a3a3a;
                border: none;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #ff4444;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.strength_bar)

        strength_layout.addLayout(progress_layout)

        layout.addWidget(strength_frame)

        # ===== ИНДИКАТОР СОВПАДЕНИЯ ПАРОЛЕЙ =====
        self.match_frame = QFrame()
        self.match_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 68, 68, 0.1);
                border-radius: 10px;
                padding: 10px;
                margin-top: 10px;
            }
        """)

        match_layout = QHBoxLayout(self.match_frame)
        match_layout.setContentsMargins(15, 10, 15, 10)

        self.match_icon = QLabel("⚠️")
        self.match_icon.setStyleSheet("font-size: 16px; background: none;")

        self.match_label = QLabel("Введите пароль для проверки")
        self.match_label.setStyleSheet("color: #ffaa44; font-size: 12px; background: none;")

        match_layout.addWidget(self.match_icon)
        match_layout.addWidget(self.match_label)
        match_layout.addStretch()

        layout.addWidget(self.match_frame)

        # Растяжка
        layout.addStretch()

        # ===== КНОПКИ =====
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Кнопка отмены
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setMinimumHeight(45)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: 1px solid #4a4a4a;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: white;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)

        # Кнопка сохранения
        self.btn_save = QPushButton("💾 Сохранить пароль")
        self.btn_save.setMinimumHeight(45)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setEnabled(False)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #357a38);
            }
            QPushButton:disabled {
                background: #3a3a3a;
                color: #6a6a6a;
            }
        """)
        self.btn_save.clicked.connect(self.save_changes)

        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_save)

        layout.addLayout(buttons_layout)

    def check_password_strength(self, password):
        """Проверка сложности пароля и обновление индикаторов"""
        if not password:
            for key in self.requirements:
                self.requirements[key]["met"] = False
                self.req_labels[key]['icon'].setText("🔴")
                self.req_labels[key]['text'].setStyleSheet("color: #808080; font-size: 12px; background: none;")
            self.strength_bar.setValue(0)
            self.strength_text.setText("Сложность пароля: Не введен")
            self.strength_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #3a3a3a;
                    border: none;
                    border-radius: 5px;
                }
                QProgressBar::chunk {
                    background-color: #808080;
                    border-radius: 5px;
                }
            """)
            self.check_passwords_match()
            return

        # Проверка требований
        self.requirements['length']["met"] = len(password) >= 8
        self.requirements['uppercase']["met"] = any(c.isupper() for c in password)
        self.requirements['lowercase']["met"] = any(c.islower() for c in password)
        self.requirements['digit']["met"] = any(c.isdigit() for c in password)
        self.requirements['special']["met"] = any(c in "!@#$%^&*()_+-=[]{};:,.<>?" for c in password)

        # Обновление иконок и цветов требований
        for key, req in self.requirements.items():
            if req["met"]:
                self.req_labels[key]['icon'].setText("🟢")
                self.req_labels[key]['text'].setStyleSheet("color: #4CAF50; font-size: 12px; background: none;")
            else:
                self.req_labels[key]['icon'].setText("🔴")
                self.req_labels[key]['text'].setStyleSheet("color: #808080; font-size: 12px; background: none;")

        # Расчет сложности
        met_count = sum(1 for req in self.requirements.values() if req["met"])
        strength_percent = (met_count / len(self.requirements)) * 100

        self.strength_bar.setValue(int(strength_percent))

        # Обновление цвета и текста
        if strength_percent < 40:
            self.strength_text.setText("Сложность пароля: Слабый")
            self.strength_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #3a3a3a;
                    border: none;
                    border-radius: 5px;
                }
                QProgressBar::chunk {
                    background-color: #ff4444;
                    border-radius: 5px;
                }
            """)
        elif strength_percent < 70:
            self.strength_text.setText("Сложность пароля: Средний")
            self.strength_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #3a3a3a;
                    border: none;
                    border-radius: 5px;
                }
                QProgressBar::chunk {
                    background-color: #ffaa44;
                    border-radius: 5px;
                }
            """)
        else:
            self.strength_text.setText("Сложность пароля: Надежный")
            self.strength_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #3a3a3a;
                    border: none;
                    border-radius: 5px;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 5px;
                }
            """)

        self.check_passwords_match()

    def check_passwords_match(self):
        """Проверка совпадения паролей"""
        new_pass = self.new_input.text()
        confirm_pass = self.confirm_input.text()

        if not new_pass and not confirm_pass:
            self.match_icon.setText("⚠️")
            self.match_label.setText("Введите пароль для проверки")
            self.match_label.setStyleSheet("color: #ffaa44; font-size: 12px; background: none;")
            self.match_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 170, 68, 0.1);
                    border-radius: 10px;
                    padding: 10px;
                    margin-top: 10px;
                }
            """)
            self.btn_save.setEnabled(False)
            return

        if not new_pass or not confirm_pass:
            self.match_icon.setText("⚠️")
            self.match_label.setText("Заполните оба поля")
            self.match_label.setStyleSheet("color: #ffaa44; font-size: 12px; background: none;")
            self.match_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 170, 68, 0.1);
                    border-radius: 10px;
                    padding: 10px;
                    margin-top: 10px;
                }
            """)
            self.btn_save.setEnabled(False)
            return

        if new_pass != confirm_pass:
            self.match_icon.setText("❌")
            self.match_label.setText("Пароли не совпадают")
            self.match_label.setStyleSheet("color: #ff4444; font-size: 12px; background: none;")
            self.match_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 68, 68, 0.1);
                    border-radius: 10px;
                    padding: 10px;
                    margin-top: 10px;
                }
            """)
            self.btn_save.setEnabled(False)
            return

        if new_pass and confirm_pass and new_pass == confirm_pass:
            # Проверяем, что все требования выполнены
            all_met = all(req["met"] for req in self.requirements.values())

            if all_met:
                self.match_icon.setText("✅")
                self.match_label.setText("Пароли совпадают, все требования выполнены")
                self.match_label.setStyleSheet("color: #4CAF50; font-size: 12px; background: none;")
                self.match_frame.setStyleSheet("""
                    QFrame {
                        background-color: rgba(76, 175, 80, 0.1);
                        border-radius: 10px;
                        padding: 10px;
                        margin-top: 10px;
                    }
                """)
                self.btn_save.setEnabled(True)
            else:
                self.match_icon.setText("⚠️")
                self.match_label.setText("Выполните все требования к паролю")
                self.match_label.setStyleSheet("color: #ffaa44; font-size: 12px; background: none;")
                self.match_frame.setStyleSheet("""
                    QFrame {
                        background-color: rgba(255, 170, 68, 0.1);
                        border-radius: 10px;
                        padding: 10px;
                        margin-top: 10px;
                    }
                """)
                self.btn_save.setEnabled(False)

    def save_changes(self):
        current_pass = self.current_input.text()
        new_pass = self.new_input.text()

        if not current_pass:
            QMessageBox.warning(self, "Ошибка", "Введите текущий пароль!")
            return

        if not new_pass:
            QMessageBox.warning(self, "Ошибка", "Введите новый пароль!")
            return

        # Вызов функции сохранения в БД
        success = update_password_in_db(self.user_id, current_pass, new_pass)

        if success:
            QMessageBox.information(self, "Успех", "✅ Пароль успешно изменен!")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "❌ Не удалось изменить пароль. Проверьте текущий пароль.")


class Ui_Setting_Password(object):
    def __init__(self, user_id):
        self.user_id = user_id

    def setupUi(self, Setting_Password):
        dialog = ModernPasswordDialog(self.user_id, Setting_Password)
        dialog.exec_()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # Применяем темную палитру
    app.setStyle('Fusion')
    palette = QtWidgets.QPalette()
    palette.setColor(QtWidgets.QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QtWidgets.QPalette.WindowText, Qt.white)
    palette.setColor(QtWidgets.QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QtWidgets.QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QtWidgets.QPalette.Text, Qt.white)
    palette.setColor(QtWidgets.QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QtWidgets.QPalette.ButtonText, Qt.white)
    palette.setColor(QtWidgets.QPalette.Highlight, QColor(76, 175, 80))
    app.setPalette(palette)

    dialog = ModernPasswordDialog(user_id=1)
    dialog.show()

    sys.exit(app.exec_())