import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingeneric-like Website")
        self.setGeometry(100, 100, 1000, 800)

        # Главный виджет и компоновщик
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Шапка (Header)
        header = QWidget()
        header.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            padding: 10px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("INGENERIC")
        logo.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(logo)

        menu_buttons = QHBoxLayout()
        menu_buttons.setSpacing(20)
        buttons = ["Главная", "Каталог", "О компании", "Услуги", "Контакты", "Корзина"]
        for text in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    border-radius: 4px;
                }
            """)
            menu_buttons.addWidget(btn)
        header_layout.addLayout(menu_buttons)
        main_layout.addWidget(header)

        # 2. Баннер (Slider)
        banner = QLabel()
        banner.setPixmap(QPixmap("banner.jpg").scaled(1000, 300, Qt.KeepAspectRatioByExpanding))
        banner.setStyleSheet("background-color: #3498db;")
        banner.setAlignment(Qt.AlignCenter)
        banner.setText("Добро пожаловать в Ingeneric!")
        banner.setFont(QFont("Arial", 24, QFont.Bold))
        banner.setStyleSheet("color: white;")
        main_layout.addWidget(banner)

        # 3. Основной контент (Товары/Услуги)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Пример блока товара
        product = QFrame()
        product.setFrameShape(QFrame.StyledPanel)
        product.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        product_layout = QVBoxLayout(product)
        product_layout.addWidget(QLabel("Название товара"))
        product_layout.addWidget(QLabel("Описание товара или услуги..."))
        product_layout.addWidget(QPushButton("Подробнее"))
        content_layout.addWidget(product)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # 4. Футер (Footer)
        footer = QWidget()
        footer.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            padding: 20px;
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.addWidget(QLabel("© 2025 Ingeneric. Все права защищены."))
        footer_layout.addStretch()
        footer_layout.addWidget(QLabel("Контакты: +7 (XXX) XXX-XX-XX"))
        main_layout.addWidget(footer)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
