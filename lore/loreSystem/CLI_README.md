# LoreSystem CLI - Interactive Presentation Tool

A comprehensive command-line interface for managing lore entities in the LoreSystem project.

## Features Implemented

### Core Functionality
- ✅ **Interactive Menu-Driven Interface**: Numbered options with easy navigation
- ✅ **Entity Management**: Full CRUD for Worlds, Characters, Events, Items, Quests, and Notes
- ✅ **Search Functionality**: Search across all entity types at once
- ✅ **Export to JSON**: Complete data export with relationships preserved
- ✅ **Rich Formatting**: Beautiful tables and colored output using Rich library
- ✅ **Input Validation**: Ensures data integrity at all levels
- ✅ **Confirmations**: Safety prompts before destructive actions
- ✅ **Sub-Menus**: Dedicated menus for each entity type
- ✅ **Sample Data**: Demo mode with pre-populated entities

### Supported Entity Types

1. **Worlds** - Top-level containers for game lore
   - Create with name and description
   - Version tracking
   - Cascade deletion (deletes all related entities)

2. **Characters** - Actors within worlds
   - Create with name, backstory, and abilities
   - Support for combat stats (HP, ATK, DEF)
   - Rarity levels (Common to Legendary)
   - Ability management with power levels

3. **Events** - Timeline occurrences
   - Create with name, description, and participants
   - Date range tracking
   - Outcome tracking (Success, Failure, Ongoing)
   - Multiple character participants

4. **Items** - World objects
   - Types: Weapon, Armor, Artifact, Consumable, Tool, Other
   - Rarity levels: Common, Uncommon, Rare, Epic, Legendary, Mythic
   - Full description support

5. **Quests** - Tasks and objectives
   - Status tracking (Active, Completed, Failed, Cancelled)
   - World association
   - Description support

6. **Notes** - Documentation
   - Types: General, Reminder, Session, Character, Plot
   - Full content support
   - World association

## Installation & Setup

### Prerequisites

The CLI requires the following Python packages (already in requirements.txt):
- click>=8.1.7
- rich>=13.7.0

### Running the CLI

```bash
# Activate virtual environment
cd lore/loreSystem
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Run the CLI
python3 src/presentation/cli.py

# Run with sample data
python3 src/presentation/cli.py --demo

# Show help
python3 src/presentation/cli.py --help

# Show version
python3 src/presentation/cli.py --version
```

## How to Use the CLI

### Main Menu Navigation

The CLI starts with a main menu showing all available options:

```
╔══════════════════════════════════════════╗
║              MAIN MENU                   ║
╚══════════════════════════════════════════╝
  [1] 📚 Worlds
  [2] 👥 Characters
  [3] 📅 Events
  [4] 🎒 Items
  [5] ⚔️  Quests
  [6] 📝 Notes
  [7] 🔍 Search all entities
  [8] 💾 Export to JSON
  [9] ℹ️  Help & Documentation
  [0] 🚪 Exit
```

Simply type the number corresponding to your choice and press Enter.

### Sub-Menus

Each entity type has its own sub-menu with three options:
1. List all entities
2. Create new entity
3. Delete entity

Select option `0` to return to the main menu.

### Creating Entities

#### Step-by-Step: Create a World

1. From main menu, select `[1] 📚 Worlds`
2. Select `[2] Create new world`
3. Enter world name (e.g., "Mystic Realms")
4. Enter description
5. The world is created and assigned an ID

#### Step-by-Step: Create a Character

1. Create a world first (if not already done)
2. From main menu, select `[2] 👥 Characters`
3. Select `[2] Create new character`
4. Select the world from the list
5. Enter character name
6. Enter backstory (minimum 100 characters)
7. Choose to add abilities (optional)
   - For each ability: name, description, power level (1-10)
8. Choose to add combat stats (optional)
   - Rarity, HP, ATK, DEF
9. The character is created and assigned an ID

#### Step-by-Step: Create an Event

