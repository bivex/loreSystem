# MCP Tools Reference | Справочник инструментов

Complete list of available MCP server tools for managing game lore.

---

## 🌍 World Management

### `create_world`
Create a new world in the lore system.

**Parameters:**
```json
{
  "tenant_id": "string",      // Tenant ID (required)
  "name": "string",            // World name, max 100 characters (required)
  "description": "string",     // World description, max 1000 characters (required)
  "parent_id": "string"        // Parent world ID (optional)
}
```

**Example:**
```json
{
  "tenant_id": "my-game",
  "name": "Aetherya",
  "description": "A magical world where ancient technology meets mysticism"
}
```

**Response:**
```json
{
  "success": true,
  "world": {
    "id": 1,
    "name": "Aetherya",
    "description": "...",
    "version": 1
  },
  "message": "World 'Aetherya' created successfully"
}
```

---

### `get_world`
Get a world by ID.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string"
}
```

---

### `list_worlds`
List all worlds for a tenant.

**Parameters:**
```json
{
  "tenant_id": "string",
  "limit": 100,        // Default: 100
  "offset": 0          // Default: 0
}
```

---

### `update_world`
Update world name or description.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "name": "string",           // New name (optional)
  "description": "string"     // New description (optional)
}
```

---

### `delete_world`
Delete a world.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string"
}
```

---

## 🦸 Character Management

### `create_character`
Create a new character in a world.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "name": "string",                    // Character name, max 100 characters
  "backstory": "string",               // Backstory, minimum 100 characters!
  "rarity": "string",                  // COMMON | UNCOMMON | RARE | EPIC | LEGENDARY
  "element": "string",                 // physical | fire | water | earth | wind | light | dark
  "role": "string",                    // dps | tank | support | specialist
  "base_hp": integer,                  // Base health
  "base_atk": integer,                 // Base attack
  "base_def": integer,                 // Base defense
  "base_speed": integer,               // Base speed
  "energy_cost": integer               // Ultimate cost
}
```

**Example:**
```json
{
  "tenant_id": "my-game",
  "world_id": "1",
  "name": "Lyra Starweaver",
  "backstory": "Born under a celestial convergence, Lyra discovered her affinity for star magic at the age of five. She spent decades studying magic at the Arcane Nexus, eventually becoming one of the youngest Archmages in history.",
  "rarity": "LEGENDARY",
  "element": "light",
  "role": "dps",
  "base_hp": 800,
  "base_atk": 320,
  "base_def": 120,
  "base_speed": 180,
  "energy_cost": 120
}
```

**Important:**
- ⚠️ **Backstory must be minimum 100 characters** - this is a domain requirement for character depth
- All combat stats are optional
- Name must be unique within the world

---

### `get_character`
Get a character by ID.

**Parameters:**
```json
{
  "tenant_id": "string",
  "character_id": "string"
}
```

---

### `list_characters`
List characters in a world.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "limit": 100,
  "offset": 0
}
```

---

### `update_character`
Update character data.

**Parameters:**
```json
{
  "tenant_id": "string",
  "character_id": "string",
  "backstory": "string",     // New backstory (min 100 characters)
  "status": "string"         // active | inactive
}
```

---

### `delete_character`
Delete a character.

**Parameters:**
```json
{
  "tenant_id": "string",
  "character_id": "string"
}
```

---

### `add_ability`
Add an ability to a character.

**Parameters:**
```json
{
  "tenant_id": "string",
  "character_id": "string",
  "ability_name": "string",
  "description": "string",
  "power_level": integer     // From 1 to 10 (not 1-100!)
}
```

**Example:**
```json
{
  "tenant_id": "my-game",
  "character_id": "1",
  "ability_name": "Cosmic Cascade",
  "description": "Summons a rain of starlight that damages all enemies",
  "power_level": 9
}
```

**Important:**
- ⚠️ **Power level: 1-10** (1 = weak, 10 = strongest)
- DO NOT use the 1-100 scale!

---

## 📖 Story Management

### `create_story`
Create a new story in a world.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "name": "string",
  "description": "string",
  "story_type": "string",    // LINEAR | NON_LINEAR | INTERACTIVE
  "content": "string"
}
```

