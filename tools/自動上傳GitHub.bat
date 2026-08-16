@echo off
chcp 65001 >nul
title 自動上傳 GitHub — GOO BLASTER
cd /d "%~dp0"

where git >nul 2>nul || (
  echo.
  echo   找不到 git。請先安裝：https://git-scm.com/download/win
  echo   安裝時全部用預設值即可。
  echo.
  pause & goto :eof
)

where python >nul 2>nul && (python auto-push.py & goto :eof)
where py     >nul 2>nul && (py auto-push.py & goto :eof)
where python3 >nul 2>nul && (python3 auto-push.py & goto :eof)

echo.
echo   找不到 Python。請安裝：https://www.python.org/downloads/
echo   安裝時記得勾選 "Add Python to PATH"
echo.
pause
