# Lore System MCP Server

Model Context Protocol (MCP) server for managing game lore with CRUD operations.

## Features

- **World Management**: Create, read, update, delete worlds
- **Character Management**: Full CRUD for characters with abilities
- **Story Management**: Linear and non-linear story creation
- **Event Management**: Timeline events with outcomes
- **Page Management**: Custom lore pages
- **Multi-tenant Support**: Isolated data per tenant
- **Domain-Driven Design**: Validates all business rules

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install parent project dependencies
pip install -r ../requirements.txt
```

## Usage

### Running the Server

```bash
# Run directly
python server.py

# Or make it executable
chmod +x server.py
./server.py
```

### Configuring in Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "lore-system": {
      "command": "python",
      "args": ["/path/to/loreSystem/mcp/server.py"]
    }
  }
}
```

## Available Tools

### World Operations

- **create_world**: Create a new world
  ```json
  {
    "tenant_id": "tenant-1",
    "name": "Middle Earth",
    "description": "A fantasy world created by Tolkien",
    "parent_id": null
  }
  ```

- **get_world**: Retrieve a world by ID
- **list_worlds**: List all worlds for a tenant
- **update_world**: Update world name or description
- **delete_world**: Delete a world

### Character Operations

- **create_character**: Create a new character
  ```json
  {
    "tenant_id": "tenant-1",
    "world_id": "world-123",
    "name": "Aragorn",
    "backstory": "A descendant of Isildur, Aragorn is the rightful heir to the throne of Gondor. He was raised in Rivendell by Elrond and became a ranger of the North, protecting the Shire and its inhabitants from dark forces.",
    "rarity": "LEGENDARY",
    "element": "physical",
    "role": "dps",
    "base_hp": 1200,
    "base_atk": 250,
    "base_def": 180,
    "base_speed": 150,
    "energy_cost": 100
  }
  ```

- **get_character**: Retrieve a character by ID
- **list_characters**: List characters in a world
- **update_character**: Update character backstory or status
- **delete_character**: Delete a character
- **add_ability**: Add an ability to a character
  ```json
  {
    "tenant_id": "tenant-1",
    "character_id": "char-456",
    "ability_name": "Andúril Strike",
    "description": "A powerful sword attack with the legendary blade",
    "power_level": 9
  }
  ```

### Story Operations

- **create_story**: Create a new story
  ```json
  {
    "tenant_id": "tenant-1",
    "world_id": "world-123",
    "name": "The Fellowship of the Ring",
    "description": "The first part of the Lord of the Rings trilogy",
    "story_type": "LINEAR",
    "content": "In a hole in the ground there lived a hobbit..."
  }
  ```

- **get_story**: Retrieve a story by ID
- **list_stories**: List stories in a world

### Event Operations

- **create_event**: Create a timeline event
  ```json
  {
    "tenant_id": "tenant-1",
    "world_id": "world-123",
    "name": "The Battle of Helm's Deep",
    "description": "A pivotal battle between Rohan and Saruman's forces",
    "start_date": "3019-03-03T00:00:00",
    "end_date": "3019-03-04T06:00:00",
    "outcome": "success"
  }
  ```

- **list_events**: List events in a world

### Page Operations

- **create_page**: Create a custom lore page
  ```json
  {
    "tenant_id": "tenant-1",
    "world_id": "world-123",
    "name": "The One Ring",
    "content": "# The One Ring\n\nForged by Sauron in the fires of Mount Doom..."
  }
  ```

- **list_pages**: List pages in a world

### Persistence Operations

- **save_to_json**: Save all lore data to JSON files
  ```json
  {
    "tenant_id": "tenant-1"
  }
  ```
  Creates individual JSON files for each entity in the `lore_data` directory.

- **export_tenant**: Export all tenant data to a single JSON file
  ```json
  {
    "tenant_id": "tenant-1",
    "filename": "my_world_export.json"
  }
  ```
  Creates a single comprehensive export file with all entities.

- **list_saved_files**: List all saved JSON files
  ```json
  {
    "tenant_id": "tenant-1"
  }
  ```
  Optional tenant_id parameter to filter files.

- **get_storage_stats**: Get statistics about stored data
  ```json
  {}
  ```
  Returns file counts and sizes for all entity types.

## Domain Model

### World
- Top-level container for all lore
- Supports hierarchical structure (parent worlds)
- Enforces unique names per tenant

### Character
- Must belong to a world
- Requires backstory (min 100 characters)
- Optional combat stats for gacha RPG systems
- Can have multiple abilities
- Supports elements: physical, fire, water, earth, wind, light, dark
- Supports roles: dps, tank, support, specialist
- Supports rarities: COMMON, UNCOMMON, RARE, EPIC, LEGENDARY

### Story
- Narrative content with types:
  - LINEAR: Traditional sequential storytelling
  - NON_LINEAR: Branching narratives
  - INTERACTIVE: Player-driven choices

### Event
- Timeline occurrences with date ranges
- Outcomes: success, failure, ongoing
- Can have participant characters

### Page
- Custom documentation
- Supports markdown content
- Hierarchical (can have parent pages)

## Architecture

The MCP server:
- Uses **in-memory repositories** for demo/development
- Supports **JSON file persistence** for saving/loading data
- Can be switched to **PostgreSQL** for production
- Validates all domain invariants
- Returns structured JSON responses
- Provides detailed error messages

### Data Storage

The server provides multiple persistence options:

1. **In-Memory** (default): Fast, but data is lost on restart
2. **JSON Files**: Save/load data through tool calls
   - Individual files per entity in `lore_data/` directory
   - Organized by entity type (worlds, characters, stories, events, pages)
   - Single-file export for easy sharing
3. **PostgreSQL** (production): Implement database repositories for persistence

## Error Handling

All tools return JSON with:
- `success`: boolean indicating operation status
- `error`: error message if failed
- `type`: exception type if failed
- Entity data if successful

Example error response:
```json
{
  "success": false,
  "error": "Backstory must be at least 100 characters",
  "type": "ValueError"
}
```

## Development

### Testing the Server

```bash
# Test basic functionality
echo '{"method":"tools/list"}' | python server.py

# Create a test world (requires proper MCP client)
# See examples in the examples/ directory
```

### Extending the Server

To add new tools:

1. Add the tool definition in `list_tools()`
2. Add the handler in `call_tool()`
3. Import required domain entities
4. Follow existing patterns for error handling

## License

Part of the loreSystem project. See parent directory for license information.
