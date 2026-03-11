#!/bin/bash

echo "📦 Preparing Supermarket ERP for Customer Delivery"
echo "=================================================="

# Create delivery folder
DELIVERY_FOLDER="SupermarketERP_Delivery"
rm -rf "$DELIVERY_FOLDER"
mkdir -p "$DELIVERY_FOLDER"

# 1. Copy the executable
echo "1️⃣ Copying executable..."
if [ -f "dist/SupermarketERP" ]; then
    cp dist/SupermarketERP "$DELIVERY_FOLDER/"
    chmod +x "$DELIVERY_FOLDER/SupermarketERP"
    echo "   ✅ Executable copied"
else
    echo "   ❌ Executable not found in dist/ folder"
    echo "   Please run pyinstaller first"
    exit 1
fi

# 2. Create launcher script
echo "2️⃣ Creating launcher script..."
cat > "$DELIVERY_FOLDER/start.sh" << 'SCRIPT'
#!/bin/bash
# Launcher for Supermarket ERP
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
export QT_QPA_PLATFORM=wayland
./SupermarketERP
SCRIPT
chmod +x "$DELIVERY_FOLDER/start.sh"
echo "   ✅ Launcher script created"

# 3. Copy database schema
echo "3️⃣ Copying database files..."
mkdir -p "$DELIVERY_FOLDER/database"
if [ -f "database/schema.sql" ]; then
    cp database/schema.sql "$DELIVERY_FOLDER/database/"
    echo "   ✅ schema.sql copied"
else
    echo "   ⚠️ schema.sql not found"
fi

if [ -f "database/schema_update_fixed.sql" ]; then
    cp database/schema_update_fixed.sql "$DELIVERY_FOLDER/database/"
    echo "   ✅ schema_update_fixed.sql copied"
fi

# 4. Copy configuration file (with password placeholder)
echo "4️⃣ Creating configuration file..."
cat > "$DELIVERY_FOLDER/config.py" << 'CONFIG'
# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # CHANGE THIS TO YOUR MYSQL PASSWORD
    'database': 'supermarket_erp',
    'port': 3306
}

# Application settings
APP_NAME = "Supermarket ERP System"
APP_VERSION = "1.0.0"
COMPANY_NAME = "Your Company Name"

# Tax settings
TAX_RATE = 0.10  # 10% VAT/GST

# Currency symbol
CURRENCY_SYMBOL = "₹"
CONFIG
echo "   ✅ config.py created"

# 5. Create installation guide
echo "5️⃣ Creating installation guide..."
cat > "$DELIVERY_FOLDER/INSTALLATION_GUIDE.txt" << 'GUIDE'
╔═══════════════════════════════════════════════════════════════════╗
║         SUPERMARKET ERP - COMPLETE INSTALLATION GUIDE             ║
╚═══════════════════════════════════════════════════════════════════╝

📋 STEP 1: INSTALL MYSQL DATABASE
─────────────────────────────────
WINDOWS:
• Download MySQL from: https://dev.mysql.com/downloads/installer/
• Install and remember your root password

LINUX:
• sudo apt update
• sudo apt install mysql-server -y
• sudo mysql_secure_installation

📋 STEP 2: CREATE DATABASE
─────────────────────────
Open terminal/command prompt and run:

mysql -u root -p

Enter your password, then run:

CREATE DATABASE supermarket_erp;
USE supermarket_erp;
SOURCE database/schema.sql;
EXIT;

📋 STEP 3: CONFIGURE THE APPLICATION
───────────────────────────────────
1. Open the "config.py" file in any text editor
2. Change 'your_password' to your actual MySQL password
3. Save the file

📋 STEP 4: RUN THE APPLICATION
─────────────────────────────
LINUX:
• Double-click "start.sh" or run: ./start.sh

WINDOWS:
• Double-click "SupermarketERP.exe"

📋 DEFAULT LOGIN
────────────────
Username: admin
Password: admin123

For support: your-email@example.com
GUIDE
echo "   ✅ Installation guide created"

# 6. Create simple README
echo "6️⃣ Creating README..."
cat > "$DELIVERY_FOLDER/README.txt" << 'README'
====================================
SUPERMARKET ERP SYSTEM v1.0
====================================

📁 FILES IN THIS FOLDER:
------------------------
• SupermarketERP    - Main program
• start.sh          - Launcher script (Linux)
• config.py         - Configuration file (EDIT THIS!)
• database/         - Database setup files
• INSTALLATION_GUIDE.txt - Read this first!

🚀 QUICK START:
--------------
1. Install MySQL
2. Edit config.py with your MySQL password
3. Run: mysql -u root -p < database/schema.sql
4. Run ./start.sh (Linux) or SupermarketERP.exe (Windows)

🔑 LOGIN: admin / admin123

📞 SUPPORT: your-email@example.com
README
echo "   ✅ README created"

# 7. Create ZIP file
echo "7️⃣ Creating ZIP package..."
zip -r SupermarketERP_Client_Package.zip "$DELIVERY_FOLDER/"
echo "   ✅ ZIP file created: SupermarketERP_Client_Package.zip"

# Show package info
echo ""
echo "=================================================="
echo "✅ PACKAGE CREATED SUCCESSFULLY!"
echo "=================================================="
echo "📁 Package: SupermarketERP_Client_Package.zip"
echo "📏 Size: $(du -h SupermarketERP_Client_Package.zip | cut -f1)"
echo "📦 Contents:"
ls -la "$DELIVERY_FOLDER/"
echo ""
echo "➡️  Next steps:"
echo "   1. Upload SupermarketERP_Client_Package.zip to cloud storage"
echo "   2. Share the download link with your client"
echo "   3. Tell them to read INSTALLATION_GUIDE.txt first"
echo ""
