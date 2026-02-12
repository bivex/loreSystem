---
name: loresystem-environment
description: Extract environmental entities (environment, weather_pattern, atmosphere, lighting, time_period, disaster) from loreSystem source files into structured JSON.
---

# Environmental Scientist

## Purpose

The Environmental Scientist extracts environmental and atmospheric entities from loreSystem source files, covering weather, lighting, time, and natural disasters.

## Entity Types

### Environmental Conditions

- **environment**: General environmental state definitions
- **weather_pattern**: Weather systems and conditions (rain, snow, storm)
- **atmosphere**: Atmospheric composition and properties
- **lighting**: Lighting conditions and setups

### Temporal Events

- **time_period**: Time-based environmental states (day, night, seasons)
- **disaster**: Natural disaster events and effects

## Extraction Process

1. Identify environmental descriptions in source content
2. Extract weather patterns and conditions
3. Document atmospheric properties (fog, haze, air quality)
4. Note lighting configurations (natural, artificial)
5. Track time periods and cyclical changes
6. Extract disaster events and their effects
7. Map environmental transitions and triggers

## Output Format

All entities must conform to the loreSystem entity schema with required fields:
- `entity_type`
- `id`
- `attributes`
- `relationships` (for environmental transitions)
