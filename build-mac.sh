#!/bin/bash
# Сборка time-tracker для macOS
# Запускать на macOS: bash build-mac.sh
# Требуется: python3, pip, pyinstaller
#
# Результат: dist/time-tracker.app (перетащить в Applications)
#
# Если Python не установлен:
#   brew install python@3.12
#   pip3 install pyinstaller PyQt5

set -e

echo "=== Проверка зависимостей ==="
python3 --version || { echo "Нужен python3. Установи: brew install python@3.12"; exit 1; }
pip3 install pyinstaller PyQt5 2>/dev/null || pip3 install --user pyinstaller PyQt5

echo ""
echo "=== Сборка .app bundle ==="
pyinstaller \
    --onefile \
    --clean \
    --name time-tracker \
    main.py

echo ""
echo "=== Готово ==="
echo "Бинарник: dist/time-tracker"
echo "Чтобы сделать .app bundle:"
echo "  mkdir -p dist/time-tracker.app/Contents/MacOS"
echo "  mkdir -p dist/time-tracker.app/Contents/Resources"
echo "  cp dist/time-tracker dist/time-tracker.app/Contents/MacOS/"
echo "  # Или просто запусти dist/time-tracker"
echo ""
echo "Для .app с иконкой используй bundler (py2app или manually)."

# Автоматический .app bundle
if [ -f "dist/time-tracker" ]; then
    echo ""
    echo "=== Создаю .app bundle ==="
    APP="dist/TimeTracker.app"
    mkdir -p "$APP/Contents/MacOS"
    mkdir -p "$APP/Contents/Resources"
    cp dist/time-tracker "$APP/Contents/MacOS/"

    cat > "$APP/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>TimeTracker</string>
    <key>CFBundleDisplayName</key>
    <string>Time Tracker</string>
    <key>CFBundleIdentifier</key>
    <string>com.anatoliy.time-tracker</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

    echo "Готово: $APP"
    echo "Перетащи в Applications или запусти: open $APP"
fi
