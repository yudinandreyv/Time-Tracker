"""Диалог настроек: тема (тёмная/светлая) и язык.

Toggle-кнопка для темы: Moon (dark) ↔ Sun (light).
Плавное переключение через smooth_transition (1.5 сек).
"""

from __future__ import annotations

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF
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
from .icons import moon_icon, sun_icon


class ThemeToggle(QWidget):
    """Кастомная toggle-кнопка: Moon (dark) ↔ Sun (light)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_light = False
        self.setFixedSize(52, 28)
        self.setCursor(Qt.PointingHandCursor)
        self._circle_x = 4.0  # 4=dark, 30=light

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
        if emit and hasattr(self.parent(), "_on_theme_toggled"):
            self.parent()._on_theme_toggled(self._is_light)

    def mousePressEvent(self, event) -> None:
        self.set_light(not self._is_light)
        # Сигнал через parent
        if hasattr(self.parent(), "_on_theme_toggled"):
            self.parent()._on_theme_toggled(self._is_light)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Фон (скруглённый прямоугольник)
        if self._is_light:
            bg = QColor("#d1d5db")
        else:
            bg = QColor("#374151")
        p.setBrush(bg)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(0, 0, 52, 28), 14, 14)

        # Круг
        if self._is_light:
            circle = QColor("#fbbf24")  # солнце
        else:
            circle = QColor("#94a3b8")  # луна
        p.setBrush(circle)
        p.drawEllipse(QRectF(self._circle_x, 4, 20, 20))

        # Иконка на круге
        p.setPen(QPen(QColor("#ffffff"), 1.5))
        cx = self._circle_x + 10
        cy = 14
        if self._is_light:
            # Солнце: круг + лучи
            p.drawEllipse(QRectF(cx - 4, cy - 4, 8, 8))
            for angle in range(0, 360, 45):
                import math
                rad = math.radians(angle)
                x1 = cx + 5 * math.cos(rad)
                y1 = cy + 5 * math.sin(rad)
                x2 = cx + 7 * math.cos(rad)
                y2 = cy + 7 * math.sin(rad)
                p.drawLine(int(x1), int(y1), int(x2), int(y2))
        else:
            # Луна: полумесяц
            p.drawEllipse(QRectF(cx - 5, cy - 5, 10, 10))
            p.setBrush(QColor("#374151"))
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
        self._moon_icon = QLabel()
        self._moon_icon.setPixmap(moon_icon().pixmap(16, 16))
        theme_row.addWidget(self._moon_icon)

        self._theme_toggle = ThemeToggle(self)
        theme_row.addWidget(self._theme_toggle)

        self._sun_icon = QLabel()
        self._sun_icon.setPixmap(sun_icon().pixmap(16, 16))
        theme_row.addWidget(self._sun_icon)

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
