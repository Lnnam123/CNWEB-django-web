@echo off
title CoinTap Web Server
echo ========================================================
echo   DANG KHOI DONG MAY CHU COINTAP DJANGO...
echo   Dia chi truy cap: http://127.0.0.1:8000
echo ========================================================
cd /d "%~dp0"
call .venv\Scripts\activate
python manage.py runserver
pause

