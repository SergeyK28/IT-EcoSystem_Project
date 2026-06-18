# Handlers/employee_session.py
# -*- coding: utf-8 -*-
"""
Модуль управления сессией сотрудника.
Хранит данные текущего авторизованного сотрудника.
"""

from typing import Dict, Any, Optional


class EmployeeSessionManager:
    """
    Менеджер сессии сотрудника (Singleton паттерн).
    Хранит данные текущего авторизованного сотрудника.
    """

    _instance = None
    _authenticated = False  # Добавляем атрибут класса
    _employee_data = None
    _main_window = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(EmployeeSessionManager, cls).__new__(cls)
            cls._instance._authenticated = False
            cls._instance._employee_data = None
            cls._instance._main_window = None
        return cls._instance

    def login(self, employee_data: Dict[str, Any]) -> bool:
        """
        Выполняет вход сотрудника.

        Аргументы:
            employee_data: Словарь с данными сотрудника

        Returns:
            True если успешно
        """
        if employee_data:
            self._employee_data = employee_data
            self._authenticated = True
            return True
        return False

    def logout(self):
        """Выполняет выход сотрудника"""
        self._employee_data = None
        self._authenticated = False

    def is_authenticated(self) -> bool:
        """
        Проверяет, авторизован ли сотрудник.

        Returns:
            True если авторизован
        """
        return self._authenticated

    def get_employee_data(self) -> Optional[Dict[str, Any]]:
        """
        Возвращает данные текущего сотрудника.

        Returns:
            Словарь с данными сотрудника или None
        """
        if self.is_authenticated():
            return self._employee_data
        return None

    def get_employee_id(self) -> Optional[int]:
        """
        Возвращает ID текущего сотрудника.

        Returns:
            ID сотрудника или None
        """
        if self.is_authenticated() and self._employee_data:
            return self._employee_data.get('EmployeeID')
        return None

    def get_employee_name(self) -> Optional[str]:
        """
        Возвращает полное имя текущего сотрудника.

        Returns:
            Имя и фамилия сотрудника или None
        """
        if self.is_authenticated() and self._employee_data:
            first_name = self._employee_data.get('FirstName', '')
            last_name = self._employee_data.get('LastName', '')
            if first_name or last_name:
                return f"{first_name} {last_name}".strip()
            return None
        return None

    def get_employee_position(self) -> Optional[str]:
        """
        Возвращает должность текущего сотрудника.

        Returns:
            Должность сотрудника или None
        """
        if self.is_authenticated() and self._employee_data:
            return self._employee_data.get('Position')
        return None

    def get_employee_role(self) -> Optional[str]:
        """
        Возвращает роль текущего сотрудника.

        Returns:
            Роль сотрудника или None
        """
        if self.is_authenticated() and self._employee_data:
            return self._employee_data.get('Role')
        return None

    def has_role(self, role: str) -> bool:
        """
        Проверяет, имеет ли сотрудник указанную роль.

        Аргументы:
            role: Название роли ('admin', 'manager', 'technician', 'consultant')

        Returns:
            True если имеет
        """
        if self.is_authenticated() and self._employee_data:
            return self._employee_data.get('Role') == role
        return False

    def has_permission(self, permission: str) -> bool:
        """
        Проверяет, имеет ли сотрудник указанное разрешение.

        Аргументы:
            permission: Название разрешения

        Returns:
            True если имеет
        """
        if not self.is_authenticated():
            return False

        role = self._employee_data.get('Role')

        # Права доступа по ролям
        permissions = {
            'admin': ['view_orders', 'edit_orders', 'delete_orders', 'view_clients',
                      'edit_clients', 'delete_clients', 'view_finance', 'edit_finance',
                      'view_warehouse', 'edit_warehouse', 'view_reports', 'edit_settings',
                      'manage_employees'],
            'manager': ['view_orders', 'edit_orders', 'view_clients', 'edit_clients',
                        'view_finance', 'view_warehouse', 'view_reports'],
            'technician': ['view_orders', 'edit_orders', 'view_clients', 'view_warehouse'],
            'consultant': ['view_orders', 'view_clients']
        }

        return permission in permissions.get(role, [])

    def set_main_window(self, main_window):
        """
        Устанавливает ссылку на главное окно.

        Аргументы:
            main_window: Объект главного окна
        """
        self._main_window = main_window

    def get_main_window(self):
        """
        Возвращает ссылку на главное окно.

        Returns:
            Объект главного окна или None
        """
        return self._main_window


# Создаем глобальный экземпляр сессии
employee_session = EmployeeSessionManager()