@echo off
REM ============================================
REM Build Script for PixelForge Studio Windows
REM ============================================
REM This script creates a standalone .exe using PyInstaller
REM Must be run on Windows!

echo ========================================
echo  PixelForge Studio - Windows Build
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Create icon.ico from icon.png if needed
if not exist "icon.ico" (
    echo Creating icon.ico...
    python -c "from PIL import Image; img = Image.open('icon.png'); img.save('icon.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])"
)

REM Build with PyInstaller
echo.
echo Building executable...
pyinstaller --clean pixelforge.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo The executable is located in:
echo   dist\PixelForge Studio\PixelForge Studio.exe
echo.
echo To create an installer, run build_installer.bat
echo.
pause
