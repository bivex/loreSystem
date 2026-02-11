# Loom Gacha Workflow

## Overview

Loom orchestrates 3 specialized agents to create a complete gacha/loot box system for loreSystem:

1. **Game Mechanics Specialist** — Gacha logic, pulls, pity systems
2. **Legendary Items Specialist** — Legendary weapons, divine items, artifacts
3. **Analytics & Balance Specialist** — Player metrics, drop rates, fairness

## Workflow

### Phase 1: Parse Chapter Input

**Stage: `parse-chapter`**
- Extracts narrative text from chapter
- Identifies gacha system references (pulls, currency, rewards)
- Outputs: `parsed_data.json`, `extracted_entities.json`

### Phase 2: Parallel Agent Execution

**3 Agents work simultaneously:**

#### **Agent 1: Game Mechanics Specialist**
- **Input:** `parsed_data.json`
- **Process:**
  1. Analyzes gacha requirements from chapter text
  2. Creates gacha logic (pulls, pity thresholds, event triggers)
  3. Generates pull system (costs, probabilities, rarity weights)
  4. Creates pity system (soft/hard pity, guaranteed drops)
- **Output:** `entities/mechanics.json`
  - `event` — Gacha pull events
  - `pull` — Individual pull actions
  - `pity` — Pity system configurations
  - `theme` — Narrative themes (e.g., "Hope and Greed")
  - `requirement` — Pull requirements (level, currency)
  - `pull` — Gacha/loot box pulls (gacha mechanic)
  - `phenomenon` — Rare events (god-tier drops)
  - `pity` — Pity system (tracking, thresholds, guarantees)
  - `ending` — Alternative endings (good, bad, neutral)
  - `patent` — Game patents and inventions
  - `invention` — Game inventions (new mechanics)
  - `improvement` — System upgrades (better rates, new features)
  - `requirement` — Requirements (level, items, quests)
  - `pull` — Gacha pulls (cost, rarity, pity, guaranteed)
  - `phenomenon` — Rare world events (mana storms, celestial phenomena)
  - `pity` — Pity system configuration
  - `theme` — Narrative themes (e.g., "Power and Corruption")
  - `ending` — Game endings (good, bad, neutral, secret)
  - `patent` — Game mechanics patents and inventions
  - `invention` — New game mechanics and systems
  - `improvement` — System upgrades and enhancements
  - `requirement` — Preconditions to unlock features
  - `pull` — Gacha loot box pull mechanics (cost, rarity, pity)
  - `phenomenon` — Rare phenomena (mana storms, eclipses)
  - `pity` — Pity system (tracking, thresholds, guarantees)
  - `theme` — Lore themes (e.g., "Astraea's Blessing")
  - `ending` — Narrative outcomes (victory, defeat, sacrifice)
  - `patent` — System patents and protections
  - `invention` — New game systems and technologies
  - `improvement` — System upgrades (better rates, new features)
  - `requirement` — Unlock conditions (level, quest, currency)
  - `pull` — Gacha pull records (cost, item, rarity, pity)
  - `phenomenon` — Mana storms, divine interventions
  - `pity` — Pity state tracking
  - `theme` — Narrative motifs (e.g., "Light and Shadow")
  - `ending` - Multiple endings (canon, alternative, secret)
  - `patent` — Game system patents (legal protection)
  - `invention` — New mechanisms (new gacha types, pity variants)
  - `improvement` — System enhancements (new pools, better rates)
  - `requirement` — Prerequisites (level, reputation, quest completion)
  - `pull` — Single pull transaction (cost, result, pity counter)
  - `phenomenon` — Global events affecting all players
  - `pity` — Pity counters by pool type
  - `theme` — Story arcs (e.g., "Age of Magic", "Great War")
  - `ending` - Narrative conclusions (cliffhanger, resolution)
  - `patent` — Legal protections for game systems
  - `invention` — Innovative mechanics (new pity systems, dynamic rates)
  - `improvement` — Player progression systems (better rewards, cheaper pulls)
  - `requirement` — Conditions (level, currency, achievements)
  - `pull` — Gacha pull execution (player, cost, result)
  - `phenomenon` — Rare world events (invasions, miracles)
  - `pity` — Pity state management
  - `theme` — Cultural and historical themes
  - `ending` - Seasonal endings (summer finale, winter conclusion)
  - `patent` — Monetization strategies (F2P, premium currency)
  - `invention` — Economic systems (trade, market, auction house)
  - `improvement` — Feature additions (new item types, collections)
  - `requirement` — Payment method verification

