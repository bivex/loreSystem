---
name: historical-research
description: Extract historical entities from narrative text. Use when analyzing eras, timelines, calendars, holidays, seasons, alliances, empires, kingdoms, and era transitions.
---
# historical-research

Domain skill for historical and chronological extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `era` | Historical era, age, or epoch |
| `era_transition` | Transition between eras |
| `timeline` | Chronological sequence of events |
| `calendar` | Calendar or timekeeping system |
| `holiday` | Holiday or special date |
| `season` | Named season or time of year |
| `alliance` | Historical or political alliance |
| `empire` | Empire or major state entity |
| `kingdom` | Kingdom or sovereign territory |
| `nation` | Nation or country |

## Extraction Rules

1. **Eras**: Named periods (Age of Magic, Dark Times) — extract with timeframe
2. **Transitions**: What caused era changes (wars, discoveries, cataclysms)
3. **Timelines**: Chronological sequence of mentioned events
4. **Calendars**: Timekeeping systems, named months, cycles
5. **States**: Empires, kingdoms, nations — with their boundaries and rulers

## Output Format

Write to `entities/society.json` (society-team file):

```json
{
  "era": [
    {
      "id": "uuid",
      "name": "Age of Magic",
      "description": "Ancient era when sorcerers ruled the skies",
      "timeframe": "ancient",
      "status": "past"
    }
  ],
  "era_transition": [
    {
      "id": "uuid",
      "name": "The Great War Transition",
      "description": "Magic waned after the Great War, ending the Age of Magic",
      "from_era_id": "era-uuid-1",
      "to_era_id": "era-uuid-2",
      "cause": "Great War"
    }
  ],
  "cross_references": [
    {
      "source_type": "era_transition",
      "source_id": "uuid",
      "target_type": "war",
      "target_skill": "military-strategy",
      "target_hint": "The Great War that caused the era transition"
    }
  ],
  "_metadata": { "source": "...", "skill": "historical-research", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Relative time**: Not all systems use absolute dates (cycles, ages)
- **Multiple perspectives**: History may differ by culture (victors write history)
- **Cross-references**: Wars → military-strategy; rulers → character-design; ceremonies → social-culture
