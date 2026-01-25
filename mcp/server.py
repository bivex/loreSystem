#!/usr/bin/env python3
"""
Lore System MCP Server - Main Entry Point

This is the main entry point for the MCP server.
The actual server implementation is in src/server.py
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the server
if __name__ == "__main__":
    from src.server import main
    import asyncio
    asyncio.run(main())
