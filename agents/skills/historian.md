---
name: loresystem-historical
description: Extract historical entities (era, era_transition, timeline, calendar, festival, celebration, ceremony, exhibition, tournament, competition) from loreSystem source files into structured JSON.
---

# Historian

## Purpose

The Historian extracts historical and temporal entities from loreSystem source files, covering eras, timelines, calendars, and cultural events.

## Entity Types

### Time Structures

- **era**: Major historical periods
- **era_transition**: Periods of change between eras
- **timeline**: Sequential event chains
- **calendar**: Timekeeping systems and definitions

### Cultural Events

- **festival**: Recurring cultural celebrations
- **celebration**: Special occasions and festivities
- **ceremony**: Ritual or formal events
- **exhibition**: Display events (artifacts, art)
- **tournament**: Competitive events
- **competition**: Contests and challenges

## Extraction Process

1. Identify era names and time periods
2. Extract timeline information and dates
3. Document calendar systems (months, years, cycles)
4. Extract festival and celebration details
5. Note ceremony types and purposes
6. Document tournaments and competitions
7. Map historical transitions and causes

## Output Format

All entities must conform to the loreSystem entity schema with required fields:
- `entity_type`
- `id`
- `attributes`
- `relationships` (for era transitions and timeline sequences)
