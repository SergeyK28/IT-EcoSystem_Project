# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox


class Ui_Setting_Password(object):
    def setupUi(self, Setting_Password):
        Setting_Password.setObjectName("Setting_Password")
        Setting_Password.resize(400, 450)
        Setting_Password.setStyleSheet("""
            QDialog {
                background-color: rgb(47, 47, 47);
                border-radius: 10px;
            }
        """)

        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Password)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(15)

        # Заголовок
        self.title_label = QtWidgets.QLabel("🔒 Изменение пароля")
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.verticalLayout.addWidget(self.title_label)

        # Текущий пароль
        self.current_label = QtWidgets.QLabel("Текущий пароль:")
        self.current_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 13px;")
        self.verticalLayout.addWidget(self.current_label)

        self.current_input = QtWidgets.QLineEdit()
        self.current_input.setPlaceholderText("Введите текущий пароль")
        self.current_input.setMinimumHeight(40)
        self.current_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.current_input.setStyleSheet("""
            QLineEdit {
                background-color: rgb(60, 60, 60);
                color: white;
                border: 2px solid rgb(80, 80, 80);
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid rgb(103, 155, 118);
            }
            QLineEdit::placeholder {
                color: rgb(150, 150, 150);
            }
        """)
        self.verticalLayout.addWidget(self.current_input)

        # Новый пароль
        self.new_label = QtWidgets.QLabel("Новый пароль:")
        self.new_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 13px;")
        self.verticalLayout.addWidget(self.new_label)

        self.new_input = QtWidgets.QLineEdit()
        self.new_input.setPlaceholderText("Введите новый пароль")
        self.new_input.setMinimumHeight(40)
        self.new_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_input.setStyleSheet("""
            QLineEdit {
                background-color: rgb(60, 60, 60);
                color: white;
                border: 2px solid rgb(80, 80, 80);
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid rgb(103, 155, 118);
            }
            QLineEdit::placeholder {
                color: rgb(150, 150, 150);
            }
        """)
        self.verticalLayout.addWidget(self.new_input)

        # Подтверждение пароля
        self.confirm_label = QtWidgets.QLabel("Подтвердите пароль:")
        self.confirm_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 13px;")
        self.verticalLayout.addWidget(self.confirm_label)

        self.confirm_input = QtWidgets.QLineEdit()
        self.confirm_input.setPlaceholderText("Повторите новый пароль")
        self.confirm_input.setMinimumHeight(40)
        self.confirm_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                background-color: rgb(60, 60, 60);
                color: white;
                border: 2px solid rgb(80, 80, 80);
                border-radius: 8px;
                padding: 0 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid rgb(103, 155, 118);
            }
            QLineEdit::placeholder {
                color: rgb(150, 150, 150);
            }
        """)
        self.verticalLayout.addWidget(self.confirm_input)

        # Индикатор сложности пароля
        self.strength_frame = QtWidgets.QFrame()
        self.strength_frame.setStyleSheet("""
            QFrame {
                background-color: rgb(60, 60, 60);
                border-radius: 5px;
                padding: 10px;
            }
        """)
        strength_layout = QtWidgets.QVBoxLayout(self.strength_frame)
        strength_layout.setContentsMargins(10, 10, 10, 10)
        strength_layout.setSpacing(5)

        self.strength_label = QtWidgets.QLabel("Сложность пароля:")
        self.strength_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px;")
        strength_layout.addWidget(self.strength_label)

        self.strength_bar = QtWidgets.QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgb(80, 80, 80);
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: rgb(103, 155, 118);
                border-radius: 3px;
            }
        """)
        strength_layout.addWidget(self.strength_bar)

        self.strength_text = QtWidgets.QLabel("Минимум 6 символов")
        self.strength_text.setStyleSheet("color: rgb(255, 100, 100); font-size: 11px;")
        self.strength_text.setAlignment(Qt.AlignRight)
        strength_layout.addWidget(self.strength_text)

        self.verticalLayout.addWidget(self.strength_frame)

        # Добавляем растяжку
        self.verticalLayout.addStretch()

        # Кнопка сохранения
        self.save_button = QtWidgets.QPushButton("💾 Сохранить изменения")
        self.save_button.setMinimumHeight(45)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(103, 155, 118);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgb(93, 145, 108);
            }
            QPushButton:pressed {
                background-color: rgb(83, 135, 98);
            }
        """)
        self.verticalLayout.addWidget(self.save_button)

        # Кнопка отмены
        self.cancel_button = QtWidgets.QPushButton("✕ Отмена")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(70, 70, 70);
                color: rgb(200, 200, 200);
                border: 1px solid rgb(100, 100, 100);
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(100, 100, 100);
                color: white;
            }
        """)
        self.verticalLayout.addWidget(self.cancel_button)

        # Подключение сигналов
        self.new_input.textChanged.connect(self.check_password_strength)
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(Setting_Password.reject)

        self.retranslateUi(Setting_Password)
        QtCore.QMetaObject.connectSlotsByName(Setting_Password)

    def check_password_strength(self, password):
        """Проверка сложности пароля"""
        strength = 0

        if len(password) >= 6:
            strength += 25
        if any(c.isupper() for c in password):
            strength += 25
        if any(c.islower() for c in password):
            strength += 25
        if any(c in "!@#$%^&*()_+-=[]{};:,.<>?" for c in password):
            strength += 25

        self.strength_bar.setValue(strength)

        if strength < 25:
            self.strength_text.setText("Слишком простой пароль")
            self.strength_text.setStyleSheet("color: #ff4444; font-size: 11px;")
            self.strength_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #ff4444;
                    border-radius: 3px;
                }
            """)
        elif strength < 50:
            self.strength_text.setText("Слабый пароль")
            self.strength_text.setStyleSheet("color: #ffaa44; font-size: 11px;")
            self.strength_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #ffaa44;
                    border-radius: 3px;
                }
            """)
        elif strength < 75:
            self.strength_text.setText("Средний пароль")
            self.strength_text.setStyleSheet("color: #ffff44; font-size: 11px;")
            self.strength_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #ffff44;
                    border-radius: 3px;
                }
            """)
        else:
            self.strength_text.setText("Надежный пароль")
            self.strength_text.setStyleSheet("color: #44ff44; font-size: 11px;")
            self.strength_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #44ff44;
                    border-radius: 3px;
                }
            """)

    def retranslateUi(self, Setting_Password):
        _translate = QtCore.QCoreApplication.translate
        Setting_Password.setWindowTitle(_translate("Setting_Password", "IT-EcoSystem - Пароль"))

    def save_changes(self):
        current = self.current_input.text()
        new_pass = self.new_input.text()
        confirm = self.confirm_input.text()

        if not current or not new_pass or not confirm:
            QMessageBox.warning(self.parent(), "Ошибка", "Заполните все поля!")
            return

        if new_pass != confirm:
            QMessageBox.warning(self.parent(), "Ошибка", "Новый пароль и подтверждение не совпадают!")
            return

        if len(new_pass) < 6:
            QMessageBox.warning(self.parent(), "Ошибка", "Пароль должен содержать минимум 6 символов!")
            return

        # Здесь должна быть проверка текущего пароля и сохранение нового
        # success = update_password_in_db(self.user_id, current, new_pass)
        success = True  # Заглушка

        if success:
            QMessageBox.information(self.parent(), "Успех", "Пароль успешно изменен!")
            self.parent().accept()
        else:
            QMessageBox.critical(self.parent(), "Ошибка", "Не удалось изменить пароль. Проверьте текущий пароль.")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Setting_Password()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())