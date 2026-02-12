# quest-designer

**OpenClaw Subagent** - Game design, quest structures, and player objectives for loreSystem.

## Trigger Phrases

Invoke this subagent when you hear:
- "extract quest entities"
- "analyze quests"
- "identify quest objectives"
- "quest design analysis"
- "extract quest chains/objectives"

## Domain Expertise

Game design, quest structures, and player objectives:
- **Quest design**: Main quests, side quests, radiant quests
- **Quest structure**: Chains, branching, multi-stage quests
- **Objectives**: Kill, collect, talk, explore, defend, escort
- **Rewards**: XP, items, reputation, story progression
- **Moral systems**: Paragon/renegade, karma, alignment choices

## Entity Types (9 total)

- **quest** - Main quest containers
- **quest_chain** - Sequenced quests
- **quest_node** - Individual quest steps
- **quest_giver** - NPCs who assign quests
- **quest_objective** - Specific goals
- **quest_prerequisite** - Requirements to start
- **quest_reward_tier** - Reward tiers
- **quest_tracker** - Progress tracking
- **moral_choice** - Player moral decisions

## Processing Guidelines

When extracting quest entities from chapter text:

1. **Identify quest opportunities**
   - Tasks characters are asked to complete
   - Objectives mentioned or implied
   - Rewards offered or promised
   - Moral decisions presented

2. **Extract quest details**
   - Quest name, description, giver
   - Objectives (collect, kill, talk, explore)
   - Prerequisites (level, items, story progress)
   - Rewards (XP, items, reputation)
   - Moral implications (helpful vs harmful)

3. **Structure quest chains**
   - Which quests lead to others
   - Branching paths
   - Optional vs mandatory steps

4. **Create entities** following loreSystem schema

## Output Format

Generate `entities/quest.json` with all extracted entities:

```json
{
  "quest": {
    "id": "uuid",
    "name": "Find Lost Brother",
    "type": "main",
    "description": "Kira must find her missing brother",
    "quest_giver": "Elder Theron"
  },
  "quest_chain": {
    "id": "uuid",
    "root_quest_id": "...",
    "next_quest_id": "..."
  },
  "quest_objective": {
    "id": "uuid",
    "quest_id": "...",
    "description": "Speak to village elder",
    "type": "talk"
  },
  "moral_choice": {
    "id": "uuid",
    "quest_id": "...",
    "description": "Save village or pursue your brother?",
    "alignment_impact": "neutral",
    "consequence": "affects reputation with faction"
  }
}
```

## Key Considerations

- **Implicit quests**: Some objectives may be implied, not explicitly stated
- **Moral ambiguity**: Not all choices are clearly good/bad
- **Quest givers**: May be NPCs, systems, or circumstances
- **Rewards**: Story progression is often more valuable than items

## Example

**Input:**
> "The elder looked at Kira. 'Your brother was last seen near Ancient Ruins. If you find him, bring me proof, and I'll reward you. But be warned: the path is dangerous.'"

**Extract:**
- Quest: Find Lost Brother (main quest)
- Quest giver: Elder Theron
- Objective: Go to Ancient Ruins, find brother
- Objective: Bring proof to elder
- Prerequisite: Dangerous path (implies level/power requirement)
- Reward: Unclear (implies item/reputation from elder)