**Story types:**
- **LINEAR** - Linear narrative (A → B → C → End)
- **NON_LINEAR** - Branching plot (multiple endings)
- **INTERACTIVE** - Interactive narrative (player choices)

**Example:**
```json
{
  "tenant_id": "my-game",
  "world_id": "1",
  "name": "The Fracture Awakening",
  "description": "As dimensional rifts begin appearing across Aetherya, Lyra must unite with unlikely allies",
  "story_type": "NON_LINEAR",
  "content": "Chapter 1: The First Tremor\n\nArcane sensors flickered with impossible readings..."
}
```

---

### `get_story`
Get a story by ID.

**Parameters:**
```json
{
  "tenant_id": "string",
  "story_id": "string"
}
```

---

### `list_stories`
List stories in a world.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "limit": 100,
  "offset": 0
}
```

---

## 📅 Event Management

### `create_event`
Create an event on the timeline.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "name": "string",
  "description": "string",
  "start_date": "string",           // ISO date (2026-01-26T12:00:00)
  "end_date": "string",             // ISO date (optional)
  "participant_ids": ["string"],    // Array of character IDs (minimum 1!)
  "outcome": "string"               // success | failure | ongoing
}
```

**Example:**
```json
{
  "tenant_id": "my-game",
  "world_id": "1",
  "name": "Battle for the Shattered Sky",
  "description": "A massive rift opened above the capital, unleashing otherworldly horrors",
  "start_date": "3024-06-15T14:30:00",
  "end_date": "3024-06-15T23:45:00",
  "participant_ids": ["1", "2", "3"],
  "outcome": "success"
}
```

**Important:**
- ⚠️ **Minimum 1 participant required** (`participant_ids`)
- Events without participants violate the domain invariant

---

### `list_events`
List events in a world.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "limit": 100,
  "offset": 0
}
```

---

## 📄 Page Management

### `create_page`
Create a custom lore page.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "name": "string",
  "content": "string"     // Markdown supported
}
```

**Example:**
```json
{
  "tenant_id": "my-game",
  "world_id": "1",
  "name": "Arcane Nexus",
  "content": "# Arcane Nexus\n\n## Overview\nThe Arcane Nexus is the premier institution for magical study in Aetherya...\n\n## History\nFounded in Year 1247 by the Council of Seven..."
}
```

---

### `list_pages`
List pages in a world.

**Parameters:**
```json
{
  "tenant_id": "string",
  "world_id": "string",
  "limit": 100,
  "offset": 0
}
```

---

## 💾 Persistence (Save to JSON)

### `save_to_json`
Save all lore data to JSON files.

**Parameters:**
```json
{
  "tenant_id": "string"
}
```

**What happens:**
- Creates `lore_data/` structure
- Each entity saved to separate file
- Organized by type (worlds/, characters/, stories/, events/, pages/)

**Response:**
```json
{
  "success": true,
  "tenant_id": "my-game",
  "counts": {
    "worlds": 1,
    "characters": 5,
    "stories": 3,
    "events": 10,
    "pages": 15,
    "total_files": 34
  },
  "data_directory": "/path/to/lore_data"
}
```

**File structure:**
```
lore_data/
├── worlds/
│   └── my-game_world_1.json
├── characters/
│   ├── my-game_char_1.json
│   ├── my-game_char_2.json
│   └── my-game_char_3.json
├── stories/
├── events/
└── pages/
```

---

### `export_tenant`
Export an entire tenant to a single JSON file.

**Parameters:**
```json
{
  "tenant_id": "string",
  "filename": "string"     // Example: "my_world_backup.json"
}
```

**Response:**
```json
{
  "success": true,
  "tenant_id": "my-game",
  "filepath": "lore_data/my_world_backup.json",
  "size_bytes": 52341,
  "size_kb": 51.11
}
```

**Export format:**
```json
{
  "metadata": {
    "tenant_id": "my-game",
    "exported_at": "2026-01-26T12:34:56",
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
    "worlds": 1,
    "characters": 5,
    "stories": 3,
    "events": 10,
    "pages": 15
  }
}
```

