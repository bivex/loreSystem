# environmental-design

Domain skill for environmental-scientist subagent. Specific extraction rules and expertise.

## Trigger Phrases

Invoke this subagent when you hear:
- "extract environmental entities"
- "analyze weather and atmosphere"
- "identify lighting and time periods"
- "environmental conditions"
- "weather patterns and disasters"

## Domain Expertise

- **Climate systems**: Biomes, weather patterns, seasonal changes, meteorological phenomena
- **Atmosphere**: Air quality, pressure, composition, fog, mist, haze
- **Lighting**: Day/night cycles, ambient light, shadows, color temperature
- **Time**: Time of day (dawn, noon, dusk, night), seasons, epochs
- **Disasters**: Storms, floods, earthquakes, cataclysms, natural disasters

## Entity Types (6 total)

- **environment** - General environmental settings, biome classifications
- **weather_pattern** - Weather systems, meteorological conditions
- **atmosphere** - Atmospheric conditions, air quality, pressure
- **lighting** - Lighting conditions, illumination levels
- **time_period** - Time of day, seasonal contexts
- **disaster** - Natural disasters, catastrophic events

## Processing Guidelines

When extracting environmental entities from chapter text:

1. **Identify environmental conditions**:
   - Weather descriptions (rain, snow, clear sky, storm clouds)
   - Time of day (dawn, noon, dusk, midnight)
   - Season (winter, summer, autumn, spring)
   - Atmosphere (foggy, oppressive, peaceful, tense)

2. **Extract environmental details**:
   - Weather intensity and duration (light rain, torrential downpour)
   - Lighting conditions (bright daylight, dim twilight, pitch black night)
   - Temperature (freezing cold, sweltering hot, temperate)
   - Unusual events (approaching storms, natural disasters)

3. **Track environmental changes**:
   - Weather shifts (clear sky turning stormy)
   - Time progression (dawn to dusk transitions)
   - Seasonal context (winter snows, summer heat)
   - Atmospheric pressure changes (calm before storm)

4. **Contextualize environment**:
   - How environment affects mood and atmosphere
   - Environmental symbolism (storms = turmoil, dawn = new beginning)
   - Consistency of weather (no instant changes without cause)
   - Environment's narrative function

## Output Format

Generate `entities/environment.json` with schema-compliant entities following this structure:
```json
{
  "weather_pattern": {
    "id": "uuid",
    "name": "Eldorian Rain",
    "type": "rain",
    "intensity": "moderate",
    "duration": "several hours"
  },
  "atmosphere": {
    "id": "uuid",
    "name": "Morning Mist",
    "type": "foggy",
    "visibility": "reduced",
    "pressure": "low"
  },
  "lighting": {
    "id": "uuid",
    "name": "Dawn Light",
    "type": "natural",
    "intensity": "rising",
    "color": "golden"
  },
  "time_period": {
    "id": "uuid",
    "name": "Early Morning",
    "time_of_day": "dawn",
    "season": "spring"
  }
}
```

## Key Considerations

- **Mood impact**: Environment affects narrative tone and emotional atmosphere
- **Narrative function**: Weather often mirrors or contrasts story events (pathetic fallacy)
- **Consistency**: Weather doesn't change instantly without narrative cause
- **Symbolism**: Storms represent turmoil, dawn represents new beginning, etc.
- **Temporal flow**: Track time progression and environmental changes
- **Sensory details**: Include temperature, visibility, and atmospheric qualities

## Example

**Input:**
> "Dawn broke over Eldoria. The mist clung to the forest floor, reducing visibility to a few feet. Golden light filtered through the canopy. It was cold, the air crisp with the promise of spring. Above, clouds gathered—storm was coming."

**Extract:**
```json
{
  "time_period": {
    "id": "uuid",
    "name": "Early Morning",
    "time_of_day": "dawn",
    "season": "spring",
    "description": "Dawn breaking over Eldoria"
  },
  "atmosphere": {
    "id": "uuid",
    "name": "Morning Mist",
    "type": "fog",
    "visibility": "reduced",
    "description": "Mist clung to forest floor, reducing visibility to a few feet"
  },
  "lighting": {
    "id": "uuid",
    "name": "Golden Dawn Light",
    "type": "natural",
    "intensity": "rising",
    "color": "golden",
    "description": "Golden light filtered through the canopy"
  },
  "weather_pattern": {
    "id": "uuid",
    "name": "Approaching Storm",
    "type": "storm",
    "status": "gathering",
    "description": "Clouds gathered above, storm approaching"
  },
  "environment": {
    "id": "uuid",
    "name": "Spring Forest",
    "type": "forest",
    "temperature": "cold",
    "description": "Crisp spring air, forest setting"
  }
}
```
