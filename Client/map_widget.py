# -*- coding: utf-8 -*-
"""
Модуль для отображения интерактивной карты на основе 2GIS API
Использует Qt WebEngine для встраивания веб-содержимого
"""

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDialog, QHBoxLayout, QPushButton, QApplication
from PyQt5.QtGui import QFont

# ВАЖНО: Устанавливаем атрибут OpenGl ДО создания QApplication
# Это необходимо для корректной работы Qt WebEngine
if not QtCore.QCoreApplication.testAttribute(Qt.AA_ShareOpenGLContexts):
    QtCore.QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)

# Импортируем WebEngine только после установки атрибута
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings

    WEBENGINE_AVAILABLE = True
except ImportError as e:
    WEBENGINE_AVAILABLE = False
    print(f"⚠️ Qt WebEngineWidgets не доступен: {e}")
    print("Функция карты будет работать в режиме совместимости")


class MapWidget(QWidget):
    """
    Виджет для отображения интерактивной карты 2GIS через iframe и JavaScript API

    Особенности:
    - Встраивает карту 2GIS с кастомным маркером
    - Отображает информационное окно с контактами
    - Предоставляет кнопку для построения маршрута
    - Автоматически подстраивается под размер родительского виджета
    """

    def __init__(self, parent=None):
        """
        Инициализация виджета карты

        Args:
            parent: Родительский виджет (QWidget)
        """
        super().__init__(parent)
        self.web_view = None
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы
        layout.setSpacing(0)

        # Проверяем доступность WebEngine
        if not WEBENGINE_AVAILABLE:
            # Если WebEngine недоступен, показываем информационное сообщение
            self.show_fallback_message(layout)
            return

        try:
            # Создаем веб-виджет
            self.web_view = QWebEngineView()

            # Настройки веб-движка для лучшей производительности
            settings = self.web_view.settings()
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
            settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
            settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)

            # Загружаем HTML с картой
            self.load_map_html()

            layout.addWidget(self.web_view)

        except Exception as e:
            print(f"❌ Ошибка при создании WebEngineView: {e}")
            self.show_fallback_message(layout)

    def load_map_html(self):
        """
        Генерирует и загружает HTML-код с картой 2GIS и кастомными элементами

        Использует 2GIS JavaScript API для создания интерактивной карты
        с маркером, информационным окном и кнопкой маршрута
        """

        # Координаты организации (Красноярск, ул. Микуцкого, 12)
        LATITUDE = 56.118543  # Широта
        LONGITUDE = 92.923147  # Долгота

        # URL организации в 2GIS для кнопки маршрута
        ORGANIZATION_URL = "https://2gis.ru/krasnoyarsk/firm/70000001087708026"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* Сброс отступов для полного заполнения экрана */
                body, html, #map-container {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}

                /* Контейнер для карты */
                #map {{
                    width: 100%;
                    height: 100%;
                    position: absolute;
                    top: 0;
                    left: 0;
                    z-index: 1;
                }}

                /* Стилизованное информационное окно с контактами */
                .info-box {{
                    position: absolute;
                    bottom: 30px;
                    left: 30px;
                    background: rgba(255, 255, 255, 0.95);
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    z-index: 1000;
                    max-width: 280px;
                    backdrop-filter: blur(5px);
                    border: 1px solid rgba(255,255,255,0.2);
                    transition: transform 0.2s;
                }}

                .info-box:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 25px rgba(0,0,0,0.2);
                }}

                .info-box h3 {{
                    margin: 0 0 12px 0;
                    color: #4CAF50;
                    font-size: 18px;
                    border-bottom: 2px solid #4CAF50;
                    padding-bottom: 8px;
                }}

                .info-box p {{
                    margin: 8px 0;
                    color: #333;
                    font-size: 13px;
                    line-height: 1.5;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}

                .info-box .hours {{
                    margin-top: 15px;
                    padding-top: 12px;
                    border-top: 1px solid #e0e0e0;
                    background: rgba(76, 175, 80, 0.05);
                    border-radius: 6px;
                    padding: 12px;
                }}

                .info-box .hours p {{
                    margin: 5px 0;
                }}

                .info-box .hours b {{
                    color: #4CAF50;
                }}

                /* Стиль для emoji в тексте */
                .info-box .emoji {{
                    font-size: 16px;
                    min-width: 24px;
                }}
            </style>
        </head>
        <body>
            <div id="map-container">
                <div id="map"></div>

                <!-- Информационное окно с данными организации -->
                <div class="info-box">
                    <h3>🏪 IT-EcoSystem</h3>
                    <p><span class="emoji">📍</span> Красноярск, Улица Микуцкого, 12</p>
                    <p><span class="emoji">📞</span> +7 (999) 123-45-67</p>
                    <p><span class="emoji">📧</span> info@it-eco.ru</p>
                    <div class="hours">
                        <p><b>🕒 Режим работы:</b></p>
                        <p>Пн-Пт: 10:00-20:00</p>
                        <p>Сб-Вс: 12:00-19:00</p>
                    </div>
                </div>
            </div>

            <!-- Загрузка 2GIS API -->
            <script src="https://maps.api.2gis.ru/2.0/loader.js?pkg=full&lazy=true"></script>

            <script>
                // Глобальная переменная для объекта карты
                var map;

                // Функция инициализации карты после загрузки API
                DG.then(function() {{
                    console.log('2GIS API загружен, инициализация карты...');

                    try {{
                        // Создаем карту с центром в указанных координатах
                        map = DG.map('map', {{
                            center: [{LATITUDE}, {LONGITUDE}],  // [широта, долгота]
                            zoom: 17,                           // Уровень масштабирования
                            zoomControl: true,                  // Показывать кнопки зума
                            fullscreenControl: true,            // Кнопка полноэкранного режима
                            geoclicker: true                     // Возможность кликать по объектам
                        }});

                        console.log('Карта создана успешно');

                        // Создаем маркер на карте
                        var marker = DG.marker([{LATITUDE}, {LONGITUDE}])
                            .addTo(map);

                        console.log('Маркер добавлен');

                        // Добавляем всплывающее окно к маркеру
                        marker.bindPopup(
                            '<b>🏪 IT-EcoSystem</b><br>' +
                            '📍 Красноярск, Улица Микуцкого, 12<br>' +
                            '📞 +7 (999) 123-45-67<br>' +
                            '🕒 Пн-Пт: 10:00-20:00, Сб-Вс: 12:00-19:00'
                        ).openPopup();  // Открываем сразу

                        // Создаем кастомную кнопку для построения маршрута
                        var routeButton = DG.control({{
                            position: 'topleft'  // Размещаем слева сверху
                        }});

                        // Определяем внешний вид и поведение кнопки
                        routeButton.onAdd = function() {{
                            var button = document.createElement('button');
                            button.innerHTML = '🚗 Построить маршрут';
                            button.title = 'Открыть маршрут в 2GIS';
                            button.style.cssText = `
                                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                                color: white;
                                border: none;
                                border-radius: 30px;
                                padding: 10px 20px;
                                font-size: 14px;
                                font-weight: bold;
                                cursor: pointer;
                                margin: 10px;
                                box-shadow: 0 4px 10px rgba(76, 175, 80, 0.3);
                                transition: all 0.3s;
                                border: 1px solid rgba(255,255,255,0.2);
                                font-family: 'Segoe UI', Arial, sans-serif;
                            `;

                            // Добавляем hover эффект
                            button.onmouseover = function() {{
                                this.style.background = 'linear-gradient(135deg, #45a049 0%, #3d8b40 100%)';
                                this.style.transform = 'scale(1.05)';
                                this.style.boxShadow = '0 6px 15px rgba(76, 175, 80, 0.4)';
                            }};

                            button.onmouseout = function() {{
                                this.style.background = 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)';
                                this.style.transform = 'scale(1)';
                                this.style.boxShadow = '0 4px 10px rgba(76, 175, 80, 0.3)';
                            }};

                            // Обработчик клика - открываем страницу организации в новой вкладке
                            button.onclick = function() {{
                                window.open('{ORGANIZATION_URL}', '_blank');
                            }};

                            return button;
                        }};

                        // Добавляем кнопку на карту
                        routeButton.addTo(map);

                    }} catch (error) {{
                        console.error('Ошибка при инициализации карты:', error);
                        // Показываем сообщение об ошибке на странице
                        document.getElementById('map').innerHTML = 
                            '<div style="padding:20px;text-align:center;color:red;">' +
                            '❌ Ошибка загрузки карты. Пожалуйста, обновите страницу.' +
                            '</div>';
                    }}
                }});

                // Обработчик ошибок загрузки API
                window.addEventListener('error', function(e) {{
                    console.error('Ошибка загрузки ресурса:', e);
                }});
            </script>
        </body>
        </html>
        """

        try:
            # Загружаем HTML в WebEngine
            # Второй параметр - базовый URL для разрешения относительных путей
            self.web_view.setHtml(html_content, QUrl("https://maps.2gis.ru"))
        except Exception as e:
            print(f"❌ Ошибка при загрузке HTML в WebEngine: {e}")

    def show_fallback_message(self, layout):
        """
        Показывает сообщение-заглушку, когда WebEngine недоступен

        Args:
            layout: QLayout, в который добавляется сообщение
        """
        fallback_label = QtWidgets.QLabel(
            "🗺️ Карта временно недоступна\n\n"
            "Пожалуйста, откройте карту в браузере:\n"
            "https://2gis.ru/krasnoyarsk/firm/70000001087708026"
        )
        fallback_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #b0b0b0;
                font-size: 14px;
                padding: 30px;
                border-radius: 10px;
                qproperty-alignment: AlignCenter;
            }
        """)
        fallback_label.setWordWrap(True)
        layout.addWidget(fallback_label)

    def resizeEvent(self, event):
        """
        Обработчик изменения размера виджета

        Переопределяем для корректного изменения размера web_view
        """
        super().resizeEvent(event)
        if self.web_view:
            self.web_view.setGeometry(self.rect())


