#!/usr/bin/env python3
"""
Smart Data Cleaner - Main Entry Point
Revolutionary data preprocessing with intelligent automation
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from gui.main_window import SmartDataCleanerApp
    import customtkinter as ctk
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Initialize and run the Smart Data Cleaner application"""
    # Set appearance mode and color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run the application
    app = SmartDataCleanerApp()
    app.mainloop()

if __name__ == "__main__":
    main()