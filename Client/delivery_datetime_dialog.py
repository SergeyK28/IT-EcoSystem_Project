# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCalendarWidget, QComboBox, \
    QTimeEdit, QMessageBox
from datetime import datetime, timedelta


class DeliveryDateTimeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_datetime = None
        self.setupUi()

    def setupUi(self):
        self.setObjectName("DeliveryDateTimeDialog")
        self.setWindowTitle("Выбор даты и времени визита")
        self.resize(500, 450)

        # Устанавливаем иконку
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../Pictures/Screenshot from 2025-09-15 14-30-16.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        # Темный стиль
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #232323, stop:1 #1a1a1a);
            }
            QLabel {
                color: white;
            }
            QCalendarWidget {
                background-color: #2a2a2a;
                color: white;
            }
            QCalendarWidget QWidget {
                background-color: #2a2a2a;
                color: white;
            }
            QCalendarWidget QToolButton {
                background-color: #3a3a3a;
                color: white;
                border-radius: 4px;
                padding: 5px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #4CAF50;
            }
            QCalendarWidget QMenu {
                background-color: #3a3a3a;
                color: white;
            }
            QCalendarWidget QSpinBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
            }
            QComboBox, QTimeEdit {
                background-color: #3a3a3a;
                color: white;
                border: 2px solid #4a4a4a;
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
            }
            QComboBox:hover, QTimeEdit:hover {
                border: 2px solid #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: white;
                selection-background-color: #4CAF50;
                border: 1px solid #4a4a4a;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton#confirmBtn {
                background-color: rgb(40, 167, 69);
            }
            QPushButton#confirmBtn:hover {
                background-color: rgb(50, 187, 79);
            }
            QPushButton#cancelBtn:hover {
                background-color: rgb(220, 53, 69);
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("📅 Выберите дату и время визита")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Пояснение
        info_label = QLabel("Выберите удобное для вас время, когда вы сможете принести технику в сервисный центр")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #b0b0b0; font-size: 12px; padding: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)

        # Календарь
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDateTime.currentDateTime().date())
        self.calendar.setMaximumDate(
            QDateTime.currentDateTime().date().addDays(30))  # Можно выбрать дату до 30 дней вперед

        # Запрещаем прошедшие даты
        self.calendar.setDateEditEnabled(True)
        self.calendar.setDateEditAcceptDelay(1000)

        main_layout.addWidget(self.calendar)

        # Выбор времени
        time_layout = QHBoxLayout()
        time_label = QLabel("Время:")
        time_label.setStyleSheet("font-size: 14px; font-weight: bold; min-width: 60px;")

        self.time_combo = QComboBox()
        self.time_combo.setMinimumWidth(200)

        # Добавляем доступные временные слоты (с 10:00 до 19:00 с интервалом 30 минут)
        start_time = datetime.strptime("10:00", "%H:%M")
        end_time = datetime.strptime("19:00", "%H:%M")
        current_time = start_time

        while current_time <= end_time:
            self.time_combo.addItem(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)

        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_combo)
        time_layout.addStretch()

        main_layout.addLayout(time_layout)

        # Информация о выбранном времени
        self.selected_info = QLabel("")
        self.selected_info.setStyleSheet(
            "color: #4CAF50; font-size: 14px; padding: 10px; background-color: #2a2a2a; border-radius: 5px;")
        self.selected_info.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.selected_info)

        # Обновляем информацию при изменении
        self.calendar.selectionChanged.connect(self.update_selected_info)
        self.time_combo.currentTextChanged.connect(self.update_selected_info)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.confirm_btn = QPushButton("✅ Подтвердить")
        self.confirm_btn.setObjectName("confirmBtn")
        self.confirm_btn.setMinimumHeight(40)
        self.confirm_btn.clicked.connect(self.confirm)

        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

        # Инициализируем информацию
        self.update_selected_info()

    def update_selected_info(self):
        """Обновляет информацию о выбранной дате и времени"""
        selected_date = self.calendar.selectedDate().toString("dd.MM.yyyy")
        selected_time = self.time_combo.currentText()

        # Проверяем, что выбранное время не прошло (если выбрана сегодняшняя дата)
        current_datetime = QDateTime.currentDateTime()
        selected_datetime_str = f"{self.calendar.selectedDate().toString('yyyy-MM-dd')} {selected_time}"
        selected_datetime = QDateTime.fromString(selected_datetime_str, "yyyy-MM-dd HH:mm")

        if selected_datetime < current_datetime:
            self.selected_info.setText("⚠️ Выбранное время уже прошло. Пожалуйста, выберите будущее время.")
            self.selected_info.setStyleSheet(
                "color: #ff6b6b; font-size: 14px; padding: 10px; background-color: #2a2a2a; border-radius: 5px;")
            self.confirm_btn.setEnabled(False)
        else:
            self.selected_info.setText(f"📅 Вы выбрали: {selected_date} в {selected_time}")
            self.selected_info.setStyleSheet(
                "color: #4CAF50; font-size: 14px; padding: 10px; background-color: #2a2a2a; border-radius: 5px;")
            self.confirm_btn.setEnabled(True)

    def confirm(self):
        """Подтверждает выбор"""
        selected_date = self.calendar.selectedDate()
        selected_time = self.time_combo.currentText()

        # Формируем строку с датой и временем
        datetime_str = f"{selected_date.toString('yyyy-MM-dd')} {selected_time}:00"
        self.selected_datetime = datetime_str

        self.accept()

    def get_selected_datetime(self):
        """Возвращает выбранную дату и время"""
        return self.selected_datetime