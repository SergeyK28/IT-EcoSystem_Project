from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtWidgets import QDialog, QApplication
from main_window import Ui_main_window_Dialog
from session_manager import session
import sys
import os

# Добавляем корневую директорию проекта в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MainWindow(QDialog, Ui_main_window_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Устанавливаем ссылку на главное окно в менеджере сессии
        session.set_main_window(self)

        # Устанавливаем event filter на себя
        self.installEventFilter(self)

        # Проверяем, есть ли сохраненная сессия при запуске
        self.check_saved_session()

    def check_saved_session(self):
        """Проверяет наличие сохраненной сессии при запуске"""
        if session.is_authenticated():
            # Если есть сохраненная сессия, показываем уведомление
            from PyQt5.QtWidgets import QMessageBox
            from PyQt5.QtCore import QTimer

            # Используем QTimer для отложенного показа (чтобы главное окно успело загрузиться)
            QTimer.singleShot(500, self.show_welcome_back_message)

    def show_welcome_back_message(self):
        """Показывает приветственное сообщение при восстановлении сессии"""
        from PyQt5.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("С возвращением!")
        msg.setText(f"👋 С возвращением, {session.get_user_name()}!")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
                border-radius: 15px;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 14px;
                padding: 20px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        msg.exec_()

    def eventFilter(self, obj, event):
        """Фильтр событий для отслеживания кликов вне области поиска"""
        if event.type() == QEvent.MouseButtonPress:
            # Если виджет результатов видим
            if hasattr(self, 'search_results') and self.search_results.isVisible():
                # Получаем глобальные координаты клика
                global_pos = event.globalPos()

                # Проверяем, был ли клик по полю поиска
                search_global_rect = QtCore.QRect(
                    self.Search.mapToGlobal(QtCore.QPoint(0, 0)),
                    self.Search.size()
                )

                # Проверяем, был ли клик по результатам поиска
                if self.search_results.isVisible():
                    results_global_rect = QtCore.QRect(
                        self.search_results.mapToGlobal(QtCore.QPoint(0, 0)),
                        self.search_results.size()
                    )

                    # Если клик не по полю поиска и не по результатам - скрываем результаты
                    if not search_global_rect.contains(global_pos) and not results_global_rect.contains(global_pos):
                        self.search_results.hide()

        return super().eventFilter(obj, event)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())