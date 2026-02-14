---
name: progression-design
description: Extract progression entities from narrative text. Use when analyzing skills, perks, attributes, experience, level-ups, talent trees, mastery systems, and character advancement.
---
# progression-design

Domain skill for progression-engineer subagent. Specific extraction rules and expertise.

## Domain Expertise

- **RPG progression**: Levels, XP, skill points, talent trees, character advancement
- **Attributes**: Core stats (STR, DEX, INT), derived stats, stat scaling
- **Skills**: Active abilities, passive perks, character traits, talent specializations
- **Balance**: Progression curves, diminishing returns, power spikes, advancement pacing
- **Mastery systems**: Specialization paths, expertise levels, skill trees

## Entity Types (10 total)

- **skill** - Character abilities, active powers, combat techniques
- **perk** - Passive bonuses, innate advantages, automatic benefits
- **trait** - Character traits, personality attributes, inherent qualities
- **attribute** - Core stats (STR, DEX, INT, etc.), derived statistics
- **experience** - XP tracking, advancement points, progression currency
- **level_up** - Level thresholds, advancement milestones, power increases
- **talent_tree** - Skill trees, specialization paths, ability trees
- **mastery** - Mastery levels, expertise tiers, skill proficiency
- **progression_event** - Specific progression moments, advancement events
- **progression_state** - Current progression status, character advancement state

## Processing Guidelines

When extracting progression entities from chapter text:

1. **Identify progression elements**:
   - Level mentions or milestones (level 5, reached a new tier)
   - Skill/ability unlocks (learned a new technique)
   - Stat improvements or changes (stronger, faster, smarter)
   - Training or learning moments (completed training, mastered something)

2. **Extract progression details**:
   - What characters can do now vs before (new capabilities)
   - New abilities or power levels (strength increases)
   - Attribute changes (agility increased, intelligence boosted)
   - Talent trees or specializations mentioned (skill paths)

3. **Track progression events**:
   - Level up moments (Kira reached level 15)
   - Skill unlocks (learned Shadow Strike)
   - Training completions (mastered the elder's teachings)
   - Mastery achievements (expertise in shadow arts)

4. **Contextualize progression**:
   - Which character is progressing
   - What triggered the advancement
   - How the progression affects capabilities
   - Multiple characters (track all, not just protagonist)

## Output Format

Generate `entities/progression.json` with schema-compliant entities following this structure:
```json
{
  "skill": {
    "id": "uuid",
    "name": "Shadow Strike",
    "type": "active",
    "description": "Deal 200% damage from stealth",
    "prerequisite": "stealth_level_5"
  },
  "perk": {
    "id": "uuid",
    "name": "Eagle Eye",
    "type": "passive",
    "effect": "+50% detection range"
  },
  "attribute": {
    "id": "uuid",
    "character_id": "...",
    "name": "agility",
    "current_value": 75,
    "max_value": 100
  },
  "progression_event": {
    "id": "uuid",
    "character_id": "...",
    "type": "level_up",
    "description": "Kira reached level 15",
    "timestamp": "chapter_7"
  }
}
```

## Key Considerations

- **Implicit progression**: Characters getting stronger may be implied, not explicitly stated
- **Skill trees**: Look for mentioned or implied specialization paths
- **Balance**: Progression should feel earned through training/experience, not arbitrary
- **Multiple characters**: Track progression for all characters in the scene, not just the protagonist
- **Training context**: Progression often follows training, practice, or revelation

## Example

**Input:**
> "Kira felt different. The training had paid off. She could now move faster, see further. The elder's teachings about shadow arts had unlocked something within her—she could strike from darkness like never before."

**Extract:**
```json
{
  "progression_event": {
    "id": "uuid",
    "character_id": "kira",
    "type": "training_complete",
    "description": "Kira completed the elder's training"
  },
  "attribute": {
    "id": "uuid",
    "character_id": "kira",
    "name": "agility",
    "current_value": "increased",
    "description": "Can now move faster"
  },
  "attribute": {
    "id": "uuid",
    "character_id": "kira",
    "name": "perception",
    "current_value": "increased",
    "description": "Can now see further"
  },
  "skill": {
    "id": "uuid",
    "character_id": "kira",
    "name": "Shadow Strike",
    "type": "active",
    "description": "Strike from darkness with enhanced power"
  },
  "mastery": {
    "id": "uuid",
    "character_id": "kira",
    "name": "Shadow Arts",
    "level": "unlocked",
    "description": "Elder's teachings unlocked shadow arts potential"
  }
}
```
