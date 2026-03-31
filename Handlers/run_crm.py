#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QDialog

# Добавляем путь к корневой директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Handlers.Employees.employee_login import EmployeeLoginDialog
from Handlers.main_CRM import MainCRMWindow
from Handlers.Employees.employee_session import employee_session
from Handlers.splash_screen_CRM import SplashScreen


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Устанавливаем иконку приложения
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "Pictures", "Screenshot from 2025-09-15 14-30-16.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QtGui.QIcon(icon_path))

    # Устанавливаем шрифт
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Устанавливаем темную палитру
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QPalette.Text, QtCore.Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    app.setPalette(palette)

    # Создаем главное окно (но не показываем его сразу)
    main_window = None

    # Показываем загрузочное окно
    splash = SplashScreen()

    # Функция для продолжения загрузки после сплэша
    def continue_loading():
        nonlocal main_window
        # Сначала показываем окно входа
        login_dialog = EmployeeLoginDialog()

        # Если пользователь успешно вошел
        if login_dialog.exec_() == QDialog.Accepted:
            employee_data = login_dialog.get_employee_data()
            if employee_data:
                # Выполняем вход в сессию
                employee_session.login(employee_data)

                # Создаем и показываем главное окно CRM
                main_window = MainCRMWindow()
                main_window.show()
        else:
            # Если пользователь закрыл окно входа, завершаем программу
            app.quit()

    # Подключаем сигнал завершения загрузки
    splash.finished.connect(continue_loading)

    # Запускаем загрузку
    splash.start_loading()

    # Запускаем event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()