# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLabel, QPushButton, QFrame, \
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout

from Server.db import update_email_in_db


class ModernEmailDialog(QDialog):
    """Современный диалог изменения email"""

    def __init__(self, user_id, current_email="", parent=None):
        super(ModernEmailDialog, self).__init__(parent)
        self.user_id = user_id
        self.current_email = current_email
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(400, 450)

        # Главный контейнер
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 400, 450)
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
        layout.setSpacing(20)

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
        icon_label = QLabel("📧")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                background: none;
                margin-left: 10px;
            }
        """)

        title_label = QLabel("Изменить Email")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
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
        desc_label = QLabel("Введите новый email адрес. На него будут приходить уведомления о статусе заказов.")
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

        # ===== ТЕКУЩИЙ EMAIL =====
        current_label = QLabel("Текущий email:")
        current_label.setStyleSheet("color: #808080; font-size: 12px; margin-top: 5px;")
        layout.addWidget(current_label)

        current_email_label = QLabel(self.current_email if self.current_email else "—")
        current_email_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 600;
                padding: 10px;
                background-color: #2d2d2d;
                border-radius: 10px;
                border: 1px solid #3a3a3a;
            }
        """)
        layout.addWidget(current_email_label)

        # ===== НОВЫЙ EMAIL =====
        new_label = QLabel("Новый email:")
        new_label.setStyleSheet("color: #808080; font-size: 12px; margin-top: 10px;")
        layout.addWidget(new_label)

        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("example@domain.com")
        self.email_input.setMinimumHeight(45)
        self.email_input.setStyleSheet("""
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
        layout.addWidget(self.email_input)

        # ===== ИНДИКАТОР ВАЛИДАЦИИ =====
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: #ff4444; font-size: 11px; margin-top: 5px;")
        layout.addWidget(self.validation_label)

        # Подключаем проверку ввода
        self.email_input.textChanged.connect(self.validate_email)

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
        self.btn_save = QPushButton("💾 Сохранить")
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

    def validate_email(self, email):
        """Проверка корректности email"""
        if not email:
            self.validation_label.setText("")
            self.btn_save.setEnabled(False)
            return

        # Простая валидация email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(email_pattern, email):
            if email == self.current_email:
                self.validation_label.setText("⚠️ Новый email совпадает с текущим")
                self.validation_label.setStyleSheet("color: #ffaa44; font-size: 11px; margin-top: 5px;")
                self.btn_save.setEnabled(False)
            else:
                self.validation_label.setText("✅ Email корректен")
                self.validation_label.setStyleSheet("color: #4CAF50; font-size: 11px; margin-top: 5px;")
                self.btn_save.setEnabled(True)
        else:
            self.validation_label.setText("❌ Неверный формат email")
            self.validation_label.setStyleSheet("color: #ff4444; font-size: 11px; margin-top: 5px;")
            self.btn_save.setEnabled(False)

    def save_changes(self):
        new_email = self.email_input.text().strip()

        if new_email == self.current_email:
            QMessageBox.warning(self, "Ошибка", "Новый email совпадает с текущим!")
            return

        # Вызов функции сохранения в БД
        success = update_email_in_db(self.user_id, new_email)

        if success:
            QMessageBox.information(self, "Успех", "✅ Email успешно обновлен!")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "❌ Не удалось обновить email. Возможно, такой email уже используется.")


class Ui_Setting_Email(object):
    def __init__(self, user_id, current_email=""):
        self.user_id = user_id
        self.current_email = current_email

    def setupUi(self, Setting_Email):
        dialog = ModernEmailDialog(self.user_id, self.current_email, Setting_Email)
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

    dialog = ModernEmailDialog(user_id=1, current_email="user@example.com")
    dialog.show()

    sys.exit(app.exec_())