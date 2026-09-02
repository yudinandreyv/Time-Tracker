import time
from dataclasses import dataclass, field


@dataclass
class TimerEngine:
    """Точный таймер без дрейфа: накапливает прошедшее время через time.monotonic.

    - `elapsed` — накопленное время (сек).
    - `running` — идёт ли счёт.
    - При паузе фиксируется накопленное, при старте снова отсчёт.
    """

    elapsed: float = 0.0
    running: bool = False
    _started_at: float = field(default=0.0, repr=False)

    def start(self) -> None:
        if not self.running:
            self._started_at = time.monotonic()
            self.running = True

    def pause(self) -> float:
        if self.running:
            self.elapsed = self.current()
            self.running = False
        return self.elapsed

    def reset(self) -> None:
        self.elapsed = 0.0
        self.running = False
        self._started_at = 0.0

    def current(self) -> float:
        """Текущее накопленное время (включая идущий отрезок)."""
        if self.running:
            return self.elapsed + (time.monotonic() - self._started_at)
        return self.elapsed

    def tick(self) -> float:
        """Возвращает текущее время; вызывается периодически для обновления UI."""
        return self.current()
