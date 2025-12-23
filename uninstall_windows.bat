@echo off
:: Uninstall script for PixelForge Studio on Windows

echo.
echo =====================================
echo   PixelForge Studio - Desinstallation
echo =====================================
echo.

set APP_DIR=%LOCALAPPDATA%\PixelForgeStudio

echo Suppression des fichiers...
if exist "%APP_DIR%" rmdir /S /Q "%APP_DIR%"

echo Suppression des raccourcis...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\PixelForge Studio.lnk" del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\PixelForge Studio.lnk"
if exist "%USERPROFILE%\Desktop\PixelForge Studio.lnk" del "%USERPROFILE%\Desktop\PixelForge Studio.lnk"

echo.
echo =====================================
echo   Desinstallation terminee !
echo =====================================
echo.
echo Note: Les fichiers de configuration dans %%APPDATA%%\pixelforge-studio
echo n'ont pas ete supprimes.
echo.
pause
