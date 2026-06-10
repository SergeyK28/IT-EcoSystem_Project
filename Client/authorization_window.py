# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer, pyqtSlot, QDate
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QBrush, QPalette, QPixmap, QIcon, QDrag, QPainter, QPen, QPainterPath
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFrame, QMessageBox, QDialog, QGridLayout, QApplication

from identification_window import IdenDialog
from profil_window import Ui_profil
from Server.db import check_user, get_user_data_by_login, hash_password, get_connection
from Server.email_service import send_verification_email, generate_verification_code
from session_manager import session
import random
import string
import threading
import os
import json
from pathlib import Path
from datetime import datetime, timedelta


class PuzzlePiece(QLabel):
    """Фрагмент пазла - можно перетаскивать"""

    def __init__(self, piece_id, correct_pos, pixmap, parent=None):
        super().__init__(parent)
        self.piece_id = piece_id
        self.correct_row = correct_pos[0]
        self.correct_col = correct_pos[1]
        self.setFixedSize(120, 110)
        self.setPixmap(pixmap.scaled(120, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setScaledContents(True)
        self.setCursor(Qt.ClosedHandCursor)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #4a4a4a;
                border-radius: 5px;
                background-color: #2d2d2d;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    background-color: #3d3d3d;
                }
            """)
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if (event.pos() - self.drag_start_position).manhattanLength() > QApplication.startDragDistance():
                drag = QDrag(self)
                mime_data = QtCore.QMimeData()
                mime_data.setText(str(self.piece_id))
                drag.setMimeData(mime_data)

                pixmap = self.pixmap()
                if pixmap:
                    drag.setPixmap(pixmap.scaled(90, 82, Qt.KeepAspectRatio))
                    drag.setHotSpot(QPoint(45, 41))

                drag.exec_(Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #4a4a4a;
                border-radius: 5px;
                background-color: #2d2d2d;
            }
        """)
        event.accept()


