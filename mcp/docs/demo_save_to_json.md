# JSON Persistence Demo

This guide shows how to use the JSON persistence features to save and load your lore data.

## Quick Example

### 1. Create Some Lore Content

In Claude Desktop (with the MCP server configured):

```
Create a world called "Fantasy Realm" with description "A magical world of adventure"
for tenant "my-game"

Add a legendary character named "Aragorn" to Fantasy Realm with backstory:
"A ranger of the North, heir to the throne of Gondor. He has spent years wandering
the wild lands, protecting the innocent while concealing his true identity as the
last of the Dúnedain chieftains."

Add an ability "Leadership" to Aragorn with power 8 and description "Inspires allies"
```

### 2. Save to JSON Files

```
Save all lore data for tenant "my-game" to JSON files
```

**Result**: Creates organized JSON files in `lore_data/`:
```
lore_data/
├── worlds/
│   └── my-game_world_1.json
├── characters/
│   └── my-game_char_1.json
├── stories/
├── events/
└── pages/
```

### 3. Export to Single File

```
Export all data for tenant "my-game" to "fantasy_realm_backup.json"
```

**Result**: Creates `lore_data/fantasy_realm_backup.json` with:
```json
{
  "metadata": {
    "tenant_id": "my-game",
    "exported_at": "2026-01-26T12:34:56.789",
    "version": "1.0.0"
  },
  "data": {
    "worlds": [...],
    "characters": [...],
    "stories": [],
    "events": [],
    "pages": []
  },
  "counts": {
    "worlds": 1,
    "characters": 1,
    "stories": 0,
    "events": 0,
    "pages": 0
  }
}
```

### 4. Check Storage Stats

```
Get storage statistics
```

**Response**:
```json
{
  "success": true,
  "statistics": {
    "total_files": 2,
    "by_type": {
      "worlds": {"count": 1, "size_bytes": 423},
      "characters": {"count": 1, "size_bytes": 511},
      "stories": {"count": 0, "size_bytes": 0},
      "events": {"count": 0, "size_bytes": 0},
      "pages": {"count": 0, "size_bytes": 0}
    },
    "total_size_bytes": 934,
    "data_directory": "/path/to/loreSystem/mcp/lore_data"
  }
}
```

### 5. List Saved Files

```
List saved files for tenant "my-game"
```

**Response**:
```json
{
  "success": true,
  "tenant_id": "my-game",
  "total_files": 2,
  "files": {
    "worlds": ["lore_data/worlds/my-game_world_1.json"],
    "characters": ["lore_data/characters/my-game_char_1.json"],
    "stories": [],
    "events": [],
    "pages": []
  }
}
```

## Example JSON Files

### World File (`my-game_world_1.json`)
```json
{
  "id": 1,
  "tenant_id": 42,
  "name": "Fantasy Realm",
  "description": "A magical world of adventure",
  "parent_id": null,
  "created_at": "2026-01-26T12:00:00.000000",
  "updated_at": "2026-01-26T12:00:00.000000",
  "version": 1
}
```

### Character File (`my-game_char_1.json`)
```json
{
  "id": 1,
  "tenant_id": 42,
  "world_id": 1,
  "name": "Aragorn",
  "backstory": "A ranger of the North, heir to the throne of Gondor...",
  "status": "active",
  "abilities": [
    {
      "name": "Leadership",
      "description": "Inspires allies",
      "power_level": 8
    }
  ],
  "parent_id": null,
  "location_id": null,
  "rarity": null,
  "element": null,
  "role": null,
  "base_hp": null,
  "base_atk": null,
  "base_def": null,
  "base_speed": null,
  "energy_cost": null,
  "created_at": "2026-01-26T12:01:00.000000",
  "updated_at": "2026-01-26T12:02:00.000000",
  "version": 2
}
```

## Use Cases

### Version Control
```bash
# Save your lore regularly
git add lore_data/
git commit -m "Added Aragorn character"
git push
```

### Team Collaboration
```
Export tenant "shared-world" to "world_v1.0.json"
```
Share the exported file with team members.

### Backup Strategy
```
# Daily backup
Save all lore data for tenant "my-game" to JSON files

# Weekly archive
Export tenant "my-game" to "weekly_backup_2026-01-26.json"
```

### Migration
1. Export from development environment
2. Copy JSON file to production
3. (Future feature) Import from JSON file

## File Organization

```
lore_data/
├── worlds/
│   ├── tenant1_world_1.json
│   ├── tenant1_world_2.json
│   └── tenant2_world_1.json
├── characters/
│   ├── tenant1_char_1.json
│   ├── tenant1_char_2.json
│   └── tenant2_char_1.json
├── stories/
│   └── tenant1_story_1.json
├── events/
│   └── tenant1_event_1.json
├── pages/
│   └── tenant1_page_1.json
└── exports/
    ├── full_backup_2026-01-26.json
    └── weekly_archive.json
```

## Best Practices

### 1. Save After Major Changes
```
# After creating a new world and characters
Save all lore data for tenant "my-game" to JSON files
```

### 2. Export Before Updates
```
# Before making major changes
Export tenant "my-game" to "backup_before_changes.json"
```

### 3. Regular Backups
Set a reminder to save/export your lore regularly:
- Daily: `save_to_json` for incremental backups
- Weekly: `export_tenant` for full archives

### 4. Check Storage Periodically
```
Get storage statistics
```
Monitor file counts and sizes to ensure everything is being saved.

### 5. Organize Exports
Use descriptive filenames:
- `world_v1.0.json` - Version releases
- `backup_2026-01-26.json` - Date-based backups
- `before_big_update.json` - Pre-change snapshots

## Troubleshooting

### "No files saved"
- Make sure you created content first
- Check the tenant_id matches exactly
- Verify the `lore_data/` directory exists

### "Permission denied"
- Ensure the server has write permissions
- Check the data directory path

### "File not found when listing"
- The tenant_id might not match
- Use `list_saved_files` without tenant_id to see all files

## Future Features

Coming soon:
- `load_from_json` - Restore data from JSON files
- `import_tenant` - Import from exported JSON file
- Automatic backup scheduling
- Incremental saves (only changed entities)
- Compression for large exports

---

**Pro Tip**: Use `export_tenant` before major changes to your lore. It's like a save point in a video game - you can always go back if needed!
