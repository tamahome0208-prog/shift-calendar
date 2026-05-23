@echo off
chcp 65001 > nul
REM 使い方: update.bat "<新しいシフトxlsxのパス>"

if "%~1"=="" (
  echo Usage: update.bat "C:\path\to\シフト.xlsx"
  exit /b 1
)

cd /d "C:\Users\tamah\Desktop\shift_calendar"
echo === ビルド中 ===
python build.py "%~1"
if errorlevel 1 (
  echo ビルド失敗
  exit /b 1
)

echo.
echo === GitHubに反映中 ===
git add index.html manifest.json sw.js
git commit -m "シフト更新"
git push

echo.
echo 完了! 1〜2分後に以下のURLで確認:
echo https://tamahome0208-prog.github.io/shift-calendar/