class MapDialog(QDialog):
    """
    Диалоговое окно с картой для отображения в отдельном окне

    Предоставляет полноэкранный режим и удобное управление
    """

    def __init__(self, parent=None):
        """
        Инициализация диалогового окна с картой

        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.setWindowTitle("🗺️ Наше местоположение - IT-EcoSystem")
        self.setModal(False)  # Не модальное окно (можно работать с главным окном)
        self.resize(1000, 700)  # Размер окна по умолчанию

        # Устанавливаем иконку окна
        self.setWindowIcon(self.get_app_icon())

        # Устанавливаем стиль окна
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)

        self.init_ui()

    def get_app_icon(self):
        """Получает иконку приложения или возвращает пустую иконку"""
        icon = QtGui.QIcon()
        try:
            # Пытаемся загрузить иконку из основного приложения
            app = QApplication.instance()
            if app and app.windowIcon():
                return app.windowIcon()
        except:
            pass
        return icon

    def init_ui(self):
        """Инициализация пользовательского интерфейса диалога"""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Добавляем виджет карты
        self.map_widget = MapWidget(self)
        layout.addWidget(self.map_widget)

        # Нижняя панель с кнопками
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Кнопка "Открыть в браузере"
        self.browser_btn = QPushButton("🌐 Открыть в браузере")
        self.browser_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        self.browser_btn.clicked.connect(self.open_in_browser)

        # Кнопка "Копировать координаты"
        self.copy_btn = QPushButton("📋 Копировать координаты")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_coordinates)

        # Растягивающееся пространство
        button_layout.addStretch()

        # Кнопка "Закрыть"
        self.close_btn = QPushButton("✕ Закрыть")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        # Добавляем кнопки в layout
        button_layout.addWidget(self.browser_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def open_in_browser(self):
        """Открывает карту в системном браузере"""
        import webbrowser
        url = "https://2gis.ru/krasnoyarsk/firm/70000001087708026"
        webbrowser.open(url)

        # Показываем уведомление
        self.show_notification("🌐 Карта открыта в браузере")

    def copy_coordinates(self):
        """Копирует координаты организации в буфер обмена"""
        clipboard = QApplication.clipboard()
        coordinates = "56.118543, 92.923147"
        clipboard.setText(coordinates)

        # Показываем уведомление
        self.show_notification("📋 Координаты скопированы")

    def show_notification(self, message):
        """
        Показывает временное уведомление в углу окна

        Args:
            message: Текст уведомления
        """
        # Создаем временное уведомление
        notification = QtWidgets.QLabel(message, self)
        notification.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        notification.adjustSize()

        # Размещаем в правом нижнем углу
        x = self.width() - notification.width() - 30
        y = self.height() - notification.height() - 80
        notification.move(x, y)

        notification.show()

        # Автоматически скрываем через 2 секунды
        QtCore.QTimer.singleShot(2000, notification.deleteLater)

    def keyPressEvent(self, event):
        """
        Обработчик нажатия клавиш

        Закрывает окно при нажатии Escape
        """
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        """
        Обработчик контекстного меню (по правой кнопке мыши)
        """
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
            }
        """)

        # Добавляем действия в меню
        open_browser_action = menu.addAction("🌐 Открыть в браузере")
        copy_coords_action = menu.addAction("📋 Копировать координаты")
        menu.addSeparator()
        close_action = menu.addAction("✕ Закрыть")

        # Показываем меню и обрабатываем выбор
        action = menu.exec_(event.globalPos())

        if action == open_browser_action:
            self.open_in_browser()
        elif action == copy_coords_action:
            self.copy_coordinates()
        elif action == close_action:
            self.close()


def show_map_dialog(parent=None):
    """
    Удобная функция для показа диалога с картой

    Args:
        parent: Родительский виджет

    Returns:
        MapDialog: Созданный диалог
    """
    dialog = MapDialog(parent)
    dialog.show()
    return dialog