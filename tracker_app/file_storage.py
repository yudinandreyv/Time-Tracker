"""Хранилище в одном файле data.bin: трекеры, Session-строки учёта, статистика.

Данные сериализуются в JSON и лёгкой XOR-обфускацией с фиксированной
codepage-подстановкой. Никакой СУБД: один нечитаемый файл, перезаписываемый
атомарно.

Статистика построена на Session-строках: по одной строке на трекер за день.
Каждое обновление (tick) прибавляет дельту в строку трекера за текущий день.
Полночная функция закрывает вчерашние строки. Удаление трекера убирает его
вклад из статистики.
"""

from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

from .models import Session, Tracker


def _encode(data: bytes) -> bytes:
    """XOR с периодическим ключом + сдвиг по таблице codepage."""
    key = bytes([0x5A, 0x6B, 0x7C, 0x8D, 0x9E])
    table = bytes(range(256))
    shifted = table[97:] + table[:97]
    return bytes(shifted[b ^ key[i % len(key)]] for i, b in enumerate(data))


def _decode(data: bytes) -> bytes:
    key = bytes([0x5A, 0x6B, 0x7C, 0x8D, 0x9E])
    table = bytes(range(256))
    shifted = table[97:] + table[:97]
    unshift = [0] * 256
    for i, v in enumerate(shifted):
        unshift[v] = i
    return bytes(unshift[b] ^ key[i % len(key)] for i, b in enumerate(data))


