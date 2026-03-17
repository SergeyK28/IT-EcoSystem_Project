# session_manager.py
from session_storage import SessionStorage


class SessionManager:
    """Менеджер сессии пользователя"""

    def __init__(self):
        self._user_id = None
        self._user_name = None
        self._main_window = None
        self._storage = SessionStorage()

        # При создании менеджера пытаемся загрузить сохраненную сессию
        self._load_saved_session()

    def _load_saved_session(self):
        """Загружает сохраненную сессию при инициализации"""
        try:
            session_data = self._storage.load_session()
            if session_data:
                self._user_id = session_data.get('user_id')
                self._user_name = session_data.get('user_name')
                print(f"🔄 Восстановлена сессия: {self._user_name} (ID: {self._user_id})")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить сохраненную сессию: {e}")

    def login(self, user_id, user_name, remember_me=True):
        """Выполняет вход пользователя"""
        self._user_id = user_id
        self._user_name = user_name

        # Сохраняем сессию, если нужно запомнить пользователя
        if remember_me:
            self._storage.save_session(user_id, user_name)

        print(f"✅ Пользователь {user_name} вошел в систему")

        # Обновляем интерфейс, если есть главное окно
        if self._main_window and hasattr(self._main_window, 'update_login_button'):
            self._main_window.update_login_button()

    def logout(self):
        """Выполняет выход пользователя"""
        print(f"👋 Пользователь {self._user_name} вышел из системы")

        # Очищаем данные сессии
        self._user_id = None
        self._user_name = None

        # Удаляем сохраненную сессию
        self._storage.clear_session()

        # Обновляем интерфейс, если есть главное окно
        if self._main_window and hasattr(self._main_window, 'update_login_button'):
            self._main_window.update_login_button()

    def is_authenticated(self):
        """Проверяет, авторизован ли пользователь"""
        return self._user_id is not None

    def get_user_id(self):
        """Возвращает ID текущего пользователя"""
        return self._user_id

    def get_user_name(self):
        """Возвращает имя текущего пользователя"""
        return self._user_name

    def set_main_window(self, main_window):
        """Устанавливает ссылку на главное окно"""
        self._main_window = main_window

        # Если есть сохраненная сессия, обновляем интерфейс
        if self.is_authenticated() and hasattr(main_window, 'update_login_button'):
            main_window.update_login_button()


# Создаем глобальный экземпляр менеджера сессии
session = SessionManager()