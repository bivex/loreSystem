# Gacha Agents Workflow in Loom

## Overview

Loom orchestrates 3 specialized agents to create a complete gacha/loot box system for loreSystem:

1. **Game Mechanics Specialist** — Defines gacha logic, pulls, events
2. **Legendary Items Specialist** — Creates legendary weapons, armor, divine items
3. **Analytics & Balance Specialist** — Analyzes fairness and player experience

## Agent Roles

### 1. Game Mechanics Specialist

**Responsibility:** Design the gacha system architecture and logic.

**Creates:**
- `event` - Gacha pull events (player_initiates_pull, pity_triggered, guaranteed_drop)
- `pull` - Individual pull actions (pull_rare_weapon, pull_legendary_armor)
- `pity` - Pity system configuration (thresholds, guaranteed rarities)
- `phenomenon` - Rare events (god_tier_drop, miracle_summoning)

**Output Format:**
```json
{
  "event": {
    "id": "gacha_pull_event_001",
    "type": "gacha_pull",
    "trigger": "player_clicked_pull_button",
    "player_id": "kira_hero_01",
    "cost": 100
  },
  "pull": {
    "id": "pull_001",
    "pool_type": "weapon",
    "rarity": "legendary",
    "pity_counter": 42,
    "was_guaranteed": false
  },
  "pity": {
    "id": "pity_config_001",
    "threshold": 80,
    "guaranteed_rarity": "divine",
    "current_accumulation": 42
  },
  "phenomenon": {
    "id": "divine_event_001",
    "type": "miracle_summoning",
    "rarity": "divine",
    "global_event": true
  }
}
```

### 2. Legendary Items Specialist

**Responsibility:** Create the actual items that players pull.

**Creates:**
- `legendary_weapon` - Legendary swords, bows, staves
- `mythical_armor` - Epic armor sets
- `divine_item` - God-tier items with permanent buffs
- `cursed_item` - Powerful but cursed items
- `artifact_set` - Multi-item sets with combo bonuses
- `glyph`, `rune`, `socket`, `enchantment` - Item enhancements

**Output Format:**
```json
{
  "legendary_weapon": {
    "id": "blade_of_astraea_001",
    "name": "Blade of Astraea",
    "type": "sword",
    "rarity": "legendary",
    "base_stats": {
      "damage": 250,
      "speed": 1.4
    },
    "special_abilities": ["divine_light_strike", "holy_damage"],
    "lore": "Forged by goddess Astraea during Age of Magic. Only three were ever made.",
    "visual_style": "divine_glow",
    "acquisition_method": "gacha_pull_leg_001"
  },
  "mythical_armor": {
    "id": "shadow_weavers_vestments_001",
    "name": "Shadow Weaver's Vestments",
    "type": "light_armor",
    "rarity": "mythical",
    "base_stats": {
      "defense": 180,
      "weight": 12.0
    },
    "special_effects": ["invisibility_30s", "shadow_meld", "resistance_to_light_magic"],
    "set_bonus": "+20% shadow damage when full set equipped",
    "lore": "Worn by legendary assassin Shadow Weaver. Said to grant true invisibility.",
    "acquisition_method": "gacha_pull_rare_001"
  },
  "divine_item": {
    "id": "astraeas_compass_001",
    "name": "Astraea's Compass",
    "type": "accessory",
    "rarity": "divine",
    "effect": "Always shows true north, reveals invisible enemies within 50m",
    "passive_blessing": "+30% resistance to all curses",
    "lore": "Blessed by goddess herself to guide the worthy.",
    "blessing_strength": "permanent_god_gift",
    "acquisition_method": "gacha_guaranteed_divine_pity_001"
  },
  "cursed_item": {
    "id": "sword_of_betrayed_001",
    "name": "Sword of Betrayed",
    "type": "greatsword",
    "rarity": "cursed_legendary",
    "base_stats": {
      "damage": 300,
      "bonus": "+50% damage vs undead"
    },
    "curse_effect": "Drains 1 HP per second, cannot be unequipped, whispers betrayal",
    "lift_curse_method": "complete_redeemer_quest",
    "lore": "Forged by a betrayed knight. Seeks revenge on all living things.",
    "acquisition_method": "gacha_pull_cursed_rare_001"
  }
}
```

### 3. Analytics & Balance Specialist

**Responsibility:** Analyze player data and adjust gacha balance.

**Creates:**
- `player_metric` - Tracks pulls, costs, satisfaction
- `heatmap` - Pull frequency maps (which pools, which times)
- `drop_rate` - Actual vs expected drop rates
- `conversion_rate` - Free-to-paid player conversion
- `difficulty_curve` - Gacha difficulty scaling over time
- `balance_entities` - Global balance parameters