class PuzzleSlot(QLabel):
    """Слот для фрагмента пазла"""

    piece_dropped = QtCore.pyqtSignal(int, int, int)

    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.current_piece_id = None
        self.setFixedSize(120, 110)
        self.setAlignment(Qt.AlignCenter)
        self.setText("⬜")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #4a4a4a;
                border-radius: 5px;
                background-color: #1a1a1a;
                font-size: 32px;
                color: #4a4a4a;
            }
        """)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            piece_id = int(event.mimeData().text())
            self.piece_dropped.emit(self.row, self.col, piece_id)
            event.acceptProposedAction()

    def set_piece(self, piece_id, pixmap):
        self.current_piece_id = piece_id
        self.setText("")
        self.setPixmap(pixmap.scaled(120, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.setScaledContents(True)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                background-color: #2d2d2d;
            }
        """)

    def clear_piece(self):
        self.current_piece_id = None
        self.clear()
        self.setText("⬜")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #4a4a4a;
                border-radius: 5px;
                background-color: #1a1a1a;
                font-size: 32px;
                color: #4a4a4a;
            }
        """)


class CaptchaPuzzle(QFrame):
    """Виджет капчи-пазла (2x2) из четырёх отдельных изображений"""

    puzzle_completed = QtCore.pyqtSignal(bool)
    puzzle_failed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pieces = {}
        self.slots = []
        self.slot_pieces = {}
        self.completed = False
        self.setup_ui()
        self.load_puzzle_images()

    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #232323);
                border-radius: 15px;
                padding: 15px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title_layout = QHBoxLayout()
        icon_label = QLabel("🧩")
        icon_label.setStyleSheet("font-size: 24px; background: none;")
        title_label = QLabel("Соберите пазл, чтобы продолжить")
        title_label.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: 600; background: none;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        pieces_label = QLabel("📦 Фрагменты (перетащите на поле):")
        pieces_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        layout.addWidget(pieces_label)

        self.pieces_container = QWidget()
        self.pieces_container.setStyleSheet("background-color: #1a1a1a; border-radius: 10px; padding: 10px;")
        self.pieces_layout = QGridLayout(self.pieces_container)
        self.pieces_layout.setSpacing(8)
        layout.addWidget(self.pieces_container)

        puzzle_label = QLabel("🧩 Поле сборки (2x2):")
        puzzle_label.setStyleSheet("color: #b0b0b0; font-size: 12px; margin-top: 10px;")
        layout.addWidget(puzzle_label)

        self.puzzle_container = QWidget()
        self.puzzle_container.setStyleSheet("background-color: #1a1a1a; border-radius: 10px; padding: 10px;")
        puzzle_grid = QGridLayout(self.puzzle_container)
        puzzle_grid.setSpacing(5)

        for row in range(2):
            for col in range(2):
                slot = PuzzleSlot(row, col)
                slot.piece_dropped.connect(self.on_piece_dropped)
                puzzle_grid.addWidget(slot, row, col)
                self.slots.append(slot)

        layout.addWidget(self.puzzle_container)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.reset_btn = QPushButton("🔄 Перемешать")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: white;
            }
        """)
        self.reset_btn.clicked.connect(self.shuffle_pieces)

        self.check_btn = QPushButton("✓ Проверить")
        self.check_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
        """)
        self.check_btn.clicked.connect(self.check_puzzle)

        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.check_btn)

        layout.addLayout(buttons_layout)

        self.status_label = QLabel("Перетащите фрагменты на поле сборки")
        self.status_label.setStyleSheet("color: #ffaa44; font-size: 11px; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def load_puzzle_images(self):
        """
        Загружает 4 отдельных изображения из папки assets:
        img0.png, img1.png, img2.png, img3.png
        """
        # Определяем возможные пути к папке assets
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'assets'),
            os.path.join(os.path.dirname(__file__), 'assets'),
            "assets"
        ]

        assets_dir = None
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                assets_dir = path
                break

        images = []
        missing_indices = []

        # Пытаемся загрузить img0.png ... img3.png
        for i in range(4):
            img_path = None
            if assets_dir:
                img_path = os.path.join(assets_dir, f"img{i}.png")
            else:
                # Альтернативно ищем в текущей директории
                if os.path.exists(f"assets/img{i}.png"):
                    img_path = f"assets/img{i}.png"

            if img_path and os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(120, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    images.append(pixmap)
                    continue

            missing_indices.append(i)

        # Если не хватает изображений — генерируем замещающие картинки с номерами
        if len(images) < 4:
            for i in range(4):
                if i not in missing_indices:
                    continue
                pixmap = QPixmap(120, 110)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)

                gradient = QLinearGradient(0, 0, 120, 110)
                colors = [
                    (76, 175, 80),   # зелёный
                    (33, 150, 243),  # синий
                    (156, 39, 176),  # фиолетовый
                    (255, 152, 0)    # оранжевый
                ]
                r, g, b = colors[i]
                gradient.setColorAt(0, QColor(r, g, b, 200))
                gradient.setColorAt(1, QColor(r // 2, g // 2, b // 2, 200))
                painter.fillRect(0, 0, 120, 110, gradient)

                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.setFont(QFont("Arial", 32, QFont.Bold))
                painter.drawText(pixmap.rect(), Qt.AlignCenter, str(i))
                painter.end()
                images.append(pixmap)

        # Формируем данные фрагментов (каждый фрагмент — одно изображение)
        pieces_data = []
        for idx, pix in enumerate(images):
            correct_row = idx // 2
            correct_col = idx % 2
            pieces_data.append({
                'id': idx,
                'correct_row': correct_row,
                'correct_col': correct_col,
                'pixmap': pix
            })

        # Перемешиваем фрагменты
        random.shuffle(pieces_data)

        # Очищаем старые виджеты
        self.pieces = {}
        self.slot_pieces = {}

        # Очищаем контейнер фрагментов
        for i in reversed(range(self.pieces_layout.count())):
            widget = self.pieces_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Добавляем фрагменты в левую область
        for i, data in enumerate(pieces_data):
            piece = PuzzlePiece(data['id'], (data['correct_row'], data['correct_col']), data['pixmap'])
            row = i // 2
            col = i % 2
            self.pieces_layout.addWidget(piece, row, col)
            self.pieces[data['id']] = piece

        # Очищаем слоты
        for slot in self.slots:
            slot.clear_piece()
            self.slot_pieces[(slot.row, slot.col)] = None

        self.completed = False
        self.status_label.setText("Перетащите фрагменты на поле сборки")
        self.status_label.setStyleSheet("color: #ffaa44; font-size: 11px; padding: 5px;")
        self.puzzle_completed.emit(False)

    def on_piece_dropped(self, target_row, target_col, piece_id):
        current_pos = None
        for (row, col), pid in self.slot_pieces.items():
            if pid == piece_id:
                current_pos = (row, col)
                break

        if current_pos:
            old_slot = self.get_slot_at(current_pos[0], current_pos[1])
            if old_slot:
                old_slot.clear_piece()
                self.slot_pieces[current_pos] = None

        existing_piece = self.slot_pieces.get((target_row, target_col))
        if existing_piece is not None and existing_piece != piece_id:
            existing_widget = self.pieces.get(existing_piece)
            if existing_widget:
                existing_widget.show()

        target_slot = self.get_slot_at(target_row, target_col)
        piece_widget = self.pieces.get(piece_id)

        if target_slot and piece_widget:
            target_slot.set_piece(piece_id, piece_widget.pixmap())
            self.slot_pieces[(target_row, target_col)] = piece_id
            piece_widget.hide()

    def get_slot_at(self, row, col):
        for slot in self.slots:
            if slot.row == row and slot.col == col:
                return slot
        return None

    def shuffle_pieces(self):
        for slot in self.slots:
            if slot.current_piece_id is not None:
                piece = self.pieces.get(slot.current_piece_id)
                if piece:
                    piece.show()
                slot.clear_piece()
                self.slot_pieces[(slot.row, slot.col)] = None

        pieces_list = list(self.pieces.values())

        for i in reversed(range(self.pieces_layout.count())):
            widget = self.pieces_layout.itemAt(i).widget()
            if widget:
                self.pieces_layout.removeWidget(widget)

        random.shuffle(pieces_list)

        for i, piece in enumerate(pieces_list):
            row = i // 2
            col = i % 2
            self.pieces_layout.addWidget(piece, row, col)

        self.completed = False
        self.status_label.setText("Фрагменты перемешаны! Соберите пазл.")
        self.status_label.setStyleSheet("color: #ffaa44; font-size: 11px; padding: 5px;")
        self.puzzle_completed.emit(False)

    def check_puzzle(self):
        correct_count = 0
        total_pieces = len(self.pieces)

        for (row, col), piece_id in self.slot_pieces.items():
            if piece_id is not None:
                piece = self.pieces.get(piece_id)
                if piece and piece.correct_row == row and piece.correct_col == col:
                    correct_count += 1

        if correct_count == total_pieces:
            self.completed = True
            self.status_label.setText("✅ Пазл собран верно! Теперь можно войти.")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: bold; padding: 5px;")
            self.puzzle_completed.emit(True)

            for slot in self.slots:
                if slot.current_piece_id is not None:
                    slot.setStyleSheet("""
                        QLabel {
                            border: 2px solid #4CAF50;
                            border-radius: 5px;
                            background-color: rgba(76, 175, 80, 0.2);
                        }
                    """)
        else:
            self.completed = False
            self.status_label.setText(f"❌ Пазл собран неправильно ({correct_count}/{total_pieces} на месте)")
            self.status_label.setStyleSheet("color: #ff4444; font-size: 12px; font-weight: bold; padding: 5px;")
            self.puzzle_completed.emit(False)
            self.puzzle_failed.emit()

    def is_completed(self):
        return self.completed


class PasswordLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(50)

        self.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                padding: 0 50px 0 20px;
                font-size: 15px;
                font-weight: 400;
                selection-background-color: #4CAF50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #333333;
            }
            QLineEdit:hover:not(:focus) {
                background-color: #353535;
                border: 2px solid #454545;
            }
            QLineEdit::placeholder {
                color: #808080;
                font-style: italic;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        self.toggle_btn = QPushButton("👁", self)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #808080;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                color: #4CAF50;
            }
            QPushButton:pressed {
                color: #45a049;
            }
        """)

        self.toggle_btn.clicked.connect(self.toggle_visibility)
        self.setEchoMode(QLineEdit.Password)
        self.password_visible = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        btn_x = self.width() - self.toggle_btn.width() - 10
        btn_y = (self.height() - self.toggle_btn.height()) // 2
        self.toggle_btn.move(btn_x, btn_y)

    def toggle_visibility(self):
        if self.password_visible:
            self.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("👁")
            self.password_visible = False
        else:
            self.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("👁‍🗨")
            self.password_visible = True


