@echo off
chcp 65001 >nul
title GOO BLASTER 本機測試伺服器
cd /d "%~dp0"

rem 依序嘗試各種 Python / Node 的叫法，哪個有就用哪個
where python >nul 2>nul && (python start-server.py & goto :eof)
where py     >nul 2>nul && (py start-server.py & goto :eof)
where python3 >nul 2>nul && (python3 start-server.py & goto :eof)
where npx    >nul 2>nul && (
  echo 找不到 Python，改用 Node 的 http-server...
  echo 手機請用 http://[你的區網IP]:8000 開啟
  npx --yes http-server . -p 8000 -c-1
  goto :eof
)

echo.
echo   找不到 Python 也找不到 Node。
echo   最簡單的解法：到 https://www.python.org/downloads/ 安裝 Python
echo   安裝時記得勾選 "Add Python to PATH"
echo.
pause
