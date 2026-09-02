"""Компактная подсказка-баллон поверх всех окон (без активации окна)."""

from __future__ import annotations

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtWidgets import QApplication, QLabel


class Tooltip(QLabel):
    """Отображается у виджета при наведении мыши, поверх всех окон."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("tooltip")
        self._slot: tuple | None = None
        self.hide()

    def attach(self, widget, text: str):
        """Показывать `text` при наведении на `widget`."""
        self._slot = (widget, text)
        widget.installEventFilter(self)
        return self

    def eventFilter(self, obj, event):
        if self._slot is not None and obj is self._slot[0]:
            if event.type() == QEvent.Enter:
                self._show_at(obj)
            elif event.type() in (QEvent.Leave, QEvent.MouseButtonPress):
                self.hide()
            elif event.type() == QEvent.Hide:
                self.hide()
        return super().eventFilter(obj, event)

    def _show_at(self, widget) -> None:
        self.setText(self._slot[1])
        self.adjustSize()
        center = widget.mapToGlobal(QPoint(widget.width() // 2, widget.height() // 2))
        x = center.x() + widget.width() // 2 + 6
        y = center.y() - self.height() // 2
        screen = QApplication.screenAt(center)
        if screen is not None:
            geo = screen.availableGeometry()
            x = max(geo.left(), min(x, geo.right() - self.width()))
            y = max(geo.top(), min(y, geo.bottom() - self.height()))
        self.move(x, y)
        self.show()
        self.raise_()