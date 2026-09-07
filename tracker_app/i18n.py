"""Международизация (i18n): словари RU/EN, функция _() для перевода UI-строк."""

from __future__ import annotations

_LANG = "ru"

RU = {
    "running": "▶ в работе",
    "pin_main": "Поверх всех",
    "add_tracker": "+ Добавить трекер",
    "statistics": "Статистика",
    "collapse_all": "Свернуть все",
    "expand_all": "Развернуть все",
    "status_open": "{n} трекеров · {k} открыто",
    "status_hint": "{n} трекеров · двойной клик — открыть",
    "tray_show": "Показать окна",
    "tray_minimize": "Свернуть в трей",
    "tray_quit": "Выход",
    "pin_tracker": "Поверх всех окон",
    "start": "▶ Старт",
    "hint_start": "Введите имя задачи, затем ▶ Старт",
    "theme": "Тема",
    "language": "Язык",
    "lang_ru": "Русский",
    "lang_en": "English",
    "close": "Закрыть",
    "header_name": "Имя",
    "header_today": "Сегодня",
    "header_total": "За всё время",
    "time_h_m": "{h}ч {m:02d}м",
    "time_m_s": "{m}м {s:02d}с",
    "time_s": "{s}с",
    "no_data": "Нет данных",
    "stats_title": "Статистика",
    "by_days": "Сумма времени по дням",
    "header_date": "Дата",
    "header_time": "Время",
    "by_trackers": "Время по трекерам (за всё время)",
    "header_tracker": "Трекер",
    "refresh": "Обновить",
    "tab_days": "По дням",
    "tab_trackers": "По трекерам",
    "tab_all": "Трекеры",
    "today_label": "Сегодня: {time}",
    "no_days_data": "Нет данных по дням",
    "no_trackers_data": "Нет данных по трекерам",
    "delete": "Удалить",
    "this_tracker": "этот трекер",
    "delete_title": "Удалить трекер",
    "delete_confirm": "Удалить «{name}» и всю его статистику?",
}

EN = {
    "running": "▶ running",
    "pin_main": "Always on top",
    "add_tracker": "+ Add tracker",
    "statistics": "Statistics",
    "collapse_all": "Collapse all",
    "expand_all": "Expand all",
    "status_open": "{n} trackers · {k} open",
    "status_hint": "{n} trackers · double-click to open",
    "tray_show": "Show windows",
    "tray_minimize": "Minimize to tray",
    "tray_quit": "Quit",
    "pin_tracker": "Always on top",
    "start": "▶ Start",
    "hint_start": "Enter task name, then ▶ Start",
    "theme": "Theme",
    "language": "Language",
    "lang_ru": "Русский",
    "lang_en": "English",
    "close": "Close",
    "header_name": "Name",
    "header_today": "Today",
    "header_total": "All time",
    "time_h_m": "{h}h {m:02d}m",
    "time_m_s": "{m}m {s:02d}s",
    "time_s": "{s}s",
    "no_data": "No data",
    "stats_title": "Statistics",
    "by_days": "Total time by days",
    "header_date": "Date",
    "header_time": "Time",
    "by_trackers": "Time by trackers (all time)",
    "header_tracker": "Tracker",
    "refresh": "Refresh",
    "tab_days": "By days",
    "tab_trackers": "By trackers",
    "tab_all": "Trackers",
    "today_label": "Today: {time}",
    "no_days_data": "No daily data",
    "no_trackers_data": "No tracker data",
    "delete": "Delete",
    "this_tracker": "this tracker",
    "delete_title": "Delete tracker",
    "delete_confirm": "Delete \"{name}\" and all its statistics?",
}

_TRANSLATIONS = {"ru": RU, "en": EN}


def _(key: str, **kwargs) -> str:
    d = _TRANSLATIONS.get(_LANG, RU)
    text = d.get(key, RU.get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def set_language(lang: str) -> None:
    global _LANG
    _LANG = lang if lang in _TRANSLATIONS else "ru"


def current_language() -> str:
    return _LANG
