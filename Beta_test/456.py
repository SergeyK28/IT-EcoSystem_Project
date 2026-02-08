import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Кнопки с текстом")
        self.setGeometry(100, 100, 300, 200)

        # Тексты для кнопок
        self.button_texts = ["Кнопка 1", "Кнопка 2", "Кнопка 3", "Кнопка 4"]
        # Тексты для лейбла при нажатии на кнопку
        txt_id_1 = "text \n 123"
        self.label_texts = [txt_id_1, "Текст 2", "Текст 3", "Текст 4"]

        # Центральный виджет и лейаут
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Лейбл для вывода текста
        self.label = QLabel("Выберите кнопку")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Создаём кнопки
        self.buttons = []
        for i, text in enumerate(self.button_texts):
            button = QPushButton(text)
            button.setStyleSheet("background-color: gray;")
            button.clicked.connect(lambda checked, idx=i: self.on_button_click(idx))
            layout.addWidget(button)
            self.buttons.append(button)

        # Первая кнопка активна по умолчанию
        self.buttons[0].setStyleSheet("background-color: green;")
        self.current_active = 0

    def on_button_click(self, index):
        # Сбрасываем цвет всех кнопок
        for btn in self.buttons:
            btn.setStyleSheet("background-color: gray;")
        # Устанавливаем зелёный цвет для нажатой кнопки
        self.buttons[index].setStyleSheet("background-color: green;")
        # Меняем текст лейбла
        self.label.setText(self.label_texts[index])
        self.current_active = index

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
