# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Setting_Nomber(object):
    def setupUi(self, Setting_Nomber):
        Setting_Nomber.setObjectName("Setting_Nomber")
        Setting_Nomber.resize(353, 198)
        Setting_Nomber.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Nomber)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TXT_Nomber = QtWidgets.QLabel(Setting_Nomber)
        self.TXT_Nomber.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_Nomber.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_Nomber.setObjectName("TXT_Nomber")
        self.verticalLayout.addWidget(self.TXT_Nomber)
        self.TQ_Nomber = QtWidgets.QTextEdit(Setting_Nomber)
        self.TQ_Nomber.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_Nomber.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.TQ_Nomber.setMarkdown("")
        self.TQ_Nomber.setObjectName("TQ_Nomber")
        self.verticalLayout.addWidget(self.TQ_Nomber)
        self.PB_Nomber = QtWidgets.QPushButton(Setting_Nomber)
        self.PB_Nomber.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(103, 155, 118);")
        self.PB_Nomber.setObjectName("PB_Nomber")
        self.verticalLayout.addWidget(self.PB_Nomber)

        self.retranslateUi(Setting_Nomber)
        QtCore.QMetaObject.connectSlotsByName(Setting_Nomber)

    def retranslateUi(self, Setting_Nomber):
        _translate = QtCore.QCoreApplication.translate
        Setting_Nomber.setWindowTitle(_translate("Setting_Nomber", "IT-EcoSystem"))
        self.TXT_Nomber.setText(_translate("Setting_Nomber", "Номер телефона "))
        self.TQ_Nomber.setPlaceholderText(_translate("Setting_Nomber", "Ведите новый номер телеона"))
        self.PB_Nomber.setText(_translate("Setting_Nomber", "Сохранить изменения"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Setting_Nomber = QtWidgets.QDialog()
    ui = Ui_Setting_Nomber()
    ui.setupUi(Setting_Nomber)
    Setting_Nomber.show()
    sys.exit(app.exec_())
