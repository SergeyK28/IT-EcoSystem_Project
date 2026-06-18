# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QLinearGradient, QFont
from PyQt5.QtWidgets import QWidget, QProgressBar, QLabel
import os
import sys


class SplashScreen(QWidget):
    """Красивый загрузочный экран с градиентом и прогрессом"""

    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 400)

        # Центрируем окно
        self.center()

        # Переменные для анимации
        self.progress_value = 0
        self.status_text = "Загрузка..."
        self.dot_count = 0

        # Таймеры
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.animate_dots)

        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)

    def center(self):
        """Центрирование окна на экране"""
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def animate_dots(self):
        """Простая анимация точек"""
        self.dot_count = (self.dot_count + 1) % 4
        self.update()

    def paintEvent(self, event):
        """Отрисовка содержимого загрузочного экрана"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = self.rect()

        # Основной градиент
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        gradient.setColorAt(0.0, QColor(26, 26, 26))  # #1a1a1a
        gradient.setColorAt(0.5, QColor(35, 35, 35))  # #232323
        gradient.setColorAt(1.0, QColor(26, 26, 26))  # #1a1a1a

        painter.fillRect(rect, gradient)

        # Рисуем рамку
        painter.setPen(QColor(103, 155, 118, 100))  # Зеленый с прозрачностью
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 20, 20)

        # Заголовок CRM
        title_font = QFont("Arial", 36, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(103, 155, 118))  # Зеленый цвет
        painter.drawText(rect.adjusted(0, 80, 0, 0), Qt.AlignHCenter, "CRM")

        # Подзаголовок IT-ECOSYSTEM
        subtitle_font = QFont("Arial", 14, QFont.Normal)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(rect.adjusted(0, 140, 0, 0), Qt.AlignHCenter, "IT-ECOSYSTEM")

        # Статус загрузки
        status_font = QFont("Arial", 12)
        painter.setFont(status_font)
        painter.setPen(QColor(150, 150, 150))

        # Добавляем анимированные точки к статусу
        dots = "." * self.dot_count
        status_with_dots = f"{self.status_text}{dots}"

        painter.drawText(
            rect.adjusted(0, 200, 0, 0),
            Qt.AlignHCenter,
            status_with_dots
        )

        # Рисуем полосу прогресса
        progress_rect = QtCore.QRect(
            rect.width() // 4,
            rect.height() - 100,
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
            fill_gradient.setColorAt(0.0, QColor(103, 155, 118))  # Зеленый
            fill_gradient.setColorAt(1.0, QColor(83, 135, 98))  # Темно-зеленый

            painter.fillRect(fill_rect, fill_gradient)

        # Текст процента
        percent_font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(percent_font)
        painter.setPen(QColor(103, 155, 118))

        percent_text = f"{self.progress_value}%"
        painter.drawText(
            progress_rect.adjusted(0, -25, 0, 0),
            Qt.AlignHCenter,
            percent_text
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

        # Тень (очень легкая)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 40))
        painter.drawRoundedRect(5, 5, self.width(), self.height(), 20, 20)

    def update_progress(self):
        """Обновление прогресса"""
        if self.progress_value < 100:
            self.progress_value += 1

            # Меняем статус в зависимости от прогресса
            if self.progress_value == 30:
                self.status_text = "Подключение к БД"
            elif self.progress_value == 60:
                self.status_text = "Загрузка модулей"
            elif self.progress_value == 90:
                self.status_text = "Почти готово"

            self.update()
        else:
            self.progress_timer.stop()
            self.dots_timer.stop()
            QTimer.singleShot(300, self.finish)

    def set_progress(self, value, status_text=None):
        """Установка значения прогресса вручную"""
        self.progress_value = min(100, max(0, value))
        if status_text:
            self.status_text = status_text
        self.update()

    def show_message(self, message):
        """Показывает сообщение на загрузочном экране"""
        self.status_text = message
        self.update()

    def start_loading(self):
        """Запуск загрузки"""
        self.show()
        self.dots_timer.start(400)
        self.progress_timer.start(25)  # 2.5 секунды до 100%
        QtWidgets.QApplication.processEvents()

    def finish(self):
        """Завершение загрузки"""
        self.hide()
        self.finished.emit()