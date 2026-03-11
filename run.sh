#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set Qt platform to wayland (if on Gnome/Wayland)
export QT_QPA_PLATFORM=wayland

# Set Qt to use high DPI scaling
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_SCALE_FACTOR=1

# Run the application
python main.py
