---
name: character-design
description: Extract character entities from narrative text. Use when analyzing characters, relationships, psychology, development arcs, voice/mocap data, and character variants.
---
# character-design

Domain skill for character-architect subagent. Specific extraction rules and expertise.

## Domain Expertise

Character psychology, development, and relationships:
- **Character psychology**: Motivations, fears, desires, personality traits
- **Character development**: Growth arcs, transformation, redemption
- **Relationships**: Friends, rivals, family, romantic, allies, enemies
- **Voice/performance**: Voice acting, mannerisms, physicality
- **Character variants**: Alternate timelines, versions, appearances

## Entity Types (7 total)

- **character** - Main character entities
- **character_evolution** - Character development arcs
- **character_profile_entry** - Character details/backstory
- **character_relationship** - Relationships between characters
- **character_variant** - Alternate versions/iterations
- **voice_actor** - Voice acting information
- **motion_capture** - Motion capture data

## Processing Guidelines

When extracting character entities from chapter text:

1. **Identify characters**
   - Named characters with dialogue or actions
   - Referred-to characters (mentioned by others)
   - Character archetypes or groups

2. **Extract character details**
   - Name, role, status, location
   - Personality traits, motivations, goals
   - Relationships with other characters
   - Voice/performance cues (if applicable)

3. **Track character development**
   - Growth moments, realizations, decisions
   - Changes in motivation or worldview
   - New relationships or broken bonds

4. **Create entities** following loreSystem schema

## Output Format

Generate `entities/character.json` with all extracted entities:

```json
{
  "character": {
    "id": "uuid",
    "name": "Kira",
    "role": "protagonist",
    "personality": ["brave", "curious", "stubborn"],
    "motivation": "Find her missing brother"
  },
  "character_evolution": {
    "id": "uuid",
    "character_id": "...",
    "stage": "awakening",
    "description": "Realizes her journey has just begun"
  },
  "character_relationship": {
    "id": "uuid",
    "character_a_id": "...",
    "character_b_id": "...",
    "type": "friend",
    "strength": "strong"
  }
}
```

## Key Considerations

- **Uniqueness**: Each character has unique ID (name variations reference same ID)
- **Relationships**: Capture both explicit and implicit relationships
- **Development**: Track incremental changes, not just major turning points
- **Voice/performance**: Only include if text contains relevant details

## Example

**Input:**
> "Kira looked at Marcus. 'You've always been there for me,' she whispered. He smiled. The hesitation in her voice was gone now. She knew what she had to do."

**Extract:**
- Character: Kira (growth, confidence)
- Character: Marcus (supportive ally)
- Relationship: Kira-Marcus (friend, strong bond)
- Evolution: Kira's confidence/hesitation resolved
