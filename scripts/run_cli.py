#!/usr/bin/env python3
"""
LoreSystem CLI Runner

Development wrapper for running the CLI without full package installation.
Usage:
    python run_cli.py --help
    python run_cli.py world list
    python run_cli.py world create --name "My World" --description "A fantasy world"
"""
import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from cli import main

if __name__ == '__main__':
    sys.exit(main())
