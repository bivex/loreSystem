# LoreForge GUI Quick Start Guide

Get started with the LoreForge graphical editor in 5 minutes.

## Installation

### Step 1: Setup Python Environment

```bash
# Navigate to project directory
cd /path/to/loreSystem

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Launch the Editor

```bash
python3 run_gui.py
```

## First Steps

### Load Sample Data

1. Click **"Load"** button at the bottom
2. Navigate to `examples/sample_lore.json`
3. Click **"Open"**

You'll see:
- 2 worlds (Eternal Forge, Shadowmere Wastes)
- 3 characters (Aria, Valorian, Umbra)
- 2 events (The Great Reforging, Discovery of Lost Archives)

### Create Your First World

1. Go to **"Worlds"** tab
2. Enter world details:
   - **Name**: "Crystal Peaks"
   - **Description**: "Towering mountains of crystallized magic where dragons make their homes and ancient wizards seek enlightenment."
3. Click **"Add World"**

### Create Your First Character

1. Go to **"Characters"** tab
2. Select your world from dropdown: "Crystal Peaks"
3. Fill in character details:
   - **Name**: "Zephyr Stormrider"
   - **Backstory** (at least 100 characters): 
     ```
     A dragon rider bonded with the legendary storm dragon Tempest. 
     Raised among the clouds of Crystal Peaks, Zephyr mastered the 
     art of aerial combat and weather manipulation at a young age. 
     Now serves as guardian of the mountain realm, protecting it 
     from those who would exploit its magical crystals.
     ```
   - **Status**: "active"

4. Click **"Add Ability"**:
   - **Name**: "Dragon Bond"
   - **Description**: "Telepathic connection with storm dragon Tempest"
   - **Power Level**: 9
   - Click **"OK"**

5. Click **"Add Ability"** again:
   - **Name**: "Storm Calling"
   - **Description**: "Summon lightning and control weather patterns"
   - **Power Level**: 7
   - Click **"OK"**

6. Click **"Add Character"**

### Save Your Work

1. Click **"Save As"**
2. Choose location: `examples/my_lore.json`
3. Click **"Save"**

## Key Features

### Worlds Tab
- **Table View**: See all worlds with ID, name, description preview, and version
- **Selection**: Click a row to edit that world
- **Add**: Create new worlds
- **Update**: Modify selected world (auto-increments version)
- **Delete**: Remove world (confirmation required)

### Characters Tab
- **Table View**: Characters with world, ability count, and status
- **World Selector**: Dropdown to choose character's home world
- **Backstory Validation**: Must be ≥100 characters (business rule)
- **Abilities Manager**:
  - Add unlimited abilities per character
  - Each ability has name, description, power level (1-10)
  - Remove abilities with button click
  - Duplicate ability names are prevented
- **Status**: Toggle between active/inactive

### Data Persistence
- **JSON Format**: Human-readable, version-control friendly
- **Load**: Open any `.json` lore file
- **Save**: Update current file
- **Save As**: Create new file
- **New**: Clear all data and start fresh

## Domain Rules (Automatic Validation)

The GUI enforces these business rules automatically:

### World Rules
✅ Name: 3-100 characters  
✅ Description: 10-5000 characters  
✅ Unique names per tenant  

### Character Rules
✅ Name: 3-100 characters  
✅ Backstory: ≥100 characters (important!)  
✅ Must belong to existing world  
✅ Abilities:
  - Power level: 1-10 only
  - Unique names per character
  - Description: 10-500 characters

### What Happens on Validation Failure?
- Error message box appears
- Invalid data is NOT saved
- Form remains open for correction
- Clear error message explains the issue

## Common Tasks

### Edit a World
1. Go to Worlds tab
2. Click the world row in table
3. Modify name or description in form
4. Click "Update World"

### Add More Abilities to Character
1. Go to Characters tab
2. Select character from table
3. Click "Add Ability"
4. Fill in ability details
5. Click "Update Character"

### Delete a Character
1. Select character in table
2. Click "Delete Character"
3. Confirm deletion

### Start Fresh
1. Click "New"
2. Confirm you want to clear data
3. Start creating from scratch

## Tips & Tricks

### Backstory Requirement
Characters need at least 100 characters in backstory. This ensures rich, meaningful character development. If you get an error, add more detail about:
- Character's origin
- Their motivations
- Key life events
- Relationships with other characters
- Their role in the world

### Power Level Guidelines
- **1-3**: Minor abilities, novice level
- **4-6**: Competent, useful abilities
- **7-8**: Powerful, rare abilities
- **9**: Master-level, legendary abilities
- **10**: Godlike, world-changing power

### Ability Examples
Good ability descriptions:
- "Telekinetic control over objects up to 50kg"
- "Heals wounds through touch, drains user's stamina"
- "Transforms into shadow form, immune to physical damage"

### Version Tracking
Each edit increments the version number automatically. This helps track changes and enables future undo/redo features.

## Keyboard Shortcuts

- **Ctrl+N**: New file (future)
- **Ctrl+O**: Open/Load file (future)
- **Ctrl+S**: Save file (future)
- **Ctrl+Shift+S**: Save As (future)
- **Tab**: Navigate between form fields
- **Enter**: Submit form when in text input

## Troubleshooting

### "Failed to create character: Backstory too short"
Your backstory needs at least 100 characters. Add more detail about the character's background, personality, and history.

### "Failed to create world: Name already exists"
Each world needs a unique name within your tenant. Choose a different name or edit the existing world.

### "Power level must be between 1 and 10"
Ability power levels are constrained to 1-10 range. Adjust the power level in the ability dialog.

### "Cannot add duplicate ability"
Each character can only have one ability with a given name. Either:
- Choose a different ability name
- Remove the existing ability first
- Update the existing ability instead

### GUI Won't Start
Make sure PyQt6 is installed:
```bash
pip install PyQt6
```

If using system Python on macOS, you may need:
```bash
python3 -m venv venv
source venv/bin/activate
pip install PyQt6
python3 run_gui.py
```

### Can't Save File
- Check you have write permissions in the directory
- Ensure the file extension is `.json`
- Close other programs that might lock the file

## Next Steps

### Learn More
- Read [GUI Documentation](README.md) for architecture details
- Check [Implementation Guide](../../../docs/IMPLEMENTATION_GUIDE.md)
- Review domain model in `src/domain/`

### Extend the GUI
- Add Events tab (similar to Characters)
- Implement search functionality
- Add export to different formats
- Create visual relationship graphs

### Switch to Database
Current GUI uses JSON files. To use PostgreSQL:
1. Set up database with `alembic upgrade head`
2. Implement repository adapters
3. Replace `LoreData` with repository calls

### Advanced Features
- Git integration for version control
- Elasticsearch for full-text search
- LLM-powered improvement suggestions
- Multi-user collaboration

## Example Workflow

### Creating a Campaign
1. **Load** sample data for reference
2. **Create World**: "Frostfall Kingdom"
3. **Add Characters**:
   - King Aldric (ruler)
   - Lyra Iceweaver (mage)
   - Grom Stonefist (warrior)
4. **Define Abilities** for each
5. **Save As**: `campaigns/frostfall.json`
6. **Version control**: `git add campaigns/frostfall.json && git commit`

### Iterating on Lore
1. **Load** existing campaign
2. **Update** character backstories as story evolves
3. **Add** new abilities when characters level up
4. **Create** events for major story beats
5. **Save** regularly
6. Notice version numbers incrementing

## Sample Data

Explore `examples/sample_lore.json` to see:
- **Eternal Forge**: High-fantasy crafting world
- **Shadowmere Wastes**: Dark, mysterious wasteland
- **Aria & Valorian**: Mentor-student relationship
- **Umbra**: Tragic corrupted scholar
- **Events**: Ongoing quests and completed discoveries

## Support

For help:
- Check domain validation rules in `src/domain/`
- Review error messages carefully
- Read value object constraints in `src/domain/value_objects/`
- Check console output for detailed errors

## Contributing

To add features to the GUI:
1. Follow hexagonal architecture
2. Use domain entities for validation
3. Keep presentation logic separate
4. Add error handling
5. Update this guide

---

**Ready to forge your own legends? Launch the editor and start creating!**

```bash
python3 run_gui.py
```
