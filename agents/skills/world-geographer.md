---
name: loresystem-world
description: Extract location entities (location, hub_area, instance, dungeon, raid, arena, open_world_zone, underground, skybox, dimension, pocket_dimension) from loreSystem source files into structured JSON.
---

# World Geographer

## Purpose

The World Geographer extracts location and world-space entities from loreSystem source files, covering all types of locations from dungeons to entire dimensions.

## Entity Types

### General Locations

- **location**: Base location entity
- **hub_area**: Central gathering areas (cities, towns, safe zones)
- **instance**: Instanced content areas
- **dungeon**: Private exploration/instanced content
- **raid**: Large group content areas
- **arena**: PvP or competitive spaces

### World Spaces

- **open_world_zone**: Freely explorable regions
- **underground**: Caves, tunnels, subterranean areas
- **skybox**: Sky/atmospheric rendering definitions
- **dimension**: Alternate planes of existence
- **pocket_dimension**: Small contained spaces

## Extraction Process

1. Identify named locations in source content
2. Categorize locations by type
3. Extract location attributes (climate, size, population)
4. Map connections between locations
5. Note instance/entrance/exit points
6. Document environmental features
7. Track dimension and portal connections

## Output Format

All entities must conform to the loreSystem entity schema with required fields:
- `entity_type`
- `id`
- `attributes`
- `relationships` (for location connections and containment)
