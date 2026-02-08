# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import mysql.connector
from Server.db import update_name_surname_in_db

class Ui_Setting_Name_Surnamel(object):
    def setupUi(self, Setting_Name_Surnamel):
        Setting_Name_Surnamel.setObjectName("Setting_Name_Surnamel")
        Setting_Name_Surnamel.resize(353, 294)
        Setting_Name_Surnamel.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Name_Surnamel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TXT_Name = QtWidgets.QLabel(Setting_Name_Surnamel)
        self.TXT_Name.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_Name.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_Name.setObjectName("TXT_Name")
        self.verticalLayout.addWidget(self.TXT_Name)
        self.TQ_Name = QtWidgets.QTextEdit(Setting_Name_Surnamel)
        self.TQ_Name.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_Name.setStyleSheet("color: rgb(255, 255, 255);\n"
                                   "background-color: rgb(0, 0, 0);")
        self.TQ_Name.setObjectName("TQ_Name")
        self.verticalLayout.addWidget(self.TQ_Name)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.TXT_Surname = QtWidgets.QLabel(Setting_Name_Surnamel)
        self.TXT_Surname.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_Surname.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_Surname.setObjectName("TXT_Surname")
        self.verticalLayout.addWidget(self.TXT_Surname)
        self.TQ_Surname = QtWidgets.QTextEdit(Setting_Name_Surnamel)
        self.TQ_Surname.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_Surname.setStyleSheet("color: rgb(255, 255, 255);\n"
                                      "background-color: rgb(0, 0, 0);")
        self.TQ_Surname.setObjectName("TQ_Surname")
        self.verticalLayout.addWidget(self.TQ_Surname)
        self.PB_Name_Surnamel = QtWidgets.QPushButton(Setting_Name_Surnamel)
        self.PB_Name_Surnamel.setStyleSheet("color: rgb(255, 255, 255);\n"
                                            "background-color: rgb(103, 155, 118);")
        self.PB_Name_Surnamel.setObjectName("PB_Name_Surnamel")
        self.verticalLayout.addWidget(self.PB_Name_Surnamel)
        self.PB_Name_Surnamel.clicked.connect(self.save_changes)
        self.retranslateUi(Setting_Name_Surnamel)
        QtCore.QMetaObject.connectSlotsByName(Setting_Name_Surnamel)

    def retranslateUi(self, Setting_Name_Surnamel):
        _translate = QtCore.QCoreApplication.translate
        Setting_Name_Surnamel.setWindowTitle(_translate("Setting_Name_Surnamel", "IT-EcoSystem"))
        self.TXT_Name.setText(_translate("Setting_Name_Surnamel", "Имя"))
        self.TQ_Name.setPlaceholderText(_translate("Setting_Name_Surnamel", "Введите новое имя"))
        self.TXT_Surname.setText(_translate("Setting_Name_Surnamel", "Фамилия"))
        self.TQ_Surname.setPlaceholderText(_translate("Setting_Name_Surnamel", "Введите новую фамилию"))
        self.PB_Name_Surnamel.setText(_translate("Setting_Name_Surnamel", "Сохранить изменения"))

    def save_changes(self):
        new_first_name = self.TQ_Name.toPlainText().strip()
        new_last_name = self.TQ_Surname.toPlainText().strip()
        if new_first_name and new_last_name:
            updated = update_name_surname_in_db(self.user_id, new_first_name, new_last_name)
            if updated:
                QtWidgets.QMessageBox.information(self.PB_Name_Surnamel, "Успех", f"Имя и фамилия успешно обновлены.")
            else:
                QtWidgets.QMessageBox.critical(self.PB_Name_Surnamel, "Ошибка", "Не удалось обновить данные.")
        else:
            QtWidgets.QMessageBox.warning(self.PB_Name_Surnamel, "Внимание", "Заполните оба поля!")
