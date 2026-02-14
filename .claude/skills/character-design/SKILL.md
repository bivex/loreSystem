---
name: character-design
description: Extract character entities from narrative text. Use when analyzing characters, relationships, psychology, development arcs, voice/mocap data, and character variants.
---
# character-design

Domain skill for character extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `character` | Main character entity with name, role, personality, motivation |
| `character_evolution` | Character development arc or growth moment |
| `character_profile_entry` | Backstory detail or profile information |
| `character_relationship` | Relationship between two characters |
| `character_variant` | Alternate version, iteration, or form |
| `voice_actor` | Voice acting information |
| `motion_capture` | Motion capture performance data |

## Extraction Rules

1. **Identify characters**: Named characters with dialogue/actions, referred-to characters, groups
2. **Extract details**: Name, role, status, personality traits, motivations, goals
3. **Track development**: Growth moments, realizations, motivation changes
4. **Map relationships**: Type (friend, rival, family, romantic), strength, dynamics
5. **Note variants**: Alternate forms, timelines, disguises

## Domain Constraints

- `backstory`: minimum 100 characters
- `ability.power_level`: integer 1–10
- `combat_stats`: attack, defense, health, speed ≥ 0
- `status`: "active" or "inactive"

## Output Format

Write to `entities/narrative.json` (narrative-team file):

```json
{
  "character": [
    {
      "id": "uuid",
      "name": "Kira",
      "description": "A brave young warrior searching for her missing brother",
      "role": "protagonist",
      "personality": ["brave", "curious", "stubborn"],
      "motivation": "Find her missing brother",
      "status": "active"
    }
  ],
  "character_relationship": [
    {
      "id": "uuid",
      "name": "Kira-Marcus Bond",
      "description": "Strong friendship forged through shared battles",
      "character_a_id": "kira-uuid",
      "character_b_id": "marcus-uuid",
      "type": "friend",
      "strength": "strong"
    }
  ],
  "cross_references": [
    {
      "source_type": "character",
      "source_id": "kira-uuid",
      "target_type": "location",
      "target_skill": "world-building",
      "target_hint": "Eldoria Village — Kira's home village"
    }
  ],
  "_metadata": { "source": "...", "skill": "character-design", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Uniqueness**: Each character has a unique ID; name variations reference the same ID
- **Implicit relationships**: Track both explicit and implied connections
- **Cross-references**: Locations, factions, items mentioned with characters → cross_references
