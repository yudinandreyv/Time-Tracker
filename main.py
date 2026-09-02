"""Time Tracker — точка входа."""

from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication

from tracker_app.app import apply_theme
from tracker_app.file_storage import FileStorage, default_db_path
from tracker_app.icons import app_icon
from tracker_app.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    app = QApplication(argv if argv is not None else sys.argv)
    apply_theme(app)

    icon = app_icon()
    app.setWindowIcon(icon)

    db_path = default_db_path()
    storage = FileStorage(db_path)

    window = MainWindow(storage, icon)
    window.show()

    rc = app.exec()
    storage.close()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())