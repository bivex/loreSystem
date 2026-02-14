---
name: quest-design
description: Extract quest entities from narrative text. Use when analyzing quest chains, objectives, moral choices, prerequisites, rewards, quest givers, and branching quest structures.
---
# quest-design

Domain skill for quest structure extraction.

## Entity Types

| Type | Description |
|------|-------------|
| `quest` | Main quest container |
| `quest_chain` | Sequence of linked quests |
| `quest_node` | Individual step within a quest chain |
| `quest_giver` | NPC who assigns the quest |
| `quest_objective` | Specific goal within a quest |
| `quest_prerequisite` | Requirement to start a quest |
| `quest_reward_tier` | Reward tier or level for completion |
| `quest_tracker` | Progress tracking state |
| `moral_choice` | Player moral decision point |

## Domain Constraints

- `quest.status`: active, completed, failed, cancelled
- `objective.type`: kill, collect, interact, deliver, escort, defend, explore, talk, craft, use
- `objective.status`: not_started, in_progress, completed, failed
- `prerequisite.type`: level, quest, item, skill, location, reputation, custom

## Output Format

Write to `entities/narrative.json` (narrative-team file):

```json
{
  "quest": [
    {
      "id": "uuid",
      "name": "Find Lost Brother",
      "description": "Kira must find her missing brother near the Ancient Ruins",
      "type": "main",
      "status": "active"
    }
  ],
  "quest_objective": [
    {
      "id": "uuid",
      "name": "Speak to village elder",
      "description": "Ask Elder Theron about the brother's last known location",
      "quest_id": "quest-uuid",
      "type": "talk",
      "status": "not_started"
    }
  ],
  "cross_references": [
    {
      "source_type": "quest",
      "source_id": "quest-uuid",
      "target_type": "location",
      "target_skill": "world-building",
      "target_hint": "Ancient Ruins — quest destination"
    }
  ],
  "_metadata": { "source": "...", "skill": "quest-design", "extracted_at": "...", "entity_count": 2 }
}
```

## Key Considerations

- **Implicit quests**: Some objectives are implied, not explicitly stated
- **Moral ambiguity**: Not all choices are clearly good/bad
- **Cross-references**: Characters, locations, items mentioned in quests → cross_references to their owning skills
