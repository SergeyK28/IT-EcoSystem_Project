# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Setting_Password(object):
    def setupUi(self, Setting_Password):
        Setting_Password.setObjectName("Setting_Password")
        Setting_Password.resize(353, 374)
        Setting_Password.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Password)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TXT_Main_passwork = QtWidgets.QLabel(Setting_Password)
        self.TXT_Main_passwork.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_Main_passwork.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_Main_passwork.setObjectName("TXT_Main_passwork")
        self.verticalLayout.addWidget(self.TXT_Main_passwork)
        self.TQ_Main_passwork = QtWidgets.QTextEdit(Setting_Password)
        self.TQ_Main_passwork.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_Main_passwork.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.TQ_Main_passwork.setObjectName("TQ_Main_passwork")
        self.verticalLayout.addWidget(self.TQ_Main_passwork)
        self.TXT_New_passwork = QtWidgets.QLabel(Setting_Password)
        self.TXT_New_passwork.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_New_passwork.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_New_passwork.setObjectName("TXT_New_passwork")
        self.verticalLayout.addWidget(self.TXT_New_passwork)
        self.TQ_New_passwork = QtWidgets.QTextEdit(Setting_Password)
        self.TQ_New_passwork.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_New_passwork.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.TQ_New_passwork.setObjectName("TQ_New_passwork")
        self.verticalLayout.addWidget(self.TQ_New_passwork)
        self.TXT_Repeat_passwork = QtWidgets.QLabel(Setting_Password)
        self.TXT_Repeat_passwork.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_Repeat_passwork.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_Repeat_passwork.setObjectName("TXT_Repeat_passwork")
        self.verticalLayout.addWidget(self.TXT_Repeat_passwork)
        self.TQ_Repeat_passwork = QtWidgets.QTextEdit(Setting_Password)
        self.TQ_Repeat_passwork.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_Repeat_passwork.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.TQ_Repeat_passwork.setObjectName("TQ_Repeat_passwork")
        self.verticalLayout.addWidget(self.TQ_Repeat_passwork)
        self.PB_passwork = QtWidgets.QPushButton(Setting_Password)
        self.PB_passwork.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(103, 155, 118);")
        self.PB_passwork.setObjectName("PB_passwork")
        self.verticalLayout.addWidget(self.PB_passwork)

        self.retranslateUi(Setting_Password)
        QtCore.QMetaObject.connectSlotsByName(Setting_Password)

    def retranslateUi(self, Setting_Password):
        _translate = QtCore.QCoreApplication.translate
        Setting_Password.setWindowTitle(_translate("Setting_Password", "IT-EcoSystem"))
        self.TXT_Main_passwork.setText(_translate("Setting_Password", "Текущий пароль"))
        self.TQ_Main_passwork.setPlaceholderText(_translate("Setting_Password", "Ведите основной пароль"))
        self.TXT_New_passwork.setText(_translate("Setting_Password", "Новый пароль"))
        self.TQ_New_passwork.setPlaceholderText(_translate("Setting_Password", "Новый пароль"))
        self.TXT_Repeat_passwork.setText(_translate("Setting_Password", "Повторите пароль"))
        self.TQ_Repeat_passwork.setPlaceholderText(_translate("Setting_Password", "Подтвердите новый пароль"))
        self.PB_passwork.setText(_translate("Setting_Password", "Сохранить изменения"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Setting_Password = QtWidgets.QDialog()
    ui = Ui_Setting_Password()
    ui.setupUi(Setting_Password)
    Setting_Password.show()
    sys.exit(app.exec_())
