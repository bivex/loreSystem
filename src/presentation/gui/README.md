# LoreForge GUI Editor

PyQt6-based graphical user interface for managing game lore.

## Features

### Worlds Management
- Create, edit, and delete worlds
- View all worlds in a table
- Update world descriptions and names
- Version tracking

### Characters Management
- Create characters with detailed backstories (≥100 characters)
- Assign characters to worlds
- Manage character abilities:
  - Add/remove abilities
  - Set power levels (1-10)
  - Describe each ability
- Set character status (active/inactive)
- Calculate average power level

### Events Management
- Create timeline events with start/end dates
- Assign events to worlds
- Manage event participants (characters from same world)
- Set event outcomes (ongoing, success, failure, cancelled)
- Add/remove participants dynamically
- Date range validation

### Improvements System
- Propose lore enhancements for any entity
- Workflow management: proposed → approved → applied → rejected
- Link improvements to worlds, characters, or events
- Status transition validation
- Git commit hash tracking
- Suggestion text with full descriptions

### Items Management
- Create, edit, and delete items
- Assign items to worlds
- Set item types: weapon, armor, artifact, consumable, tool, other
- Set rarity levels: common, uncommon, rare, epic, legendary
- Add detailed descriptions
- Version tracking

### Abilities System
- Create abilities with:
  - Name
  - Description
  - Power level (1-10 scale)
- Visual ability management through dialog
- Duplicate ability prevention

### Load/Save
- Save lore to JSON files
- Load existing lore projects
- Create new projects
- Auto-saves with version tracking

## Running the GUI

### Option 1: Direct Launch
```bash
python3 run_gui.py
```

## Running Tests and Coverage

Run tests with coverage from the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

To produce a coverage report:

```bash
pytest --cov=src --cov-report=html
```

### Option 2: Module Launch
```bash
python3 -m src.presentation.gui.lore_editor
```

### Requirements
- Python 3.11+
- PyQt6 >= 6.6.1

Install dependencies:
```bash
pip install -r requirements.txt
```

Or create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 run_gui.py
```

## GUI Layout

```
┌─────────────────────────────────────────────────────┐
│              🎮 LoreForge Chronicles                │
├─────────────────────────────────────────────────────┤
│  [Worlds] [Characters] [Events] [Improvements] [Items] │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Entity List (Table)                          │  │
│  │ ┌──────┬─────────┬──────────┬─────────────┐ │  │
│  │ │  ID  │  Name   │  Info    │   Version   │ │  │
│  │ └──────┴─────────┴──────────┴─────────────┘ │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Entity Details ──────────────────────────────┐ │
│  │ Name:        [________________]               │ │
│  │ Description: [________________]               │ │
│  │              [________________]               │ │
│  └───────────────────────────────────────────────┘ │
│                                                      │
│  [Add]  [Update]  [Delete]                          │
│                                                      │
├─────────────────────────────────────────────────────┤
│  [New]  [Load]  [Save]  [Save As]                   │
│                                                      │
│  Status: Ready                                       │
└─────────────────────────────────────────────────────┘
```

## Data Format

Lore is saved as JSON with this structure:

```json
{
  "worlds": [
    {
      "id": 1,
      "name": "Eternal Forge",
      "description": "A world of eternal flame...",
      "created_at": "2024-01-01T00:00:00+00:00",
      "updated_at": "2024-01-01T00:00:00+00:00",
      "version": 1
    }
  ],
  "characters": [
    {
      "id": 2,
      "world_id": 1,
      "name": "Aria",
      "backstory": "A master blacksmith who...",
      "status": "active",
      "abilities": [
        {
          "name": "Flame Mastery",
          "description": "Control over elemental fire",
          "power_level": 8
        }
      ],
      "created_at": "2024-01-01T00:00:00+00:00",
      "updated_at": "2024-01-01T00:00:00+00:00",
      "version": 1
    }
  ],
  "events": [],
  "improvements": [],
  "items": [
    {
      "id": 3,
      "world_id": 1,
      "name": "Soulfire Blade",
      "description": "A legendary sword forged in the heart of the Eternal Forge...",
      "item_type": "weapon",
      "rarity": "legendary",
      "created_at": "2024-01-01T00:00:00+00:00",
      "updated_at": "2024-01-01T00:00:00+00:00",
      "version": 1
    }
  ],
  "next_id": 4
}
```

## Validation Rules

The GUI enforces domain-driven design invariants:

### World Validation
- Name: 3-100 characters
- Description: 10-5000 characters
- Name must be unique per tenant

### Character Validation
- Name: 3-100 characters
- Backstory: ≥100 characters (business rule)
- Must belong to a valid world
- Abilities:
  - Each ability name must be unique per character
  - Power level: 1-10 inclusive
  - Description: 10-500 characters

### Event Validation
- Must have at least 1 participant
- End date must be after start date (if provided)
- Participants must be valid characters from same world
- Date format: YYYY-MM-DD

### Improvement Validation
- Must reference existing entity (world/character/event)
- Suggestion cannot be empty
- Status transitions must be valid (proposed → approved → applied)
- Git commit hash required for tracking

### Item Validation
- Name: 1-255 characters, cannot be empty
- Description: Required, enforced by domain
- Must belong to a valid world
- Item type: Must be one of predefined types (weapon, armor, artifact, consumable, tool, other)
- Rarity: Optional, must be one of predefined levels (common, uncommon, rare, epic, legendary)

## Architecture

The GUI follows hexagonal architecture:

```
Presentation Layer (PyQt6)
    ↓
