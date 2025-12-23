@echo off
REM ============================================
REM Create Installer for PixelForge Studio
REM ============================================
REM Requires Inno Setup to be installed
REM Download from: https://jrsoftware.org/isinfo.php

echo ========================================
echo  PixelForge Studio - Installer Builder
echo ========================================
echo.

REM Check if Inno Setup is installed
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if "%ISCC%"=="" (
    echo ERROR: Inno Setup 6 is not installed!
    echo.
    echo Please download and install Inno Setup from:
    echo   https://jrsoftware.org/isinfo.php
    echo.
    pause
    exit /b 1
)

REM Check if build exists
if not exist "dist\PixelForge Studio\PixelForge Studio.exe" (
    echo ERROR: Application not built yet!
    echo.
    echo Please run build_windows.bat first.
    echo.
    pause
    exit /b 1
)

REM Create installer directory
if not exist "installer" mkdir installer

REM Build installer
echo Building installer...
"%ISCC%" installer.iss

if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installer Created Successfully!
echo ========================================
echo.
echo The installer is located in:
echo   installer\PixelForge-Studio-Setup-1.0.0.exe
echo.
pause
