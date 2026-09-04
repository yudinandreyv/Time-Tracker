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

GEAR_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" \
stroke="{_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
  <circle cx="12" cy="12" r="3"/>
  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
</svg>"""

MOON_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" \
stroke="{_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
</svg>"""

SUN_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" \
stroke="{_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
  <circle cx="12" cy="12" r="5"/>
  <line x1="12" y1="1" x2="12" y2="3"/>
  <line x1="12" y1="21" x2="12" y2="23"/>
  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
  <line x1="1" y1="12" x2="3" y2="12"/>
  <line x1="21" y1="12" x2="23" y2="12"/>
  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
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


def gear_icon() -> QIcon:
    return _icon_from_svg(GEAR_SVG)


def moon_icon() -> QIcon:
    return _icon_from_svg(MOON_SVG)


def sun_icon() -> QIcon:
    return _icon_from_svg(SUN_SVG)