# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Setting_Email(object):
    def setupUi(self, Setting_Email):
        Setting_Email.setObjectName("Setting_Email")
        Setting_Email.resize(353, 198)
        Setting_Email.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.verticalLayout = QtWidgets.QVBoxLayout(Setting_Email)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TXT_Email = QtWidgets.QLabel(Setting_Email)
        self.TXT_Email.setMaximumSize(QtCore.QSize(16777215, 30))
        self.TXT_Email.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.TXT_Email.setObjectName("TXT_Email")
        self.verticalLayout.addWidget(self.TXT_Email)
        self.TQ_Email = QtWidgets.QTextEdit(Setting_Email)
        self.TQ_Email.setMaximumSize(QtCore.QSize(16777215, 35))
        self.TQ_Email.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.TQ_Email.setMarkdown("")
        self.TQ_Email.setObjectName("TQ_Email")
        self.verticalLayout.addWidget(self.TQ_Email)
        self.PB_Email = QtWidgets.QPushButton(Setting_Email)
        self.PB_Email.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(103, 155, 118);")
        self.PB_Email.setObjectName("PB_Email")
        self.verticalLayout.addWidget(self.PB_Email)

        self.retranslateUi(Setting_Email)
        QtCore.QMetaObject.connectSlotsByName(Setting_Email)

    def retranslateUi(self, Setting_Email):
        _translate = QtCore.QCoreApplication.translate
        Setting_Email.setWindowTitle(_translate("Setting_Email", "IT-EcoSystem"))
        self.TXT_Email.setText(_translate("Setting_Email", "Электронная почта"))
        self.TQ_Email.setPlaceholderText(_translate("Setting_Email", "Ведите новый Email"))
        self.PB_Email.setText(_translate("Setting_Email", "Сохранить изменения"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Setting_Email = QtWidgets.QDialog()
    ui = Ui_Setting_Email()
    ui.setupUi(Setting_Email)
    Setting_Email.show()
    sys.exit(app.exec_())
