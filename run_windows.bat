@echo off
REM Nano Banana Batch Processor - Windows Launcher
REM Activates virtual environment if present and runs the application

cd /d "%~dp0"

REM Detect Python 3 executable - test actual execution, not just existence
REM (Windows has fake python3/python aliases that redirect to Store)
set PYTHON_CMD=

REM Try py -3 first (Python Launcher)
py -3 -c "import sys; exit(0 if sys.version_info[0]>=3 else 1)" 2>NUL
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    goto :found_python
)

REM Try python (check it's actually v3, not Store alias)
python -c "import sys; exit(0 if sys.version_info[0]>=3 else 1)" 2>NUL
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :found_python
)

echo Python 3 n'est pas detecte sur ce systeme.
echo.

REM Try to install Python via winget
where winget >NUL 2>&1
if errorlevel 1 (
    echo Winget n'est pas disponible pour l'installation automatique.
    echo Veuillez installer Python 3.10+ manuellement depuis https://www.python.org/downloads/
    echo IMPORTANT: Cochez "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

echo Voulez-vous installer Python 3.12 automatiquement via winget? (O/N)
set /p INSTALL_CHOICE=
if /i not "%INSTALL_CHOICE%"=="O" (
    echo Installation annulee.
    echo Veuillez installer Python 3.10+ manuellement depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installation de Python 3.12 en cours...
winget install Python.Python.3.12 --source winget --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo Echec de l'installation automatique.
    echo Veuillez installer Python 3.10+ manuellement depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Python 3.12 a ete installe avec succes!
echo Veuillez FERMER cette fenetre et relancer run_windows.bat
echo (Le PATH doit etre recharge)
pause
exit /b 0

:found_python
echo Python 3 detecte: %PYTHON_CMD%

REM Check for virtual environment and recreate if needed with Python 3
if not exist "venv\Scripts\activate.bat" (
    if not exist ".venv\Scripts\activate.bat" (
        echo Creation de l'environnement virtuel avec Python 3...
        %PYTHON_CMD% -m venv venv
    )
)

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activation de l'environnement virtuel...
    call .venv\Scripts\activate.bat
)

REM Upgrade pip and check dependencies
python -c "import PyQt6" 2>NUL
if errorlevel 1 (
    echo Mise a jour de pip et installation des dependances...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

REM Run the application
echo Demarrage de Nano Banana Batch Processor...
python main.py

pause
