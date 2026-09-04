"""Панель управления: список трекеров, добавление, статистика, выход."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .collector import DeltaCollector
from .file_storage import FileStorage
from .icons import gear_icon, pin_icon
from .models import Tracker
from .settings_dialog import SettingsDialog
from .stats_window import StatsWindow
from .tooltip import Tooltip
from .tracker_window import TrackerWindow


class TrackerItem(QWidget):
    """Строка в списке панели: цвет, имя, статус."""

    def __init__(self, tracker: Tracker, running: bool):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {tracker.color};")
        self._name = QLabel(tracker.name)
        self._status = QLabel("▶ в работе" if running else "—")
        self._status.setObjectName("hint" if not running else "trackerName")
        lay.addWidget(dot)
        lay.addWidget(self._name, stretch=1)
        lay.addWidget(self._status)

    def set_running(self, running: bool) -> None:
        self._status.setText("▶ в работе" if running else "—")


class MainWindow(QDialog):
    """Главное окно приложения."""

    SETTING_ON_TOP = "main_always_on_top"

    def __init__(self, storage: FileStorage, icon: QIcon | None = None):
        super().__init__()
        self._storage = storage
        self._tracker_windows: dict[int, TrackerWindow] = {}
        self._tray: QSystemTrayIcon | None = None
        self._stats_window: StatsWindow | None = None
        self._settings_window: SettingsDialog | None = None
        self._collector = DeltaCollector(storage, self)

        self.setWindowTitle("Time Tracker")
        self.setWindowFlags(
            Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(300)
        self._build_ui()
        self._build_effects()
        self._apply_main_on_top(self._storage.get_setting(self.SETTING_ON_TOP, "1") == "1")
        self._reload_list()
        self._setup_tray(icon)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        title_row = QHBoxLayout()

        self._settings_btn = QPushButton(gear_icon(), "")
        self._settings_btn.setFixedWidth(28)
        self._tooltip = Tooltip(self)
        self._tooltip.attach(self._settings_btn, "Settings")
        self._settings_btn.clicked.connect(self._open_settings)
        title_row.addWidget(self._settings_btn)

        title = QLabel("Time Tracker")
        self._title = title
        title.setObjectName("trackerName")
        title.setAlignment(Qt.AlignCenter)
        title_row.addWidget(title, stretch=1)

        self._pin_btn = QPushButton(pin_icon(), "")
        self._pin_btn.setFixedWidth(28)
        self._pin_btn.setCheckable(True)
        self._tooltip.attach(self._pin_btn, "Поверх всех")
        self._pin_btn.clicked.connect(self._toggle_main_on_top)
        title_row.addWidget(self._pin_btn)
        root.addLayout(title_row)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        root.addWidget(self._list, stretch=1)

        btn_add = QPushButton("+ Добавить трекер")
        btn_add.setObjectName("primary")
        self._btn_add = btn_add
        btn_add.clicked.connect(self.add_tracker)
        root.addWidget(btn_add)

        btn_stats = QPushButton("Статистика")
        btn_stats.clicked.connect(self.open_stats)
        root.addWidget(btn_stats)

        self._btn_toggle = QPushButton("Свернуть все")
        self._btn_toggle.setObjectName("secondary")
        self._btn_toggle.clicked.connect(self._toggle_windows)
        root.addWidget(self._btn_toggle)

        self._status_label = QLabel()
        self._status_label.setObjectName("hint")
        self._status_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self._status_label)
        self._update_status()

    # --- Эффекты (из доступных библиотек Qt) ---

    def _build_effects(self) -> None:
        glow = QGraphicsDropShadowEffect(self._btn_add)
        glow.setBlurRadius(20)
        glow.setOffset(0, 0)
        glow.setColor(QColor(14, 165, 233, 170))
        self._btn_add.setGraphicsEffect(glow)

        title_glow = QGraphicsDropShadowEffect(self._title)
        title_glow.setBlurRadius(24)
        title_glow.setOffset(0, 0)
        title_glow.setColor(QColor(125, 211, 252, 140))
        self._title.setGraphicsEffect(title_glow)

    # --- Управление трекерами ---

    def add_tracker(self) -> None:
        tracker = Tracker()  # имя "new tracker", поверх всех = False по умолчанию
        tracker = self._storage.save_tracker(tracker)
        if tracker.id is not None:
            tracker.name = f"new tracker_{tracker.id}"
            tracker = self._storage.save_tracker(tracker)
        self.open_tracker_window(tracker)

    def open_tracker_window(self, tracker: Tracker) -> None:
        existing = self._tracker_windows.get(tracker.id)
        if existing is not None:
            existing.show()
            existing.raise_()
            return
        win = TrackerWindow(tracker)
        win.closed.connect(self._on_tracker_closed)
        win.position_changed.connect(self._on_position_changed)
        win.name_changed.connect(self._on_name_changed)
        win.always_on_top_changed.connect(self._on_always_on_top_changed)
        win.elapsed_changed.connect(self._on_elapsed_changed)
        win.running_changed.connect(self._on_running_changed)
        win.show()
        self._tracker_windows[tracker.id] = win
        self._collector.register_window(win)
        self._reload_list()

    def _on_item_double_clicked(self, item) -> None:
        idx = self._list.row(item)
        trackers = self._storage.list_trackers()
        if 0 <= idx < len(trackers):
            self.open_tracker_window(trackers[idx])

    def _reload_list(self) -> None:
        self._list.clear()
        for tracker in self._storage.list_trackers():
            win = self._tracker_windows.get(tracker.id)
            running = win.is_running if win else False
            item = QListWidgetItem()
            widget = TrackerItem(tracker, running)
            widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            item.setSizeHint(widget.sizeHint())
            self._list.addItem(item)
            self._list.setItemWidget(item, widget)
        self._update_status()
        self._update_toggle_label()

    def _update_status(self) -> None:
        total = len(self._storage.list_trackers())
        open_count = len(self._tracker_windows)
        if open_count:
            self._status_label.setText(f"{total} трекеров · {open_count} открыто")
        else:
            self._status_label.setText(f"{total} трекеров · двойной клик — открыть")
    # --- Обработчики событий ---

    def _on_position_changed(self, tracker_id: int, x: int, y: int) -> None:
        self._storage.update_position(tracker_id, x, y)

    def _on_name_changed(self, tracker_id: int, name: str) -> None:
        tracker = self._storage.get_tracker(tracker_id)
        if tracker:
            tracker.name = name
            self._storage.save_tracker(tracker)
        self._reload_list()

    def _on_tracker_closed(self, tracker_id: int) -> None:
        win = self._tracker_windows.get(tracker_id)
        if win is not None:
            self._collector.unregister_window(win)
            del self._tracker_windows[tracker_id]
        self._reload_list()

    def _on_elapsed_changed(self, tracker_id: int, seconds: float) -> None:
        self._storage.update_elapsed(tracker_id, seconds)

    def _on_running_changed(self, _running: bool) -> None:
        self._reload_list()

    def _on_always_on_top_changed(self, tracker_id: int, flag: bool) -> None:
        tracker = self._storage.get_tracker(tracker_id)
        if tracker:
            tracker.always_on_top = flag
            self._storage.save_tracker(tracker)

    # --- Трей и фоновый режим ---

    def _setup_tray(self, icon: QIcon | None = None) -> None:
        tray = QSystemTrayIcon(icon or QIcon(), self)
        tray.setToolTip("Time Tracker")

        menu = QMenu()
        act_show = QAction("Показать окна", menu)
        act_show.triggered.connect(self.restore_windows)
        menu.addAction(act_show)

        act_hide = QAction("Свернуть в трей", menu)
        act_hide.triggered.connect(self.minimize_to_tray)
        menu.addAction(act_hide)

        menu.addSeparator()

        act_quit = QAction("Выход", menu)
        act_quit.triggered.connect(self.quit_app)
        menu.addAction(act_quit)

        tray.setContextMenu(menu)
        tray.activated.connect(
            lambda reason: self.restore_windows() if reason == QSystemTrayIcon.Trigger else None
        )
        tray.show()
        self._tray = tray

    def _update_toggle_label(self) -> None:
        any_visible = any(w.isVisible() for w in self._tracker_windows.values())
        self._btn_toggle.setText("Свернуть все" if any_visible else "Развернуть все")

    def _toggle_windows(self) -> None:
        any_visible = any(w.isVisible() for w in self._tracker_windows.values())
        if any_visible:
            self.hide_trackers()
        else:
            self.show_trackers()

    def hide_trackers(self) -> None:
        for win in self._tracker_windows.values():
            win.hide()
        self._update_toggle_label()

    def show_trackers(self) -> None:
        for win in self._tracker_windows.values():
            win.show()
            win.raise_()
        self._update_toggle_label()

    def minimize_to_tray(self) -> None:
        for win in self._tracker_windows.values():
            win.hide()
        self.hide()
        self._update_toggle_label()

    def restore_windows(self) -> None:
        for win in self._tracker_windows.values():
            win.show()
        self.show()
        self.raise_()
        self.activateWindow()
        self._update_toggle_label()

    def quit_app(self) -> None:
        self._collector.stop()
        for win in list(self._tracker_windows.values()):
            win.close()
        if self._tray is not None:
            self._tray.hide()
        self.close()

    # --- Поверх всех окон (главное окно) ---

    def _toggle_main_on_top(self, checked: bool) -> None:
        self._apply_main_on_top(checked)
        self._storage.set_setting(self.SETTING_ON_TOP, "1" if checked else "0")

    def _apply_main_on_top(self, flag: bool) -> None:
        self._pin_btn.setChecked(flag)
        pos = self.frameGeometry().topLeft()
        was_visible = self.isVisible()
        self.hide()
        self.setWindowFlag(Qt.WindowStaysOnTopHint, flag)
        if was_visible:
            self.show()
            self.move(pos)
        self.raise_()
        self.activateWindow()

    # --- Прочее ---

    def _open_settings(self) -> None:
        win = self._settings_window
        if win is not None and win.isVisible():
            win.raise_()
            win.activateWindow()
            return
        win = SettingsDialog(self._storage)
        win.finished.connect(self._on_settings_destroyed)
        self._settings_window = win
        win.show()

    def _on_settings_destroyed(self, *_args) -> None:
        self._settings_window = None

    def open_stats(self) -> None:
        win = self._stats_window
        if win is not None and win.isVisible():
            win.raise_()
            win.activateWindow()
            return
        win = StatsWindow(self._storage, self._collector)
        win.finished.connect(self._on_stats_destroyed)
        self._stats_window = win
        win.show()

    def _on_stats_destroyed(self, *_args) -> None:
        self._stats_window = None

    def close_tracker_window(self, tracker_id: int) -> None:
        win = self._tracker_windows.get(tracker_id)
        if win is not None:
            win.close()

    def delete_tracker(self, tracker_id: int) -> None:
        self.close_tracker_window(tracker_id)
        self._storage.delete_tracker(tracker_id)
        self._reload_list()

    def closeEvent(self, event) -> None:
        # Закрытие главного окна сворачивает приложение в трей (фоновый режим).
        if self._tray is not None and self._tray.isVisible():
            event.ignore()
            self.minimize_to_tray()
            return
        for win in list(self._tracker_windows.values()):
            win.close()
        super().closeEvent(event)

    def running_stats(self) -> int:
        return sum(1 for w in self._tracker_windows.values() if w.is_running)