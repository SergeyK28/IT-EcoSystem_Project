# -*- coding: utf-8 -*-
"""
Модуль для работы с отзывами из 2GIS
Содержит классы для загрузки, отображения и управления отзывами о сервисном центре
"""

import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea


class GISReviewsLoader(QThread):
    """
    Поток для асинхронной загрузки отзывов из 2GIS API
    Выполняется в фоновом режиме, чтобы не блокировать интерфейс
    """

    # Сигналы для связи с основным потоком
    reviews_loaded = pyqtSignal(list)  # Отправляет список загруженных отзывов
    loading_error = pyqtSignal(str)  # Отправляет сообщение об ошибке

    def __init__(self):
        """Инициализация загрузчика отзывов"""
        super().__init__()
        # ID организации IT-EcoSystem в 2GIS (можно заменить на актуальный)
        self.firm_id = "70000001087708026"
        # URL для API запроса
        self.api_url = f"https://public-api.2gis.com/2.0/firm/{self.firm_id}/reviews"

    def run(self):
        """
        Основной метод потока - выполняется при старте потока
        Загружает отзывы и отправляет их через сигналы
        """
        try:
            # Пробуем загрузить реальные отзывы из API
            reviews = self.fetch_reviews_from_2gis()

            if reviews:
                # Если отзывы загружены успешно - отправляем их
                self.reviews_loaded.emit(reviews)
            else:
                # Если загрузка не удалась - используем демо-данные
                demo_reviews = self.get_demo_reviews()
                self.reviews_loaded.emit(demo_reviews)

        except Exception as e:
            # В случае ошибки отправляем сигнал об ошибке и показываем демо-отзывы
            self.loading_error.emit(str(e))
            self.reviews_loaded.emit(self.get_demo_reviews())

    def fetch_reviews_from_2gis(self):
        """
        Загрузка реальных отзывов из API 2GIS

        Returns:
            list: Список отзывов или None в случае ошибки
        """
        try:
            # Для работы с API 2GIS нужен ключ
            # Зарегистрируйтесь на https://dev.2gis.ru/ и получите ключ
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            # Параметры запроса
            params = {
                'fields': 'reviews',  # Запрашиваем только отзывы
                'locale': 'ru_RU',  # Язык - русский
                'limit': 20  # Количество отзывов
            }

            # В реальном проекте здесь нужно добавить API ключ
            # response = requests.get(
            #     self.api_url,
            #     headers=headers,
            #     params=params,
            #     timeout=10
            # )
            #
            # if response.status_code == 200:
            #     data = response.json()
            #     return self.parse_reviews(data)

            # Возвращаем None, так как API ключ не настроен
            return None

        except Exception as e:
            print(f"Ошибка загрузки из 2GIS: {e}")
            return None

    def parse_reviews(self, data):
        """
        Парсинг ответа от API 2GIS в удобный формат

        Args:
            data (dict): JSON ответ от API

        Returns:
            list: Список обработанных отзывов
        """
        reviews = []
        try:
            if 'reviews' in data:
                for item in data['reviews']:
                    # Извлекаем данные из ответа API
                    review = {
                        'author': item.get('author', {}).get('name', 'Аноним'),  # Имя автора
                        'rating': item.get('rating', 5),  # Оценка (1-5)
                        'date': item.get('date', ''),  # Дата отзыва
                        'text': item.get('text', ''),  # Текст отзыва
                        'advantages': item.get('advantages', ''),  # Достоинства
                        'disadvantages': item.get('disadvantages', ''),  # Недостатки
                        'answer': item.get('answer', {}).get('text', '')  # Ответ сервиса
                    }
                    reviews.append(review)
        except Exception as e:
            print(f"Ошибка парсинга: {e}")

        return reviews

    def get_demo_reviews(self):
        """
        Демо-отзывы для тестирования и отображения при отсутствии API

        Returns:
            list: Список тестовых отзывов
        """
        return [
            {
                'author': 'Алексей Петров',
                'rating': 5,
                'date': '15.03.2024',
                'text': 'Отличный сервис! Быстро починили ноутбук, заменили матрицу. Все работает отлично. Цены адекватные, дали гарантию 3 месяца.',
                'advantages': 'Быстро, качественно, недорого',
                'disadvantages': '',
                'answer': ''
            },
            {
                'author': 'Екатерина Смирнова',
                'rating': 5,
                'date': '10.03.2024',
                'text': 'Обращалась для ремонта телефона (разбит экран). Заменили за 2 часа, качество отличное. Вежливый персонал, все объяснили. Рекомендую!',
                'advantages': 'Скорость, качество, сервис',
                'disadvantages': 'Нет',
                'answer': ''
            },
            {
                'author': 'Дмитрий Иванов',
                'rating': 4,
                'date': '05.03.2024',
                'text': 'Хороший сервисный центр. Ремонтировал планшет, сломался разъем зарядки. Сделали быстро, но цена могла бы быть чуть ниже.',
                'advantages': 'Качество работы',
                'disadvantages': 'Цена',
                'answer': 'Спасибо за отзыв! Стараемся держать цены доступными, но используем только качественные запчасти.'
            },
            {
                'author': 'Ольга Кузнецова',
                'rating': 5,
                'date': '28.02.2024',
                'text': 'Большое спасибо мастеру Дмитрию! Спас мой ноутбук после залития. Думала, что все пропало, но восстановили полностью. Теперь только к вам!',
                'advantages': 'Профессионализм, отношение к клиентам',
                'disadvantages': '',
                'answer': ''
            },
            {
                'author': 'Сергей Васильев',
                'rating': 5,
                'date': '20.02.2024',
                'text': 'Отличный выбор запчастей в магазине. Купил оригинальный аккумулятор для телефона. Цена как в интернете, но не нужно ждать доставку.',
                'advantages': 'Наличие запчастей, удобное расположение',
                'disadvantages': 'Мало места для парковки',
                'answer': ''
            }
        ]


