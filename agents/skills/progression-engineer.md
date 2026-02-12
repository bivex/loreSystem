---
name: loresystem-progression
description: Extract progression entities (skill, perk, trait, attribute, experience, level_up, talent_tree, mastery, progression_event, progression_state) from loreSystem source files into structured JSON.
---

# Progression Engineer

## Purpose

The Progression Engineer extracts character and system progression entities from loreSystem source files, covering skills, perks, attributes, leveling, and advancement systems.

## Entity Types

### Core Progression

- **skill**: Learnable abilities and competencies
- **perk**: Passive bonuses and abilities
- **trait**: Innate character characteristics
- **attribute**: Base stats (strength, intelligence, etc.)
- **experience**: XP gains and sources
- **level_up**: Level advancement milestones
- **talent_tree**: Structured skill/talent hierarchies
- **mastery**: Advanced proficiency levels

### Progression Tracking

- **progression_event**: Events that trigger advancement
- **progression_state**: Saved progression data

## Extraction Process

1. Identify skill names and descriptions
2. Map perk requirements and effects
3. Extract attribute definitions and scaling
4. Document level-up thresholds and rewards
5. Map talent trees and dependencies
6. Note mastery paths and requirements
7. Track progression events and triggers

## Output Format

All entities must conform to the loreSystem entity schema with required fields:
- `entity_type`
- `id`
- `attributes`
- `relationships` (for talent trees and prerequisites)
