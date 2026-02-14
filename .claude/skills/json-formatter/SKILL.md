---
name: json-formatter
description: JSON formatting rules for lore entity output. Enforces strict JSON, UUID identifiers, arrays per entity type, cross-references, and loreSystem schema compliance.
user-invocable: false
---
# json-formatter

Base skill for JSON output formatting. All extraction skills produce JSON that can be loaded by the Lore GUI (`LoreData.from_dict`).

## Rules

1. **Valid JSON**: Output must be parseable JSON — no trailing commas, no comments.
2. **Export schema**: Use the GUI export format defined in `src/presentation/gui/lore_data.py`.
3. **Plural collections**: Each entity collection is a top-level key with a plural name and an array value (e.g., `worlds`, `characters`, `locations`).
4. **IDs are numeric**: Use integer IDs and keep them consistent across references. If you generate new IDs, include `next_id` as max+1.
5. **Field names**: Use exact domain field names (snake_case). Do not invent `type` or `entity_type` unless that field exists in the domain model.
6. **Dates**: Use ISO 8601 strings for timestamps (`created_at`, `updated_at`, `start_date`, `end_date`).

## Output Structure (Export-Compatible)

```json
{
  "worlds": [],
  "characters": [],
  "locations": [],
  "quests": [],
  "items": [],
  "events": [],
  "stories": [],
  "storylines": [],
  "tags": [],
  "images": [],
  "choices": [],
  "flowcharts": [],
  "handouts": [],
  "inspirations": [],
  "environments": [],
  "factions": [],
  "maps": [],
  "notes": [],
  "requirements": [],
  "sessions": [],
  "tokenboards": [],
  "currencies": [],
  "rewards": [],
  "purchases": [],
  "event_chains": [],
  "faction_memberships": [],
  "music_controls": [],
  "music_states": [],
  "music_themes": [],
  "music_tracks": [],
  "progression_events": [],
  "character_states": [],
  "textures": [],
  "models": [],
  "next_id": 1
}
```

## Required Fields (Core Entities)

Use these minimum fields so JSON loads without validation errors:

- **worlds**: `id`, `name`, `description`, `created_at`, `updated_at`, `version`
- **characters**: `id`, `world_id`, `name`, `backstory`, `status`, `abilities`, `created_at`, `updated_at`, `version`
- **locations**: `id`, `world_id`, `name`, `description`, `location_type`, `created_at`, `updated_at`, `version`
- **quests**: `id`, `world_id`, `name`, `description`, `objectives`, `status`, `participant_ids`, `reward_ids`, `created_at`, `updated_at`, `version`

If a field is unknown, set it to `null` or an empty list (for arrays), but keep the key.