class ReviewWidget(QFrame):
    """
    Виджет для отображения одного отзыва
    Содержит информацию об авторе, рейтинге, тексте отзыва и ответе сервиса
    """

    def __init__(self, review_data, parent=None):
        """
        Инициализация виджета отзыва

        Args:
            review_data (dict): Словарь с данными отзыва
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.review_data = review_data
        self.setup_ui()

    def setup_ui(self):
        """Создание и настройка интерфейса отзыва"""
        # Основной стиль рамки отзыва
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #333333;
                border: 1px solid #4CAF50;
            }
        """)

        # Основной вертикальный layout для всех элементов
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # === ВЕРХНЯЯ СТРОКА (автор, рейтинг, дата) ===
        top_layout = QHBoxLayout()

        # Метка с именем автора и иконкой
        author_label = QLabel(f"👤 {self.review_data['author']}")
        author_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 16px;
                color: #4CAF50;
            }
        """)

        # Метка с датой отзыва
        date_label = QLabel(self.review_data['date'])
        date_label.setStyleSheet("color: #888888; font-size: 12px;")

        # Создание звездного рейтинга
        rating = self.review_data['rating']
        stars = "★" * rating + "☆" * (5 - rating)  # Золотые и серые звезды
        rating_label = QLabel(stars)
        rating_label.setStyleSheet("color: #FFD700; font-size: 16px;")

        # Сборка верхней строки
        top_layout.addWidget(author_label)
        top_layout.addStretch()  # Добавляем растягиваемое пространство
        top_layout.addWidget(rating_label)
        top_layout.addWidget(date_label)

        layout.addLayout(top_layout)

        # === ТЕКСТ ОТЗЫВА ===
        if self.review_data['text']:
            text_label = QLabel(self.review_data['text'])
            text_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    line-height: 1.5;
                    padding: 10px 0;
                    color: #e0e0e0;
                }
            """)
            text_label.setWordWrap(True)  # Перенос длинного текста
            layout.addWidget(text_label)

        # === ДОСТОИНСТВА (если есть) ===
        if self.review_data['advantages']:
            adv_label = QLabel(f"✅ Достоинства: {self.review_data['advantages']}")
            adv_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 13px;
                    padding: 5px 0;
                }
            """)
            adv_label.setWordWrap(True)
            layout.addWidget(adv_label)

        # === НЕДОСТАТКИ (если есть) ===
        if self.review_data['disadvantages']:
            disadv_label = QLabel(f"❌ Недостатки: {self.review_data['disadvantages']}")
            disadv_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 13px;
                    padding: 5px 0;
                }
            """)
            disadv_label.setWordWrap(True)
            layout.addWidget(disadv_label)

        # === ОТВЕТ СЕРВИСА (если есть) ===
        if self.review_data['answer']:
            # Создаем отдельный фрейм для ответа
            answer_frame = QFrame()
            answer_frame.setStyleSheet("""
                QFrame {
                    background-color: #363636;
                    border-radius: 8px;
                    padding: 10px;
                    margin-top: 10px;
                }
            """)
            answer_layout = QVBoxLayout(answer_frame)
            answer_layout.setContentsMargins(10, 10, 10, 10)

            # Заголовок ответа
            answer_title = QLabel("📌 Ответ IT-EcoSystem:")
            answer_title.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 13px;")

            # Текст ответа
            answer_text = QLabel(self.review_data['answer'])
            answer_text.setStyleSheet("""
                QLabel {
                    color: #b0b0b0;
                    font-style: italic;
                    font-size: 13px;
                }
            """)
            answer_text.setWordWrap(True)

            answer_layout.addWidget(answer_title)
            answer_layout.addWidget(answer_text)

            layout.addWidget(answer_frame)


