# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QCalendarWidget
import mysql.connector
from Server.db import update_birthdate_in_db
from datetime import datetime



class Ui_Setting_Date(object):
    def setupUi(self, Setting_Date):
        Setting_Date.setObjectName("Setting_Date")
        Setting_Date.resize(353, 350)  # Увеличим размер окна для размещения календаря
        Setting_Date.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Date)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TXT_Date = QtWidgets.QLabel(Setting_Date)
        self.TXT_Date.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_Date.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_Date.setObjectName("TXT_Date")
        self.verticalLayout.addWidget(self.TXT_Date)
        self.TQ_Date = QtWidgets.QTextEdit(Setting_Date)
        self.TQ_Date.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_Date.setStyleSheet("color: rgb(255, 255, 255);\n"
                                  "background-color: rgb(0, 0, 0);")
        self.TQ_Date.setObjectName("TQ_Date")
        self.verticalLayout.addWidget(self.TQ_Date)
        self.calendarWidget = QCalendarWidget(Setting_Date)  # Добавляем календарь
        self.calendarWidget.setGridVisible(True)  # Показываем сетку
        self.calendarWidget.setObjectName("calendarWidget")
        self.verticalLayout.addWidget(self.calendarWidget)
        self.PB_Date = QtWidgets.QPushButton(Setting_Date)
        self.PB_Date.setStyleSheet("color: rgb(255, 255, 255);\n"
                                  "background-color: rgb(103, 155, 118);")
        self.PB_Date.setObjectName("PB_Date")
        self.verticalLayout.addWidget(self.PB_Date)
        self.PB_Date.clicked.connect(self.save_changes)
        self.retranslateUi(Setting_Date)
        QtCore.QMetaObject.connectSlotsByName(Setting_Date)
        self.calendarWidget.clicked.connect(self.update_date_field)

    def update_date_field(self, date):
        self.TQ_Date.setText(date.toString("dd-MM-yyyy"))

    def retranslateUi(self, Setting_Date):
        _translate = QtCore.QCoreApplication.translate
        Setting_Date.setWindowTitle(_translate("Setting_Date", "IT-EcoSystem"))
        self.TXT_Date.setText(_translate("Setting_Date", "Дата рождения"))
        self.TQ_Date.setPlaceholderText(_translate("Setting_Date", "Введите новую дату рождения (дд-мм-гггг)"))
        self.PB_Date.setText(_translate("Setting_Date", "Сохранить изменения"))

    def save_changes(self):
        new_birthdate = self.TQ_Date.toPlainText().strip()
        # Проверка формата даты
        if len(new_birthdate) != 10 or new_birthdate.count('-') != 2:
            QMessageBox.warning(self.parent(), "Ошибка", "Неправильный формат даты! Используйте дд-мм-гггг.")
            return
        parts = new_birthdate.split('-')
        if not (parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit()):
            QMessageBox.warning(self.parent(), "Ошибка", "Дата должна содержать только цифры!")
            return
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
            QMessageBox.warning(self.parent(), "Ошибка", "Недействительная дата!")
            return
        # Преобразуем дату в формат 'YYYY-MM-DD'
        try:
            formatted_birthdate = datetime.strptime(new_birthdate, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            QMessageBox.warning(self.parent(), "Ошибка", "Недействительная дата!")
            return
        # Используем current_user_id из класса диалога
        success = update_birthdate_in_db(self.current_user_id, formatted_birthdate)
        if success:
            QMessageBox.information(self.parent(), "Успешно", "Дата рождения успешно обновлена.")
        else:
            QMessageBox.critical(self.parent(), "Ошибка", "Не удалось обновить дату рождения.")

    def retranslateUi(self, Setting_Date):
        _translate = QtCore.QCoreApplication.translate
        Setting_Date.setWindowTitle(_translate("Setting_Date", "IT-EcoSystem"))
        self.TXT_Date.setText(_translate("Setting_Date", "Дата рождения"))
        self.TQ_Date.setPlaceholderText(_translate("Setting_Date", "Ведите: дд-мм-гггг"))
        self.PB_Date.setText(_translate("Setting_Date", "Сохранить изменения"))

    def save_changes(self):
        new_birthdate = self.TQ_Date.toPlainText().strip()
        # Проверка формата даты
        if len(new_birthdate) != 10 or new_birthdate.count('-') != 2:
            QMessageBox.warning(self.parent(), "Ошибка", "Неправильный формат даты! Используйте дд-мм-гггг.")
            return
        parts = new_birthdate.split('-')
        if not (parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit()):
            QMessageBox.warning(self.parent(), "Ошибка", "Дата должна содержать только цифры!")
            return
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
            QMessageBox.warning(self.parent(), "Ошибка", "Недействительная дата!")
            return
        # Преобразуем дату в формат 'YYYY-MM-DD'
        try:
            formatted_birthdate = datetime.strptime(new_birthdate, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            QMessageBox.warning(self.parent(), "Ошибка", "Недействительная дата!")
            return
        # Используем current_user_id из класса диалога
        success = update_birthdate_in_db(self.current_user_id, formatted_birthdate)
        if success:
            QMessageBox.information(self.parent(), "Успешно", "Дата рождения успешно обновлена.")
        else:
            QMessageBox.critical(self.parent(), "Ошибка", "Не удалось обновить дату рождения.")

    def retranslateUi(self, Setting_Date):
        _translate = QtCore.QCoreApplication.translate
        Setting_Date.setWindowTitle(_translate("Setting_Date", "IT-EcoSystem"))
        self.TXT_Date.setText(_translate("Setting_Date", "Дата рождения"))
        self.TQ_Date.setPlaceholderText(_translate("Setting_Date", "Ведите новую ДР"))
        self.PB_Date.setText(_translate("Setting_Date", "Сохранить изменения"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Setting_Date = QtWidgets.QDialog()
    ui = Ui_Setting_Date()
    ui.setupUi(Setting_Date)
    Setting_Date.show()
    sys.exit(app.exec_())
