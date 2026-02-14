---
name: faction-design
description: Extract faction entities from narrative text. Use when analyzing organizations, hierarchies, ideologies, territories, resources, leaders, banners, and inter-faction relationships.
---
# faction-design

Domain skill for faction and organization extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `faction` | Organization, guild, cult, or group |
| `faction_hierarchy` | Internal power structure |
| `faction_ideology` | Beliefs, goals, worldview |
| `faction_leader` | Leadership position or person |
| `faction_membership` | Member roster or membership info |
| `faction_resource` | Controlled resources and assets |
| `faction_territory` | Controlled or influenced territory |
| `banner` | Faction banner, emblem, or symbol |

## Domain Constraints

- `faction.type`: political, religious, military, criminal, magical, merchant, secret, monster
- `faction.alignment`: good, neutral, evil, chaotic
- `faction_membership.reputation`: integer -1000 to 1000

## Extraction Rules

1. **Named groups**: Guilds, armies, cults, orders — extract with exact name
2. **Implied groups**: Bandits, rebels, authorities — create descriptive name
3. **Hierarchy**: Who leads, how power is organized, ranks
4. **Relationships**: Allies, enemies, neutral parties between factions
5. **Resources**: Wealth, military power, information, magic, territory

## Output Format

Write to `entities/society.json`:

```json
{
  "faction": [
    {
      "id": "uuid",
      "name": "Shadow Brotherhood",
      "description": "Secret criminal organization operating in the underworld",
      "type": "criminal",
      "alignment": "evil"
    }
  ],
  "faction_leader": [
    {
      "id": "uuid",
      "name": "The Hooded Master",
      "description": "Mysterious leader of the Shadow Brotherhood",
      "faction_id": "faction-uuid",
      "rank": "supreme_leader"
    }
  ],
  "cross_references": [
    {
      "source_type": "faction_leader",
      "source_id": "uuid",
      "target_type": "character",
      "target_skill": "character-design",
      "target_hint": "The Hooded Master — also a character entity"
    }
  ],
  "_metadata": { "source": "...", "skill": "faction-design", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Overlapping membership**: Characters may belong to multiple factions
- **Hidden factions**: Some operate in secret — extract even unnamed ones
- **Dynamic relationships**: Alliances shift; note current state from text
- **Cross-references**: Faction leaders → character-design; territories → world-building
