#!/bin/bash
# Launcher for Supermarket ERP
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
export QT_QPA_PLATFORM=wayland
./SupermarketERP
