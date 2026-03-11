#!/bin/bash

echo "🧹 Cleaning up Supermarket ERP Project"
echo "======================================"

# 1. Clean Python cache files
echo "📁 Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# 2. Remove build artifacts
echo "🔨 Removing build artifacts..."
rm -rf build/ dist/ *.spec
rm -rf __pycache__/

# 3. Remove Wine/Winetricks files
echo "🍷 Removing Wine files (optional)..."
rm -rf ~/.wine ~/.wine64 2>/dev/null
rm -rf ~/.cache/wine 2>/dev/null

# 4. Remove temporary files
echo "🗑️ Removing temporary files..."
rm -f *.log
rm -f *.tmp
rm -f *.temp
rm -rf tmp/

# 5. Remove database backups
echo "💾 Removing old database backups..."
rm -f *.sql.bak
rm -f *.sql.old

# 6. Remove IDE files
echo "📝 Removing IDE files..."
rm -rf .vscode/ .idea/ 2>/dev/null
rm -f *.code-workspace

# 7. Remove downloaded installers
echo "📦 Removing downloaded installers..."
rm -f *.exe *.msi *.dmg
rm -f python-*.exe
rm -f mysql-*.exe
rm -f innosetup*.exe

# 8. Remove old ZIP packages
echo "📚 Removing old distribution packages..."
rm -f *.zip
rm -f *.tar.gz
rm -f SupermarketERP_*.zip

# 9. Clean matplotlib cache
echo "📊 Cleaning matplotlib cache..."
rm -rf ~/.cache/matplotlib 2>/dev/null

# 10. Remove any leftover Wine/Python Windows files
echo "🍷 Cleaning up Wine Python installations..."
rm -rf ~/.wine/drive_c/Python* 2>/dev/null

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📁 Current directory contents:"
ls -la --group-directories-first
