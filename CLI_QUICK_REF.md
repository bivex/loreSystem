# CLI Quick Reference

## Installation

```bash
# Development mode (no installation needed)
cd lore/loreSystem
python3 run_cli.py --help

# Or make executable
chmod +x run_cli.py
./run_cli.py --help
```

## Common Commands

### World Operations

```bash
# List all worlds
lore-cli world list

# Create a world
lore-cli world create --name "My World" --description "A fantasy world"

# Show world details
lore-cli world show --world-id 1

# Update a world
lore-cli world update --world-id 1 --name "New Name"

# Delete a world
lore-cli world delete --world-id 1
```

### Character Operations

```bash
# List all characters
lore-cli character list

# List characters in a world
lore-cli character list --world-id 1

# Create a character
lore-cli character create \
  --world-id 1 \
  --name "Hero Name" \
  --backstory "A long backstory... (minimum 100 characters)"

# Show character details
lore-cli character show --character-id 1

# Update character status
lore-cli character update --character-id 1 --status inactive

# Delete a character
lore-cli character delete --character-id 1
```

### Event Operations

```bash
# List events in a world
lore-cli event list --world-id 1

# Create an event
lore-cli event create \
  --world-id 1 \
  --name "Battle of Something" \
  --description "Description of event" \
  --participant-ids "1,2,3"

# Show event details
lore-cli event show --event-id 1
```

### Story Operations

```bash
# List stories in a world
lore-cli story list --world-id 1

# Create a story
lore-cli story create \
  --world-id 1 \
  --name "Story Title" \
  --content "The story content..." \
  --description "Optional description"

# Create interactive story
lore-cli story create \
  --world-id 1 \
  --name "Choose Your Path" \
  --content "Interactive content..." \
  --type interactive

# Show story details
lore-cli story show --story-id 1
```

### Import/Export

```bash
# Export all data
lore-cli export --output backup.json

# Import data
lore-cli import --input backup.json

# Custom export path
lore-cli export -o /backups/lore_$(date +%Y%m%d).json
```

### Statistics

```bash
# Show system statistics
lore-cli stats
```

## Options

- `-v, --verbose` - Enable verbose output for debugging
- `-f, --force` - Skip confirmation prompts (for delete operations)

## Tips

1. **Backstory Length**: Character backstories must be at least 100 characters
2. **World ID Required**: Characters, events, and stories need a valid world ID
3. **Participant IDs**: Events require comma-separated character IDs (e.g., "1,2,3")
4. **Confirmation**: Delete operations ask for confirmation unless `--force` is used
5. **JSON Format**: Export format includes all entities with relationships

## Error Examples

```bash
# Missing required field
$ lore-cli world create --name "Test"
✗ World description is required

# Backstory too short
$ lore-cli character create --world-id 1 --name "Test" --backstory "Too short"
✗ Validation error: Backstory must be at least 100 characters, got 10

# World not found
$ lore-cli character create --world-id 999 --name "Test" --backstory "A"*100
✗ World with ID 999 not found
```

## JSON Export Format

```json
{
  "exported_at": "2024-01-15T10:30:00.123456",
  "tenant_id": 1,
  "worlds": [
    {
      "id": 1,
      "name": "World Name",
      "description": "World description",
      "parent_id": null,
      "created_at": "2024-01-15T10:00:00+00:00",
      "updated_at": "2024-01-15T10:00:00+00:00",
      "version": 1
    }
  ],
  "characters": [...],
  "events": [...],
  "stories": [...]
}
```

## Color Legend

- 🟢 **Green** - Success operations
- 🔴 **Red** - Error messages
- 🟡 **Yellow** - Warnings
- 🔵 **Blue** - Information
- 🟣 **Cyan** - Headers and emphasis
