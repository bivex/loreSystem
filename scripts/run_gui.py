#!/usr/bin/env python3
"""
Launcher script for MythWeave GUI.

Usage:
    python run_gui.py
"""
import sys
from src.presentation.gui.lore_editor import main

if __name__ == '__main__':
    sys.exit(main())
