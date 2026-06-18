from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QLinearGradient, QPainter, QFont
from PyQt5.QtWidgets import QSplashScreen, QProgressBar


class SplashScreen(QSplashScreen):
    """Красивый загрузочный экран с прогрессом"""

    def __init__(self):
        # Создаем pixmap с градиентом
        pixmap = QtGui.QPixmap(600, 400)
        pixmap.fill(Qt.transparent)

        super().__init__(pixmap)

        # Настройки окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Переменные для анимации
        self.progress_value = 0
        self.status_text = "Загрузка..."

        # Таймер для плавного увеличения прогресса
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

    def showEvent(self, event):
        """Запускаем анимацию при показе"""
        super().showEvent(event)
        self.timer.start(50)  # Обновление каждые 50 мс

    def drawContents(self, painter):
        """Отрисовка содержимого загрузочного экрана"""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Рисуем фон с градиентом
        rect = self.rect()

        # Основной градиент
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        gradient.setColorAt(0.0, QColor(26, 26, 26))  # #1a1a1a
        gradient.setColorAt(0.5, QColor(35, 35, 35))  # #232323
        gradient.setColorAt(1.0, QColor(26, 26, 26))  # #1a1a1a

        painter.fillRect(rect, gradient)

        # Рисуем рамку
        painter.setPen(QColor(76, 175, 80, 100))  # #4CAF50 с прозрачностью
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 20, 20)

        # Заголовок
        title_font = QFont("Arial", 28, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(rect.adjusted(0, 50, 0, 0), Qt.AlignHCenter, "IT-EcoSystem")

        # Подзаголовок
        subtitle_font = QFont("Arial", 14)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(176, 176, 176))  # #b0b0b0
        painter.drawText(rect.adjusted(0, 100, 0, 0), Qt.AlignHCenter, "Сервисный центр")

        # Рисуем полосу прогресса
        progress_rect = QtCore.QRect(
            rect.width() // 4,
            rect.height() - 80,
            rect.width() // 2,
            6
        )

        # Фон полосы
        painter.fillRect(progress_rect, QColor(60, 60, 60))

        # Заполнение
        if self.progress_value > 0:
            fill_width = int(progress_rect.width() * (self.progress_value / 100))
            fill_rect = QtCore.QRect(
                progress_rect.x(),
                progress_rect.y(),
                fill_width,
                progress_rect.height()
            )

            # Градиент для заполнения
            fill_gradient = QLinearGradient(
                progress_rect.x(), 0,
                progress_rect.x() + progress_rect.width(), 0
            )
            fill_gradient.setColorAt(0.0, QColor(76, 175, 80))  # #4CAF50
            fill_gradient.setColorAt(1.0, QColor(69, 160, 73))  # #45a049

            painter.fillRect(fill_rect, fill_gradient)

        # Текст статуса
        status_font = QFont("Arial", 10)
        painter.setFont(status_font)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(
            progress_rect.adjusted(0, 15, 0, 0),
            Qt.AlignHCenter,
            f"{self.status_text} ({self.progress_value}%)"
        )

        # Версия (внизу слева)
        version_font = QFont("Arial", 9)
        painter.setFont(version_font)
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(
            rect.adjusted(15, -15, 0, -15),
            Qt.AlignBottom | Qt.AlignLeft,
            "v1.0.0"
        )

        # Копирайт (внизу справа)
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(
            rect.adjusted(0, -15, -15, -15),
            Qt.AlignBottom | Qt.AlignRight,
            "© 2026"
        )

    def update_progress(self):
        """Обновление прогресса"""
        if self.progress_value < 100:
            self.progress_value += 1
            self.repaint()
        else:
            self.timer.stop()

    def set_progress(self, value, status_text=None):
        """Установка значения прогресса вручную"""
        self.progress_value = min(100, max(0, value))
        if status_text:
            self.status_text = status_text
        self.repaint()

    def show_message(self, message):
        """Показывает сообщение на загрузочном экране"""
        self.status_text = message
        self.repaint()


class LoadingThread(QtCore.QThread):
    """Поток для загрузки приложения"""
    progress_updated = pyqtSignal(int, str)
    finished_loading = pyqtSignal()

    def run(self):
        """Запуск загрузки"""
        # Имитация загрузки различных компонентов
        steps = [
            (10, "Инициализация базы данных..."),
            (25, "Загрузка модулей..."),
            (40, "Настройка интерфейса..."),
            (55, "Загрузка конфигурации..."),
            (70, "Проверка сессии..."),
            (85, "Подготовка главного окна..."),
            (95, "Завершение..."),
            (100, "Готово!")
        ]

        for progress, message in steps:
            self.progress_updated.emit(progress, message)
            self.msleep(300)  # Имитация времени загрузки

        self.finished_loading.emit()