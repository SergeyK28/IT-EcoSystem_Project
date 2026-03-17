# Server/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Абсолютный путь к .env файлу
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'

# Принудительная загрузка с override
load_dotenv(ENV_FILE, override=True)


class Config:
    # База данных - берем напрямую из os.environ
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME', 'SQL_IT_EcoSyttem_BD')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))

    @classmethod
    def print_config(cls):
        """Для отладки"""
        print("=== КОНФИГУРАЦИЯ БД ===")
        print(f"DB_HOST: {cls.DB_HOST}")
        print(f"DB_USER: {cls.DB_USER}")
        print(f"DB_PASSWORD: {'*' * len(cls.DB_PASSWORD) if cls.DB_PASSWORD else 'НЕ УСТАНОВЛЕН'}")
        print(f"DB_NAME: {cls.DB_NAME}")
        print(f"DB_PORT: {cls.DB_PORT}")
        print("=" * 30)