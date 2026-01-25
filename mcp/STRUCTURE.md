# MCP Server Folder Structure

Organized structure for the Lore System MCP Server.

## 📁 Directory Layout

```
mcp/
├── 📄 server.py                 # Main entry point
├── 📄 config.json               # Configuration
├── 📄 requirements.txt          # Python dependencies
├── 📄 README.md                 # Project overview
├── 📄 __init__.py               # Package marker
│
├── 📂 src/                      # Source code
│   ├── __init__.py
│   ├── server.py               # MCP server implementation (22 tools)
│   └── persistence.py          # JSON persistence layer
│
├── 📂 tests/                    # Test suite
│   ├── test_server.py          # Component tests ✅
│   └── test_persistence.py     # Persistence tests ✅
│
├── 📂 examples/                 # Usage examples
│   └── example_usage.py        # Full demo script
│
├── 📂 docs/                     # Documentation
│   ├── README.md               # Full API documentation
│   ├── QUICKSTART.md           # Quick start guide
│   ├── tools.md                # All 22 tools reference (RU/EN)
│   ├── FEATURES.md             # Complete features list
│   ├── INDEX.md                # Project navigation index
│   ├── demo_save_to_json.md    # JSON persistence guide
│   └── CHANGELOG.md            # Version history
│
├── 📂 scripts/                  # Utility scripts
│   └── setup.sh                # Installation script
│
└── 📂 lore_data/               # Generated data (created on save)
    ├── worlds/
    ├── characters/
    ├── stories/
    ├── events/
    └── pages/
```

## 🎯 File Purposes

### Root Level

**server.py** - Main entry point that imports and runs `src.server.main()`
- Run with: `python3 server.py`
- Configured in Claude Desktop config

**config.json** - Server configuration
- Limits (max entities, pagination)
- Validation rules (min/max lengths, ranges)

**requirements.txt** - Python dependencies
- mcp>=1.0.0

**README.md** - Project overview
- Quick start
- Features summary
- Links to detailed docs

**__init__.py** - Makes mcp a Python package
- Allows `from mcp.src import ...`

### src/ - Source Code

**src/server.py** (34KB) - MCP server implementation
- 22 MCP tools for CRUD operations
- Worlds (5 tools)
- Characters (6 tools)
- Stories (3 tools)
- Events (2 tools)
- Pages (2 tools)
- Persistence (4 tools)

**src/persistence.py** (12KB) - JSON persistence
- Save/load to individual files
- Export to single file
- Storage statistics
- File listing

### tests/ - Test Suite

**tests/test_server.py** - Component tests
- Import validation
- Repository operations
- Character creation with abilities
- ✅ 3/3 tests passing

**tests/test_persistence.py** - Persistence tests
- Save to JSON files
- Export to single file
- Load from JSON
- Storage stats
- ✅ 6/6 tests passing

### examples/ - Usage Examples

**examples/example_usage.py** - Full demonstration
- Creates world, characters, stories, events, pages
- Adds abilities to characters
- Saves to JSON
- Exports to single file
- Shows all 22 tools in action

### docs/ - Documentation

**docs/README.md** - Complete API reference
- All tool schemas
- Request/response formats
- Examples for each tool
- Architecture details

**docs/QUICKSTART.md** - Get started in 5 minutes
- Installation
- Configuration
- First commands
- Troubleshooting

**docs/tools.md** (17KB) - Complete tools reference
- All 22 tools with examples
- Russian + English
- Parameters and responses
- Important limitations
- Common scenarios

**docs/FEATURES.md** - Feature documentation
- Domain model
- Validation rules
- Use cases
- Technical details

**docs/INDEX.md** - Project navigation
- File index
- Reading guide
- Quick links

**docs/demo_save_to_json.md** - Persistence tutorial
- Save examples
- Export examples
- Best practices
- Use cases

**docs/CHANGELOG.md** - Version history
- v1.1.0 - JSON persistence
- v1.0.0 - Initial release

### scripts/ - Utility Scripts

**scripts/setup.sh** - Automated installation
- Check Python version
- Install dependencies
- Run tests
- Show configuration instructions

## 🔧 Import Structure

The project uses a clear import hierarchy:

```python
# From loreSystem root:
from src.domain.entities.world import World              # Domain code
from mcp.src.server import app                           # MCP server
from mcp.src.persistence import JSONPersistence          # Persistence

# Path setup in each file:
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
# This adds loreSystem/ to path, enabling imports from both:
# - src.domain.*  (loreSystem/src/domain)
# - mcp.src.*     (loreSystem/mcp/src)
```

## 🚀 Running Commands

### From mcp/ directory:

```bash
# Run server
python3 server.py

# Run tests
python3 tests/test_server.py
python3 tests/test_persistence.py

# Run example
python3 examples/example_usage.py

# Install
./scripts/setup.sh
```

### From loreSystem/ directory:

```bash
cd mcp
python3 server.py
```

## 📊 File Statistics

| Category | Files | Size |
|----------|-------|------|
| Source Code | 2 | 46 KB |
| Tests | 2 | 10 KB |
| Examples | 1 | 8.5 KB |
| Documentation | 7 | 60 KB |
| Scripts | 1 | 1.2 KB |
| Configuration | 3 | 1.5 KB |
| **Total** | **16** | **~127 KB** |

## ✅ Benefits of This Structure

1. **Clear Separation**
   - Source code in `src/`
   - Tests in `tests/`
   - Docs in `docs/`
   - Examples in `examples/`

2. **Easy Navigation**
   - Logical grouping
   - Self-documenting structure
   - Standard Python package layout

3. **Maintainability**
   - Tests alongside code
   - Documentation centralized
   - Clear dependencies

4. **Scalability**
   - Easy to add new tools
   - New docs go in `docs/`
   - New tests go in `tests/`

5. **Professional**
   - Follows Python best practices
   - Standard project layout
   - Clear module boundaries

## 🔄 Migration from Flat Structure

**Before:**
```
mcp/
├── server.py
├── persistence.py
├── test_server.py
├── test_persistence.py
├── example_usage.py
├── README.md
├── QUICKSTART.md
├── tools.md
├── ... (all files in root)
```

**After:**
```
mcp/
├── server.py  (entry point)
├── src/       (source code)
├── tests/     (test suite)
├── examples/  (examples)
├── docs/      (documentation)
└── scripts/   (utilities)
```

## 📝 Notes

- All tests passing ✅ (9/9)
- No breaking changes to functionality
- Import paths updated in all files
- Entry point remains `server.py` in root
- Documentation updated to reflect structure

**Version:** 1.1.0
**Date:** 2026-01-26
**Status:** Production Ready ✅
