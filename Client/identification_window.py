# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from Server.db import register_user

class DateInputWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        input_frame = QtWidgets.QFrame()
        input_frame_layout = QtWidgets.QHBoxLayout(input_frame)
        input_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.Data = QtWidgets.QLineEdit()
        self.Data.setPlaceholderText("дд-мм-гггг")
        self.Data.setMaxLength(10)
        self.Data.setFixedWidth(165)
        self.Data.setStyleSheet("color: rgb(255, 255, 255);")
        self.Data.textEdited.connect(self.auto_format_date)
        self.btn_calendar = QtWidgets.QPushButton("📅")
        self.btn_calendar.setFixedWidth(30)
        self.btn_calendar.clicked.connect(self.show_calendar)
        input_frame_layout.addWidget(self.Data)
        input_frame_layout.addWidget(self.btn_calendar)
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QtCore.QDate.currentDate())
        self.calendar.clicked.connect(self.set_date_from_calendar)
        self.calendar.hide()
        layout.addWidget(input_frame)
        layout.addWidget(self.calendar)
        self.setLayout(layout)

    def auto_format_date(self, text):
        if not text:
            return
        if not text[-1:].isdigit() and text[-1:] != "-":
            self.Data.setText(text[:-1])
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите дату цифрами или используйте календарь.")
            return
        if len(text) == 2 and text.isdigit():
            self.Data.setText(text + "-")
        elif len(text) == 5 and text[2] == "-" and text[3:5].isdigit():
            self.Data.setText(text + "-")
        elif len(text) == 10 and text[2] == "-" and text[5] == "-" and text[6:].isdigit():
            if self.is_valid_date(text):
                self.focusNextChild()
            else:
                self.Data.setText(text[:-1])
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Некорректная дата.")

    def is_valid_date(self, date_str):
        try:
            day, month, year = map(int, date_str.split('.'))
            return QtCore.QDate.isValid(year, month, day)
        except Exception as e:
            print(e)
            return False

    def show_calendar(self):
        if self.calendar.isHidden():
            self.calendar.show()
        else:
            self.calendar.hide()

    def set_date_from_calendar(self, date):
        self.Data.setText(date.toString("дд-мм-гггг"))
        self.calendar.hide()
        self.focusNextChild()

class IdenDialog(QtWidgets.QDialog):
    def __init__(self):
        super(IdenDialog, self).__init__()
        self.setupUi(self)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(492, 391)
        Dialog.setStyleSheet("background-color: rgb(47, 47, 47);")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)

        self.Surname = QtWidgets.QLineEdit(Dialog)
        self.Surname.setStyleSheet("background-color: rgb(47, 47, 47); color: rgb(255, 255, 255);")
        self.Surname.setPlaceholderText("Фамилия")
        self.verticalLayout.addWidget(self.Surname)

        self.Name = QtWidgets.QLineEdit(Dialog)
        self.Name.setStyleSheet("background-color: rgb(47, 47, 47); color: rgb(255, 255, 255);")
        self.Name.setPlaceholderText("Имя")
        self.verticalLayout.addWidget(self.Name)

        self.Login = QtWidgets.QLineEdit(Dialog)
        self.Login.setStyleSheet("background-color: rgb(47, 47, 47); color: rgb(255, 255, 255);")
        self.Login.setPlaceholderText("Логин")
        self.verticalLayout.addWidget(self.Login)

        self.DateInput = DateInputWidget()
        self.verticalLayout.addWidget(self.DateInput)

        self.Nomber = QtWidgets.QLineEdit(Dialog)
        self.Nomber.setStyleSheet("color: rgb(255, 255, 255);")
        self.Nomber.setPlaceholderText("Телефон (+7...)")
        self.Nomber.setMaxLength(12)
        self.verticalLayout.addWidget(self.Nomber)

        self.Email = QtWidgets.QLineEdit(Dialog)
        self.Email.setStyleSheet("color: rgb(255, 255, 255);")
        self.Email.setPlaceholderText("Email")
        self.verticalLayout.addWidget(self.Email)

        self.Create_password = QtWidgets.QLineEdit(Dialog)
        self.Create_password.setStyleSheet("color: rgb(255, 255, 255);")
        self.Create_password.setPlaceholderText("Пароль")
        self.Create_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.verticalLayout.addWidget(self.Create_password)

        self.Repeat_create_password = QtWidgets.QLineEdit(Dialog)
        self.Repeat_create_password.setStyleSheet("color: rgb(255, 255, 255);")
        self.Repeat_create_password.setPlaceholderText("Повторный пароль")
        self.Repeat_create_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.verticalLayout.addWidget(self.Repeat_create_password)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.User_agreement = QtWidgets.QCheckBox(Dialog)
        self.User_agreement.setStyleSheet("color: rgb(255, 255, 255);")
        self.User_agreement.setText("Я прочитал и принимаю условия\nпользовательского соглашения\nполностью.")
        self.User_agreement.stateChanged.connect(self.toggle_register_button)
        self.horizontalLayout_2.addWidget(self.User_agreement)

        self.Creat_account = QtWidgets.QPushButton(Dialog)
        self.Creat_account.setStyleSheet("background-color: rgb(103, 155, 118); color: rgb(255, 255, 255);")
        self.Creat_account.setText("Зарегистрироваться")
        self.Creat_account.setEnabled(False)
        self.Creat_account.clicked.connect(self.register)
        self.horizontalLayout_2.addWidget(self.Creat_account)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        # Переключение по Enter
        self.Surname.returnPressed.connect(self.Name.setFocus)
        self.Name.returnPressed.connect(self.Login.setFocus)
        self.Login.returnPressed.connect(self.DateInput.Data.setFocus)
        self.DateInput.Data.returnPressed.connect(self.Nomber.setFocus)
        self.Nomber.returnPressed.connect(self.Email.setFocus)
        self.Email.returnPressed.connect(self.Create_password.setFocus)
        self.Create_password.returnPressed.connect(self.Repeat_create_password.setFocus)
        self.Repeat_create_password.returnPressed.connect(self.Creat_account.setFocus)

    def toggle_register_button(self, state):
        self.Creat_account.setEnabled(state == QtCore.Qt.Checked)

    def register(self):
        surname = self.Surname.text()
        first_name = self.Name.text()
        login = self.Login.text()
        password = self.Create_password.text()
        repeat_password = self.Repeat_create_password.text()
        phone = self.Nomber.text()
        email = self.Email.text()  # Добавляем получение электронного адреса

        if not all([surname, first_name, login, password, repeat_password, phone, email]):
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Заполните все поля!")
            return
        if password != repeat_password:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Пароли не совпадают!")
            return
        if not phone.startswith("+7") or len(phone) != 12:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Телефон должен начинаться с +7 и быть 12 символов!")
            return

        # Передача всех пяти аргументов
        if register_user(surname, first_name, login, password, email):
            QtWidgets.QMessageBox.information(None, "Успех", "Регистрация прошла успешно!")
            self.close()
        else:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Ошибка регистрации!")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = IdenDialog()
    dialog.show()
    sys.exit(app.exec_())