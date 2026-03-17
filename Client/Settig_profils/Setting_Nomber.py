# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox


class Ui_Setting_Nomber(object):
    def setupUi(self, Setting_Nomber):
        Setting_Nomber.setObjectName("Setting_Nomber")
        Setting_Nomber.resize(400, 250)
        Setting_Nomber.setStyleSheet("""
            QDialog {
                background-color: rgb(47, 47, 47);
                border-radius: 10px;
            }
        """)

        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Nomber)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(15)

        # Заголовок
        self.title_label = QtWidgets.QLabel("📱 Изменение номера телефона")
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

        # Информация
        info_label = QtWidgets.QLabel("Введите новый номер телефона в формате +7XXXXXXXXXX")
        info_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 12px;")
        info_label.setWordWrap(True)
        self.verticalLayout.addWidget(info_label)

        # Поле ввода
        self.phone_input = QtWidgets.QLineEdit()
        self.phone_input.setPlaceholderText("+7XXXXXXXXXX")
        self.phone_input.setMinimumHeight(40)
        self.phone_input.setMaxLength(12)
        self.phone_input.setStyleSheet("""
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
        self.verticalLayout.addWidget(self.phone_input)

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
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(Setting_Nomber.reject)

        self.retranslateUi(Setting_Nomber)
        QtCore.QMetaObject.connectSlotsByName(Setting_Nomber)

    def retranslateUi(self, Setting_Nomber):
        _translate = QtCore.QCoreApplication.translate
        Setting_Nomber.setWindowTitle(_translate("Setting_Nomber", "IT-EcoSystem - Номер телефона"))

    def save_changes(self):
        new_phone = self.phone_input.text().strip()

        if not new_phone:
            QMessageBox.warning(self.parent(), "Ошибка", "Введите номер телефона!")
            return

        if not new_phone.startswith("+7") or len(new_phone) != 12 or not new_phone[2:].isdigit():
            QMessageBox.warning(self.parent(), "Ошибка",
                                "Неверный формат номера!\nНомер должен начинаться с +7 и содержать 12 цифр.\n"
                                "Например: +79991234567")
            return

        # Здесь должна быть функция сохранения в БД
        # success = update_phone_in_db(self.user_id, new_phone)
        success = True  # Заглушка

        if success:
            QMessageBox.information(self.parent(), "Успех", "Номер телефона успешно обновлен!")
            self.parent().accept()
        else:
            QMessageBox.critical(self.parent(), "Ошибка", "Не удалось обновить номер телефона.")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Setting_Nomber()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())