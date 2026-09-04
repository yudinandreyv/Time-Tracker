"""Тёмная и светлая темы (QSS). Плавное переключение через цветовую интерполяцию."""

from __future__ import annotations

import re
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QTimer, pyqtProperty
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication

DARK_QSS = """
QWidget {
    background-color: #1a1b1f;
    color: #e5e7eb;
    font-size: 13px;
}
QFrame#Panel, QWidget#Card {
    background-color: #222328;
    border: 1px solid #363840;
    border-radius: 8px;
}
QLineEdit {
    background-color: #141518;
    border: 1px solid #363840;
    border-radius: 6px;
    padding: 5px 8px;
}
QLineEdit:focus { border: 1px solid #7dd3fc; }
QPushButton {
    background-color: #2b2d34;
    border: 1px solid #363840;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #33353c; border-color: #3e4048; }
QPushButton:pressed { background-color: #2b2d34; }
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
    background-color: #222328;
    color: #e5e7eb;
    border: 1px solid #363840;
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
    background-color: #141518;
    gridline-color: #2a2d34;
    border: none;
}
QHeaderView::section {
    background-color: #222328;
    color: #9ca3af;
    border: none;
    padding: 5px;
}
QComboBox {
    background-color: #2b2d34;
    border: 1px solid #363840;
    border-radius: 6px;
    padding: 5px 8px;
    font-weight: 600;
}
QComboBox:hover { background-color: #33353c; border-color: #3e4048; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #222328;
    border: 1px solid #363840;
    selection-background-color: #0ea5e9;
    selection-color: #06121a;
}
"""

LIGHT_QSS = """
QWidget {
    background-color: #f0f0f0;
    color: #1e1f24;
    font-size: 13px;
}
QFrame#Panel, QWidget#Card {
    background-color: #fafafa;
    border: 1px solid #c8c8c8;
    border-radius: 8px;
}
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #c8c8c8;
    border-radius: 6px;
    padding: 5px 8px;
}
QLineEdit:focus { border: 1px solid #0ea5e9; }
QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #c8c8c8;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
    color: #1e1f24;
}
QPushButton:hover { background-color: #d0d0d0; border-color: #b0b0b0; }
QPushButton:pressed { background-color: #e0e0e0; }
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
    background-color: #fafafa;
    color: #1e1f24;
    border: 1px solid #c8c8c8;
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
    gridline-color: #c8c8c8;
    border: none;
}
QHeaderView::section {
    background-color: #f0f0f0;
    color: #6b7280;
    border: none;
    padding: 5px;
}
QComboBox {
    background-color: #e0e0e0;
    border: 1px solid #c8c8c8;
    border-radius: 6px;
    padding: 5px 8px;
    font-weight: 600;
    color: #1e1f24;
}
QComboBox:hover { background-color: #d0d0d0; border-color: #b0b0b0; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #fafafa;
    border: 1px solid #c8c8c8;
    selection-background-color: #0ea5e9;
    selection-color: #06121a;
}
"""

THEMES = {"dark": DARK_QSS, "light": LIGHT_QSS}

# Ключевые цвета для интерполяции — сбалансированные пары
_KEY_COLORS = {
    "dark": {
        "QWidget": "#1a1b1f",
        "QWidget#Card": "#222328",
        "QPushButton": "#2b2d34",
        "QPushButton_hov": "#33353c",
        "QLineEdit": "#141518",
        "QLabel#timer": "#f1f5f9",
        "QTableWidget": "#141518",
        "QHeaderView": "#222328",
        "QTabBar": "#9ca3af",
        "QTabBar_sel": "#e5e7eb",
        "QComboBox": "#2b2d34",
        "color_main": "#e5e7eb",
        "color_hint": "#9ca3af",
        "border_main": "#363840",
        "border_focus": "#7dd3fc",
    },
    "light": {
        "QWidget": "#f0f0f0",
        "QWidget#Card": "#fafafa",
        "QPushButton": "#e0e0e0",
        "QPushButton_hov": "#d0d0d0",
        "QLineEdit": "#ffffff",
        "QLabel#timer": "#1e1f24",
        "QTableWidget": "#ffffff",
        "QHeaderView": "#f0f0f0",
        "QTabBar": "#6b7280",
        "QTabBar_sel": "#1e1f24",
        "QComboBox": "#e0e0e0",
        "color_main": "#1e1f24",
        "color_hint": "#6b7280",
        "border_main": "#c8c8c8",
        "border_focus": "#0ea5e9",
    },
}


def _lerp_color(c1: str, c2: str, t: float) -> str:
    """Интерполяция между двумя hex-цветами (t: 0..1)."""
    a = QColor(c1)
    b = QColor(c2)
    r = int(a.red() + (b.red() - a.red()) * t)
    g = int(a.green() + (b.green() - a.green()) * t)
    bl = int(a.blue() + (b.blue() - a.blue()) * t)
    return f"#{r:02x}{g:02x}{bl:02x}"


