# -*- coding: utf-8 -*-
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env'
load_dotenv(ENV_PATH, override=True)


class EmailService:
    """Сервис для отправки email-уведомлений через Яндекс.Почту"""

    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.yandex.ru')
        self.smtp_port = int(os.getenv('SMTP_PORT', 465))
        self.sender_email = os.getenv('SMTP_EMAIL')
        self.sender_password = os.getenv('SMTP_PASSWORD')

        # Проверяем настройки
        if not self.sender_email or not self.sender_password:
            print("⚠️ ВНИМАНИЕ: Настройки SMTP не заданы в .env файле!")
            print("Email-уведомления работать не будут.")
        else:
            print(f"✅ Настройки SMTP загружены: {self.smtp_server}:{self.smtp_port}")
            print(f"📧 Отправитель: {self.sender_email}")

    def send_verification_code(self, to_email, code, user_name=None):
        """
        Отправляет код подтверждения на email через Яндекс.Почту
        """
        if not self.sender_email or not self.sender_password:
            print("❌ Невозможно отправить email: не настроены SMTP параметры")
            # Для отладки показываем код в консоли
            print(f"🔑 Код подтверждения (отладка): {code}")
            return False

        try:
            # Создаем сообщение
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = '🔐 Восстановление пароля - IT-EcoSystem'

            # Текстовая версия письма
            text = f"""
            Здравствуйте{', ' + user_name if user_name else ''}!

            Вы запросили восстановление пароля в сервисном центре IT-EcoSystem.

            Ваш код подтверждения: {code}

            Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.

            С уважением,
            Команда IT-EcoSystem
            """

            # HTML версия письма
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        background-color: #f5f5f5;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 20px auto;
                        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                        border-radius: 20px;
                        padding: 40px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 48px;
                        color: #4CAF50;
                        margin-bottom: 10px;
                    }}
                    .title {{
                        color: #4CAF50;
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        color: #ffffff;
                        font-size: 16px;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }}
                    .code-container {{
                        background: linear-gradient(135deg, #333333 0%, #3d3d3d 100%);
                        border-radius: 15px;
                        padding: 30px;
                        text-align: center;
                        margin: 30px 0;
                        border: 2px solid #4CAF50;
                    }}
                    .code {{
                        font-family: 'Courier New', monospace;
                        font-size: 48px;
                        font-weight: bold;
                        color: #4CAF50;
                        letter-spacing: 5px;
                    }}
                    .footer {{
                        text-align: center;
                        color: #808080;
                        font-size: 14px;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #404040;
                    }}
                    .warning {{
                        background-color: rgba(255, 68, 68, 0.1);
                        border: 1px solid #ff4444;
                        border-radius: 10px;
                        padding: 15px;
                        margin-top: 20px;
                        color: #ff8888;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🚀 IT-EcoSystem</div>
                        <div class="title">Восстановление пароля</div>
                    </div>

                    <div class="content">
                        Здравствуйте{', ' + user_name if user_name else ''}!<br><br>

                        Вы запросили восстановление пароля в сервисном центре <strong>IT-EcoSystem</strong>.<br><br>

                        Для подтверждения действия используйте код ниже:
                    </div>

                    <div class="code-container">
                        <div class="code">{code}</div>
                    </div>

                    <div class="content">
                        Код действителен в течение 15 минут.<br>
                        Никому не сообщайте этот код!
                    </div>

                    <div class="warning">
                        ⚠️ Если вы не запрашивали восстановление пароля,<br>
                        просто проигнорируйте это письмо.
                    </div>

                    <div class="footer">
                        С уважением, команда IT-EcoSystem<br>
                        📍 Красноярск, Улица Микуцкого, 12<br>
                        📞 +7 (929) 356-23-78
                    </div>
                </div>
            </body>
            </html>
            """

            # Прикрепляем версии письма
            msg.attach(MIMEText(text, 'plain', 'utf-8'))
            msg.attach(MIMEText(html, 'html', 'utf-8'))

            # Отправляем письмо через Яндекс (SSL сразу, без starttls) [citation:1][citation:2]
            print(f"📧 Подключаюсь к {self.smtp_server}:{self.smtp_port}...")

            # Для порта 465 используем SMTP_SSL, для 587 - starttls
            if self.smtp_port == 465:
                # SSL/TLS сразу [citation:2][citation:6]
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
                server.login(self.sender_email, self.sender_password)
            else:
                # STARTTLS
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()
                server.login(self.sender_email, self.sender_password)

            server.send_message(msg)
            server.quit()

            print(f"✅ Код подтверждения отправлен на {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Ошибка авторизации: {e}")
            print("💡 Проверьте:")
            print("   - Используете ли вы пароль приложения, а не обычный пароль")
            print("   - Включена ли опция 'Пароли приложений' в настройках Яндекса")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP ошибка: {e}")
            return False
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_connection(self):
        """Тестирует подключение к SMTP серверу Яндекса"""
        try:
            print(f"🧪 Тестируем подключение к {self.smtp_server}:{self.smtp_port}...")

            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
                server.starttls()

            server.login(self.sender_email, self.sender_password)
            server.quit()
            print("✅ Тест подключения успешен!")
            return True
        except Exception as e:
            print(f"❌ Ошибка теста подключения: {e}")
            return False


# Глобальный экземпляр сервиса
email_service = EmailService()


def generate_verification_code(length=6):
    """
    Генерирует случайный код подтверждения
    """
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(to_email, code, user_name=None):
    """
    Упрощенная функция для отправки кода подтверждения
    """
    # Пытаемся отправить через SMTP
    success = email_service.send_verification_code(to_email, code, user_name)

    # Если не получилось, показываем код в консоли (для разработки)
    if not success:
        print("\n" + "=" * 50)
        print("⚠️ РЕЖИМ РАЗРАБОТКИ: Email не отправлен")
        print(f"📧 Код для {to_email}: {code}")
        print("=" * 50 + "\n")

        # Для отладки показываем в UI (раскомментируйте при необходимости)
        # from PyQt5.QtWidgets import QMessageBox
        # msg = QMessageBox()
        # msg.setWindowTitle("Режим разработки")
        # msg.setText(f"Код подтверждения: {code}\n(Email не отправлен - проверьте настройки SMTP)")
        # msg.setIcon(QMessageBox.Information)
        # msg.exec_()

        return True  # Возвращаем True, чтобы код работал в режиме разработки

    return success


def test_yandex_config():
    """Функция для тестирования конфигурации Яндекс.Почты"""
    print("=" * 50)
    print("🔧 ТЕСТИРОВАНИЕ НАСТРОЕК ЯНДЕКС.ПОЧТЫ")
    print("=" * 50)

    print(f"SMTP сервер: {email_service.smtp_server}")
    print(f"SMTP порт: {email_service.smtp_port}")
    print(f"Email отправителя: {email_service.sender_email}")
    print(f"Пароль задан: {'Да' if email_service.sender_password else 'Нет'}")

    if not email_service.sender_email or not email_service.sender_password:
        print("❌ Настройки неполные!")
        print("\n💡 Проверьте файл .env:")
        print("   SMTP_EMAIL=your-email@yandex.ru")
        print("   SMTP_PASSWORD=ваш_пароль_приложения")
        return False

    return email_service.test_connection()


if __name__ == "__main__":
    # Если файл запущен напрямую, тестируем подключение
    test_yandex_config()