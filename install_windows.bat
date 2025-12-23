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

echo [1/5] Creation du dossier d'installation...
if not exist "%APP_DIR%" mkdir "%APP_DIR%"

echo [2/5] Copie des fichiers...
xcopy /E /I /Y "%SCRIPT_DIR%*.py" "%APP_DIR%\" >nul
xcopy /E /I /Y "%SCRIPT_DIR%gui" "%APP_DIR%\gui\" >nul
xcopy /E /I /Y "%SCRIPT_DIR%utils" "%APP_DIR%\utils\" >nul
copy /Y "%SCRIPT_DIR%requirements.txt" "%APP_DIR%\" >nul
if exist "%SCRIPT_DIR%icon.ico" copy /Y "%SCRIPT_DIR%icon.ico" "%APP_DIR%\" >nul

echo [3/5] Creation de l'environnement Python...
python -m venv "%APP_DIR%\venv"

echo [4/5] Installation des dependances...
"%APP_DIR%\venv\Scripts\pip.exe" install --upgrade pip -q
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

:: Create Start Menu shortcut using PowerShell
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\PixelForge Studio.lnk'); $SC.TargetPath = '%APP_DIR%\launch.vbs'; $SC.WorkingDirectory = '%APP_DIR%'; $SC.Description = 'Editez et generez des images avec IA'; $SC.Save()"

:: Create Desktop shortcut
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\PixelForge Studio.lnk'); $SC.TargetPath = '%APP_DIR%\launch.vbs'; $SC.WorkingDirectory = '%APP_DIR%'; $SC.Description = 'Editez et generez des images avec IA'; $SC.Save()"

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
