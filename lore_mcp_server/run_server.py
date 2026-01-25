#!/usr/bin/env python3
"""
Lore System MCP Server - Main Entry Point

Run this file to start the MCP server.
"""

import sys
from pathlib import Path

# Setup paths for imports
# Add loreSystem root for domain imports (src.domain.*)
lore_system_root = str(Path(__file__).parent.parent)
if lore_system_root not in sys.path:
    sys.path.insert(0, lore_system_root)

# Add lore_mcp_server folder for MCP server imports (mcp_server.*)
mcp_server_folder = str(Path(__file__).parent)
if mcp_server_folder not in sys.path:
    sys.path.insert(0, mcp_server_folder)

# Import and run the server
if __name__ == "__main__":
    from mcp_server.server import main
    import asyncio
    asyncio.run(main())
