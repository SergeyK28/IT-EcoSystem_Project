# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog

from Settig_profils.Setting_Date import Ui_Setting_Date
from Settig_profils.Setting_Email import Ui_Setting_Email
from Settig_profils.Setting_Login import Ui_Setting_Login
from Settig_profils.Setting_Nomber import Ui_Setting_Nomber
from Settig_profils.Setting_Passwork import Ui_Setting_Password
from Settig_profils.Setting_Name_Surnamel import Ui_Setting_Name_Surnamel
from Server.db import update_name_surname_in_db
from Server.db import update_birthdate_in_db


class SettingDateDialog(QDialog, Ui_Setting_Date):
    def __init__(self, current_user_id, parent=None):
        super(SettingDateDialog, self).__init__(parent)
        self.setupUi(self)
        self.current_user_id = current_user_id

class SettingEmail(QtWidgets.QDialog, Ui_Setting_Email):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class SettingLogin(QtWidgets.QDialog, Ui_Setting_Login):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class SettingNomber(QtWidgets.QDialog, Ui_Setting_Nomber):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class SettingPassword(QtWidgets.QDialog, Ui_Setting_Password):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class SettingNameSurname(QtWidgets.QDialog, Ui_Setting_Name_Surnamel):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setupUi(self)

class Ui_Setting_Profil(object):
    def __init__(self, user_id):
        self.user_id = user_id

    def setupUi(self, Setting_Profil, user_id=None):
        Setting_Profil.setObjectName("Setting_Profil")
        Setting_Profil.resize(353, 516)
        Setting_Profil.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Setting_Profil)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.QVB_Login = QtWidgets.QVBoxLayout()
        self.QVB_Login.setObjectName("QVB_Login")
        self.pushButton_Name_Surname = QtWidgets.QPushButton(Setting_Profil)
        self.pushButton_Name_Surname.setStyleSheet("background-color: rgb(103, 155, 118);\ncolor: rgb(255, 255, 255);")
        self.pushButton_Name_Surname.setObjectName("pushButton_Name_Surname")
        self.QVB_Login.addWidget(self.pushButton_Name_Surname)
        self.pushButton_Login = QtWidgets.QPushButton(Setting_Profil)
        self.pushButton_Login.setStyleSheet("background-color: rgb(103, 155, 118);\ncolor: rgb(255, 255, 255);")
        self.pushButton_Login.setObjectName("pushButton_Login")
        self.QVB_Login.addWidget(self.pushButton_Login)
        self.pushButton_Date = QtWidgets.QPushButton(Setting_Profil)
        self.pushButton_Date.setStyleSheet("background-color: rgb(103, 155, 118);\ncolor: rgb(255, 255, 255);")
        self.pushButton_Date.setObjectName("pushButton_Date")
        self.QVB_Login.addWidget(self.pushButton_Date)
        self.verticalLayout_3.addLayout(self.QVB_Login)
        self.QVB_Contacts = QtWidgets.QVBoxLayout()
        self.QVB_Contacts.setObjectName("QVB_Contacts")
        self.pushButton_Passwork = QtWidgets.QPushButton(Setting_Profil)
        self.pushButton_Passwork.setStyleSheet("background-color: rgb(103, 155, 118);\ncolor: rgb(255, 255, 255);")
        self.pushButton_Passwork.setObjectName("pushButton_Passwork")
        self.QVB_Contacts.addWidget(self.pushButton_Passwork)
        self.pushButton_Nomber = QtWidgets.QPushButton(Setting_Profil)
        self.pushButton_Nomber.setStyleSheet("background-color: rgb(103, 155, 118);\ncolor: rgb(255, 255, 255);")
        self.pushButton_Nomber.setObjectName("pushButton_Nomber")
        self.QVB_Contacts.addWidget(self.pushButton_Nomber)
        self.pushButton_Email = QtWidgets.QPushButton(Setting_Profil)
        self.pushButton_Email.setStyleSheet("background-color: rgb(103, 155, 118);\ncolor: rgb(255, 255, 255);")
        self.pushButton_Email.setObjectName("pushButton_Email")
        self.QVB_Contacts.addWidget(self.pushButton_Email)
        self.verticalLayout_3.addLayout(self.QVB_Contacts)

        # Обработчики нажатия кнопок
        self.pushButton_Name_Surname.clicked.connect(lambda: SettingNameSurname(self.user_id).exec_())
        self.pushButton_Login.clicked.connect(lambda: SettingLogin().exec_())
        self.pushButton_Date.clicked.connect(self.open_setting_date)
        self.pushButton_Passwork.clicked.connect(lambda: SettingPassword().exec_())
        self.pushButton_Nomber.clicked.connect(lambda: SettingNomber().exec_())
        self.pushButton_Email.clicked.connect(lambda: SettingEmail().exec_())

        self.retranslateUi(Setting_Profil)
        QtCore.QMetaObject.connectSlotsByName(Setting_Profil)

    def retranslateUi(self, Setting_Profil):
        _translate = QtCore.QCoreApplication.translate
        Setting_Profil.setWindowTitle(_translate("Setting_Profil", "IT-EcoSystem"))
        self.pushButton_Name_Surname.setText(_translate("Setting_Profil", "Имя и Фамилия"))
        self.pushButton_Login.setText(_translate("Setting_Profil", "Никнейм"))
        self.pushButton_Date.setText(_translate("Setting_Profil", "Дата рождения"))
        self.pushButton_Passwork.setText(_translate("Setting_Profil", "Пароль"))
        self.pushButton_Nomber.setText(_translate("Setting_Profil", "Номер телефона"))
        self.pushButton_Email.setText(_translate("Setting_Profil", "Email"))

    def open_setting_date(self):
        dialog = SettingDateDialog(self.user_id)  # Передаем user_id
        dialog.exec_()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Setting_Profil = QtWidgets.QDialog()
    ui = Ui_Setting_Profil()
    ui.setupUi(Setting_Profil)
    Setting_Profil.show()
    sys.exit(app.exec_())