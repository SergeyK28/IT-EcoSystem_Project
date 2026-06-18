# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from Server.db import update_name_surname_in_db


class Ui_Setting_Name_Surnamel(object):
    def setupUi(self, Setting_Name_Surnamel):
        Setting_Name_Surnamel.setObjectName("Setting_Name_Surnamel")
        Setting_Name_Surnamel.resize(400, 350)
        Setting_Name_Surnamel.setStyleSheet("""
            QDialog {
                background-color: rgb(47, 47, 47);
                border-radius: 10px;
            }
        """)

        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Name_Surnamel)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(15)

        # Заголовок
        self.title_label = QtWidgets.QLabel("👤 Изменение имени и фамилии")
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

        # Поле для имени
        self.name_label = QtWidgets.QLabel("Имя:")
        self.name_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 13px;")
        self.verticalLayout.addWidget(self.name_label)

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Введите новое имя")
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet("""
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
        self.verticalLayout.addWidget(self.name_input)

        # Поле для фамилии
        self.surname_label = QtWidgets.QLabel("Фамилия:")
        self.surname_label.setStyleSheet("color: rgb(180, 180, 180); font-size: 13px;")
        self.verticalLayout.addWidget(self.surname_label)

        self.surname_input = QtWidgets.QLineEdit()
        self.surname_input.setPlaceholderText("Введите новую фамилию")
        self.surname_input.setMinimumHeight(40)
        self.surname_input.setStyleSheet("""
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
        self.verticalLayout.addWidget(self.surname_input)

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
        self.cancel_button.clicked.connect(Setting_Name_Surnamel.reject)

        self.retranslateUi(Setting_Name_Surnamel)
        QtCore.QMetaObject.connectSlotsByName(Setting_Name_Surnamel)

    def retranslateUi(self, Setting_Name_Surnamel):
        _translate = QtCore.QCoreApplication.translate
        Setting_Name_Surnamel.setWindowTitle(_translate("Setting_Name_Surnamel", "IT-EcoSystem - Имя и фамилия"))

    def save_changes(self):
        new_name = self.name_input.text().strip()
        new_surname = self.surname_input.text().strip()

        if not new_name or not new_surname:
            QMessageBox.warning(self.parent(), "Ошибка", "Заполните оба поля!")
            return

        # Здесь должна быть функция сохранения в БД
        # success = update_name_surname_in_db(self.user_id, new_name, new_surname)
        success = True  # Заглушка

        if success:
            QMessageBox.information(self.parent(), "Успех", "Имя и фамилия успешно обновлены!")
            self.parent().accept()
        else:
            QMessageBox.critical(self.parent(), "Ошибка", "Не удалось обновить данные.")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Setting_Name_Surnamel()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())