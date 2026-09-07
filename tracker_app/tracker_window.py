"""Независимое фреймлесс-окошко трекера: имя, таймер, управление."""

from __future__ import annotations

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .i18n import _
from .icons import close_gray_icon, pin_icon
from .models import Tracker
from .timer import TimerEngine
from .tooltip import Tooltip


def fmt_duration(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


class TrackerWindow(QWidget):
    """Одно окно-таймер. Открывается поверх, независимо от других."""

    closed = pyqtSignal(int)  # tracker_id
    position_changed = pyqtSignal(int, int, int)  # tracker_id, x, y
    name_changed = pyqtSignal(int, str)  # tracker_id, name
    always_on_top_changed = pyqtSignal(int, bool)  # tracker_id, flag
    elapsed_changed = pyqtSignal(int, float)  # tracker_id, seconds
    running_changed = pyqtSignal(bool)  # running

    def __init__(self, tracker: Tracker, app_quit: bool = False):
        super().__init__()
        self._tracker = tracker
        self._app_quit = app_quit
        self._drag_offset = None  # QPoint | None
        self._timer_engine = TimerEngine(elapsed=tracker.elapsed_seconds)
        self._ui_timer = QTimer(self)
        self._ui_timer.timeout.connect(self._refresh)
        self._ui_timer.start(100)

        self._name_debounce = QTimer(self)
        self._name_debounce.setSingleShot(True)
        self._name_debounce.setInterval(300)
        self._name_debounce.timeout.connect(self._commit_name)

        self.setWindowTitle(tracker.name)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, tracker.always_on_top)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("Card")
        self.setMinimumWidth(230)

        self._build_ui()
        self.move(tracker.pos_x, tracker.pos_y)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        header = QHBoxLayout()
        self._name_edit = QLineEdit(self._tracker.name)
        self._name_edit.textChanged.connect(self._on_name_changed)
        header.addWidget(self._name_edit, stretch=1)

        self._pin_btn = QPushButton(pin_icon(), "")
        self._pin_btn.setFixedWidth(28)
        self._pin_btn.setCheckable(True)
        self._pin_btn.setChecked(self._tracker.always_on_top)
        self._tooltip = Tooltip(self)
        self._tooltip.attach(self._pin_btn, _("pin_tracker"))
        self._pin_btn.clicked.connect(self._toggle_always_on_top)
        header.addWidget(self._pin_btn)

        self._close_btn = QPushButton(close_gray_icon(), "")
        self._close_btn.setFixedWidth(28)
        self._close_btn.clicked.connect(self._on_close)
        header.addWidget(self._close_btn)
        root.addLayout(header)

        self._time_label = QLabel(fmt_duration(0))
        self._time_label.setObjectName("timer")
        self._time_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self._time_label)

        controls = QHBoxLayout()
        self._start_btn = QPushButton(_("start"))
        self._start_btn.setObjectName("primary")
        glow = QGraphicsDropShadowEffect(self._start_btn)
        glow.setBlurRadius(20)
        glow.setOffset(0, 0)
        glow.setColor(QColor(14, 165, 233, 170))
        self._start_btn.setGraphicsEffect(glow)
        self._pause_btn = QPushButton("⏸")
        self._stop_btn = QPushButton("⏹")
        self._start_btn.clicked.connect(self.start)
        self._pause_btn.clicked.connect(self.pause)
        self._stop_btn.clicked.connect(self.stop)
        self._pause_btn.setEnabled(False)
        self._stop_btn.setEnabled(False)
        controls.addWidget(self._start_btn)
        controls.addWidget(self._pause_btn)
        controls.addWidget(self._stop_btn)
        root.addLayout(controls)

        self._hint = QLabel(_("hint_start"))
        self._hint.setObjectName("hint")
        self._hint.setAlignment(Qt.AlignCenter)
        root.addWidget(self._hint)

    def _hide_hint(self) -> None:
        self._hint.hide()

    def _show_hint(self) -> None:
        self._hint.show()

    # --- Управление таймером ---

    def start(self) -> None:
        if self._timer_engine.running:
            return
        self._timer_engine.start()
        self._set_running_state(True)
        self._persist_elapsed()

    def pause(self) -> None:
        if not self._timer_engine.running:
            return
        self._timer_engine.pause()
        self._set_running_state(False)
        self._refresh()
        self._persist_elapsed()

    def stop(self) -> None:
        """Останавливает и сбрасывает счётчик трекера."""
        self._timer_engine.reset()
        self._set_running_state(False)
        self._refresh()
        self._persist_elapsed()

    def _persist_elapsed(self) -> None:
        if self._tracker.id is not None:
            self.elapsed_changed.emit(self._tracker.id, self._timer_engine.current())


    def _set_running_state(self, running: bool) -> None:
        self._pause_btn.setEnabled(running)
        self._stop_btn.setEnabled(running)
        self._start_btn.setEnabled(not running)
        if running:
            self._hide_hint()
        else:
            self._show_hint()
        self.running_changed.emit(running)

    def _on_name_changed(self, name: str) -> None:
        self._name_debounce.start()

    def _commit_name(self) -> None:
        name = self._name_edit.text().strip()
        if name and self._tracker.id is not None:
            self._tracker.name = name
            self.name_changed.emit(self._tracker.id, name)

    def _toggle_always_on_top(self, checked: bool) -> None:
        self.set_always_on_top(checked)

    def set_always_on_top(self, flag: bool) -> None:
        self._tracker.always_on_top = flag
        self._pin_btn.setChecked(flag)
        x, y = self.x(), self.y()
        was_visible = self.isVisible()
        self.hide()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, flag)
        if was_visible:
            self.show()
            self.move(x, y)
        self.raise_()
        self.activateWindow()
        self.always_on_top_changed.emit(self._tracker.id, flag)

    # --- Events ---

    def _on_close(self) -> None:
        self.close()

    def closeEvent(self, event) -> None:
        # При закрытии окна сохраняем накопленное время (трекер продолжит с него).
        self._persist_elapsed()
        if not self._app_quit:
            self._timer_engine.pause()
        if self._tracker.id is not None:
            self.closed.emit(self._tracker.id)
        super().closeEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._drag_offset is not None:
            self._drag_offset = None
            if self._tracker.id is not None:
                self.position_changed.emit(self._tracker.id, self.x(), self.y())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _refresh(self) -> None:
        self._time_label.setText(fmt_duration(self._timer_engine.tick()))

    @property
    def tracker(self) -> Tracker:
        return self._tracker

    @property
    def is_running(self) -> bool:
        return self._timer_engine.running

    def current_seconds(self) -> float:
        return self._timer_engine.current()