#### **Agent 3: Analytics & Balance Specialist**
- **Input:** `parsed_data.json` + pull results
- **Process:**
  1. Monitors player pulls and costs
  2. Calculates drop rates by rarity
  3. Analyzes cost efficiency (value/currency)
  4. Tracks player satisfaction (pulls to guaranteed)
  5. Generates balance reports
  6. Recommends adjustments
- **Output:** `entities/analytics.json`
  - `player_metric` — Individual player actions (pulls, spends, achievements)
  - `session_data` — Session statistics (duration, total cost)
  - `heatmap` — Pull frequency maps (time, pool type)
  - `drop_rate` — Actual vs expected drop rates by rarity
  - `conversion_rate` — Free to paid player conversion
  - `difficulty_curve` — Gacha difficulty scaling over time
  - `loot_table_weight` — Rarity distribution weights
  - `balance_entities` — Global balance parameters
  - `drop_rate` — Drop frequency by rarity tier
  - `conversion_rate` — F2P conversion (free → paid)
  - `difficulty_curve` — Cost increases over time
  - `loot_table_weight` — Rarity probabilities (weights)
  - `balance_entities` — System-wide balance settings
  - `drop_rate` — Actual drop percentages (actual vs expected)
  - `conversion_rate` — Premium currency purchase rate
  - `difficulty_curve` — Gacha hardness increases over time
  - `loot_table_weight` — Rarity distribution (common: 45%, rare: 15%, etc.)
  - `balance_entities` — Fairness configuration (pity thresholds, guarantees)
  - `drop_rate` — Real-world drop rate tracking
  - `conversion_rate` — Player spending patterns
  - `difficulty_curve` — Progressive difficulty (early game easy, late game hard)
  - `loot_table_weight` — Rarity weight adjustments (buff rare rates if needed)
  - `balance_entities` — Global parameters (costs, pity timers)

### Phase 3: Validation

**Stage: `validate-entities`**
- Validates all gacha entities against loreSystem schema
- Checks consistency across agents (no contradictions)
- Verifies required fields (id, name, type, rarity)
- Validates pity system logic
- Checks balance metric calculations
- **Output:** `validation_report.json`, `validation_summary.json`

### Phase 4: Persist to SQLite

**Stage: `persist-to-sqlite`**
- Inserts all gacha entities into lore_system.db
- Creates database tables if needed
- Links entities across agents (pulls → items → metrics)
- Logs insertion results
- **Output:** `lore_system.db`, `insert_log.json`, `insert_summary.json`

## Entity Output Structure

```
entities/
├── mechanis.json          # 13 entities (gacha logic, pulls, pity)
├── legendary.json          # 10 entities (weapons, armor, divine, cursed)
└── analytics.json          # 8 entities (metrics, heatmaps, balance)
```

## Loom Execution

```bash
cd /root/clawd
loom init doc/plans/narrative-to-entities.md
loom run --max-parallel 30  # All agents including gacha
```

## Benefits

- **Parallel Processing**: 3 gacha agents work alongside 27 narrative agents
- **Consistent Logic**: All gacha mechanics defined by specialized agents
- **Fairness Monitoring**: Analytics agent tracks balance continuously
- **Lore Integration**: Legendary items have rich history and abilities
- **Scalability**: Add new gacha pools or items by creating new agent skills
- **Fairness**: Transparent mechanics, visible rates, pity protection
- **Rich Rewards**: Legendary items with deep lore and unique abilities
- **Ethical Monetization**: Balanced monetization with fair drop rates
- **Player Protection**: Pity systems prevent extreme bad luck
- **Data-Driven Decisions**: Analytics guide balance adjustments

## Documentation

- **Mechanics** — `docs/GACHA_MECHANICS.md`
- **Agents** — `docs/GACHA_AGENTS.md`
- **Workflow** — `docs/LOOM_GACHA_WORKFLOW.md` (this file)
