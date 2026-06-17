#!/usr/bin/env python3
"""
Lore System MCP Server Entry Point
"""

# CRITICAL: Import MCP library FIRST before manipulating sys.path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

import sys
import asyncio
from pathlib import Path
from typing import Any

# Setup paths for domain imports
lore_system_root = str(Path(__file__).parent.parent.parent)
if lore_system_root not in sys.path:
    sys.path.insert(0, lore_system_root)

# Import local modules
from .tools_list import get_tools
from .tools_call import call_tool as tools_call_impl

# Create MCP server
app = Server("lore-system-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return get_tools()

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    return await tools_call_impl(name, arguments)

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
