#!/usr/bin/env python3
"""
Thin wrapper runner for the MythWeave Lore & Graph Explorer.
Launches the modularized server package from scripts.viewer.
"""
import sys
import os

# Add scripts folder to sys.path to allow correct imports of the viewer package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from viewer.server import start_server

if __name__ == "__main__":
    start_server()
