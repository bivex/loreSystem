---
name: loresystem-character
description: Extract character entities (character, character_evolution, character_profile_entry, character_relationship, character_variant, voice_actor, motion_capture) from loreSystem source files into structured JSON.
---

# Character Architect

## Purpose

The Character Architect extracts character-related entities from loreSystem source files, including character definitions, their evolution throughout the narrative, relationships, variants, and production metadata.

## Entity Types

### Core Character Entities

- **character**: Base character definition with name, description, role
- **character_evolution**: How a character changes over time/stories
- **character_profile_entry**: Detailed character attribute entries
- **character_relationship**: Connections between characters (allies, enemies, family, romance)
- **character_variant**: Alternate versions of a character (different timelines, transformations)
- **voice_actor**: Voice talent assigned to characters
- **motion_capture**: Performance capture data for character animations

## Extraction Process

1. Identify all named characters in source content
2. Extract character attributes (name, role, personality, appearance)
3. Map character relationships and connections
4. Track character evolution across story points
5. Note any variants or alternate versions
6. Extract production metadata (voice actors, mocap references)

## Output Format

All entities must conform to the loreSystem entity schema with required fields:
- `entity_type`
- `id`
- `attributes`
- `relationships` (for character relationships)
