# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap

from Server.db import update_avatar_in_db, get_avatar_path_by_user_id
from Setting_profil import Ui_Setting_Profil

class Ui_profil(object):
    def __init__(self, user_id, full_name):
        self.user_id = user_id  # сохраняем ID пользователя
        self.full_name = full_name  # сохраняем имя и фамилию пользователяя

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(353, 516)
        Dialog.setStyleSheet("background-color: rgb(23, 23, 23);")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Dialog)
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.Ava_Profile = QtWidgets.QLabel(self.splitter)
        avatar_path = get_avatar_path_by_user_id(self.user_id)
        if avatar_path:
            ava_pixmap = QPixmap(avatar_path)
            self.Ava_Profile.setPixmap(ava_pixmap.scaled(75, 75, QtCore.Qt.KeepAspectRatio))
        else:
            st_ava = QPixmap('/home/sk28/PycharmProjects/IT-EcoSystem/Client/FotoPNG/standart_avatar.jpeg')
            self.Ava_Profile.setPixmap(st_ava.scaled(75, 75, QtCore.Qt.KeepAspectRatio))
        self.Ava_Profile.setMaximumSize(QtCore.QSize(70, 70))
        self.Ava_Profile.setStyleSheet("background-color: rgb(94, 92, 100);")
        self.Ava_Profile.setAlignment(QtCore.Qt.AlignCenter)
        self.Ava_Profile.mousePressEvent = self.load_avatar
        self.Name_Profile = QtWidgets.QLabel(self.splitter)
        self.Name_Profile.setMaximumSize(QtCore.QSize(16777215, 70))
        self.Name_Profile.setStyleSheet("background-color: rgb(94, 92, 100); color: rgb(255, 255, 255);")
        self.Name_Profile.setText(self.full_name)  # устанавливаем имя и фамилию пользователя
        self.verticalLayout_3.addWidget(self.splitter)
        spacerItem = QtWidgets.QSpacerItem(20, 150, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.pushButton_Settings = QtWidgets.QPushButton(Dialog)
        self.pushButton_Settings.setStyleSheet("background-color: rgb(103, 155, 118); color: rgb(255, 255, 255);")
        self.pushButton_Settings.setText("Настройки")
        self.verticalLayout.addWidget(self.pushButton_Settings)
        self.pushButton_Settings.clicked.connect(self.open_Ui_Setting_Profil)
        self.pushButton_Support = QtWidgets.QPushButton(Dialog)
        self.pushButton_Support.setStyleSheet("background-color: rgb(103, 155, 118); color: rgb(255, 255, 255);")
        self.pushButton_Support.setText("Чат поддержка")
        self.verticalLayout.addWidget(self.pushButton_Support)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.pushButton_Pay = QtWidgets.QPushButton(Dialog)
        self.pushButton_Pay.setStyleSheet("background-color: rgb(103, 155, 118); color: rgb(255, 255, 255);")
        self.pushButton_Pay.setText("Оплата")
        self.verticalLayout_2.addWidget(self.pushButton_Pay)
        self.pushButton_LegalDoc = QtWidgets.QPushButton(Dialog)
        self.pushButton_LegalDoc.setStyleSheet("background-color: rgb(103, 155, 118); color: rgb(255, 255, 255);")
        self.pushButton_LegalDoc.setText("Правовые документы")
        self.verticalLayout_2.addWidget(self.pushButton_LegalDoc)
        self.Nomber_Mail = QtWidgets.QLabel(Dialog)
        self.Nomber_Mail.setStyleSheet("color: rgb(154, 153, 150);")
        self.Nomber_Mail.setText("📞+79232942924 | 📧it.ecosystem.krsk@gmail.com")
        self.verticalLayout_2.addWidget(self.Nomber_Mail)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "IT-EcoSystem"))

    def open_Ui_Setting_Profil(self):
        self.Dialog = QtWidgets.QDialog()
        self.ui = Ui_Setting_Profil(self.user_id)  # Передаем user_id
        self.ui.setupUi(self.Dialog)
        self.Dialog.show()

    def load_avatar(self, event):
        file_path, _ = QFileDialog.getOpenFileName(None, "Выберите изображение", "", "Images (*.png *.xpm *.jpg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.Ava_Profile.setPixmap(pixmap.scaled(75, 75, QtCore.Qt.KeepAspectRatio))
                update_avatar_in_db(self.user_id, file_path)
            else:
                QMessageBox.warning(None, "Ошибка", "Не удалось загрузить изображение!")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    ui = Ui_profil()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())
