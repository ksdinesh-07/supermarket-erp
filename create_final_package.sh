#!/bin/bash

echo "📦 Creating Supermarket ERP Final Package"
echo "=========================================="

# Create distribution folder
mkdir -p SupermarketERP_Final

# Copy all necessary files
echo "1️⃣ Copying application files..."
cp -r modules SupermarketERP_Final/
cp -r database SupermarketERP_Final/
cp -r ui SupermarketERP_Final/
cp -r utils SupermarketERP_Final/
cp main.py SupermarketERP_Final/
cp config.py SupermarketERP_Final/
cp requirements.txt SupermarketERP_Final/

# Remove old database if exists (will be created on first run)
rm -f SupermarketERP_Final/supermarket.db

# Create launcher for Linux
echo "2️⃣ Creating Linux launcher..."
cat > SupermarketERP_Final/start.sh << 'LAUNCHER'
#!/bin/bash
# Supermarket ERP Launcher for Linux
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
export QT_QPA_PLATFORM=wayland
python3 main.py
LAUNCHER
chmod +x SupermarketERP_Final/start.sh

# Create launcher for Windows
echo "3️⃣ Creating Windows launcher..."
cat > SupermarketERP_Final/start.bat << 'BATCH'
@echo off
cd /d "%~dp0"
python main.py
pause
BATCH

# Create one-click installer for Windows
echo "4️⃣ Creating Windows installer..."
cat > SupermarketERP_Final/install_windows.bat << 'INSTALL'
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
    echo Download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b
) else (
    echo ✅ Python found
)

echo [2/4] Installing dependencies...
pip install -r requirements.txt

echo [3/4] Creating desktop shortcut...
powershell "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\Supermarket ERP.lnk'); $SC.TargetPath = '%~dp0start.bat'; $SC.IconLocation = '%~dp0icon.ico'; $SC.Save()" 2>nul

echo [4/4] Creating start menu shortcut...
powershell "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Supermarket ERP.lnk'); $SC.TargetPath = '%~dp0start.bat'; $SC.IconLocation = '%~dp0icon.ico'; $SC.Save()" 2>nul

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

# Create a simple icon (base64 encoded 1x1 pixel icon - replace with your own)
echo "5️⃣ Creating icon..."
cat > SupermarketERP_Final/icon.ico << 'ICON'
ÿÿÿÿ
ICON

# Create comprehensive README
echo "6️⃣ Creating README..."
cat > SupermarketERP_Final/README.txt << 'README'
╔══════════════════════════════════════════════════════════╗
║         SUPERMARKET ERP - COMPLETE SOLUTION             ║
╚══════════════════════════════════════════════════════════╝

📋 SYSTEM REQUIREMENTS:
──────────────────────
• Windows 10/11 OR Linux (Ubuntu 20.04+)
• Python 3.8 or higher
• 4GB RAM minimum
• 500MB free disk space

🚀 QUICK START:
──────────────

FOR WINDOWS USERS:
─────────────────
1. Double-click "install_windows.bat"
2. Wait for dependencies to install
3. Application starts automatically!
4. Desktop shortcut created

FOR LINUX USERS:
───────────────
1. Open terminal in this folder
2. Run: ./start.sh
   or
   python3 main.py

🔑 DEFAULT LOGIN:
────────────────
Username: admin
Password: admin123

📁 FOLDER STRUCTURE:
──────────────────
• main.py              - Main application
• modules/             - All Python modules
• database/            - Database files
• ui/                  - UI styles
• utils/               - Utility functions
• start.sh             - Linux launcher
• start.bat            - Windows launcher
• install_windows.bat  - Windows installer
• requirements.txt     - Python dependencies

✅ NO DATABASE SETUP NEEDED:
───────────────────────────
• SQLite database is created automatically on first run
• No MySQL installation required
• No server configuration needed

❓ TROUBLESHOOTING:
──────────────────
• If application doesn't start, run manually: python main.py
• Make sure Python is in PATH
• On Linux, you may need: pip install -r requirements.txt
• Default database file: supermarket.db

📞 SUPPORT:
──────────
Email: your-email@example.com
Phone: +91 XXXXXXXXXX

Thank you for choosing Supermarket ERP!
README

# Create the final ZIP package
echo "7️⃣ Creating ZIP package..."
zip -r SupermarketERP_Final.zip SupermarketERP_Final/

echo "=========================================="
echo "✅ FINAL PACKAGE CREATED SUCCESSFULLY!"
echo "=========================================="
echo "📁 Package: SupermarketERP_Final.zip"
echo "📏 Size: $(du -h SupermarketERP_Final.zip | cut -f1)"
echo ""
echo "📦 Send this ZIP file to your customer!"
echo ""
echo "Customer installation:"
echo "  Windows: Double-click install_windows.bat"
echo "  Linux:   Run ./start.sh"
echo "=========================================="
