"""Окно статистики: читает накопленную статистику и рисует таблицы.

Накоплением времени занимается всегда-живой DeltaCollector (см. collector.py),
запущенный в MainWindow. Окно статистики — чистый читатель:
- подписывается на сигнал collected и перерисовывается после каждого тика;
- кнопка «Обновить» просит коллектор выполнить сбор (тот же тик) и рисует;
- для жёсткого совпадения с таймером (1:1) при отрисовке добавляет живой
  сегмент идущих трекеров (live_offsets).
"""

from __future__ import annotations

from datetime import date

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .file_storage import FileStorage
from .tracker_window import fmt_duration

TRACKER_HEADERS = ["Имя", "Сегодня", "За всё время", ""]


def _hms(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}ч {m:02d}м"
    if m:
        return f"{m}м {s:02d}с"
    return f"{s}с"


class TablePanel(QWidget):
    """Контейнер с заголовком и таблицей (или надписью «нет данных»)."""

    def __init__(self, title: str, headers: list[str]):
        super().__init__()
        self._lay = QVBoxLayout(self)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("trackerName")
        self._empty_label = QLabel("Нет данных")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setObjectName("hint")
        self._table = QTableWidget(0, len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        header = self._table.horizontalHeader()
        for i in range(len(headers) - 1, -1, -1):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        self._lay.addWidget(title_lbl)
        self._lay.addWidget(self._empty_label)
        self._lay.addWidget(self._table)
        self._table.hide()

    def set_data(self, headers: list[str], rows: list[tuple]) -> None:
        self._table.setRowCount(0)
        for values in rows:
            row = self._table.rowCount()
            self._table.insertRow(row)
            for col, value in enumerate(values):
                self._table.setItem(row, col, QTableWidgetItem(value))
        self._empty_label.hide()
        self._table.show()

    def show_empty(self, message: str) -> None:
        self._empty_label.setText(message)
        self._empty_label.show()
        self._table.hide()


class StatsWindow(QDialog):
    """Статистика. Чистый читатель: рисует данные из storage + живой сегмент."""

    def __init__(self, storage: FileStorage, collector, parent=None):
        super().__init__(parent)
        self._storage = storage
        self._collector = collector
        self.setWindowTitle("Статистика")
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
            | Qt.WindowCloseButtonHint
        )
        self.resize(800, 600)

        self._daily_panel = TablePanel("Сумма времени по дням", ["Дата", "Время"])
        self._track_panel = TablePanel("Время по трекерам (за всё время)", ["Трекер", "Время"])

        self._build_ui()
        self._collector.collected.connect(self._refresh_ui)
        self.collect_now()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        header = QHBoxLayout()
        self._total_label = QLabel()
        self._total_label.setObjectName("trackerName")
        header.addWidget(self._total_label)
        self._refresh_btn = QPushButton("Обновить")
        self._refresh_btn.clicked.connect(self.collect_now)
        header.addWidget(self._refresh_btn)
        root.addLayout(header)

        tabs = QTabWidget()

        w_daily = QWidget()
        lay_daily = QVBoxLayout(w_daily)
        lay_daily.addWidget(self._daily_panel)
        tabs.addTab(w_daily, "По дням")

        w_track = QWidget()
        lay_track = QVBoxLayout(w_track)
        lay_track.addWidget(self._track_panel)
        tabs.addTab(w_track, "По трекерам")

        tabs.addTab(self._build_tracker_list_tab(), "Трекеры")
        root.addWidget(tabs)

    def _build_tracker_list_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        self._tracker_table = QTableWidget(0, len(TRACKER_HEADERS))
        self._tracker_table.setHorizontalHeaderLabels(TRACKER_HEADERS)
        self._tracker_table.verticalHeader().setVisible(False)
        header = self._tracker_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._tracker_table.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._tracker_table)
        return w

    # --- Единая функция обновления (кнопка и авто-тик коллектора) ---

    def collect_now(self) -> None:
        """Просим коллектор выполнить сбор, затем рисуем."""
        if self._collector is not None:
            self._collector.collect_now()
        else:
            self._refresh_ui()

    def _refresh_ui(self) -> None:
        live = self._collector.live_offsets() if self._collector is not None else {}

        today = date.today().isoformat()
        today_total = self._storage.total_today() + sum(v for v in live.values())
        self._total_label.setText(f"Сегодня: {fmt_duration(today_total)}")

        per_day = self._storage.per_day()
        if per_day:
            self._daily_panel.set_data(
                ["Дата", "Время"], [(d, _hms(v)) for d, v in per_day]
            )
        else:
            self._daily_panel.show_empty("Нет данных по дням")

        per_tracker = self._storage.per_tracker_total()
        if per_tracker:
            self._track_panel.set_data(
                ["Трекер", "Время"],
                [(name, _hms(v + live.get(tid, 0))) for name, v, tid in per_tracker],
            )
        else:
            self._track_panel.show_empty("Нет данных по трекерам")

        self._populate_tracker_list(live, today)

    def _populate_tracker_list(self, live: dict, today: str) -> None:
        self._tracker_table.setRowCount(0)
        for tr in self._storage.list_trackers():
            live_sec = live.get(tr.id, 0)
            total = self._storage.tracker_total(tr.id) + live_sec
            today_secs = sum(
                s.total_seconds
                for s in self._storage.list_sessions()
                if s.tracker_id == tr.id and s.day == today
            ) + live_sec
            row = self._tracker_table.rowCount()
            self._tracker_table.insertRow(row)
            self._tracker_table.setItem(row, 0, QTableWidgetItem(tr.name))
            self._tracker_table.setItem(row, 1, QTableWidgetItem(_hms(today_secs)))
            self._tracker_table.setItem(row, 2, QTableWidgetItem(_hms(total)))

            actions = QWidget()
            lay = QHBoxLayout(actions)
            lay.setContentsMargins(2, 2, 2, 2)
            lay.setSpacing(4)
            close_btn = QPushButton("Закрыть")
            close_btn.clicked.connect(lambda _, tid=tr.id: self._close_tracker(tid))
            del_btn = QPushButton("Удалить")
            del_btn.clicked.connect(lambda _, tid=tr.id: self._delete_tracker(tid))
            lay.addWidget(close_btn)
            lay.addWidget(del_btn)
            self._tracker_table.setCellWidget(row, 3, actions)

    def _close_tracker(self, tracker_id: int) -> None:
        main = self._collector._main if self._collector is not None else None
        if main is None:
            return
        main.close_tracker_window(tracker_id)

    def _delete_tracker(self, tracker_id: int) -> None:
        if self._collector is not None:
            self._collector.pause_tracking(tracker_id)
        tracker = self._storage.get_tracker(tracker_id)
        name = tracker.name if tracker else "этот трекер"
        answer = QMessageBox.question(
            self, "Удалить трекер",
            f"Удалить «{name}» и всю его статистику?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        if self._collector is not None and self._collector._main is not None:
            self._collector._main.delete_tracker(tracker_id)
        else:
            self._storage.delete_tracker(tracker_id)

    def closeEvent(self, event) -> None:
        if self._collector is not None:
            try:
                self._collector.collected.disconnect(self._refresh_ui)
            except TypeError:
                pass
        super().closeEvent(event)
