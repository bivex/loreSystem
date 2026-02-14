---
name: social-culture
description: Extract social and cultural entities from narrative text. Use when analyzing social classes, honor, karma, reputation, festivals, ceremonies, tournaments, competitions, and social mobility.
---
# social-culture

Domain skill for social systems and cultural event extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `social_class` | Social class or caste |
| `social_mobility` | Social advancement or demotion mechanism |
| `affinity` | Affinity or positive disposition |
| `disposition` | General attitude or stance |
| `honor` | Honor system or code |
| `karma` | Karma or moral balance system |
| `reputation` | Reputation level or standing |
| `festival` | Festival or recurring cultural event |
| `celebration` | One-time celebration or joyous event |
| `ceremony` | Formal ceremony or ritual observance |
| `concert` | Musical performance event |
| `competition` | Contest or competitive event |
| `tournament` | Organized tournament or championship |

## Extraction Rules

1. **Social structure**: Class hierarchy, barriers, privileges
2. **Moral systems**: Honor codes, karma rules, reputation effects
3. **Cultural events**: Festivals, ceremonies — meaning, frequency, significance
4. **Social mobility**: Can people change class? How?
5. **Reputation**: How it's gained/lost, what it affects

## Output Format

Write to `entities/society.json` (society-team file):

```json
{
  "social_class": [
    {
      "id": "uuid",
      "name": "Noble Caste",
      "description": "Hereditary aristocratic class with political privileges",
      "rank": 1
    }
  ],
  "festival": [
    {
      "id": "uuid",
      "name": "Festival of Lights",
      "description": "Annual winter festival remembering those lost in the Great War",
      "frequency": "annual",
      "season": "winter"
    }
  ],
  "cross_references": [
    {
      "source_type": "festival",
      "source_id": "uuid",
      "target_type": "era",
      "target_skill": "historical-research",
      "target_hint": "Festival commemorates the Great War era"
    }
  ],
  "_metadata": { "source": "...", "skill": "social-culture", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Social stratification**: Clear hierarchies with barriers between classes
- **Reputation effects**: Honor/karma/reputation affect NPC interactions
- **Cultural values**: Festivals reflect what society values most
- **Cross-references**: Historical eras → historical-research; locations → world-building
