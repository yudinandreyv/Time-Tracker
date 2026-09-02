from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Tracker:
    """Конфигурация трекера (окна-таймера)."""

    name: str = "new tracker"
    color: str = "#7dd3fc"
    pos_x: int = 100
    pos_y: int = 100
    always_on_top: bool = False
    elapsed_seconds: float = 0.0
    id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class Session:
    """Одна строка учёта одного трекера.

    Хранит все данные о времени трекера: дату (день), время старта,
    общее время за день, текущую дельту с прошлого тика, точку отсчёта
    и признак работы. Положение/управление окна сюда НЕ входит.

    Список сессий = все текущие трекеры (по одной строке на трекер за день).
    """

    tracker_id: int
    day: str  # дата в формате YYYY-MM-DD
    started_at: str  # время старта трека (ISO)
    ended_at: str = ""  # время последнего тика / завершения (ISO)
    total_seconds: float = 0.0  # общее время трекера за этот день
    delta_seconds: float = 0.0  # дельта с прошлого тика
    running: bool = False  # идёт ли отсчёт в данный момент
    name: str = ""
    id: int | None = None
