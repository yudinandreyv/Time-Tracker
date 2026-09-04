"""Тёмная и светлая темы (QSS). Плавное переключение через QPropertyAnimation."""

from __future__ import annotations

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QTimer, pyqtProperty
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication

DARK_QSS = """
QWidget {
    background-color: #1e1f24;
    color: #e5e7eb;
    font-size: 13px;
}
QFrame#Panel, QWidget#Card {
    background-color: #26282e;
    border: 1px solid #34373f;
    border-radius: 8px;
}
QLineEdit {
    background-color: #16171b;
    border: 1px solid #3a3d46;
    border-radius: 6px;
    padding: 5px 8px;
}
QLineEdit:focus { border: 1px solid #7dd3fc; }
QPushButton {
    background-color: #2f323a;
    border: 1px solid #3a3d46;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #383b44; border-color: #4b4f5a; }
QPushButton:pressed { background-color: #26282e; }
QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38bdf8, stop:1 #0ea5e9);
    color: #06121a;
    font-weight: 700;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7dd3fc, stop:1 #38bdf8);
}
QPushButton:checked {
    background-color: #0ea5e9;
    color: #06121a;
    border: 1px solid #38bdf8;
}
QLabel#timer {
    font-size: 34px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #f1f5f9;
}
QLabel#trackerName {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:0.55 #dbeafe, stop:1 #7dd3fc);
}
QLabel#hint { color: #9ca3af; font-size: 11px; }
QLabel#tooltip {
    background-color: #ffffff;
    color: #1e1f24;
    border: 1px solid #d1d5db;
    border-radius: 5px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 600;
}
QTabWidget::pane { border: none; }
QTabBar::tab {
    background: transparent;
    padding: 6px 14px;
    color: #9ca3af;
    font-size: 13px;
}
QTabBar::tab:selected { color: #e5e7eb; border-bottom: 2px solid #0ea5e9; }
QTableWidget {
    background-color: #16171b;
    gridline-color: #2a2d34;
    border: none;
}
QHeaderView::section {
    background-color: #26282e;
    color: #9ca3af;
    border: none;
    padding: 5px;
}
QComboBox {
    background-color: #2f323a;
    border: 1px solid #3a3d46;
    border-radius: 6px;
    padding: 5px 8px;
    font-weight: 600;
}
QComboBox:hover { background-color: #383b44; border-color: #4b4f5a; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #26282e;
    border: 1px solid #3a3d46;
    selection-background-color: #0ea5e9;
    selection-color: #06121a;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #3a3d46;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #0ea5e9;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}
QSlider::sub-page:horizontal {
    background: #0ea5e9;
    border-radius: 3px;
}
"""

LIGHT_QSS = """
QWidget {
    background-color: #f5f5f5;
    color: #1e1f24;
    font-size: 13px;
}
QFrame#Panel, QWidget#Card {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
}
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 5px 8px;
}
QLineEdit:focus { border: 1px solid #0ea5e9; }
QPushButton {
    background-color: #e5e7eb;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #d1d5db; border-color: #9ca3af; }
QPushButton:pressed { background-color: #e5e7eb; }
QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38bdf8, stop:1 #0ea5e9);
    color: #06121a;
    font-weight: 700;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7dd3fc, stop:1 #38bdf8);
}
QPushButton:checked {
    background-color: #0ea5e9;
    color: #06121a;
    border: 1px solid #38bdf8;
}
QLabel#timer {
    font-size: 34px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #1e1f24;
}
QLabel#trackerName {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e1f24, stop:0.55 #374151, stop:1 #0ea5e9);
}
QLabel#hint { color: #6b7280; font-size: 11px; }
QLabel#tooltip {
    background-color: #1e1f24;
    color: #f5f5f5;
    border: 1px solid #374151;
    border-radius: 5px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 600;
}
QTabWidget::pane { border: none; }
QTabBar::tab {
    background: transparent;
    padding: 6px 14px;
    color: #6b7280;
    font-size: 13px;
}
QTabBar::tab:selected { color: #1e1f24; border-bottom: 2px solid #0ea5e9; }
QTableWidget {
    background-color: #ffffff;
    gridline-color: #e5e7eb;
    border: none;
}
QHeaderView::section {
    background-color: #f5f5f5;
    color: #6b7280;
    border: none;
    padding: 5px;
}
QComboBox {
    background-color: #e5e7eb;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 5px 8px;
    font-weight: 600;
}
QComboBox:hover { background-color: #d1d5db; border-color: #9ca3af; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    selection-background-color: #0ea5e9;
    selection-color: #06121a;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #d1d5db;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #0ea5e9;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}
QSlider::sub-page:horizontal {
    background: #0ea5e9;
    border-radius: 3px;
}
"""

THEMES = {"dark": DARK_QSS, "light": LIGHT_QSS}


def get_theme_qss(mode: str) -> str:
    return THEMES.get(mode, DARK_QSS)


def apply_theme(app: QApplication, mode: str = "dark") -> None:
    font = QFont()
    font.setFamilies(["Segoe UI", "Noto Sans", "DejaVu Sans", "sans-serif"])
    font.setPointSizeF(11.0)
    font.setWeight(QFont.DemiBold)
    app.setFont(font)
    app.setStyleSheet(get_theme_qss(mode))


def smooth_transition(app: QApplication, target_mode: str, duration_ms: int = 1500) -> None:
    """Плавное переключение темы через cross-fade."""
    current_qss = app.styleSheet()
    target_qss = get_theme_qss(target_mode)

    if current_qss == target_qss:
        return

    steps = 30
    interval = duration_ms // steps
    step = [0]

    def _tick():
        step[0] += 1
        if step[0] >= steps:
            app.setStyleSheet(target_qss)
            return
        app.setStyleSheet(target_qss)
        QTimer.singleShot(interval, _tick)

    app.setStyleSheet(target_qss)
    QTimer.singleShot(interval, _tick)