Application Layer (Use Cases)
    ↓
Domain Layer (Entities, Value Objects)
```

### Key Components

- **MainWindow**: Application entry point with tabs
- **WorldsTab**: World CRUD operations
- **CharactersTab**: Character management with abilities
- **EventsTab**: Event management with participants
- **ImprovementsTab**: Improvement workflow management
- **ItemsTab**: Item CRUD operations with type and rarity
- **AbilityDialog**: Modal dialog for ability creation/editing
- **LoreData**: In-memory storage with serialization

### Domain Integration

The GUI uses domain entities directly:
- `World.create()` - Factory for new worlds
- `Character.create()` - Factory for new characters
- Value objects enforce validation:
  - `WorldName`, `CharacterName` - Name constraints
  - `Backstory` - Minimum 100 characters
  - `PowerLevel` - Range 1-10
  - `Ability` - Composite value object

### Error Handling

All domain exceptions are caught and displayed as user-friendly messages:
- Validation errors show in message boxes
- Invariant violations are prevented before persistence
- Clear error messages guide users to correct input

## Future Enhancements

- [ ] Events tab implementation
- [ ] Improvements workflow UI
- [ ] Requirements management
- [ ] Search and filter functionality
- [ ] Export to different formats
- [ ] Undo/redo functionality
- [ ] Database persistence (PostgreSQL)
- [ ] Elasticsearch integration for search
- [ ] Git version control UI
- [ ] LLM-powered improvement suggestions
- [ ] Drag-and-drop relationships
- [ ] Visual graph view of lore connections

## Troubleshooting

### Import Errors
Make sure you're running from the project root:
```bash
cd /path/to/loreSystem
python3 run_gui.py
```

### PyQt6 Not Found
Install PyQt6:
```bash
pip install PyQt6
```

### Domain Validation Errors
The GUI enforces strict domain rules. Check:
- Backstory has at least 100 characters
- Ability power levels are between 1-10
- Names meet length requirements (3-100 chars)
- Descriptions meet minimum lengths

### File Save/Load Issues
- Ensure you have write permissions
- JSON files must be valid format
- Check file extension is `.json`

## Examples

### Creating a Fantasy World

1. Go to "Worlds" tab
2. Enter name: "Mystical Realm"
3. Enter description: "A realm of magic and mystery where ancient powers still dwell..."
4. Click "Add World"

### Creating a Character

1. Go to "Characters" tab
2. Select world from dropdown
3. Enter name: "Elara Moonwhisper"
4. Enter backstory (≥100 chars): "Born under a blood moon, Elara discovered her magical abilities at a young age. She spent decades mastering the arcane arts..."
5. Click "Add Ability"
   - Name: "Moon Magic"
   - Description: "Harnesses lunar energy"
   - Power: 9
6. Click "Add Character"

### Saving Your Work

1. Click "Save As"
2. Choose location and filename (e.g., `mystical_realm.json`)
3. Click "Save"

### Loading Existing Lore

1. Click "Load"
2. Select your `.json` file
3. All worlds, characters, events, and improvements will be loaded

## Contributing

When extending the GUI:

1. Maintain hexagonal architecture
2. Use domain entities, never bypass validation
3. Keep UI code separate from business logic
4. Add proper error handling
5. Update this README with new features

## License

Part of the LoreForge system. See main project LICENSE.
