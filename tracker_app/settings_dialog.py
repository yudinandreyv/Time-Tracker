"""Диалог настроек: тема (тёмная/светлая) и язык.

Toggle-кнопка для темы: клик → переключение.
Плавное переключение через smooth_transition (1 сек).
Кнопка блокируется во время анимации.
"""

from __future__ import annotations

import math

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .app import smooth_transition


class ThemeToggle(QWidget):
    """Кастомная toggle-кнопка: dark ↔ light. Блокируется во время анимации."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_light = False
        self.setFixedSize(52, 28)
        self.setCursor(Qt.PointingHandCursor)
        self._circle_x = 4.0
        self._locked = False
        self._on_toggled_cb = None

    @pyqtProperty(float)
    def circle_x(self):
        return self._circle_x

    @circle_x.setter
    def circle_x(self, val):
        self._circle_x = val
        self.update()

    def is_light(self) -> bool:
        return self._is_light

    def set_light(self, light: bool, emit: bool = True) -> None:
        if self._is_light == light:
            return
        self._is_light = light
        anim = QPropertyAnimation(self, b"circle_x")
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.setStartValue(self._circle_x)
        anim.setEndValue(30.0 if light else 4.0)
        anim.start()
        self._anim = anim
        if emit and self._on_toggled_cb:
            self._on_toggled_cb(self._is_light)

    def set_on_toggled(self, cb) -> None:
        self._on_toggled_cb = cb

    def mousePressEvent(self, event) -> None:
        if self._locked:
            return
        self._locked = True
        self.set_light(not self._is_light)
        # Разблокировка через 1100ms (после перехода темы 1000ms + запас)
        QTimer.singleShot(1100, self._unlock)

    def _unlock(self) -> None:
        self._locked = False

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        if self._is_light:
            bg = QColor("#c8c8c8")
            circle = QColor("#fbbf24")
            inner = QColor("#fafafa")
        else:
            bg = QColor("#363840")
            circle = QColor("#94a3b8")
            inner = QColor("#1a1b1f")

        p.setBrush(bg)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(0, 0, 52, 28), 14, 14)

        p.setBrush(circle)
        p.drawEllipse(QRectF(self._circle_x, 4, 20, 20))

        cx = self._circle_x + 10
        cy = 14
        p.setPen(QPen(QColor("#ffffff"), 1.5))

        if self._is_light:
            p.drawEllipse(QRectF(cx - 3.5, cy - 3.5, 7, 7))
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = cx + 5 * math.cos(rad)
                y1 = cy + 5 * math.sin(rad)
                x2 = cx + 7 * math.cos(rad)
                y2 = cy + 7 * math.sin(rad)
                p.drawLine(int(x1), int(y1), int(x2), int(y2))
        else:
            p.drawEllipse(QRectF(cx - 5, cy - 5, 10, 10))
            p.setBrush(inner)
            p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(cx - 2, cy - 6, 8, 10))

        p.end()


class SettingsDialog(QDialog):
    """Настройки приложения (немодальное окно)."""

    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self._storage = storage
        self.setWindowTitle("Settings")
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
            | Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(320)
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        # --- Тема ---
        theme_lbl = QLabel("Тема")
        theme_lbl.setObjectName("trackerName")
        root.addWidget(theme_lbl)

        theme_row = QHBoxLayout()
        self._theme_toggle = ThemeToggle(self)
        self._theme_toggle.set_on_toggled(self._on_theme_toggled)
        theme_row.addWidget(self._theme_toggle)
        theme_row.addStretch()
        root.addLayout(theme_row)

        # --- Язык ---
        lang_lbl = QLabel("Язык")
        lang_lbl.setObjectName("trackerName")
        root.addWidget(lang_lbl)

        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["Русский", "English"])
        self._lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        root.addWidget(self._lang_combo)

        root.addStretch()

        # --- Закрыть ---
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        root.addWidget(close_btn)

    def _load_settings(self) -> None:
        theme = self._storage.get_setting("theme", "dark")
        self._theme_toggle.set_light(theme == "light", emit=False)

        lang = self._storage.get_setting("language", "ru")
        idx = 1 if lang == "en" else 0
        self._lang_combo.blockSignals(True)
        self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.blockSignals(False)

    def _on_theme_toggled(self, is_light: bool) -> None:
        mode = "light" if is_light else "dark"
        self._storage.set_setting("theme", mode)
        from PyQt5.QtWidgets import QApplication
        qapp = QApplication.instance()
        if qapp is not None:
            smooth_transition(qapp, mode)

    def _on_lang_changed(self, index: int) -> None:
        lang = "en" if index == 1 else "ru"
        self._storage.set_setting("language", lang)
