# Changelog

All notable changes to the Lore System MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - 2026-01-26

### Added
- **JSON Persistence Layer**: Save and load lore data through tool calls
  - `save_to_json` - Save all tenant data to individual JSON files
  - `export_tenant` - Export entire tenant to single comprehensive JSON file
  - `list_saved_files` - List all saved JSON files with optional filtering
  - `get_storage_stats` - Get statistics about stored data (file counts, sizes)
- Automatic directory structure creation (`lore_data/worlds/`, `lore_data/characters/`, etc.)
- File organization by entity type for easy browsing
- Backup and export functionality for version control and sharing
- Test suite for JSON persistence (`test_persistence.py`)

### Changed
- Updated example usage to demonstrate JSON save/export features
- Enhanced documentation with persistence instructions
- Added data persistence recommendations to QUICKSTART guide

### Technical
- New `persistence.py` module with JSONPersistence class
- Proper datetime serialization for Timestamp value objects
- Support for nested value object serialization
- Export includes metadata (timestamp, version, counts)

## [1.0.0] - 2026-01-26

### Added
- Initial release of Lore System MCP Server
- World CRUD operations (create, read, update, delete, list)
- Character CRUD operations with ability management
- Story creation and listing (linear, non-linear, interactive)
- Event creation and listing with participant tracking
- Page creation and listing for custom lore documentation
- In-memory repository implementations for development
- Domain-driven design with full validation
- Multi-tenant support
- Comprehensive README with examples
- Configuration file with limits and validation rules
- Example usage script demonstrating all features

### Features
- **World Management**: Hierarchical world structures with parent-child relationships
- **Character System**:
  - Full combat stats (HP, ATK, DEF, Speed)
  - Rarity levels (COMMON to LEGENDARY)
  - Elemental affinities (Physical, Fire, Water, Earth, Wind, Light, Dark)
  - Combat roles (DPS, Tank, Support, Specialist)
  - Ability management with power levels
- **Story System**: Support for linear, non-linear, and interactive narratives
- **Event System**: Timeline events with date ranges, outcomes, and participants
- **Page System**: Custom lore pages with markdown support
- **Validation**: All business rules enforced at domain level
- **Error Handling**: Structured JSON responses with detailed error messages

### Technical Details
- Built on Model Context Protocol (MCP) 1.0
- Python 3.11+ required
- Uses domain entities from loreSystem parent project
- Async/await pattern for MCP communication
- Type-safe value objects throughout

### Known Limitations
- Uses in-memory storage (data not persisted between restarts)
- Events require at least one participant character
- Backstory must be minimum 100 characters
- Some advanced features (relationships, sessions, choices) not yet exposed

### Next Steps
- Add PostgreSQL persistence layer
- Expose character relationships
- Add session management tools
- Add choice/branching narrative tools
- Add search and query tools
- Add bulk import/export
