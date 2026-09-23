#!/bin/bash
# СБОРКА time-tracker → dist/time-tracker (Python 3.12)
set -e
cd "$(dirname "$0")"

echo "=== СБОРКА ==="

PY=".venv/bin/python"
PYI=".venv/bin/pyinstaller"

if [ ! -x "$PY" ]; then
    echo "ОШИБКА: нет .venv"
    echo "  создать: python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi
if ! "$PY" -c "import sys; sys.exit(0 if sys.version_info[:2]==(3,12) else 1)"; then
    echo "ОШИБКА: нужен Python 3.12, сейчас: $($PY --version)"
    exit 1
fi
if ! "$PY" -c "import PyQt5" 2>/dev/null; then
    echo "ОШИБКА: PyQt5 не установлен — .venv/bin/pip install -r requirements.txt"
    exit 1
fi
if [ ! -x "$PYI" ]; then
    echo "ОШИБКА: pyinstaller не установлен — .venv/bin/pip install -r requirements.txt"
    exit 1
fi
echo "Зависимости OK: $($PY --version), $($PYI --version 2>/dev/null | head -1)"

# Мусор прошлых сборок (промежуточные файлы PyInstaller)
rm -rf build/

"$PYI" --onefile --clean --name time-tracker main.py -y

echo "=== ГОТОВО ==="
ls -lh dist/time-tracker
