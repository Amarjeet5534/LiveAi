@echo off
cd /d "%~dp0"
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt --timeout=1000
) else (
    call .venv\Scripts\activate.bat
)
echo Launching LiveAI Desktop App...
python desktop.py
pause
