#!/bin/bash
# Setup script for Lore System MCP Server

set -e

echo "========================================="
echo "Lore System MCP Server Setup"
echo "========================================="
echo

# Check Python version
echo "Checking Python version..."
python3 --version || {
    echo "Error: Python 3 is not installed"
    exit 1
}

# Install MCP dependencies
echo "Installing MCP server dependencies..."
pip install -r requirements.txt

# Install parent project dependencies
echo "Installing loreSystem dependencies..."
pip install -r ../requirements.txt

echo
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo
echo "To run the server:"
echo "  python server.py"
echo
echo "To configure in Claude Desktop, add to config:"
echo "  ~/.config/Claude/claude_desktop_config.json (Linux)"
echo "  ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)"
echo "  %APPDATA%\\Claude\\claude_desktop_config.json (Windows)"
echo
echo "Example config:"
echo '  {
    "mcpServers": {
      "lore-system": {
        "command": "python",
        "args": ["'$(pwd)'/server.py"]
      }
    }
  }'
echo
