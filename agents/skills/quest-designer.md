---
name: loresystem-quest
description: Extract quest entities (quest, quest_chain, quest_node, quest_giver, quest_objective, quest_prerequisite, quest_reward_tier, quest_tracker, moral_choice) from loreSystem source files into structured JSON.
---

# Quest Designer

## Purpose

The Quest Designer extracts quest and mission-related entities from loreSystem source files, including complete quest structures, chains, objectives, rewards, and moral decision points.

## Entity Types

### Quest Structure

- **quest**: Individual quest/mission definition
- **quest_chain**: Linked sequences of quests
- **quest_node**: Individual steps within a quest

### Quest Elements

- **quest_giver**: NPC or entity that assigns quests
- **quest_objective**: Specific goals or tasks within quests
- **quest_prerequisite**: Requirements to start or complete quests

### Rewards and Tracking

- **quest_reward_tier**: Reward levels based on completion criteria
- **quest_tracker**: Progress tracking for multi-stage quests

### Choices

- **moral_choice**: Decision points with ethical consequences

## Extraction Process

1. Identify quest names and descriptions in source content
2. Map quest chains and sequential dependencies
3. Extract objectives and completion criteria
4. Identify quest givers and related NPCs
5. Note prerequisites and conditions
6. Extract reward information
7. Document moral choices and their consequences

## Output Format

All entities must conform to the loreSystem entity schema with required fields:
- `entity_type`
- `id`
- `attributes`
- `relationships` (for quest chains and prerequisites)
