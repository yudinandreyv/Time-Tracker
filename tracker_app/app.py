"""Тёмная и светлая темы (QSS). Плавное переключение: 20 предвычисленных шагов."""

from __future__ import annotations

from PyQt5.QtCore import QTimer
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

# ── Конечные точки палитры (0=dark, 9=light) ──
_DARK = {
    "bg":"#1a1b1f","card":"#222328","btn":"#2b2d34","btn_h":"#33353c","inp":"#141518",
    "timer":"#f1f5f9","tbl":"#141518","hdr":"#222328","tab":"#9ca3af","tab_sel":"#e5e7eb",
    "combo":"#2b2d34","text":"#e5e7eb","hint":"#9ca3af","border":"#363840",
}
_LIGHT = {
    "bg":"#f0f0f0","card":"#fafafa","btn":"#e0e0e0","btn_h":"#d0d0d0","inp":"#ffffff",
    "timer":"#1e1f24","tbl":"#ffffff","hdr":"#f0f0f0","tab":"#6b7280","tab_sel":"#1e1f24",
    "combo":"#e0e0e0","text":"#1e1f24","hint":"#6b7280","border":"#c8c8c8",
}

# Ключи, ОДИНАКОВЫЕ в обеих темах — НЕ интерполируются (accent blue, primary text и т.д.)
_STATIC_COLORS = {"#0ea5e9", "#06121a", "#38bdf8", "#7dd3fc"}


def _lerp_hex(c1: str, c2: str, t: float) -> str:
    a, b = QColor(c1), QColor(c2)
    return "#{:02x}{:02x}{:02x}".format(
        int(a.red()   + (b.red()   - a.red())   * t),
        int(a.green() + (b.green() - a.green()) * t),
        int(a.blue()  + (b.blue()  - a.blue())  * t),
    )


def _build_palette(step: int, total: int) -> dict:
    """Одна палитра для шага step (0..total-1)."""
    t = step / (total - 1)
    return {k: _lerp_hex(_DARK[k], _LIGHT[k], t) for k in _DARK}


_QSS_TPL = """\
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
QLineEdit:focus {{ border: 1px solid #7dd3fc; }}
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
    color: {timer};
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

# 20 предвычисленных шагов (0=dark, 19=light)
_STEPS = 20
_STEP_QSS = [_QSS_TPL.format(**_build_palette(i, _STEPS)) for i in range(_STEPS)]


def get_theme_qss(mode: str) -> str:
    return THEMES.get(mode, DARK_QSS)


def apply_theme(app: QApplication, mode: str = "dark") -> None:
    font = QFont()
    font.setFamilies(["Segoe UI", "Noto Sans", "DejaVu Sans", "sans-serif"])
    font.setPointSizeF(11.0)
    font.setWeight(QFont.DemiBold)
    app.setFont(font)
    idx = _STEPS - 1 if mode == "light" else 0
    app.setStyleSheet(_STEP_QSS[idx])


def smooth_transition(app: QApplication, target_mode: str, duration_ms: int = 1000) -> None:
    """20 шагов, каждый ~50мс. Шаги предвычислены — без интерполяции на лету."""
    current_qss = app.styleSheet()

    from_idx = None
    for i, s in enumerate(_STEP_QSS):
        if current_qss == s:
            from_idx = i
            break
    if from_idx is None:
        return

    to_idx = _STEPS - 1 if target_mode == "light" else 0
    if from_idx == to_idx:
        return

    if to_idx > from_idx:
        step_list = list(range(from_idx + 1, to_idx + 1))
    else:
        step_list = list(range(from_idx - 1, to_idx - 1, -1))
    interval = duration_ms // max(len(step_list), 1)
    pos = [0]

    def _tick():
        app.setStyleSheet(_STEP_QSS[step_list[pos[0]]])
        pos[0] += 1
        if pos[0] < len(step_list):
            QTimer.singleShot(interval, _tick)

    QTimer.singleShot(interval, _tick)
