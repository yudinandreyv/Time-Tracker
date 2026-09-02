"""Всегда-живой сборщик времени в статистику (Session-строки).

DeltaCollector живёт всю жизнь приложения (независимо от окна статистики)
и накапливает дельты времени идущих трекеров через storage.add_delta.

- Один QTimer, интервал чередуется 10 000 -> 15 000 мс (через bool).
- База дельт ставится в момент старта трекера (running_changed True),
  чтобы первый тик давал дельту от истинного старта, а не 0.
- При смене дня вызывается rollover_day и сбрасывается база.
- Сигнал collected испускается после каждого тика (для обновления UI).
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from PyQt5.QtCore import QTimer, pyqtSignal, QObject

if TYPE_CHECKING:
    from .file_storage import FileStorage

INTERVAL_SHORT = 10_000
INTERVAL_LONG = 15_000
MIDNIGHT_CHECK_MS = 7_000


class DeltaCollector(QObject):
    """Накопление дельт времени идущих трекеров (только прибавляет)."""

    collected = pyqtSignal()  # после тика: статистика обновилась

    def __init__(self, storage: "FileStorage", main_window=None):
        super().__init__()
        self._storage = storage
        self._main = main_window
        # базы дельт: {tracker_id: current_seconds}
        self._prev: dict[int, float] = {}
        self._long_interval = False  # чередование 10/15 через bool
        self._day = date.today().isoformat()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.collect_now)
        self._timer.start(INTERVAL_SHORT)
        self._midnight_timer = QTimer(self)
        self._midnight_timer.timeout.connect(self._check_midnight)
        self._midnight_timer.start(MIDNIGHT_CHECK_MS)

    # --- Внешнее управление ---

    def register_window(self, win) -> None:
        """Подписывается на старт/паузу трекера, чтобы ставить базу вовремя."""
        tid = win.tracker.id
        if tid is None:
            return
        if not hasattr(win, "_collector_start_cb"):
            win._collector_start_cb = lambda: self._on_tracker_started(win)
            win.running_changed.connect(win._collector_start_cb)

    def unregister_window(self, win) -> None:
        tid = win.tracker.id
        if tid is not None:
            self._prev.pop(tid, None)
        cb = getattr(win, "_collector_start_cb", None)
        if cb is not None:
            try:
                win.running_changed.disconnect(cb)
            except TypeError:
                pass

    def pause_tracking(self, tracker_id: int) -> None:
        """Трекер перестал работать: стираем базу, чтобы не было ложной дельты."""
        self._prev.pop(tracker_id, None)

    def collect_now(self) -> None:
        """Единая функция накопления: дельты + сигнал. (кнопка и авто-таймер)"""
        try:
            # чередование интервала через bool: 10 -> 15 -> 10 -> 15 …
            if self._long_interval:
                self._timer.setInterval(INTERVAL_LONG)
            else:
                self._timer.setInterval(INTERVAL_SHORT)
            self._long_interval = not self._long_interval

            self._collect_deltas()
        except Exception:
            import traceback

            traceback.print_exc()
        self.collected.emit()

    def stop(self) -> None:
        """Финальный коммит и остановка таймеров (при выходе)."""
        try:
            self._collect_deltas()
        except Exception:
            import traceback

            traceback.print_exc()
        self._timer.stop()
        self._midnight_timer.stop()

    def _on_tracker_started(self, win) -> None:
        if win.is_running:
            self._prev[win.tracker.id] = win.current_seconds()
        else:
            self._prev.pop(win.tracker.id, None)

    def _collect_deltas(self) -> None:
        today = self._day
        windows = getattr(self._main, "_tracker_windows", None)
        if windows is None:
            return
        for tid, win in windows.items():
            current = win.current_seconds()
            if not win.is_running:
                self._prev.pop(tid, None)
                continue
            prev = self._prev.get(tid)
            if prev is None:
                # первый тик после старта без базы — ставим точку, дельта 0
                self._prev[tid] = current
                self._storage.ensure_session(tid, today)
                continue
            delta = current - prev
            self._prev[tid] = current
            if delta > 0:
                self._storage.add_delta(tid, today, delta)

    def _check_midnight(self) -> None:
        today = date.today().isoformat()
        if today == self._day:
            return
        self._storage.rollover_day(self._day)
        self._day = today
        self._prev.clear()

    # --- Для жёсткого 1:1: живой сегмент идущих трекеров ---

    def live_offsets(self) -> dict[int, float]:
        """{tracker_id: секунд, накопленных но ещё не попавших в статистику}."""
        out: dict[int, float] = {}
        windows = getattr(self._main, "_tracker_windows", None)
        if windows is None:
            return out
        for tid, win in windows.items():
            if not win.is_running:
                continue
            base = self._prev.get(tid)
            if base is None:
                continue
            seg = win.current_seconds() - base
            if seg > 0:
                out[tid] = seg
        return out