1. From main menu, select `[3] 📅 Events`
2. Select `[2] Create new event`
3. Select the world
4. Enter event name
5. Enter description
6. Add participants from available characters
7. The event is created

### Viewing Entities

Select the `[1] List all [entity type]` option from any sub-menu to see a formatted table:

Example output for Characters:

```
Characters
┏━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ ID    ┃ Name          ┃ World        ┃ Status   ┃ Abilities ┃ Rarity  ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ 2     │ Aria Forge    │ Eternal Forg │ active   │ 2         │ LEGENDA │
┗━━━━━━━┻━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━┻━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━┛

Total: 1 character(s)
```

### Deleting Entities

1. Navigate to the entity type's sub-menu
2. Select `[3] Delete [entity type]`
3. View the list of entities
4. Enter the ID of the entity to delete
5. Confirm the deletion (required for safety)
6. Entity is deleted (with cascade for worlds)

### Searching

1. From main menu, select `[7] 🔍 Search all entities`
2. Enter a search term
3. Results are displayed grouped by entity type
4. Shows matching names and descriptions

Example:
```
Searching for: 'forge'
==================================================

Worlds:
  • Eternal Forge (ID: 1)
    A vast universe where reality itself can be reforged...

Characters:
  • Aria the Forge Master (ID: 2)
    Aria the Forge Master was born in the Eternal Crucible...

Events:
  • The Great Reforging (ID: 3)
    The Forge Masters gather at the Eternal Crucible to perform...
```

### Exporting to JSON

1. From main menu, select `[8] 💾 Export to JSON`
2. Enter filename (default: lore_export.json)
3. All entities are exported with their relationships
4. Summary is shown with counts

Export format:
```json
{
  "export_date": "2025-01-29T12:34:56.789012",
  "worlds": [...],
  "characters": [...],
  "events": [...],
  "items": [...],
  "quests": [...],
  "notes": [...]
}
```

### Getting Help

Select `[9] ℹ️  Help & Documentation` from the main menu to see:
- Overview of the CLI
- Detailed descriptions of each entity type
- Operations guide (Create, Read, Update, Delete)
- Search tips
- Export information
- Keyboard shortcuts
- Tips for getting started
- Getting started walkthrough

## Examples of Usage

### Example 1: Quick Start with Demo Data

```bash
python3 src/presentation/cli.py --demo
```

This loads:
- 1 World: "Eternal Forge"
- 1 Character: "Aria the Forge Master" with 2 abilities
- 1 Event: "The Great Reforging"
- 1 Item: "Cosmic Hammer"
- 1 Quest: "Prevent the Unraveling"
- 1 Note: "Plot Ideas"

### Example 2: Create a Fantasy World

```bash
python3 src/presentation/cli.py

# Select [1] Worlds -> [2] Create new world
World name: Kingdom of Eldoria
Description: A medieval kingdom filled with magic and mystery

# Select [2] Characters -> [2] Create new character
Select World ID: 1
Character name: Sir Galahad
Backstory: A noble knight sworn to protect the realm from dark forces...
Add abilities? Yes
Ability name: Holy Strike
Ability description: A powerful attack blessed by divine light
Power level (1-10): 8
Add another ability? No
Add combat stats? Yes
Rarity: epic
Base HP: 120
Base ATK: 30
Base DEF: 25

# Select [3] Events -> [2] Create new event
Select World ID: 1
Event name: The Dragon's Attack
Description: A fierce dragon descends upon the kingdom...
Add participants? Yes
Enter Character ID (or 'done' to finish): 2
Added character: Sir Galahad
Enter Character ID (or 'done' to finish): done
```

### Example 3: Search and Export

```bash
python3 src/presentation/cli.py

# Select [7] Search all entities
Enter search term: dragon

# View results across all entity types
# Worlds, Characters, Events, Items, Quests, Notes containing "dragon"

# Select [8] Export to JSON
Export filename: dragon_lore.json

# Review export summary
✅ Exported to 'dragon_lore.json'
ℹ️  Worlds: 2
ℹ️  Characters: 5
ℹ️  Events: 3
ℹ️  Items: 8
ℹ️  Quests: 2
ℹ️  Notes: 4
```

