# Lore System MCP Server

Model Context Protocol (MCP) server for managing game lore with CRUD operations and JSON persistence.

## 📂 Project Structure

```
mcp/
├── src/                    # Source code
│   ├── server.py          # Main MCP server (22 tools)
│   └── persistence.py     # JSON persistence layer
│
├── tests/                 # Test suite
│   ├── test_server.py     # Component tests
│   └── test_persistence.py # Persistence tests
│
├── examples/              # Usage examples
│   └── example_usage.py   # Full demo script
│
├── docs/                  # Documentation
│   ├── README.md          # Full API documentation
│   ├── QUICKSTART.md      # Quick start guide
│   ├── tools.md           # All 22 tools reference
│   ├── FEATURES.md        # Complete features list
│   ├── INDEX.md           # Project index
│   ├── demo_save_to_json.md # JSON persistence guide
│   └── CHANGELOG.md       # Version history
│
├── scripts/               # Utility scripts
│   └── setup.sh          # Installation script
│
├── server.py              # Main entry point
├── config.json            # Configuration
└── requirements.txt       # Dependencies
```

## 🚀 Quick Start

### 1. Install
```bash
./scripts/setup.sh
```

### 2. Test
```bash
python tests/test_server.py
python tests/test_persistence.py
```

### 3. Run
```bash
python server.py
```

### 4. Configure Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "lore-system": {
      "command": "python",
      "args": ["/absolute/path/to/loreSystem/mcp/server.py"]
    }
  }
}
```

## 📖 Documentation

- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[docs/tools.md](docs/tools.md)** - All 22 tools reference (RU/EN)
- **[docs/README.md](docs/README.md)** - Complete API documentation
- **[docs/FEATURES.md](docs/FEATURES.md)** - Full features list
- **[docs/INDEX.md](docs/INDEX.md)** - Project navigation

## 🎯 Features

### 22 MCP Tools

- **Worlds** (5): create, get, list, update, delete
- **Characters** (6): create, get, list, update, delete, add_ability
- **Stories** (3): create, get, list
- **Events** (2): create, list
- **Pages** (2): create, list
- **Persistence** (4): save_to_json, export_tenant, list_saved_files, get_storage_stats

### JSON Persistence

Save your lore data to JSON files:
```
lore_data/
├── worlds/
├── characters/
├── stories/
├── events/
└── pages/
```

## 🧪 Testing

All tests passing ✅

```bash
# Component tests
python tests/test_server.py
# ✓ All tests passed (3/3)

# Persistence tests
python tests/test_persistence.py
# ✅ All JSON persistence tests passed!
```

## 📊 Stats

- **Version**: 1.1.0
- **Tools**: 22 MCP tools
- **Tests**: 9 tests (100% passing)
- **Docs**: 7 comprehensive guides
- **Languages**: English + Russian
- **Code**: ~1200 lines Python
- **Size**: ~110 KB total

## 🎮 Example Usage

```python
# In Claude Desktop with MCP configured:

# Create a world
create_world(tenant_id="my-game", name="Aetheria",
             description="A magical realm")

# Add a character
create_character(
    tenant_id="my-game",
    world_id="1",
    name="Lyra Starweaver",
    backstory="Born under a celestial convergence..." # min 100 chars
)

# Save to JSON
save_to_json(tenant_id="my-game")

# Export everything
export_tenant(tenant_id="my-game", filename="backup.json")
```

## ⚠️ Important Rules

- **Backstory**: Minimum 100 characters
- **Power Level**: 1-10 (not 1-100!)
- **Events**: Require at least 1 participant
- **Names**: Unique per world/tenant

## 🔧 Technology

- Python 3.11+
- MCP Protocol 1.0+
- Domain-Driven Design
- In-Memory + JSON Storage

## 📝 License

Part of the loreSystem project.

---

**For detailed documentation, see [docs/](docs/) folder**