class ModernLineEdit(QLineEdit):
    def __init__(self, placeholder="", icon=None, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                padding: 0 20px;
                font-size: 15px;
                font-weight: 400;
                selection-background-color: #4CAF50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #333333;
            }
            QLineEdit:hover:not(:focus) {
                background-color: #353535;
                border: 2px solid #454545;
            }
            QLineEdit::placeholder {
                color: #808080;
                font-style: italic;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernButton(QPushButton):
    def __init__(self, text="", primary=True, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(55)
        self.setCursor(Qt.PointingHandCursor)

        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #45a049, stop:1 #3d8b40);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3d8b40, stop:1 #357a38);
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: #b0b0b0;
                    border: 2px solid #4a4a4a;
                    border-radius: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #454545;
                    color: white;
                    border: 2px solid #4CAF50;
                }
                QPushButton:pressed {
                    background-color: #353535;
                }
            """)


class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super(ForgotPasswordDialog, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.current_user_id = None
        self.current_user_email = None
        self.current_user_name = None
        self.verification_code = None
        self.code_expiry = None
        self.remaining_seconds = 0
        self.timer = None
        self.code_timer_label = None
        self.setupUi()

    def setupUi(self):
        self.setObjectName("ForgotPasswordDialog")
        self.resize(450, 500)

        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 450, 500)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 30px;
                border: 1px solid #3a3a3a;
            }
        """)

        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(30)
        main_shadow.setColor(QColor(0, 0, 0, 150))
        main_shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(main_shadow)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        self.btn_close.clicked.connect(self.reject)

        title_label = QLabel("🔐 Восстановление пароля")
        title_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")

        logo_label = QLabel("🔄")
        logo_label.setStyleSheet("color: #4CAF50; font-size: 28px;")

        header_layout.addWidget(self.btn_close)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(logo_label)

        layout.addLayout(header_layout)

        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(76, 175, 80, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(76, 175, 80, 0.3);
                padding: 15px;
            }
        """)

        info_layout = QVBoxLayout(info_frame)
        info_text = QLabel("📧 Введите email или логин для получения кода подтверждения")
        info_text.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: 500;")
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_frame)

        self.email_input = ModernLineEdit("Email или логин")
        layout.addWidget(self.email_input)

        self.code_input = ModernLineEdit("Код подтверждения")
        self.code_input.hide()
        layout.addWidget(self.code_input)

        self.new_password_input = PasswordLineEdit("Новый пароль")
        self.new_password_input.hide()
        layout.addWidget(self.new_password_input)

        self.confirm_password_input = PasswordLineEdit("Подтвердите пароль")
        self.confirm_password_input.hide()
        layout.addWidget(self.confirm_password_input)

        self.password_strength_frame = QFrame()
        self.password_strength_frame.setStyleSheet("background-color: #2a2a2a; border-radius: 10px; padding: 10px;")
        self.password_strength_frame.hide()

        strength_layout = QVBoxLayout(self.password_strength_frame)

        strength_label = QLabel("Сложность пароля:")
        strength_label.setStyleSheet("color: #b0b0b0; font-size: 13px;")

        self.strength_bar = QFrame()
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setStyleSheet("background-color: #3a3a3a; border-radius: 3px;")

        self.strength_indicator = QFrame(self.strength_bar)
        self.strength_indicator.setGeometry(0, 0, 0, 6)
        self.strength_indicator.setStyleSheet("background-color: #ff4444; border-radius: 3px;")

        self.strength_text = QLabel("Минимум 6 символов")
        self.strength_text.setStyleSheet("color: #ff4444; font-size: 12px;")
        self.strength_text.setAlignment(Qt.AlignRight)

        strength_layout.addWidget(strength_label)
        strength_layout.addWidget(self.strength_bar)
        strength_layout.addWidget(self.strength_text)

        layout.addWidget(self.password_strength_frame)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.send_code_btn = ModernButton("📧 Отправить код", True)
        self.verify_code_btn = ModernButton("✓ Проверить код", True)
        self.verify_code_btn.hide()
        self.reset_password_btn = ModernButton("🔄 Сменить пароль", True)
        self.reset_password_btn.hide()
        self.cancel_btn = ModernButton("✕ Отмена", False)

        button_layout.addWidget(self.send_code_btn)
        button_layout.addWidget(self.verify_code_btn)
        button_layout.addWidget(self.reset_password_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        self.send_code_btn.clicked.connect(self.send_verification_code)
        self.verify_code_btn.clicked.connect(self.verify_code)
        self.reset_password_btn.clicked.connect(self.reset_password)
        self.cancel_btn.clicked.connect(self.reject)

        self.new_password_input.textChanged.connect(self.check_password_strength)

    def find_user_by_login_or_email(self, login_or_email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID, Login, Email, FirstName, LastName FROM Client WHERE Login = %s",
                           (login_or_email,))
            user = cursor.fetchone()
            if not user:
                cursor.execute("SELECT ID, Login, Email, FirstName, LastName FROM Client WHERE Email = %s",
                               (login_or_email,))
                user = cursor.fetchone()
            return user
        finally:
            cursor.close()
            conn.close()

    def send_verification_code(self):
        login_or_email = self.email_input.text().strip()
        if not login_or_email:
            self.show_custom_message("Ошибка", "❌ Введите email или логин!", "error")
            return

        self.send_code_btn.setEnabled(False)
        self.send_code_btn.setText("⏳ Отправка...")

        user = self.find_user_by_login_or_email(login_or_email)

        if not user:
            self.show_custom_message("Ошибка", "❌ Пользователь с таким логином или email не найден!", "error")
            self.send_code_btn.setEnabled(True)
            self.send_code_btn.setText("📧 Отправить код")
            return

        self.current_user_id = user['ID']
        self.current_user_email = user['Email']
        self.current_user_name = f"{user['FirstName']} {user['LastName']}"

        self.verification_code = generate_verification_code(6)
        self.code_expiry = datetime.now() + timedelta(minutes=15)

        def send_email_thread():
            success = send_verification_email(self.current_user_email, self.verification_code, user['FirstName'])
            from PyQt5.QtCore import QMetaObject, Qt
            if success:
                QMetaObject.invokeMethod(self, "on_email_sent_success", Qt.QueuedConnection)
            else:
                QMetaObject.invokeMethod(self, "on_email_sent_failed", Qt.QueuedConnection)

        thread = threading.Thread(target=send_email_thread)
        thread.daemon = True
        thread.start()

    @pyqtSlot()
    def on_email_sent_success(self):
        self.show_custom_message("Успех", f"✅ Код подтверждения отправлен на {self.current_user_email}", "success")
        self.email_input.setEnabled(False)
        self.send_code_btn.hide()
        self.code_input.show()
        self.verify_code_btn.show()
        self.cancel_btn.setText("← Назад")

        self.code_timer_label = QLabel()
        self.code_timer_label.setStyleSheet(
            "color: #4CAF50; font-size: 12px; padding: 5px; background-color: rgba(76, 175, 80, 0.1); border-radius: 5px;")

        layout = self.layout()
        if layout:
            index = layout.indexOf(self.code_input)
            if index >= 0:
                layout.insertWidget(index + 1, self.code_timer_label)

        self.start_code_timer()

    @pyqtSlot()
    def on_email_sent_failed(self):
        self.show_custom_message("Ошибка",
                                 "❌ Не удалось отправить код подтверждения.\nПроверьте подключение к интернету или попробуйте позже.",
                                 "error")
        self.send_code_btn.setEnabled(True)
        self.send_code_btn.setText("📧 Отправить код")

    def start_code_timer(self):
        self.remaining_seconds = 15 * 60
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.update_timer()

    def update_timer(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.code_timer_label.setText("⏱️ Срок действия кода истек")
            self.code_timer_label.setStyleSheet(
                "color: #ff4444; font-size: 12px; padding: 5px; background-color: rgba(255, 68, 68, 0.1); border-radius: 5px;")
            self.verify_code_btn.setEnabled(False)
            return

        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.code_timer_label.setText(f"⏱️ Код действителен: {minutes:02d}:{seconds:02d}")
        if self.remaining_seconds < 60:
            self.code_timer_label.setStyleSheet(
                "color: #ffaa44; font-size: 12px; padding: 5px; background-color: rgba(255, 170, 68, 0.1); border-radius: 5px;")

    def verify_code(self):
        if self.remaining_seconds <= 0:
            self.show_custom_message("Ошибка", "❌ Срок действия кода истек!", "error")
            return

        entered_code = self.code_input.text().strip()
        if not entered_code:
            self.show_custom_message("Ошибка", "❌ Введите код подтверждения!", "error")
            return

        if entered_code == self.verification_code:
            if self.timer:
                self.timer.stop()
            self.code_input.setEnabled(False)
            self.verify_code_btn.hide()
            if self.code_timer_label:
                self.code_timer_label.hide()
            self.new_password_input.show()
            self.confirm_password_input.show()
            self.password_strength_frame.show()
            self.reset_password_btn.show()
            self.cancel_btn.setText("✕ Отмена")
        else:
            self.show_custom_message("Ошибка", "❌ Неверный код подтверждения!", "error")

    def check_password_strength(self, password):
        strength = 0
        width = self.strength_bar.width()

        if len(password) >= 6:
            strength += 25
        if any(c.isupper() for c in password):
            strength += 25
        if any(c.islower() for c in password):
            strength += 25
        if any(c in "!@#$%^&*()_+-=[]{};:,.<>?" for c in password):
            strength += 25

        self.strength_indicator.setFixedWidth(int(width * (strength / 100)) if width > 0 else 0)

        if strength < 25:
            self.strength_indicator.setStyleSheet("background-color: #ff4444; border-radius: 3px;")
            self.strength_text.setText("⚠️ Слишком простой пароль")
            self.strength_text.setStyleSheet("color: #ff4444; font-size: 12px;")
        elif strength < 50:
            self.strength_indicator.setStyleSheet("background-color: #ffaa44; border-radius: 3px;")
            self.strength_text.setText("⚠️ Слабый пароль")
            self.strength_text.setStyleSheet("color: #ffaa44; font-size: 12px;")
        elif strength < 75:
            self.strength_indicator.setStyleSheet("background-color: #ffff44; border-radius: 3px;")
            self.strength_text.setText("✓ Средний пароль")
            self.strength_text.setStyleSheet("color: #ffff44; font-size: 12px;")
        else:
            self.strength_indicator.setStyleSheet("background-color: #44ff44; border-radius: 3px;")
            self.strength_text.setText("✅ Надежный пароль")
            self.strength_text.setStyleSheet("color: #44ff44; font-size: 12px;")

    def reset_password(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not new_password or not confirm_password:
            self.show_custom_message("Ошибка", "❌ Заполните все поля!", "error")
            return
        if new_password != confirm_password:
            self.show_custom_message("Ошибка", "❌ Пароли не совпадают!", "error")
            return
        if len(new_password) < 6:
            self.show_custom_message("Ошибка", "❌ Пароль должен содержать минимум 6 символов!", "error")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            hashed_password = hash_password(new_password)
            cursor.execute("UPDATE Client SET PasswordHash = %s WHERE ID = %s", (hashed_password, self.current_user_id))
            conn.commit()
            self.show_custom_message("Успех", "✅ Пароль успешно изменен!", "success")
            self.accept()
        except Exception as e:
            self.show_custom_message("Ошибка", f"❌ Не удалось изменить пароль: {str(e)}", "error")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def show_custom_message(self, title, text, msg_type="info"):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
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
        if msg_type == "error":
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Information)
        msg.exec_()


class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super(AuthDialog, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Система блокировки
        self.failed_attempts = 0
        self.puzzle_failed_attempts = 0
        self.MAX_ATTEMPTS = 3
        self.BLOCK_DURATION_HOURS = 1.5
        self.blocked_until = None

        # Таймеры
        self.unblock_timer = QTimer()
        self.unblock_timer.timeout.connect(self.check_unblock)

        # UI элементы для блокировки (будут созданы позже)
        self.block_message_frame = None
        self.update_block_timer = None

        # Сначала настраиваем UI
        self.setupUi(self)

        # А теперь загружаем сохраненную блокировку (после того как UI создан)
        self.load_blocked_state()

    def get_block_file_path(self):
        """Возвращает путь к файлу блокировки"""
        block_dir = Path.home() / '.it_ecosystem'
        block_dir.mkdir(exist_ok=True)
        return block_dir / 'auth_block.json'

    def load_blocked_state(self):
        """Загружает сохраненное состояние блокировки"""
        block_file = self.get_block_file_path()
        if block_file.exists():
            try:
                with open(block_file, 'r') as f:
                    data = json.load(f)
                    blocked_until_str = data.get('blocked_until', '')
                    if blocked_until_str:
                        self.blocked_until = datetime.fromisoformat(blocked_until_str)
                    self.failed_attempts = data.get('failed_attempts', 0)
                    self.puzzle_failed_attempts = data.get('puzzle_failed_attempts', 0)

                    if self.blocked_until and self.blocked_until > datetime.now():
                        self.apply_block()
                    else:
                        self.clear_block()
            except Exception as e:
                print(f"Ошибка загрузки состояния блокировки: {e}")
                self.clear_block()

    def save_blocked_state(self):
        """Сохраняет состояние блокировки"""
        data = {
            'blocked_until': self.blocked_until.isoformat() if self.blocked_until else '',
            'failed_attempts': self.failed_attempts,
            'puzzle_failed_attempts': self.puzzle_failed_attempts
        }

        try:
            with open(self.get_block_file_path(), 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Ошибка сохранения состояния блокировки: {e}")

    def apply_block(self):
        """Применяет блокировку"""
        if hasattr(self, 'login'):
            self.login.setEnabled(False)
        if hasattr(self, 'password'):
            self.password.setEnabled(False)
        if hasattr(self, 'sign_up'):
            self.sign_up.setEnabled(False)
        if hasattr(self, 'captcha_puzzle'):
            self.captcha_puzzle.setEnabled(False)

        # Показываем сообщение о блокировке
        self.show_block_message()

        # Запускаем таймер для проверки разблокировки
        self.unblock_timer.start(60000)

    def clear_block(self):
        """Снимает блокировку"""
        self.failed_attempts = 0
        self.puzzle_failed_attempts = 0
        self.blocked_until = None

        if hasattr(self, 'login'):
            self.login.setEnabled(True)
        if hasattr(self, 'password'):
            self.password.setEnabled(True)
        if hasattr(self, 'sign_up'):
            self.sign_up.setEnabled(True)
        if hasattr(self, 'captcha_puzzle'):
            self.captcha_puzzle.setEnabled(True)

        self.unblock_timer.stop()

        # Закрываем таймер обновления времени
        if self.update_block_timer:
            self.update_block_timer.stop()

        # Удаляем сообщение о блокировке
        if self.block_message_frame:
            self.block_message_frame.deleteLater()
            self.block_message_frame = None

        # Обновляем пазл
        if hasattr(self, 'captcha_puzzle'):
            self.captcha_puzzle.shuffle_pieces()

        # Удаляем файл блокировки
        block_file = self.get_block_file_path()
        if block_file.exists():
            block_file.unlink()

    def check_unblock(self):
        """Проверяет, не истекло ли время блокировки"""
        if self.blocked_until and datetime.now() >= self.blocked_until:
            self.clear_block()

    def show_block_message(self):
        """Показывает сообщение о блокировке"""
        if self.block_message_frame or not hasattr(self, 'captcha_puzzle'):
            return

        # Создаем контейнер для сообщения
        self.block_message_frame = QFrame(self.captcha_puzzle.parent())
        self.block_message_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 15px;
                border: 2px solid #ff4444;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(self.block_message_frame)

        # Иконка
        icon_label = QLabel("🚫")
        icon_label.setStyleSheet("font-size: 48px; color: #ff4444;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Заголовок
        title_label = QLabel("ДОСТУП ЗАБЛОКИРОВАН")
        title_label.setStyleSheet("""
            color: #ff4444;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Причина блокировки
        reason_label = QLabel(
            "Причина: 3 неудачные попытки подряд.\n"
            "Попробуйте снова через 1.5 часа или обратитесь к администратору."
        )
        reason_label.setStyleSheet("color: #b0b0b0; font-size: 14px;")
        reason_label.setAlignment(Qt.AlignCenter)
        reason_label.setWordWrap(True)
        layout.addWidget(reason_label)

        # Время до разблокировки
        self.unblock_time_label = QLabel()
        self.unblock_time_label.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
        self.unblock_time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.unblock_time_label)

        # Кнопка обращения к администратору
        contact_btn = QPushButton("📞 Обратиться к администратору")
        contact_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        contact_btn.clicked.connect(self.contact_admin)
        layout.addWidget(contact_btn)

        # Размещаем поверх капчи
        self.block_message_frame.setGeometry(10, 10, 440, 350)
        self.block_message_frame.show()

        # Запускаем таймер обновления времени
        self.update_block_timer = QTimer()
        self.update_block_timer.timeout.connect(self.update_unblock_time)
        self.update_block_timer.start(1000)

    def update_unblock_time(self):
        """Обновляет отображение времени до разблокировки"""
        if self.blocked_until:
            remaining = self.blocked_until - datetime.now()
            if remaining.total_seconds() > 0:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                seconds = int(remaining.total_seconds() % 60)
                self.unblock_time_label.setText(f"⏱️ До разблокировки: {hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                self.update_block_timer.stop()
                self.clear_block()
        else:
            if self.update_block_timer:
                self.update_block_timer.stop()
            self.clear_block()

    def contact_admin(self):
        """Обращение к администратору"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Обращение к администратору")
        msg.setText("Для снятия блокировки обратитесь к системному администратору:\n\n"
                    "📞 Телефон: +7 (929) 356-23-78\n"
                    "📧 Email: admin@it-ecosystem.ru\n\n"
                    "Пожалуйста, укажите ваш логин и время блокировки.")
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
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
            }
        """)
        msg.exec_()

    def on_puzzle_failed(self):
        """Обработчик неудачной сборки пазла"""
        if self.blocked_until and datetime.now() < self.blocked_until:
            return

        self.puzzle_failed_attempts += 1

        if self.puzzle_failed_attempts >= self.MAX_ATTEMPTS:
            self.blocked_until = datetime.now() + timedelta(hours=self.BLOCK_DURATION_HOURS)
            self.save_blocked_state()
            self.apply_block()
            self.show_custom_message("Доступ заблокирован",
                                     f"❌ Три неудачные попытки сборки пазла подряд!\n"
                                     f"Доступ заблокирован до {self.blocked_until.strftime('%H:%M:%S')}\n"
                                     "Обратитесь к администратору.", "error")
            return

        remaining = self.MAX_ATTEMPTS - self.puzzle_failed_attempts
        self.show_custom_message("Проверка безопасности",
                                 f"🧩 Пазл собран неверно!\n\n"
                                 f"⚠️ Осталось попыток: {remaining} из {self.MAX_ATTEMPTS}", "warning")

    def setupUi(self, Dialog):
        Dialog.setObjectName("AuthDialog")
        Dialog.resize(550, 750)

        self.dialog = Dialog

        main_container = QFrame(Dialog)
        main_container.setGeometry(0, 0, 550, 750)
        main_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a2a2a, stop:1 #1f1f1f);
                border-radius: 30px;
                border: 1px solid #3a3a3a;
            }
        """)

        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(30)
        main_shadow.setColor(QColor(0, 0, 0, 150))
        main_shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(main_shadow)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #45a049;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(40, 40)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #b0b0b0;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        title_label = QLabel("🔑 Вход в IT-EcoSystem")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")

        logo_label = QLabel("🚀")
        logo_label.setStyleSheet("color: #4CAF50; font-size: 32px;")

        header_layout.addWidget(self.btn_close)
        header_layout.addStretch()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(logo_label)

        layout.addLayout(header_layout)

        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(76, 175, 80, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(76, 175, 80, 0.3);
                padding: 15px;
            }
        """)

        info_layout = QVBoxLayout(info_frame)
        info_text = QLabel("👋 Войдите в свой аккаунт для доступа к IT-EcoSystem")
        info_text.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: 500;")
        info_text.setAlignment(Qt.AlignCenter)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        layout.addWidget(info_frame)

        self.login = ModernLineEdit("Логин или Email")
        layout.addWidget(self.login)

        self.password = PasswordLineEdit("Пароль")
        layout.addWidget(self.password)

        self.forgot_password_btn = QPushButton("Забыли пароль?")
        self.forgot_password_btn.setStyleSheet("""
            QPushButton {
                color: #4CAF50;
                background-color: transparent;
                border: none;
                font-size: 14px;
                font-weight: 500;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #45a049;
            }
        """)
        self.forgot_password_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.forgot_password_btn, 0, Qt.AlignRight)

        self.captcha_puzzle = CaptchaPuzzle()
        self.captcha_puzzle.puzzle_failed.connect(self.on_puzzle_failed)
        layout.addWidget(self.captcha_puzzle)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.sign_up = ModernButton("🔓 Войти", True)
        self.sign_in = ModernButton("📝 Регистрация", False)

        button_layout.addWidget(self.sign_up)
        button_layout.addWidget(self.sign_in)

        layout.addLayout(button_layout)

        self.sign_up.clicked.connect(self.open_profil_window)
        self.sign_in.clicked.connect(self.open_ide_window)
        self.forgot_password_btn.clicked.connect(self.open_forgot_password_dialog)

        self.login.returnPressed.connect(self.password.setFocus)
        self.password.returnPressed.connect(self.sign_up.click)

        scroll_area.setWidget(scroll_content)

        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def open_ide_window(self):
        self.registration_dialog = IdenDialog(self)
        self.registration_dialog.show()

    def open_profil_window(self):
        # Проверяем, не заблокирован ли пользователь
        if self.blocked_until and datetime.now() < self.blocked_until:
            self.show_block_message()
            return

        # Проверка пазла
        if not self.captcha_puzzle.is_completed():
            self.puzzle_failed_attempts += 1

            if self.puzzle_failed_attempts >= self.MAX_ATTEMPTS:
                self.blocked_until = datetime.now() + timedelta(hours=self.BLOCK_DURATION_HOURS)
                self.save_blocked_state()
                self.apply_block()
                self.show_custom_message("Доступ заблокирован",
                                         f"❌ Три неудачные попытки подряд!\n"
                                         f"Доступ заблокирован до {self.blocked_until.strftime('%H:%M:%S')}\n"
                                         "Обратитесь к администратору.", "error")
                return

            remaining = self.MAX_ATTEMPTS - self.puzzle_failed_attempts
            self.show_custom_message("Проверка безопасности",
                                     f"🧩 Пожалуйста, соберите пазл, чтобы подтвердить, что вы не робот!\n\n"
                                     f"⚠️ Осталось попыток: {remaining} из {self.MAX_ATTEMPTS}", "warning")
            self.captcha_puzzle.shuffle_pieces()
            return

        # Сбрасываем счетчик успешного выполнения пазла
        self.puzzle_failed_attempts = 0

        login = self.login.text()
        password = self.password.text()
        remember_me = True

        if login and password:
            if check_user(login, password):
                # Успешный вход - сбрасываем все счетчики
                self.failed_attempts = 0
                self.puzzle_failed_attempts = 0
                self.clear_block()

                user_data = get_user_data_by_login(login)
                session.login(user_data["ID"], user_data["FirstName"] + " " + user_data["LastName"], remember_me)
                self.close()

                self.profile_dialog = QDialog()
                self.profile_ui = Ui_profil(user_data["ID"], user_data["FirstName"] + " " + user_data["LastName"])
                self.profile_ui.setupUi(self.profile_dialog)

                if hasattr(session, '_main_window') and session._main_window:
                    self.profile_dialog.finished.connect(lambda: session._main_window.update_login_button())

                self.profile_dialog.show()
            else:
                # Неудачная попытка входа
                self.failed_attempts += 1

                if self.failed_attempts >= self.MAX_ATTEMPTS:
                    self.blocked_until = datetime.now() + timedelta(hours=self.BLOCK_DURATION_HOURS)
                    self.save_blocked_state()
                    self.apply_block()
                    self.show_custom_message("Доступ заблокирован",
                                             f"❌ Три неудачные попытки входа подряд!\n"
                                             f"Доступ заблокирован до {self.blocked_until.strftime('%H:%M:%S')}\n"
                                             "Обратитесь к администратору.", "error")
                    return

                remaining = self.MAX_ATTEMPTS - self.failed_attempts
                self.show_custom_message("Ошибка",
                                         f"❌ Неверный логин или пароль!\n\n"
                                         f"⚠️ Осталось попыток: {remaining} из {self.MAX_ATTEMPTS}", "error")
                self.captcha_puzzle.shuffle_pieces()
        else:
            self.show_custom_message("Ошибка", "❌ Заполните все поля!", "error")

    def open_forgot_password_dialog(self):
        # Проверяем блокировку перед восстановлением
        if self.blocked_until and datetime.now() < self.blocked_until:
            self.show_block_message()
            return

        self.forgot_dialog = ForgotPasswordDialog(self)
        self.forgot_dialog.exec_()

    def show_custom_message(self, title, text, msg_type="info"):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: white;
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
        if msg_type == "error":
            msg.setIcon(QMessageBox.Critical)
        elif msg_type == "warning":
            msg.setIcon(QMessageBox.Warning)
        else:
            msg.setIcon(QMessageBox.Information)
        msg.exec_()


if __name__ == "__main__":
    import sys

    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QtWidgets.QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(76, 175, 80))
    palette.setColor(QPalette.Highlight, QColor(76, 175, 80))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    dialog = AuthDialog()
    dialog.show()
    sys.exit(app.exec_())