class FileStorage:
    """Тонкая обёртка над JSON в одном файле."""

    def __init__(self, path: str | Path):
        self._path = str(path)
        self.data_path = self._path
        self._trackers: list[Tracker] = []
        self._sessions: list[Session] = []  # строки учёта (трекер × день)
        self._settings: dict[str, str] = {}
        self._next_tracker_id = 1
        self._next_session_id = 1
        self._load()

    # --- Загрузка / сброс диска ---

    def _load(self) -> None:
        p = Path(self._path)
        if not p.exists():
            return
        try:
            data = _decode(p.read_bytes())
            obj = __import__("json").loads(data.decode("utf-8"))
        except Exception:
            # Бэкап битого файла перед перезаписью
            try:
                import shutil
                from time import time
                backup = f"{self._path}.corrupt.{int(time())}"
                shutil.copy2(self._path, backup)
            except Exception:
                pass
            obj = None
        if not isinstance(obj, dict):
            return
        self._trackers = [self._dict_to_tracker(t) for t in obj.get("trackers", [])]
        self._sessions = [self._dict_to_session(s) for s in obj.get("sessions", [])]
        self._settings = dict(obj.get("settings", {}))
        self._next_tracker_id = max([t.id or 0 for t in self._trackers], default=0) + 1
        self._next_session_id = max([s.id or 0 for s in self._sessions], default=0) + 1

    def _save(self) -> None:
        import json

        obj = {
            "trackers": [self._tracker_to_dict(t) for t in self._trackers],
            "sessions": [self._session_to_dict(s) for s in self._sessions],
            "settings": self._settings,
        }
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        tmp = self._path + ".tmp"
        with open(tmp, "wb") as fh:
            fh.write(_encode(payload))
        os.replace(tmp, self._path)

    @staticmethod
    def _tracker_to_dict(t: Tracker) -> dict:
        return {
            "id": t.id,
            "name": t.name,
            "color": t.color,
            "pos_x": t.pos_x,
            "pos_y": t.pos_y,
            "always_on_top": t.always_on_top,
            "elapsed_seconds": t.elapsed_seconds,
            "created_at": t.created_at,
        }

    @staticmethod
    def _session_to_dict(s: Session) -> dict:
        return {
            "id": s.id,
            "tracker_id": s.tracker_id,
            "day": s.day,
            "started_at": s.started_at,
            "ended_at": s.ended_at,
            "total_seconds": s.total_seconds,
            "delta_seconds": s.delta_seconds,
            "running": s.running,
            "name": s.name,
        }

    @staticmethod
    def _dict_to_tracker(d: dict) -> Tracker:
        return Tracker(
            id=d.get("id"),
            name=d.get("name", "new tracker"),
            color=d.get("color", "#7dd3fc"),
            pos_x=d.get("pos_x", 100),
            pos_y=d.get("pos_y", 100),
            always_on_top=bool(d.get("always_on_top", False)),
            elapsed_seconds=float(d.get("elapsed_seconds", 0.0)),
            created_at=d.get("created_at", ""),
        )

    @staticmethod
    def _dict_to_session(d: dict) -> Session:
        return Session(
            id=d.get("id"),
            tracker_id=d.get("tracker_id"),
            day=d.get("day", date.today().isoformat()),
            started_at=d.get("started_at", ""),
            ended_at=d.get("ended_at", ""),
            total_seconds=float(d.get("total_seconds", 0.0)),
            delta_seconds=float(d.get("delta_seconds", 0.0)),
            running=bool(d.get("running", False)),
            name=d.get("name", ""),
        )

    # --- Трекеры ---

    def save_tracker(self, tracker: Tracker) -> Tracker:
        if tracker.id is None:
            tracker.id = self._next_tracker_id
            self._next_tracker_id += 1
            self._trackers.append(tracker)
        else:
            for i, t in enumerate(self._trackers):
                if t.id == tracker.id:
                    self._trackers[i] = tracker
                    break
        self._save()
        return tracker

    def get_tracker(self, tracker_id: int) -> Tracker | None:
        for t in self._trackers:
            if t.id == tracker_id:
                return t
        return None

    def list_trackers(self) -> list[Tracker]:
        return list(self._trackers)

    def delete_tracker(self, tracker_id: int) -> None:
        # Сначала убираем вклад трекера из статистики (Session), потом сам трекер.
        self.remove_tracker_stats(tracker_id)
        self._trackers = [t for t in self._trackers if t.id != tracker_id]
        self._sessions = [s for s in self._sessions if s.tracker_id != tracker_id]
        self._save()

    def update_position(self, tracker_id: int, x: int, y: int) -> None:
        t = self.get_tracker(tracker_id)
        if t:
            t.pos_x = x
            t.pos_y = y
            self._save()

    def update_elapsed(self, tracker_id: int, seconds: float) -> None:
        t = self.get_tracker(tracker_id)
        if t:
            t.elapsed_seconds = seconds
            self._save()

    # --- Настройки ---

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        return self._settings.get(key, default)

    def set_setting(self, key: str, value: str) -> None:
        self._settings[key] = value
        self._save()

    # --- Session (строки учёта / статистика) ---

    def list_sessions(self) -> list[Session]:
        return sorted(self._sessions, key=lambda s: (s.day, s.tracker_id))

    def ensure_session(self, tracker_id: int, day: str | None = None) -> Session:
        """Возвращает (или создаёт) строку учёта трекера за день."""
        day = day or date.today().isoformat()
        for s in self._sessions:
            if s.tracker_id == tracker_id and s.day == day:
                return s
        t = self.get_tracker(tracker_id)
        now = datetime.now().isoformat(timespec="seconds")
        session = Session(
            id=self._next_session_id,
            tracker_id=tracker_id,
            day=day,
            started_at=now,
            ended_at=now,
            name=t.name if t else "",
        )
        self._next_session_id += 1
        self._sessions.append(session)
        self._save()
        return session

    def add_delta(self, tracker_id: int, day: str, seconds: float) -> None:
        """Прибавляет дельту в статистику трекера за день (только вперёд)."""
        if seconds <= 0:
            return
        s = self.ensure_session(tracker_id, day)
        s.total_seconds += seconds
        s.delta_seconds = seconds
        s.ended_at = datetime.now().isoformat(timespec="seconds")
        self._save()

    def mark_session_running(self, tracker_id: int, running: bool, day: str, now: str) -> None:
        s = self.ensure_session(tracker_id, day)
        s.running = running
        s.started_at = now if s.started_at == "" else s.started_at
        s.ended_at = now
        self._save()

    def rollover_day(self, old_day: str) -> None:
        """Полночная функция: закрывает вчерашние строки, открывает сегодняшние.

        Дельту трекера, которая «перешла через полночь», относим к вчерашнему
        дню (дню начала), а сегодняшний день начинает отсчёт заново.
        """
        today = date.today().isoformat()
        if today == old_day:
            return
        for s in self._sessions:
            if s.day == old_day and s.running:
                s.running = False
                s.ended_at = datetime.now().isoformat(timespec="seconds")
        self._save()

    def remove_tracker_stats(self, tracker_id: int) -> None:
        """Единственное изъятие: убирает вклад трекера из статистики."""
        self._sessions = [s for s in self._sessions if s.tracker_id != tracker_id]
        self._save()

    # --- Агрегаты статистики (читаются из Session-строк) ---

    def per_day(self) -> list[tuple[str, float]]:
        acc: dict[str, float] = {}
        for s in self._sessions:
            acc[s.day] = acc.get(s.day, 0.0) + s.total_seconds
        return sorted(acc.items())

    def per_tracker_total(self) -> list[tuple[str, float, int]]:
        acc: dict[int, float] = {}
        for s in self._sessions:
            acc[s.tracker_id] = acc.get(s.tracker_id, 0.0) + s.total_seconds
        names = {t.id: (t.name if t else "") for t in self._trackers}
        return [
            (names.get(tid, "?"), total, tid)
            for tid, total in sorted(acc.items(), key=lambda kv: kv[1], reverse=True)
        ]

    def total_today(self) -> float:
        today = date.today().isoformat()
        return sum(s.total_seconds for s in self._sessions if s.day == today)

    def tracker_total(self, tracker_id: int) -> float:
        return sum(s.total_seconds for s in self._sessions if s.tracker_id == tracker_id)

    def close(self) -> None:
        self._save()


def default_db_path() -> str:
    """Путь файла данных по умолчанию: ~/.local/share/time-tracker/data.bin."""
    base = Path.home() / ".local" / "share" / "time-tracker"
    base.mkdir(parents=True, exist_ok=True)
    return str(base / "data.bin")