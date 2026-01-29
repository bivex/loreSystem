"""
Pytest configuration and fixtures for the lore system tests.
"""
import sys
from pathlib import Path

# Add src to Python path so we can import modules
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))