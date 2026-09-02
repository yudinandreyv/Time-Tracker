#!/bin/bash
# Сборка time-tracker для Linux (Debian/Ubuntu/Fedora/Arch)
# Запускать на Linux: bash build-linux.sh

set -e

echo "=== Проверка зависимостей ==="
python3 --version || { echo "Нужен python3"; exit 1; }
pip3 install pyinstaller PyQt5 2>/dev/null || pip3 install --user pyinstaller PyQt5

echo ""
echo "=== Сборка ==="
pyinstaller --onefile --clean --name time-tracker main.py

echo ""
echo "=== Готово ==="
ls -lh dist/time-tracker
echo "Запуск: ./dist/time-tracker"
