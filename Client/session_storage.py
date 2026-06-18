# session_storage.py
import os
import json
import pickle
from pathlib import Path


class SessionStorage:
    """Класс для сохранения и загрузки сессии пользователя"""

    def __init__(self):
        # Создаем папку для хранения данных сессии в домашней директории пользователя
        self.storage_dir = Path.home() / '.it_ecosystem'
        self.session_file = self.storage_dir / 'session.dat'

        # Создаем папку, если её нет
        self.storage_dir.mkdir(exist_ok=True)

    def save_session(self, user_id, user_name):
        """Сохраняет данные сессии в файл"""
        try:
            session_data = {
                'user_id': user_id,
                'user_name': user_name,
                'remember_me': True
            }

            with open(self.session_file, 'wb') as f:
                pickle.dump(session_data, f)

            print(f"✅ Сессия сохранена для пользователя: {user_name}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения сессии: {e}")
            return False

    def load_session(self):
        """Загружает данные сессии из файла"""
        try:
            if not self.session_file.exists():
                return None

            with open(self.session_file, 'rb') as f:
                session_data = pickle.load(f)

            print(f"✅ Сессия загружена для пользователя: {session_data.get('user_name')}")
            return session_data
        except Exception as e:
            print(f"❌ Ошибка загрузки сессии: {e}")
            return None

    def clear_session(self):
        """Удаляет файл сессии"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                print("✅ Сессия очищена")
                return True
        except Exception as e:
            print(f"❌ Ошибка очистки сессии: {e}")
            return False

    def is_session_exists(self):
        """Проверяет, существует ли файл сессии"""
        return self.session_file.exists()