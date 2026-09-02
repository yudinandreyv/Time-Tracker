"""SVG-иконки для кнопок приложения (встроены как строки, без внешних файлов)."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer

_COLOR = "#e5e7eb"
_GRAY = "#9ca3af"

PIN_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" \
stroke="{_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
  <path d="M12 17v5"/>
  <path d="M9 5h6l-1 7-1.5 2h-1L9 5z"/>
  <path d="M12 21c1.66 0 3-1.34 3-3H9c0 1.66 1.34 3 3 3z"/>
</svg>"""

CLOSE_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" \
stroke="{_COLOR}" stroke-width="2.2" stroke-linecap="round" width="14" height="14">
  <path d="M6 6l12 12M18 6L6 18"/>
</svg>"""


CLOSE_GRAY_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" \
stroke="{_GRAY}" stroke-width="2.2" stroke-linecap="round" width="14" height="14">
  <path d="M6 6l12 12M18 6L6 18"/>
</svg>"""


def _icon_from_svg(svg: str) -> QIcon:
    renderer = QSvgRenderer()
    renderer.load(svg.encode("utf-8"))
    icon = QIcon()
    if renderer.isValid():
        size = renderer.defaultSize()
        pixmap = QPixmap(max(size.width(), 1), max(size.height(), 1))
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pixmap)
    return icon


APP_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <rect x="2" y="2" width="252" height="252" rx="24" fill="#1e1f24"/>
  <circle cx="128" cy="116" r="65" fill="#0ea5e9"/>
  <polygon points="121.4,52.8 147.6,55.6 128,86" fill="#f1f5f9"/>
  <path d="M 121.4 52.8 A 63.5 63.5 0 1 1 96.3 171.0"
        fill="none" stroke="#f1f5f9" stroke-width="16" stroke-linecap="round"/>
</svg>"""


def app_icon() -> QIcon:
    return _icon_from_svg(APP_ICON_SVG)


def pin_icon() -> QIcon:
    return _icon_from_svg(PIN_SVG)


def close_icon() -> QIcon:
    return _icon_from_svg(CLOSE_SVG)


def close_gray_icon() -> QIcon:
    return _icon_from_svg(CLOSE_GRAY_SVG)