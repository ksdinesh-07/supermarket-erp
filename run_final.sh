#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set Qt platform to wayland
export QT_QPA_PLATFORM=wayland

# Suppress Qt warnings
export QT_LOGGING_RULES="qt.qpa.wayland=false"

# Run the application
python main.py
