"""Тёмная минималистичная тема (QSST-строка)."""

from __future__ import annotations

from PyQt5.QtGui import QFont
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
"""


def apply_theme(app: QApplication) -> None:
    font = QFont()
    font.setFamilies(["Segoe UI", "Noto Sans", "DejaVu Sans", "sans-serif"])
    font.setPointSizeF(11.0)
    font.setWeight(QFont.DemiBold)
    app.setFont(font)
    app.setStyleSheet(DARK_QSS)