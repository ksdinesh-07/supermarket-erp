#!/bin/bash

echo "🧹 SUPERMARKET ERP - CLEANUP AND RUN"
echo "====================================="

# Step 1: Remove all unwanted files
echo ""
echo "📁 Step 1: Removing unwanted files..."

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
echo "   ✅ Removed Python cache files"

# Remove build artifacts
rm -rf build/ dist/ *.spec 2>/dev/null
echo "   ✅ Removed build artifacts"

# Remove old database (will be recreated)
rm -f supermarket.db
rm -f *.db
echo "   ✅ Removed old database files"

# Remove temporary files
rm -f *.log
rm -f *.tmp
rm -f *.temp
rm -rf tmp/ 2>/dev/null
echo "   ✅ Removed temporary files"

# Remove downloaded installers
rm -f *.exe *.msi *.dmg
rm -f python-*.exe
rm -f mysql-*.exe
rm -f innosetup*.exe
echo "   ✅ Removed downloaded installers"

# Remove old ZIP packages
rm -f *.zip
rm -f *.tar.gz
rm -f SupermarketERP_*.zip
rm -rf SupermarketERP_*/ 2>/dev/null
echo "   ✅ Removed old distribution packages"

# Remove matplotlib cache
rm -rf ~/.cache/matplotlib 2>/dev/null
echo "   ✅ Removed matplotlib cache"

# Remove backup files
rm -f *.bak
rm -f *.old
echo "   ✅ Removed backup files"

# Step 2: Show current directory structure
echo ""
echo "📁 Step 2: Current directory contents:"
echo "-------------------------------------"
ls -la --group-directories-first

# Step 3: Run the application
echo ""
echo "🚀 Step 3: Starting Supermarket ERP..."
echo "====================================="
echo ""

# Set Qt platform to wayland (for Linux)
export QT_QPA_PLATFORM=wayland

# Run the application
python main.py
