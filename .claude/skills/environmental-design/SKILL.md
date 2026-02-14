---
name: environmental-design
description: Extract environmental entities from narrative text. Use when analyzing weather, atmosphere, lighting, time periods, natural disasters, cataclysms, plagues, and world events.
---
# environmental-design

Domain skill for environmental conditions and events extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `environment` | General environmental setting or biome |
| `weather_pattern` | Weather system or meteorological condition |
| `atmosphere` | Atmospheric condition (fog, pressure, air quality) |
| `lighting` | Lighting condition (natural or magical) |
| `time_period` | Time of day or seasonal context |
| `disaster` | Natural disaster (storm, flood, earthquake) |
| `cataclysm` | Major catastrophic event |
| `world_event` | Significant world-scale event |
| `seasonal_event` | Recurring seasonal occurrence |
| `plague` | Disease outbreak or epidemic |

## Domain Constraints

- `time_of_day`: day, night, dawn, dusk
- `weather`: clear, rainy, stormy, foggy
- `lighting`: bright, dim, dark, magical

## Extraction Rules

1. **Weather**: Rain, snow, storms, clear sky — note intensity and duration
2. **Time**: Dawn, noon, dusk, midnight — track progression through text
3. **Atmosphere**: Fog, oppressive heat, crisp air — sensory details
4. **Disasters**: Storms, floods, earthquakes — scale, impact, duration
5. **World events**: Wars, plagues, seasonal celebrations — scope and significance

## Output Format

Write to `entities/world.json` (world-team file):

```json
{
  "weather_pattern": [
    {
      "id": "uuid",
      "name": "Approaching Storm",
      "description": "Dark clouds gathering from the north, storm imminent",
      "type": "storm",
      "intensity": "severe"
    }
  ],
  "time_period": [
    {
      "id": "uuid",
      "name": "Early Morning",
      "description": "Dawn breaking, golden light through canopy",
      "time_of_day": "dawn",
      "season": "spring"
    }
  ],
  "cross_references": [],
  "_metadata": { "source": "...", "skill": "environmental-design", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Mood impact**: Environment affects narrative tone (storms = tension, dawn = hope)
- **Narrative function**: Weather often mirrors story events (pathetic fallacy)
- **Temporal flow**: Track time progression and environmental changes through text
- **Cross-references**: Locations where events occur → cross_references to world-building
