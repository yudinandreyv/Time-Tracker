"""Диалог настроек: тема (тёмная/светлая) и язык.

Плавное переключение темы через smooth_transition (1.5 сек).
Слайдер: Moon (dark) ↔ Sun (light).
"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from .app import smooth_transition
from .icons import moon_icon, sun_icon


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

        self._theme_slider = QSlider(Qt.Horizontal)
        self._theme_slider.setRange(0, 1)
        self._theme_slider.setTickPosition(QSlider.NoTicks)
        self._theme_slider.valueChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self._theme_slider, stretch=1)

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
        self._theme_slider.setValue(1 if theme == "light" else 0)

        lang = self._storage.get_setting("language", "ru")
        idx = 1 if lang == "en" else 0
        self._lang_combo.blockSignals(True)
        self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.blockSignals(False)

    def _on_theme_changed(self, value: int) -> None:
        mode = "light" if value == 1 else "dark"
        self._storage.set_setting("theme", mode)
        app = self._storage._settings  # нужен app, передадим через parent
        # Плавное переключение через QApplication.instance()
        from PyQt5.QtWidgets import QApplication
        qapp = QApplication.instance()
        if qapp is not None:
            smooth_transition(qapp, mode)

    def _on_lang_changed(self, index: int) -> None:
        lang = "en" if index == 1 else "ru"
        self._storage.set_setting("language", lang)
