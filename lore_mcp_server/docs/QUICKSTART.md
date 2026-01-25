# Quick Start Guide

Get started with the Lore System MCP Server in minutes!

## Prerequisites

- Python 3.11 or higher
- pip package manager

## Installation

```bash
cd mcp
./setup.sh
```

Or manually:

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r ../requirements.txt
```

## Verify Installation

Run the test suite:

```bash
python test_server.py
```

You should see:
```
✓ All tests passed (3/3)
The MCP server is ready to use!
```

## Running the Server

```bash
python server.py
```

The server will run and communicate via stdio (standard input/output) using the MCP protocol.

## Configure Claude Desktop

1. Open your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the lore-system server:

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

Replace `/absolute/path/to/loreSystem` with the actual path.

3. Restart Claude Desktop

## Basic Usage

Once configured in Claude Desktop, you can use the lore system tools in your conversations:

### Create a World

```
Please use the create_world tool to make a new fantasy world called "Aetheria"
with description "A magical realm where ancient technology meets mysticism"
```

### Create a Character

```
Use create_character to add a legendary fire mage named "Lyra Starweaver" to Aetheria.
Backstory: "Born under a celestial convergence, Lyra discovered her affinity for star magic
at age five. She spent decades studying at the Arcane Nexus..." (minimum 100 characters)
Stats: HP=800, ATK=320, DEF=120, Speed=180, Element=light, Role=dps, Rarity=LEGENDARY
```

### Add Abilities

```
Add an ability called "Cosmic Cascade" to Lyra with power level 9
and description "Summons a rain of starlight"
```

### Create a Story

```
Create a non-linear story called "The Rift Awakens" in Aetheria about
dimensional rifts threatening reality
```

### List Content

```
List all characters in Aetheria
List all stories in Aetheria
List all worlds for tenant "my-game"
```

### Save Data to JSON

```
Save all lore data for tenant "my-game" to JSON files
```

This creates individual JSON files in the `lore_data` directory:
- `lore_data/worlds/` - World files
- `lore_data/characters/` - Character files
- `lore_data/stories/` - Story files
- `lore_data/events/` - Event files
- `lore_data/pages/` - Page files

### Export to Single File

```
Export all data for tenant "my-game" to "my_world.json"
```

Creates a single comprehensive JSON file with all entities, making it easy to:
- Backup your lore
- Share with team members
- Version control your world
- Migrate between environments

## Available Tools

The MCP server provides these tools:

### World Management
- `create_world` - Create a new world
- `get_world` - Get world by ID
- `list_worlds` - List all worlds
- `update_world` - Update world details
- `delete_world` - Delete a world

### Character Management
- `create_character` - Create a new character
- `get_character` - Get character by ID
- `list_characters` - List characters in a world
- `update_character` - Update character details
- `delete_character` - Delete a character
- `add_ability` - Add ability to character

### Story Management
- `create_story` - Create a new story
- `get_story` - Get story by ID
- `list_stories` - List stories in a world

### Event Management
- `create_event` - Create a timeline event
- `list_events` - List events in a world

### Page Management
- `create_page` - Create a lore page
- `list_pages` - List pages in a world

### Persistence Management
- `save_to_json` - Save all data to JSON files
- `export_tenant` - Export tenant to single JSON file
- `list_saved_files` - List saved JSON files
- `get_storage_stats` - Get storage statistics

## Important Notes

### Data Persistence
The server supports multiple persistence modes:

1. **In-Memory** (default): Fast but temporary - data lost on restart
2. **JSON Files**: Save data through tool calls
   - Use `save_to_json` to persist all data to individual files
   - Use `export_tenant` to create a single backup file
   - Files stored in `lore_data/` directory (created automatically)
3. **PostgreSQL** (production): Implement database repositories for permanent storage

**Recommendation**: After creating lore content, use `save_to_json` or `export_tenant` to backup your work!

### Validation Rules
- **Tenant ID**: Positive integer (auto-generated from string)
- **World Name**: Max 255 characters
- **Character Name**: Max 255 characters
- **Backstory**: Minimum 100 characters (enforced!)
- **Power Level**: 1-10 (not 1-100)
- **Events**: Require at least one participant (character ID)

### Character Stats
- **Elements**: physical, fire, water, earth, wind, light, dark
- **Roles**: dps, tank, support, specialist
- **Rarities**: COMMON, UNCOMMON, RARE, EPIC, LEGENDARY

### Story Types
- **LINEAR**: Traditional sequential storytelling
- **NON_LINEAR**: Branching narratives
- **INTERACTIVE**: Player-driven choices

## Troubleshooting

### "Module not found" errors
Make sure you installed both requirements files:
```bash
pip install -r requirements.txt
pip install -r ../requirements.txt
```

### "Backstory must be at least 100 characters"
This is a domain rule. Character backstories must have narrative depth.
Add more detail to your character's history.

### "Power level must be between 1 and 10"
Power levels use a 1-10 scale for game balance, not 1-100.

### "Event must have at least one participant"
When creating events, include `participant_ids` parameter with at least one character ID.

## Next Steps

- Read the full [README.md](README.md) for detailed API documentation
- Check [CHANGELOG.md](CHANGELOG.md) for version history
- See [config.json](config.json) for configuration options
- Review [example_usage.py](example_usage.py) for programmatic usage

## Getting Help

If you encounter issues:
1. Run `python test_server.py` to verify setup
2. Check the error messages for validation failures
3. Review the domain model in `../src/domain/entities/`
4. Consult the README for detailed tool schemas

Happy lore building! 🎮📖
