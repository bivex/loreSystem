---
name: religious-lore
description: Extract religious entities from narrative text. Use when analyzing cults, sects, holy sites, scriptures, rituals, oaths, summons, pacts, curses, blessings, and miracles.
---
# religious-lore

Domain skill for religious and supernatural extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `cult` | Cult or secretive religious group |
| `sect` | Religious sect or denomination |
| `holy_site` | Sacred place or shrine |
| `scripture` | Religious text or holy book |
| `ritual` | Ritual, prayer, or religious ceremony |
| `oath` | Sacred oath or vow |
| `summon` | Summoning ritual or invocation |
| `pact` | Supernatural pact or agreement |
| `curse` | Curse or negative supernatural effect |
| `blessing` | Blessing or positive supernatural effect |
| `miracle` | Miraculous event or divine intervention |

## Extraction Rules

1. **Religious groups**: Cults, sects, churches — name, beliefs, structure
2. **Sacred places**: Temples, shrines, holy mountains — location, significance
3. **Rituals**: Procedure, required components, effects, practitioners
4. **Supernatural effects**: Curses, blessings, miracles — trigger, effect, duration
5. **Pacts**: Parties involved, terms, consequences of breaking

## Output Format

Write to `entities/society.json` (society-team file):

```json
{
  "cult": [
    {
      "id": "uuid",
      "name": "Order of the Void",
      "description": "Secretive cult worshipping the entities beyond the stars",
      "alignment": "evil"
    }
  ],
  "curse": [
    {
      "id": "uuid",
      "name": "Curse of the Blood Moon",
      "description": "Transforms the afflicted under moonlight",
      "trigger": "blood_moon",
      "effect": "transformation",
      "duration": "permanent until lifted"
    }
  ],
  "cross_references": [
    {
      "source_type": "holy_site",
      "source_id": "uuid",
      "target_type": "location",
      "target_skill": "world-building",
      "target_hint": "Temple of the Void — also a physical location"
    }
  ],
  "_metadata": { "source": "...", "skill": "religious-lore", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Multiple faiths**: Worlds often have competing religions
- **Lost religions**: Ancient faiths may have faded — extract remnants
- **Heretical practices**: Cults vs mainstream religion
- **Cross-references**: Holy sites → world-building; cult leaders → character-design; religious factions → faction-design
