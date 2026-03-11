#!/bin/bash

echo "📦 Creating Supermarket ERP Customer Package"
echo "============================================"

# Create distribution folder
mkdir -p SupermarketERP_For_Customer

# Copy all necessary files
echo "1️⃣ Copying application files..."
cp -r modules SupermarketERP_For_Customer/
cp -r database SupermarketERP_For_Customer/
cp -r ui SupermarketERP_For_Customer/
cp -r utils SupermarketERP_For_Customer/
cp main.py SupermarketERP_For_Customer/
cp config.py SupermarketERP_For_Customer/
cp requirements.txt SupermarketERP_For_Customer/

# Create launcher for Linux
echo "2️⃣ Creating Linux launcher..."
cat > SupermarketERP_For_Customer/start.sh << 'LAUNCHER'
#!/bin/bash
# Supermarket ERP Launcher for Linux
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
export QT_QPA_PLATFORM=wayland
python3 main.py
LAUNCHER
chmod +x SupermarketERP_For_Customer/start.sh

# Create launcher for Windows
echo "3️⃣ Creating Windows launcher..."
cat > SupermarketERP_For_Customer/start.bat << 'BATCH'
@echo off
cd /d "%~dp0"
python main.py
pause
BATCH

# Create one-click installer for Windows
echo "4️⃣ Creating Windows installer..."
cat > SupermarketERP_For_Customer/install.bat << 'INSTALL'
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
INSTALL

# Create simple README
echo "5️⃣ Creating README..."
cat > SupermarketERP_For_Customer/README.txt << 'README'
╔══════════════════════════════════════════════════════════╗
║         SUPERMARKET ERP - CUSTOMER PACKAGE              ║
╚══════════════════════════════════════════════════════════╝

📋 QUICK INSTALLATION:

FOR WINDOWS:
───────────
1. Double-click "install.bat"
2. Wait for dependencies to install
3. Application starts automatically!
4. Desktop shortcut created

FOR LINUX:
─────────
1. Open terminal in this folder
2. Run: ./start.sh
   or
   python3 main.py

🔑 DEFAULT LOGIN:
────────────────
Username: admin
Password: admin123

✅ NO DATABASE SETUP NEEDED!
───────────────────────────
• SQLite database creates itself automatically
• No MySQL installation required
• No server configuration needed

📞 SUPPORT:
──────────
For any issues, contact: your-email@example.com
README

# Remove any existing database file (will be created on first run)
rm -f SupermarketERP_For_Customer/supermarket.db

# Create the final ZIP
echo "6️⃣ Creating ZIP package..."
zip -r SupermarketERP_Customer_Package.zip SupermarketERP_For_Customer/

echo "============================================"
echo "✅ PACKAGE CREATED SUCCESSFULLY!"
echo "============================================"
echo "📁 Package: SupermarketERP_Customer_Package.zip"
echo "📏 Size: $(du -h SupermarketERP_Customer_Package.zip | cut -f1)"
echo ""
echo "📦 Send this ZIP file to your customer!"
echo ""
echo "Customer installation instructions:"
echo "  Windows: Extract ZIP → Double-click install.bat"
echo "  Linux:   Extract ZIP → Run ./start.sh"
echo "============================================"