**Usage:**
- 📦 Full backup
- 📤 Share with team
- 🔄 Version control (git)
- 💾 Archiving

---

### `list_saved_files`
List all saved JSON files.

**Parameters:**
```json
{
  "tenant_id": "string"    // Optional, for filtering
}
```

**Response:**
```json
{
  "success": true,
  "tenant_id": "my-game",
  "total_files": 34,
  "files": {
    "worlds": ["lore_data/worlds/my-game_world_1.json"],
    "characters": [
      "lore_data/characters/my-game_char_1.json",
      "lore_data/characters/my-game_char_2.json"
    ],
    "stories": [...],
    "events": [...],
    "pages": [...]
  },
  "data_directory": "/path/to/lore_data"
}
```

---

### `get_storage_stats`
Storage statistics.

**Parameters:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_files": 34,
    "by_type": {
      "worlds": {
        "count": 1,
        "size_bytes": 423
      },
      "characters": {
        "count": 5,
        "size_bytes": 2550
      },
      "stories": {
        "count": 3,
        "size_bytes": 1890
      },
      "events": {
        "count": 10,
        "size_bytes": 4230
      },
      "pages": {
        "count": 15,
        "size_bytes": 7650
      }
    },
    "total_size_bytes": 16743,
    "data_directory": "/path/to/lore_data"
  }
}
```

---

## 📊 Summary Table

| Category | Tools | Total |
|-----------|-------|-------|
| **Worlds** | create, get, list, update, delete | 5 |
| **Characters** | create, get, list, update, delete, add_ability | 6 |
| **Stories** | create, get, list | 3 |
| **Events** | create, list | 2 |
| **Pages** | create, list | 2 |
| **Persistence** | save_to_json, export_tenant, list_saved_files, get_storage_stats | 4 |
| **TOTAL** | | **22 tools** |

---

## 🎯 Quick Examples

### Create a complete world
```
1. create_world - create a world
2. create_character - add a hero
3. add_ability - add abilities
4. create_story - create a story
5. create_event - add an event
6. create_page - document lore
7. save_to_json - save everything
```

### Backup a project
```
1. export_tenant - full export
2. get_storage_stats - check size
```

### Data verification
```
1. list_worlds - view worlds
2. list_characters - view characters
3. get_storage_stats - storage statistics
```

---

## ⚠️ Important Constraints

| Rule | Value | Reason |
|------|-------|--------|
| Backstory min. length | 100 characters | Character depth |
| Power level range | 1-10 | Game balance |
| Event participants min. | 1 character | Logical integrity |
| World name max. | 255 characters | DB validation |
| Character name max. | 255 characters | DB validation |
| Description max. | 1000 characters | DB validation |

---

## 📝 Response Formats

### Success
```json
{
  "success": true,
  "entity": {...},
  "message": "..."
}
```

### Error
```json
{
  "success": false,
  "error": "Detailed error message",
  "type": "ValueError"
}
```

### List
```json
{
  "success": true,
  "count": 5,
  "entities": [...]
}
```

---

## 🚀 Typical Scenarios

### Creating an RPG character
```json
create_character {
  "name": "Aragorn",
  "backstory": "Descendant of Isildur, Aragorn is the rightful heir to the throne of Gondor. He grew up in Rivendell under Elrond's care and became a Ranger of the North, protecting the Shire and its inhabitants from dark forces.",
  "rarity": "LEGENDARY",
  "element": "physical",
  "role": "dps",
  "base_hp": 1200,
  "base_atk": 250
}

add_ability {
  "ability_name": "Andúril Strike",
  "power_level": 9
}
```

### Creating a story with events
```json
create_story {
  "name": "The Fellowship of the Ring",
  "story_type": "LINEAR"
}

create_event {
  "name": "Council of Elrond",
  "participant_ids": ["1", "2", "3", "4"]
}
```

### Full backup
```json
save_to_json {
  "tenant_id": "my-rpg"
}

export_tenant {
  "tenant_id": "my-rpg",
  "filename": "backup_2026-01-26.json"
}
```

---

**Version:** 1.1.0
**Last updated:** 2026-01-26
**Total tools:** 22
