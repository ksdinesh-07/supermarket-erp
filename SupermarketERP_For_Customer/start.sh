#!/bin/bash
# Supermarket ERP Launcher for Linux
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
export QT_QPA_PLATFORM=wayland
python3 main.py