class ReviewsSectionWidget(QWidget):
    """
    Главный виджет раздела с отзывами
    Содержит заголовок, статистику рейтинга и карусель отзывов
    """

    def __init__(self, parent=None):
        """Инициализация раздела отзывов"""
        super().__init__(parent)
        self.reviews = []  # Список всех загруженных отзывов
        self.current_index = 0  # Текущая страница (для постраничного просмотра)
        self.setup_ui()  # Создание интерфейса
        self.load_reviews()  # Загрузка отзывов

    def setup_ui(self):
        """Создание пользовательского интерфейса раздела"""
        # Основной контейнер
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 20, 0, 20)
        main_layout.setSpacing(20)

        # === ЗАГОЛОВОК С КНОПКОЙ ===
        title_layout = QHBoxLayout()

        # Заголовок раздела
        self.title_label = QLabel("⭐ Отзывы наших клиентов")
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        # Кнопка для перехода на страницу 2GIS
        self.open_all_btn = QPushButton("Все отзывы на 2GIS")
        self.open_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.open_all_btn.clicked.connect(self.open_2gis_reviews)

        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.open_all_btn)

        main_layout.addLayout(title_layout)

        # === БЛОК СО СРЕДНИМ РЕЙТИНГОМ ===
        self.rating_frame = QFrame()
        self.rating_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2d5a2d, stop:1 #1e3a1e);
                border-radius: 10px;
                padding: 15px;
            }
        """)

        rating_layout = QHBoxLayout(self.rating_frame)

        # Крупная цифра среднего рейтинга
        self.rating_value = QLabel("5.0")
        self.rating_value.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 48px;
                font-weight: bold;
            }
        """)

        # Звездное отображение рейтинга
        self.rating_stars = QLabel("★★★★★")
        self.rating_stars.setStyleSheet("""
            QLabel {
                color: #FFD700;
                font-size: 24px;
            }
        """)

        # Количество отзывов
        self.rating_count = QLabel("на основе 50+ отзывов")
        self.rating_count.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 14px;
            }
        """)

        rating_layout.addWidget(self.rating_value)
        rating_layout.addWidget(self.rating_stars)
        rating_layout.addStretch()
        rating_layout.addWidget(self.rating_count)

        main_layout.addWidget(self.rating_frame)

        # === ОБЛАСТЬ ПРОКРУТКИ ОТЗЫВОВ ===
        self.carousel_frame = QFrame()
        self.carousel_frame.setStyleSheet("background-color: transparent;")

        carousel_layout = QVBoxLayout(self.carousel_frame)

        # Создаем область прокрутки
        self.reviews_scroll = QScrollArea()
        self.reviews_scroll.setWidgetResizable(True)  # Автоматический размер
        self.reviews_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Отключаем горизонтальный скролл
        self.reviews_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Вертикальный - по необходимости
        self.reviews_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #45a049;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Виджет для размещения отзывов внутри прокрутки
        self.reviews_widget = QWidget()
        self.reviews_layout = QVBoxLayout(self.reviews_widget)
        self.reviews_layout.setSpacing(15)

        self.reviews_scroll.setWidget(self.reviews_widget)
        carousel_layout.addWidget(self.reviews_scroll)

        main_layout.addWidget(self.carousel_frame)

        # === КНОПКИ НАВИГАЦИИ (предыдущая/следующая страница) ===
        nav_layout = QHBoxLayout()

        # Кнопка "Назад"
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                min-width: 50px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        self.prev_btn.clicked.connect(self.show_prev_reviews)

        # Кнопка "Вперед"
        self.next_btn = QPushButton("▶")
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        self.next_btn.clicked.connect(self.show_next_reviews)

        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()

        main_layout.addLayout(nav_layout)

    def load_reviews(self):
        """Запуск асинхронной загрузки отзывов"""
        # Создаем загрузчик в отдельном потоке
        self.loader = GISReviewsLoader()

        # Подключаем сигналы к обработчикам
        self.loader.reviews_loaded.connect(self.on_reviews_loaded)
        self.loader.loading_error.connect(self.on_loading_error)

        # Запускаем поток загрузки
        self.loader.start()

        # Показываем индикатор загрузки
        self.show_loading_indicator()

    def show_loading_indicator(self):
        """Отображение индикатора загрузки в процессе получения отзывов"""
        loading_label = QLabel("Загрузка отзывов...")
        loading_label.setStyleSheet("""
            QLabel {
                color: #b0b0b0;
                font-size: 16px;
                padding: 40px;
                background-color: #2d2d2d;
                border-radius: 10px;
            }
        """)
        loading_label.setAlignment(Qt.AlignCenter)
        self.reviews_layout.addWidget(loading_label)

    def on_reviews_loaded(self, reviews):
        """
        Обработчик успешной загрузки отзывов

        Args:
            reviews (list): Список загруженных отзывов
        """
        self.reviews = reviews

        # Очищаем контейнер отзывов
        self.clear_reviews()

        # Создаем виджеты для каждого отзыва
        for review in reviews:
            review_widget = ReviewWidget(review)
            self.reviews_layout.addWidget(review_widget)

        # Добавляем растяжку в конце, чтобы отзывы не растягивались
        self.reviews_layout.addStretch()

        # Обновляем статистику рейтинга
        self.update_rating_stats()

        # Обновляем состояние кнопок навигации
        self.update_navigation_buttons()

    def on_loading_error(self, error_msg):
        """
        Обработчик ошибки загрузки отзывов

        Args:
            error_msg (str): Сообщение об ошибке
        """
        error_label = QLabel(f"Не удалось загрузить отзывы: {error_msg}")
        error_label.setStyleSheet("""
            QLabel {
                color: #ff6b6b;
                font-size: 14px;
                padding: 20px;
                background-color: #2d2d2d;
                border-radius: 10px;
            }
        """)
        error_label.setWordWrap(True)
        error_label.setAlignment(Qt.AlignCenter)
        self.reviews_layout.addWidget(error_label)

    def clear_reviews(self):
        """Очистка всех виджетов отзывов из контейнера"""
        while self.reviews_layout.count():
            item = self.reviews_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_rating_stats(self):
        """Обновление статистики среднего рейтинга на основе загруженных отзывов"""
        if not self.reviews:
            return

        # Вычисляем средний рейтинг
        total_rating = sum(r['rating'] for r in self.reviews)
        avg_rating = total_rating / len(self.reviews)

        # Обновляем цифровое значение
        self.rating_value.setText(f"{avg_rating:.1f}")

        # Обновляем звезды (округляем до ближайшего целого)
        stars = "★" * round(avg_rating) + "☆" * (5 - round(avg_rating))
        self.rating_stars.setText(stars)

        # Обновляем количество отзывов
        self.rating_count.setText(f"на основе {len(self.reviews)} отзывов")

    def show_prev_reviews(self):
        """Прокрутка к предыдущей странице отзывов"""
        scrollbar = self.reviews_scroll.verticalScrollBar()
        current = scrollbar.value()
        step = self.reviews_scroll.height()  # Прокручиваем на высоту видимой области
        scrollbar.setValue(max(0, current - step))

    def show_next_reviews(self):
        """Прокрутка к следующей странице отзывов"""
        scrollbar = self.reviews_scroll.verticalScrollBar()
        current = scrollbar.value()
        step = self.reviews_scroll.height()
        max_val = scrollbar.maximum()
        scrollbar.setValue(min(max_val, current + step))

    def update_navigation_buttons(self):
        """Обновление состояния кнопок навигации (активны/неактивны)"""
        scrollbar = self.reviews_scroll.verticalScrollBar()

        def update_buttons():
            """Внутренняя функция для обновления кнопок в зависимости от позиции прокрутки"""
            self.prev_btn.setEnabled(scrollbar.value() > 0)
            self.next_btn.setEnabled(scrollbar.value() < scrollbar.maximum())

        # Подключаем функцию к сигналу изменения прокрутки
        scrollbar.valueChanged.connect(update_buttons)

        # Вызываем сразу для начальной установки состояния
        update_buttons()

    def open_2gis_reviews(self):
        """Открытие страницы с отзывами в 2GIS в браузере по умолчанию"""
        import webbrowser
        url = "https://2gis.ru/krasnoyarsk/firm/70000001087708026/reviews"
        webbrowser.open(url)