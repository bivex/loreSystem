#!/usr/bin/env python3
"""
Lore System MCP Server - Main Entry Point

Run this file to start the MCP server.
"""

import sys
from pathlib import Path

# Setup paths to avoid 'mcp' folder/package conflict
mcp_folder = str(Path(__file__).parent)  # loreSystem/mcp/

# Remove auto-added paths that might interfere
paths_to_remove = ['', '.', str(Path(__file__).parent.parent)]
for p in paths_to_remove:
    while p in sys.path:
        sys.path.remove(p)

# Add ONLY the mcp folder for now (to import src.server)
# src/server.py will handle adding loreSystem root AFTER importing mcp library
sys.path.insert(0, mcp_folder)

# Import and run the server
if __name__ == "__main__":
    from src.server import main
    import asyncio
    asyncio.run(main())
