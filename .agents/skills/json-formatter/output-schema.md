# Output Schema Reference

Standard JSON output format for all lore extraction skills.

## Top-Level Structure

Each team writes to its own output file. The top-level keys are **entity type names** (snake_case), each containing an **array** of entities.

```json
{
  "entity_type_a": [
    { "id": "uuid-1", "name": "...", ... },
    { "id": "uuid-2", "name": "...", ... }
  ],
  "entity_type_b": [
    { "id": "uuid-3", "name": "...", ... }
  ],
  "cross_references": [
    {
      "source_type": "entity_type_a",
      "source_id": "uuid-1",
      "target_type": "entity_type_x",
      "target_skill": "other-skill-name",
      "target_hint": "Name or description of the referenced entity"
    }
  ],
  "_metadata": {
    "source": "chapter_1.txt",
    "skill": "skill-name",
    "extracted_at": "2025-02-14T12:00:00Z",
    "entity_count": 5
  }
}
```

## Entity Format

Every entity MUST have:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string (UUID v4) | ✅ | Unique identifier |
| `name` | string (max 255) | ✅ | Entity display name |
| `description` | string | ✅ | Brief description of the entity |

Common optional fields:

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Sub-classification within entity type |
| `status` | string | active, inactive, deleted, archived |
| `tags` | string[] | Freeform tags for categorization |
| `metadata` | object | Additional key-value pairs |

## Cross-References

When an entity references something owned by another skill, add it to `cross_references` instead of creating the entity:

```json
{
  "cross_references": [
    {
      "source_type": "quest",
      "source_id": "quest-uuid",
      "target_type": "character",
      "target_skill": "character-design",
      "target_hint": "Elder Theron, the quest giver"
    }
  ]
}
```

This prevents duplicate entities across team output files.

## Team Output Files

| Team | Output File |
|------|-------------|
| narrative-team | `entities/narrative.json` |
| world-team | `entities/world.json` |
| society-team | `entities/society.json` |
| systems-team | `entities/systems.json` |
| technical-team | `entities/technical.json` |
| extraction-lead | `entities/merged_lore.json` |

## Validation Rules

From the domain model (`src/domain/`):

- **Name**: max 255 characters, non-empty
- **ID**: valid UUID v4 format
- **Backstory**: min 100 characters (Character entity)
- **Ability power_level**: 1–10 integer
- **Item level**: 1–100
- **Reputation**: -1000 to 1000
- **Combat stats**: ≥ 0 (attack, defense, health, speed)
- **Version**: ≥ 1
- **Timestamps**: updated_at ≥ created_at

## Enum Values

Use these exact values from the domain model:

- **ItemType**: weapon, armor, artifact, consumable, tool, other
- **Rarity**: common, uncommon, rare, epic, legendary, mythic
- **EventOutcome**: success, failure, ongoing
- **QuestStatus**: active, completed, failed, cancelled
- **ObjectiveType**: kill, collect, interact, deliver, escort, defend, explore, talk, craft, use
- **FactionType**: political, religious, military, criminal, magical, merchant, secret, monster
- **Alignment**: good, neutral, evil, chaotic
- **LocationType**: building, house, barn, temple, castle, dungeon, cave, forest, mountain, city, village, shop, tavern, ruins, landmark, other
- **TimeOfDay**: day, night, dawn, dusk
- **Weather**: clear, rainy, stormy, foggy
- **StoryType**: linear, non_linear, interactive
- **ChoiceType**: branch, consequence, decision
