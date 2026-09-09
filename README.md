# Time Tracker

Минималистичный трекер времени.   

## Возможности

- **Независимые окна-таймеры** — каждое поверх других, со своим именем и управлением
- **Счёт без дрейфа** — `time.monotonic()`, не по тикам UI
- **Персистентность** — трекеры, позиции и статистика хранятся в `data.bin` и восстанавливаются при перезапуске
- **Статистика** — по дням, по трекерам, общее.



## Сборка бинарника

```bash
# Linux
bash build-linux.sh

# macOS (нужен Mac или GitHub Actions)
bash build-mac.sh
```

Результат: `dist/time-tracker` (Linux) или `dist/TimeTracker.app` (macOS)

## Структура

```
tracker_app/
├── models.py           # Tracker, Session (dataclass)
├── file_storage.py     # data.bin (JSON + XOR)
├── timer.py            # TimerEngine (monotonic)
├── collector.py        # DeltaCollector (всегда живой)
├── main_window.py      # панель управления
├── tracker_window.py   # окно-таймер
├── stats_window.py     # статистика (чистый читатель)
├── app.py              # тема (QSS)
├── icons.py            # SVG иконки из кода
└── tooltip.py          # балloon-подсказки
```

## CI/CD

GitHub Actions собирает автоматически:
- **Linux** (`ubuntu-latest`) → `time-tracker`
- **macOS** (`macos-latest`) → `TimeTracker.app`


