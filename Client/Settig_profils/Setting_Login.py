# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Setting_Login(object):
    def setupUi(self, Setting_Login):
        Setting_Login.setObjectName("Setting_Login")
        Setting_Login.resize(353, 139)
        Setting_Login.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Login)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TXT_Login = QtWidgets.QLabel(Setting_Login)
        self.TXT_Login.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_Login.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_Login.setObjectName("TXT_Login")
        self.verticalLayout.addWidget(self.TXT_Login)
        self.TQ_Login = QtWidgets.QTextEdit(Setting_Login)
        self.TQ_Login.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_Login.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.TQ_Login.setObjectName("TQ_Login")
        self.verticalLayout.addWidget(self.TQ_Login)
        self.PB_Login = QtWidgets.QPushButton(Setting_Login)
        self.PB_Login.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(103, 155, 118);")
        self.PB_Login.setObjectName("PB_Login")
        self.verticalLayout.addWidget(self.PB_Login)

        self.retranslateUi(Setting_Login)
        QtCore.QMetaObject.connectSlotsByName(Setting_Login)

    def retranslateUi(self, Setting_Login):
        _translate = QtCore.QCoreApplication.translate
        Setting_Login.setWindowTitle(_translate("Setting_Login", "IT-EcoSystem"))
        self.TXT_Login.setText(_translate("Setting_Login", "Логин"))
        self.TQ_Login.setPlaceholderText(_translate("Setting_Login", "Ведите новый Логин"))
        self.PB_Login.setText(_translate("Setting_Login", "Сохранить изменения"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Setting_Login = QtWidgets.QDialog()
    ui = Ui_Setting_Login()
    ui.setupUi(Setting_Login)
    Setting_Login.show()
    sys.exit(app.exec_())
