# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLabel, QPushButton, QFrame, \
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout

from Server.db import update_phone_in_db


class ModernPhoneDialog(QDialog):
    """Современный диалог изменения номера телефона"""

    def __init__(self, user_id, current_phone="", parent=None):
        super(ModernPhoneDialog, self).__init__(parent)
        self.user_id = user_id
        self.current_phone = current_phone
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
        icon_label = QLabel("📱")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                background: none;
                margin-left: 10px;
            }
        """)

        title_label = QLabel("Изменить номер телефона")
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
        desc_label = QLabel("Введите новый номер телефона в формате +7XXXXXXXXXX или +7 (XXX) XXX-XX-XX")
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

        # ===== ТЕКУЩИЙ НОМЕР =====
        current_label = QLabel("Текущий номер:")
        current_label.setStyleSheet("color: #808080; font-size: 12px; margin-top: 5px;")
        layout.addWidget(current_label)

        current_phone_label = QLabel(self.current_phone if self.current_phone else "—")
        current_phone_label.setStyleSheet("""
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
        layout.addWidget(current_phone_label)

        # ===== НОВЫЙ НОМЕР =====
        new_label = QLabel("Новый номер:")
        new_label.setStyleSheet("color: #808080; font-size: 12px; margin-top: 10px;")
        layout.addWidget(new_label)

        # Поле ввода с маской
        self.phone_input = QtWidgets.QLineEdit()
        self.phone_input.setInputMask("+7 (999) 999-99-99")
        self.phone_input.setPlaceholderText("+7 (___) ___-__-__")
        self.phone_input.setMinimumHeight(45)
        self.phone_input.setStyleSheet("""
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
        layout.addWidget(self.phone_input)

        # ===== ПРИМЕРЫ =====
        examples_frame = QFrame()
        examples_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        examples_layout = QVBoxLayout(examples_frame)
        examples_layout.setContentsMargins(10, 10, 10, 10)
        examples_layout.setSpacing(5)

        examples_title = QLabel("📋 Примеры номеров:")
        examples_title.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: 600;")
        examples_layout.addWidget(examples_title)

        example1 = QLabel("• +7 (999) 123-45-67")
        example2 = QLabel("• +7 (912) 345-67-89")
        example3 = QLabel("• +7 (925) 000-11-22")

        for example in [example1, example2, example3]:
            example.setStyleSheet("color: #808080; font-size: 11px; padding-left: 5px;")
            examples_layout.addWidget(example)

        layout.addWidget(examples_frame)

        # ===== ИНДИКАТОР ВАЛИДАЦИИ =====
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: #ff4444; font-size: 11px; margin-top: 5px;")
        layout.addWidget(self.validation_label)

        # Подключаем проверку ввода
        self.phone_input.textChanged.connect(self.validate_phone)

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

    def validate_phone(self, phone):
        """Проверка заполнения номера"""
        # Убираем все нецифровые символы для проверки
        digits = ''.join(filter(str.isdigit, phone))

        if not phone or phone == "+7 (___) ___-__-__":
            self.validation_label.setText("")
            self.btn_save.setEnabled(False)
        elif len(digits) < 11:  # Для РФ номер должен содержать 11 цифр
            self.validation_label.setText("❌ Номер должен содержать 11 цифр")
            self.validation_label.setStyleSheet("color: #ff4444; font-size: 11px; margin-top: 5px;")
            self.btn_save.setEnabled(False)
        else:
            # Проверяем, не совпадает ли с текущим
            formatted_phone = f"+{digits}"
            if formatted_phone == self.current_phone:
                self.validation_label.setText("⚠️ Новый номер совпадает с текущим")
                self.validation_label.setStyleSheet("color: #ffaa44; font-size: 11px; margin-top: 5px;")
                self.btn_save.setEnabled(False)
            else:
                self.validation_label.setText("✅ Номер корректен")
                self.validation_label.setStyleSheet("color: #4CAF50; font-size: 11px; margin-top: 5px;")
                self.btn_save.setEnabled(True)

    def save_changes(self):
        # Получаем только цифры
        phone_digits = ''.join(filter(str.isdigit, self.phone_input.text()))
        formatted_phone = f"+{phone_digits}"  # Добавляем + в начало

        if formatted_phone == self.current_phone:
            QMessageBox.warning(self, "Ошибка", "Новый номер совпадает с текущим!")
            return

        # Вызов функции сохранения в БД
        success = update_phone_in_db(self.user_id, formatted_phone)

        if success:
            QMessageBox.information(self, "Успех", "✅ Номер телефона успешно обновлен!")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "❌ Не удалось обновить номер телефона.")


class Ui_Setting_Nomber(object):
    def __init__(self, user_id, current_phone=""):
        self.user_id = user_id
        self.current_phone = current_phone

    def setupUi(self, Setting_Nomber):
        dialog = ModernPhoneDialog(self.user_id, self.current_phone, Setting_Nomber)
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

    dialog = ModernPhoneDialog(user_id=1, current_phone="+79991234567")
    dialog.show()

    sys.exit(app.exec_())