### Example 4: Managing Items with Rarity

```bash
python3 src/presentation/cli.py

# Create a legendary weapon
# Select [4] Items -> [2] Create new item
Select World ID: 1
Item name: Excalibur
Description: The legendary sword of King Arthur, imbued with magical power
Item type [weapon/armor/artifact/consumable/tool/other]: weapon
Rarity [common/uncommon/rare/epic/legendary/mythic]: legendary

# View all legendary items
# Select [4] Items -> [1] List all items
# (Sorted by rarity, legendary items highlighted)
```

## Tips & Best Practices

### Data Integrity
- Always create a world before creating other entities
- Character backstories must be at least 100 characters
- Events require at least one participant
- Use search to verify entity existence before operations

### Workflow
1. Start by creating your world(s)
2. Add characters with rich backstories
3. Create events to build your timeline
4. Add items for your world's economy
5. Define quests for story progression
6. Use notes for planning and ideas

### Backup
- Export to JSON regularly to backup your data
- Use descriptive filenames for exports (e.g., "campaign_v1.json")
- Keep multiple versions of important exports

### Productivity
- Use tab completion for prompts where available
- Press Ctrl+C to cancel current operation
- Default values are shown in brackets - press Enter to use them
- Use search to quickly locate entities without browsing menus

## Keyboard Shortcuts

- `Tab` - Autocomplete (where available)
- `Ctrl+C` - Cancel current operation
- `Enter` - Submit input / Use default value
- `0` - Go back/Return to previous menu

## Error Handling

The CLI provides clear error messages:

- ✅ **Validation Errors**: Shows what field failed and why
- ✅ **Missing Entities**: Warns when required entities don't exist
- ✅ **Confirmation Prompts**: Prevents accidental deletions
- ✅ **Cascade Warnings**: Alerts when deleting worlds will delete related data

Example:
```
⚠️  No characters available in this world.
❌ Character backstories must be at least 100 characters
⚠️  Creating event without participants (not recommended)
❌ Are you sure you want to delete 'Eternal Forge'? This will also delete all associated entities!
```

## Color Coding

The CLI uses colors to enhance readability:

- 🟢 **Green** - Success messages, confirmations
- 🔴 **Red** - Errors, warnings, destructive actions
- 🟡 **Yellow** - Warnings, highlights
- 🔵 **Blue** - Information, tips
- 🟣 **Magenta** - Headers, emphasis
- ⚪ **Cyan** - Entity names, titles
- ⚫ **Dim/Gray** - Secondary information

## Technical Details

### Architecture
- **CLI Framework**: Click for command-line interface
- **Rich Output**: Rich library for beautiful formatting
- **Domain Model**: Uses existing domain entities and value objects
- **Storage**: In-memory storage (production would use repositories)
- **Validation**: Leverages domain value objects for data integrity

### File Location
```
lore/loreSystem/src/presentation/cli.py
```

### Dependencies
- `click>=8.1.7` - CLI framework
- `rich>=13.7.0` - Rich terminal output
- Domain entities from `src.domain.entities.*`
- Value objects from `src.domain.value_objects.*`

## Future Enhancements

Potential improvements for production use:
- Integration with actual database repositories
- Update operations for existing entities
- Advanced search filters (by date, rarity, type, etc.)
- Import from JSON
- Entity relationships visualization
- Batch operations
- Custom queries and reports
- Configuration file support
- Plugin system for custom commands

## Support & Documentation

For additional help:
- Use the built-in help: Menu option `[9]`
- View sample data: Run with `--demo` flag
- Check domain entity documentation
- Review value objects for validation rules

---

**LoreSystem CLI v1.0.0** - Interactive Entity Management Tool
