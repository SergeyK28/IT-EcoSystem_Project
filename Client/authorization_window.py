# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from identification_window import IdenDialog
from profil_window import Ui_profil
from Server.db import check_user, get_user_id_by_login
from Server.db import get_user_data_by_login


class AuthDialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(615, 318)
        Dialog.setStyleSheet("background-color: rgb(47, 47, 47);")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.login = QtWidgets.QLineEdit(Dialog)
        self.login.setStyleSheet("background-color: rgb(47, 47, 47); color: rgb(255, 255, 255);")
        self.login.setPlaceholderText("Логин, Email")
        self.verticalLayout.addWidget(self.login)

        self.password = QtWidgets.QLineEdit(Dialog)
        self.password.setStyleSheet("background-color: rgb(47, 47, 47); color: rgb(255, 255, 255);")
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.verticalLayout.addWidget(self.password)

        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.sign_up = QtWidgets.QPushButton(Dialog)
        self.sign_up.setStyleSheet("background-color: rgb(103, 155, 118); color: rgb(255, 255, 255);")
        self.sign_up.setText("Вход в аккаунт")
        self.horizontalLayout.addWidget(self.sign_up)

        self.sign_in = QtWidgets.QPushButton(Dialog)
        self.sign_in.setStyleSheet("background-color: rgb(103, 155, 118); color: rgb(255, 255, 255);")
        self.sign_in.setText("Регистрация")
        self.horizontalLayout.addWidget(self.sign_in)

        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.sign_up.clicked.connect(self.open_profil_window)
        self.sign_in.clicked.connect(self.open_ide_window)

        # Переключение по Enter
        self.login.returnPressed.connect(self.password.setFocus)
        self.password.returnPressed.connect(self.sign_up.click)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        pass

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "IT-EcoSystem"))

    def open_ide_window(self):
        self.Dialog = QtWidgets.QDialog()
        self.ui = IdenDialog()
        self.ui.setupUi(self.Dialog)
        self.Dialog.show()

    def open_profil_window(self):
        login = self.login.text()
        password = self.password.text()
        if login and password:
            if check_user(login, password):
                user_data = get_user_data_by_login(login)
                self.Dialog = QtWidgets.QDialog()
                self.ui = Ui_profil(user_data["ID"], user_data["FirstName"] + " " + user_data["LastName"])
                self.ui.setupUi(self.Dialog)
                self.Dialog.show()
            else:
                QtWidgets.QMessageBox.warning(None, "Ошибка", "Неверный логин или пароль!")
        else:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Заполните все поля!")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = AuthDialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
