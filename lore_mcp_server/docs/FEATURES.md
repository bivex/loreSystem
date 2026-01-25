# Lore System MCP Server - Complete Feature List

## Overview
A Model Context Protocol (MCP) server providing comprehensive CRUD operations and JSON persistence for game lore management.

## Core Features

### 🌍 World Management
- **Create worlds** with hierarchical structure (parent-child relationships)
- **Update** world names and descriptions
- **Delete** worlds (with cascade considerations)
- **List** all worlds per tenant with pagination
- **Retrieve** individual worlds by ID
- Multi-tenant isolation (each tenant's data is separate)

**Validation**:
- World names unique per tenant
- Maximum 255 characters
- Version control for optimistic locking

---

### 🦸 Character Management
- **Create characters** with rich attributes:
  - Name, backstory (min 100 chars)
  - Combat stats: HP, ATK, DEF, Speed
  - Rarity: COMMON → MYTHIC
  - Element: physical, fire, water, earth, wind, light, dark
  - Role: DPS, Tank, Support, Specialist
  - Energy cost for ultimate abilities
- **Add/remove abilities** (power level 1-10)
- **Update** backstory and status (active/inactive)
- **Delete** characters
- **List** by world or tenant
- **Search** by backstory content

**Features**:
- Unique names per world
- Ability power levels (1-10 scale)
- Status management (active/inactive)
- Hierarchical relationships (parent_id)
- Location tracking (location_id)

---

### 📖 Story Management
- **Create stories** with three modes:
  - **LINEAR**: Traditional sequential narrative
  - **NON_LINEAR**: Branching storylines
  - **INTERACTIVE**: Player-driven choices
- **Rich content** support with markdown
- **Connected worlds** for cross-world narratives
- **Active/inactive** toggle
- **Choice integration** for decision points

**Story Types**:
```
LINEAR        → A → B → C → End
NON_LINEAR    → A → B ↗ C1 → End1
                      ↘ C2 → End2
INTERACTIVE   → Player choices drive narrative
```

---

### 📅 Event Management
- **Timeline events** with date ranges
- **Participant tracking** (characters involved)
- **Location-based** events
- **Outcome tracking**:
  - Success
  - Failure
  - Ongoing
- **Date validation** (start ≤ end)

**Use Cases**:
- Historical timeline
- Campaign events
- Story milestones
- Character encounters

---

### 📄 Page Management
- **Custom lore pages** with full markdown support
- **Hierarchical structure** (parent-child pages)
- **Template support** for consistent formatting
- **Tag system** for organization
- **Image embedding**

**Organization**:
```
Pages
├── The World
│   ├── Geography
│   ├── History
│   └── Factions
├── Characters
│   ├── Heroes
│   └── Villains
└── Lore
    ├── Magic System
    └── Technology
```

---

### 💾 JSON Persistence

#### Save to Individual Files
**Tool**: `save_to_json`

Creates organized file structure:
```
lore_data/
├── worlds/
│   └── tenant1_world_1.json
├── characters/
│   └── tenant1_char_1.json
├── stories/
├── events/
└── pages/
```

**Benefits**:
- Easy to browse
- Git-friendly
- Individual entity access
- Clear organization

#### Export to Single File
**Tool**: `export_tenant`

Creates comprehensive backup:
```json
{
  "metadata": {
    "tenant_id": "my-game",
    "exported_at": "2026-01-26T12:00:00",
    "version": "1.0.0"
  },
  "data": {
    "worlds": [...],
    "characters": [...],
    "stories": [...],
    "events": [...],
    "pages": [...]
  },
  "counts": {
    "worlds": 5,
    "characters": 42,
    ...
  }
}
```

**Benefits**:
- Easy to share
- Complete backup
- Version tracking
- Portable format

#### Storage Management
**Tools**: `list_saved_files`, `get_storage_stats`

Monitor your data:
- File counts by type
- Total storage size
- Directory location
- Per-tenant filtering

---

## Domain Validation

### Automatic Validation
All business rules enforced at domain level:

1. **Backstory Requirement**: ≥100 characters
   - Ensures narrative depth
   - Prevents shallow characters

2. **Power Level Range**: 1-10
   - Game balance
   - Clear progression

3. **Event Participants**: ≥1 character
   - Events must involve someone
   - Maintains logical consistency

4. **Date Ranges**: start ≤ end
   - No time paradoxes
   - Logical event duration

5. **Unique Names**: Per world/tenant
   - Prevents duplicates
   - Clear identification

6. **Version Control**: Monotonic increment
   - Optimistic locking
   - Conflict detection

---

## Multi-Tenant Support

### Tenant Isolation
- All data scoped to tenant_id
- No cross-tenant data leaks
- Independent namespaces

### Tenant Operations
```
Tenant A                    Tenant B
├── World: "Fantasy"        ├── World: "Sci-Fi"
├── Chars: [Hero1, Hero2]   ├── Chars: [Pilot1]
└── Stories: [Epic Quest]   └── Stories: [Space Opera]
```

---

## Data Types

### Value Objects (Immutable)
- **TenantId**: Tenant identifier
- **EntityId**: Generic entity ID
- **WorldName**: Validated world name
- **CharacterName**: Validated character name
- **Backstory**: Min 100 char narrative
- **Description**: Generic text
- **Timestamp**: UTC datetime
- **Version**: Optimistic locking counter
- **PowerLevel**: 1-10 ability strength
- **DateRange**: Event date span
- **Content**: Rich text content

### Enums
- **Rarity**: COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC
- **CharacterElement**: physical, fire, water, earth, wind, light, dark
- **CharacterRole**: dps, tank, support, specialist
- **CharacterStatus**: active, inactive
- **StoryType**: LINEAR, NON_LINEAR, INTERACTIVE
- **EventOutcome**: success, failure, ongoing

---

## API Response Format

### Success Response
```json
{
  "success": true,
  "entity_type": {...},
  "message": "Operation completed"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Detailed error message",
  "type": "ValueError"
}
```

---

## Performance

### In-Memory Speed
- Instant CRUD operations
- No network latency
- Perfect for development

### JSON Persistence
- Fast file I/O
- Organized storage
- Human-readable format

### Scalability
- Supports thousands of entities
- Pagination for large lists
- Efficient indexing

---

## Configuration

### Limits (`config.json`)
```json
{
  "limits": {
    "max_worlds_per_tenant": 100,
    "max_characters_per_world": 1000,
    "max_stories_per_world": 500,
    "max_events_per_world": 1000,
    "max_pages_per_world": 5000,
    "max_abilities_per_character": 20,
    "default_list_limit": 100,
    "max_list_limit": 1000
  }
}
```

### Validation Rules
```json
{
  "validation": {
    "world_name_max_length": 100,
    "character_name_max_length": 100,
    "backstory_min_length": 100,
    "description_max_length": 1000,
    "power_level_min": 1,
    "power_level_max": 10
  }
}
```

---

## Use Cases

### 🎮 Game Development
- RPG character databases
- World building
- Quest management
- Story branching

### 📚 Writing & World Building
- Novel character tracking
- Timeline management
- Lore documentation
- World bible creation

### 🎲 Tabletop RPG
- Campaign management
- NPC databases
- Session notes
- Handout organization

### 🎭 Interactive Fiction
- Choice-based narratives
- Character relationships
- Branching storylines
- World state tracking

---

## Integration

### Claude Desktop
Add to config:
```json
{
  "mcpServers": {
    "lore-system": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

### Programmatic Use
```python
from server import call_tool

result = await call_tool("create_world", {
    "tenant_id": "game1",
    "name": "Aetheria",
    "description": "A magical realm"
})
```

---

## Future Roadmap

### Phase 2
- [ ] Load from JSON (import functionality)
- [ ] Relationship management tools
- [ ] Session tracking tools
- [ ] Choice/branching tools

### Phase 3
- [ ] PostgreSQL backend
- [ ] Full-text search
- [ ] Batch operations
- [ ] Data validation reports

### Phase 4
- [ ] Real-time collaboration
- [ ] Conflict resolution
- [ ] Change history/audit log
- [ ] Advanced querying

---

## Testing

### Test Coverage
- ✅ Component tests (imports, repositories)
- ✅ Character creation with abilities
- ✅ JSON persistence (save/load/export)
- ✅ Domain validation rules

### Running Tests
```bash
python test_server.py       # Core functionality
python test_persistence.py  # JSON persistence
```

---

## Documentation

- **README.md** - Complete API reference
- **QUICKSTART.md** - Getting started guide
- **CHANGELOG.md** - Version history
- **FEATURES.md** - This document
- **demo_save_to_json.md** - Persistence tutorial

---

## Support

### Error Messages
All validation errors provide:
- Clear description of the problem
- What was expected
- What was provided
- Suggestions for fixing

### Debugging
- Structured JSON responses
- Detailed error types
- Stack traces in development

---

**Version**: 1.1.0
**Status**: Production Ready
**License**: Part of loreSystem project
**Last Updated**: 2026-01-26
