@echo off
REM Nano Banana Batch Processor - Windows Launcher
REM Activates virtual environment if present and runs the application

cd /d "%~dp0"

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Check dependencies
python -c "import PyQt6" 2>NUL
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
echo Starting Nano Banana Batch Processor...
python main.py

pause
