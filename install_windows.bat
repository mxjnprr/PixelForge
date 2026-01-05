@echo off
:: Install script for PixelForge Studio on Windows

echo.
echo ====================================
echo   PixelForge Studio - Installation
echo ====================================
echo.

set APP_NAME=PixelForge Studio
set APP_DIR=%LOCALAPPDATA%\PixelForgeStudio
set SCRIPT_DIR=%~dp0

REM ========================================
REM Detect Python 3 executable - test actual execution, not just existence
REM (Windows has fake python3/python aliases that redirect to Store)
REM ========================================
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
echo Veuillez FERMER cette fenetre et relancer install_windows.bat
echo (Le PATH doit etre recharge)
pause
exit /b 0

:found_python
echo Python 3 detecte: %PYTHON_CMD%
echo.

REM ========================================
REM Installation
REM ========================================

echo [1/5] Creation du dossier d'installation...
if not exist "%APP_DIR%" mkdir "%APP_DIR%"

echo [2/5] Copie des fichiers...
xcopy /E /I /Y "%SCRIPT_DIR%*.py" "%APP_DIR%\" >nul
xcopy /E /I /Y "%SCRIPT_DIR%gui" "%APP_DIR%\gui\" >nul
xcopy /E /I /Y "%SCRIPT_DIR%utils" "%APP_DIR%\utils\" >nul
copy /Y "%SCRIPT_DIR%requirements.txt" "%APP_DIR%\" >nul
if exist "%SCRIPT_DIR%icon.ico" copy /Y "%SCRIPT_DIR%icon.ico" "%APP_DIR%\" >nul

echo [3/5] Creation de l'environnement Python...
%PYTHON_CMD% -m venv "%APP_DIR%\venv"

echo [4/5] Installation des dependances...
"%APP_DIR%\venv\Scripts\python.exe" -m pip install --upgrade pip -q
"%APP_DIR%\venv\Scripts\pip.exe" install -r "%APP_DIR%\requirements.txt" -q

echo [5/5] Creation du raccourci...
:: Create launcher batch file
(
echo @echo off
echo cd /d "%APP_DIR%"
echo call venv\Scripts\activate.bat
echo python main.py
) > "%APP_DIR%\launch.bat"

:: Create VBScript to run without console window
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run chr^(34^) ^& "%APP_DIR%\launch.bat" ^& chr^(34^), 0
echo Set WshShell = Nothing
) > "%APP_DIR%\launch.vbs"

:: Create Start Menu shortcut using PowerShell (with icon)
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\PixelForge Studio.lnk'); $SC.TargetPath = '%APP_DIR%\launch.vbs'; $SC.WorkingDirectory = '%APP_DIR%'; $SC.IconLocation = '%APP_DIR%\icon.ico'; $SC.Description = 'Editez et generez des images avec IA'; $SC.Save()"

:: Create Desktop shortcut (try both standard and OneDrive paths)
powershell -Command "try { $WS = New-Object -ComObject WScript.Shell; $desktop = [Environment]::GetFolderPath('Desktop'); $SC = $WS.CreateShortcut((Join-Path $desktop 'PixelForge Studio.lnk')); $SC.TargetPath = '%APP_DIR%\launch.vbs'; $SC.WorkingDirectory = '%APP_DIR%'; $SC.IconLocation = '%APP_DIR%\icon.ico'; $SC.Description = 'Editez et generez des images avec IA'; $SC.Save() } catch { Write-Host 'Note: Raccourci Bureau non cree (chemin non trouve)' }"

echo.
echo ====================================
echo   Installation terminee !
echo ====================================
echo.
echo Vous pouvez maintenant lancer PixelForge Studio depuis :
echo   - Le menu Demarrer
echo   - Le raccourci sur le Bureau
echo.
echo Pour desinstaller : uninstall_windows.bat
echo.
pause

