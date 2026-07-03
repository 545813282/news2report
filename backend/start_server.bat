@echo off
chcp 65001 >nul
call .venv\Scripts\activate.bat
set PYTHONIOENCODING=utf-8
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
echo.
pause