def _build_interpolated_qss(t: float, from_mode: str, to_mode: str) -> str:
    c1 = _KEY_COLORS[from_mode]
    c2 = _KEY_COLORS[to_mode]

    bg = _lerp_color(c1["QWidget"], c2["QWidget"], t)
    card = _lerp_color(c1["QWidget#Card"], c2["QWidget#Card"], t)
    btn = _lerp_color(c1["QPushButton"], c2["QPushButton"], t)
    btn_h = _lerp_color(c1["QPushButton_hov"], c2["QPushButton_hov"], t)
    inp = _lerp_color(c1["QLineEdit"], c2["QLineEdit"], t)
    timer_color = _lerp_color(c1["QLabel#timer"], c2["QLabel#timer"], t)
    tbl = _lerp_color(c1["QTableWidget"], c2["QTableWidget"], t)
    hdr = _lerp_color(c1["QHeaderView"], c2["QHeaderView"], t)
    tab = _lerp_color(c1["QTabBar"], c2["QTabBar"], t)
    tab_sel = _lerp_color(c1["QTabBar_sel"], c2["QTabBar_sel"], t)
    combo = _lerp_color(c1["QComboBox"], c2["QComboBox"], t)
    text = _lerp_color(c1["color_main"], c2["color_main"], t)
    hint = _lerp_color(c1["color_hint"], c2["color_hint"], t)
    border = _lerp_color(c1["border_main"], c2["border_main"], t)
    bfocus = _lerp_color(c1["border_focus"], c2["border_focus"], t)

    return f"""
QWidget {{
    background-color: {bg};
    color: {text};
    font-size: 13px;
}}
QFrame#Panel, QWidget#Card {{
    background-color: {card};
    border: 1px solid {border};
    border-radius: 8px;
}}
QLineEdit {{
    background-color: {inp};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 5px 8px;
}}
QLineEdit:focus {{ border: 1px solid {bfocus}; }}
QPushButton {{
    background-color: {btn};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
    color: {text};
}}
QPushButton:hover {{ background-color: {btn_h}; border-color: {border}; }}
QPushButton:pressed {{ background-color: {btn}; }}
QPushButton#primary {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38bdf8, stop:1 #0ea5e9);
    color: #06121a;
    font-weight: 700;
}}
QPushButton#primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7dd3fc, stop:1 #38bdf8);
}}
QPushButton:checked {{
    background-color: #0ea5e9;
    color: #06121a;
    border: 1px solid #38bdf8;
}}
QLabel#timer {{
    font-size: 34px;
    font-weight: 700;
    letter-spacing: 2px;
    color: {timer_color};
}}
QLabel#trackerName {{
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: {text};
}}
QLabel#hint {{ color: {hint}; font-size: 11px; }}
QLabel#tooltip {{
    background-color: {card};
    color: {text};
    border: 1px solid {border};
    border-radius: 5px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 600;
}}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{
    background: transparent;
    padding: 6px 14px;
    color: {tab};
    font-size: 13px;
}}
QTabBar::tab:selected {{ color: {tab_sel}; border-bottom: 2px solid #0ea5e9; }}
QTableWidget {{
    background-color: {tbl};
    gridline-color: {border};
    border: none;
}}
QHeaderView::section {{
    background-color: {hdr};
    color: {tab};
    border: none;
    padding: 5px;
}}
QComboBox {{
    background-color: {combo};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 5px 8px;
    font-weight: 600;
    color: {text};
}}
QComboBox:hover {{ border-color: {border}; }}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {card};
    border: 1px solid {border};
    selection-background-color: #0ea5e9;
    selection-color: #06121a;
}}
"""


def get_theme_qss(mode: str) -> str:
    return THEMES.get(mode, DARK_QSS)


def apply_theme(app: QApplication, mode: str = "dark") -> None:
    font = QFont()
    font.setFamilies(["Segoe UI", "Noto Sans", "DejaVu Sans", "sans-serif"])
    font.setPointSizeF(11.0)
    font.setWeight(QFont.DemiBold)
    app.setFont(font)
    app.setStyleSheet(get_theme_qss(mode))


def smooth_transition(app: QApplication, target_mode: str, duration_ms: int = 1000) -> None:
    """Плавное переключение темы через интерполяцию цветов."""
    current_qss = app.styleSheet()
    target_qss = get_theme_qss(target_mode)

    if current_qss == target_qss:
        return

    from_mode = "light" if "#f0f0f0" in current_qss else "dark"
    if from_mode == target_mode:
        return

    steps = 30
    interval = duration_ms // steps
    step = [0]

    def _tick():
        step[0] += 1
        t = min(step[0] / steps, 1.0)
        t = t * t * (3 - 2 * t)
        qss = _build_interpolated_qss(t, from_mode, target_mode)
        app.setStyleSheet(qss)
        if step[0] < steps:
            QTimer.singleShot(interval, _tick)
        else:
            app.setStyleSheet(target_qss)

    QTimer.singleShot(interval, _tick)
