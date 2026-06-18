# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDialog
from datetime import datetime
from Server.db import update_birthdate_in_db


class Ui_Setting_Date(object):
    def setupUi(self, Setting_Date):
        Setting_Date.setObjectName("Setting_Date")
        Setting_Date.resize(400, 450)
        Setting_Date.setStyleSheet("""
            QDialog {
                background-color: rgb(47, 47, 47);
                border-radius: 10px;
            }
        """)

        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Date)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(15)

        # Заголовок
        self.title_label = QtWidgets.QLabel("📅 Изменение даты рождения")
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

        # Поле ввода
        self.date_input = QtWidgets.QLineEdit()
        self.date_input.setPlaceholderText("дд.мм.гггг")
        self.date_input.setMinimumHeight(40)
        self.date_input.setStyleSheet("""
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
        self.verticalLayout.addWidget(self.date_input)

        # Календарь
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: rgb(60, 60, 60);
                border-radius: 8px;
                padding: 5px;
            }
            QCalendarWidget QWidget {
                background-color: rgb(60, 60, 60);
                color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: rgb(60, 60, 60);
                color: white;
                selection-background-color: rgb(103, 155, 118);
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: rgb(103, 155, 118);
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QCalendarWidget QToolButton {
                background-color: transparent;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QCalendarWidget QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QCalendarWidget QSpinBox {
                background-color: rgb(80, 80, 80);
                color: white;
                border: 1px solid rgb(103, 155, 118);
                border-radius: 4px;
            }
        """)
        self.verticalLayout.addWidget(self.calendar)

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
        self.calendar.clicked.connect(self.update_date_from_calendar)
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(Setting_Date.reject)

        self.retranslateUi(Setting_Date)
        QtCore.QMetaObject.connectSlotsByName(Setting_Date)

    def update_date_from_calendar(self, date):
        self.date_input.setText(date.toString("dd.MM.yyyy"))

    def retranslateUi(self, Setting_Date):
        _translate = QtCore.QCoreApplication.translate
        Setting_Date.setWindowTitle(_translate("Setting_Date", "IT-EcoSystem - Дата рождения"))

    def save_changes(self):
        new_date = self.date_input.text().strip()
        if not new_date:
            QMessageBox.warning(self.parent(), "Ошибка", "Введите дату рождения!")
            return

        try:
            date_obj = datetime.strptime(new_date, "%d.%m.%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self.parent(), "Ошибка",
                                "Неверный формат даты!\nИспользуйте формат: дд.мм.гггг\nНапример: 15.05.1990")
            return

        # Здесь должна быть функция сохранения в БД
        # success = update_birthdate_in_db(self.current_user_id, formatted_date)
        success = True  # Заглушка

        if success:
            QMessageBox.information(self.parent(), "Успех", "Дата рождения успешно обновлена!")
            self.parent().accept()
        else:
            QMessageBox.critical(self.parent(), "Ошибка", "Не удалось обновить дату рождения.")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_Setting_Date()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())