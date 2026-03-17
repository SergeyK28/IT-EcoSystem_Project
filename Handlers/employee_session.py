# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class EmployeeSessionManager:
    """Класс для управления сессией сотрудника"""

    _instance = None
    _is_authenticated = False
    _employee_id = None
    _employee_name = None
    _employee_email = None
    _employee_position = None
    _employee_role = None
    _main_window = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmployeeSessionManager, cls).__new__(cls)
        return cls._instance

    @property
    def main_window(self):
        return self._main_window

    def set_main_window(self, main_window):
        self._main_window = main_window

    def login(self, employee_data):
        """Выполняет вход сотрудника"""
        self._is_authenticated = True
        self._employee_id = employee_data.get('EmployeeID')
        self._employee_name = f"{employee_data.get('FirstName', '')} {employee_data.get('LastName', '')}"
        self._employee_email = employee_data.get('Email')
        self._employee_position = employee_data.get('Position')
        self._employee_role = employee_data.get('Role')

        # Обновляем кнопку профиля в CRM
        if self._main_window and hasattr(self._main_window, 'update_profile_button'):
            self._main_window.update_profile_button()

    def logout(self):
        """Выполняет выход сотрудника"""
        self._is_authenticated = False
        self._employee_id = None
        self._employee_name = None
        self._employee_email = None
        self._employee_position = None
        self._employee_role = None

        if self._main_window and hasattr(self._main_window, 'update_profile_button'):
            self._main_window.update_profile_button()

    def is_authenticated(self):
        """Проверяет, авторизован ли сотрудник"""
        return self._is_authenticated

    def get_employee_id(self):
        """Возвращает ID сотрудника"""
        return self._employee_id

    def get_employee_name(self):
        """Возвращает имя сотрудника"""
        return self._employee_name

    def get_employee_email(self):
        """Возвращает email сотрудника"""
        return self._employee_email

    def get_employee_position(self):
        """Возвращает должность сотрудника"""
        return self._employee_position

    def get_employee_role(self):
        """Возвращает роль сотрудника"""
        return self._employee_role

    def has_permission(self, required_role):
        """Проверяет права доступа"""
        if not self._is_authenticated:
            return False

        # admin имеет все права
        if self._employee_role == 'admin':
            return True

        # Проверяем конкретную роль
        return self._employee_role == required_role


# Глобальный экземпляр менеджера сессии сотрудников
employee_session = EmployeeSessionManager()