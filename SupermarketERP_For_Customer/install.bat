@echo off
title Supermarket ERP Installer
color 0A
echo ========================================
echo    Supermarket ERP - One Click Install
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set version=%%i
    echo ✅ Python %version% found
)

echo [2/4] Installing dependencies...
pip install -r requirements.txt

echo [3/4] Creating desktop shortcut...
powershell "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\Supermarket ERP.lnk'); $SC.TargetPath = '%~dp0start.bat'; $SC.Save()" 2>nul

echo [4/4] Setup complete!
echo.
echo ========================================
echo    ✅ INSTALLATION COMPLETE!
echo ========================================
echo.
echo 🔑 Default Login: admin / admin123
echo.
echo Starting Supermarket ERP...
start start.bat
echo.
pause