**Output Format:**
```json
{
  "player_metric": {
    "id": "player_experience_001",
    "player_id": "kira_hero_01",
    "type": "gacha_satisfaction",
    "metric_name": "pulls_to_guaranteed",
    "value": 73.5,
    "measurement": "average pulls to get guaranteed divine drop"
  },
  "heatmap": {
    "id": "gacha_heatmap_001",
    "type": "pull_frequency",
    "data_points": {
      "weapon_pool": 1500_pulls_total",
      "armor_pool": 1200_pulls_total",
      "peak_hours": ["18:00", "20:00"],
      "off_peak_hours": ["02:00", "06:00"]
    },
    "visualization": {
      "x_axis": "time_of_day",
      "y_axis": "pulls_per_hour",
      "intensity": "number_of_pulls"
    }
  },
  "drop_rate": {
    "id": "divine_drop_rate_analysis",
    "pool_type": "weapon_pool",
    "rarity": "divine",
    "actual_drop_rate": 0.51,  # 0.51% of pulls
    "expected_drop_rate": 0.50,  # 0.50% based on weights
    "deviation": "+0.01%",  # Slightly higher than expected
    "status": "balanced"
  },
  "conversion_rate": {
    "id": "f2p_conversion",
    "funnel": {
      "free_players": 50000,
      "trial_users": 8000,
      "paid_conversions": 1200
    },
    "percentages": {
      "free_to_trial": 0.16,
      "trial_to_paid": 0.15,
      "free_to_paid": 0.024
    },
    "time_to_conversion": 14,
    "average_ltv": 8.50
  },
  "difficulty_curve": {
    "id": "gacha_difficulty_scaling",
    "data_points": [
      {"days_since_launch": 1, "pull_cost": 100},
      {"days_since_launch": 30, "pull_cost": 100},
      {"days_since_launch": 60, "pull_cost": 120},
      {"days_since_launch": 90, "pull_cost": 150}
    ],
    "curve_fit": "exponential",
    "formula": "cost = 100 * 1.005^(days)",
    "rationale": "Gacha gets more expensive over time to maintain revenue"
  },
  "balance_entities": {
    "id": "global_gacha_balance",
    "parameters": {
      "pity_threshold": 80,
      "divine_rate": 0.005,
      "legendary_rate": 0.025,
      "cost_efficiency_target": 50,
      "player_satisfaction_target": 75
    },
    "current_state": {
      "pity_threshold": 80,
      "divine_rate": 0.005,
      "legendary_rate": 0.025,
      "cost_efficiency": 48,
      "player_satisfaction": 72
    },
    "status": "within_target_range"
  }
}
```

## Loom Orchestration Flow

```
Chapter Text Input
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 1. PARSE CHAPTER                                                 │
│    - Extract gacha references (pulls, pools, currencies)        │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. PARALLEL AGENT EXECUTION (3 agents)                         │
│    ├─ Game Mechanics Specialist → entities/mechanics.json        │
│    ├─ Legendary Items Specialist → entities/legendary.json         │
│    └─ Analytics & Balance Specialist → entities/analytics.json     │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. VALIDATION                                                   │
│    - Validate gacha logic consistency                              │
│    - Verify item rarity and stats                                 │
│    - Check balance metrics and player experience                    │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. PERSIST TO SQLITE                                            │
│    - Insert gacha events, pulls, pity state, items             │
│    - Insert player metrics, heatmaps, analytics                    │
│    - Store balance configuration and parameters                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Entity Coverage

| Agent | Creates | Entity Types | Count |
|--------|----------|--------------|-------|
| Game Mechanics Specialist | Gacha logic | event, pull, pity, phenomenonon | 13 |
| Legendary Items Specialist | Gacha rewards | legendary_weapon, mythical_armor, divine_item, cursed_item, artifact_set, glyph, rune, socket, enchantment | 10 |
| Analytics & Balance Specialist | Gacha metrics | player_metric, heatmap, drop_rate, conversion_rate, difficulty_curve, balance_entities | 8 |
| **TOTAL** | **Gacha system** | **31 entities** |

## Usage

```bash
cd /root/clawd
loom init doc/plans/narrative-to-entities.md
loom run --max-parallel 30  # Including gacha agents
```

## Output Files

```
entities/
├── mechanis.json          # 13 entities (gacha logic)
├── legendary.json          # 10 entities (gacha rewards)
└── analytics.json          # 8 entities (gacha metrics)
```

## Key Benefits

- **Parallel Processing**: 3 agents work simultaneously
- **Consistency**: All gacha entities reference each other (pulls → items)
- **Fairness**: Analytics agent monitors and adjusts balance
- **Player Experience**: Metrics track satisfaction and frustration
- **Pity System**: Game Mechanics agent prevents bad luck streaks
- **Rich Rewards**: Legendary Items agent creates compelling, lore-rich items

## Documentation

- **Mechanics** - See `docs/GACHA_MECHANICS.md` for full gacha system details
- **Agents** - See `docs/GACHA_AGENTS.md` for agent workflow (this file)
- **Integration** - See `docs/LOOM_GACHA_WORKFLOW.md` for Loom orchestration

This architecture ensures loreSystem's gacha system is fair, engaging, and properly integrated with the rest of the game world.
