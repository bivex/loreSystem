# Loom Agent Orchestration for loreSystem

This directory contains Loom-based agent orchestration system for converting narrative chapters into loreSystem entities.

## Structure

```
agents/
├── skills/                    # 15 specialized agent skills
│   ├── narrative-specialist.md
│   ├── character-architect.md
│   ├── quest-designer.md
│   ├── progression-engineer.md
│   ├── world-geographer.md
│   ├── environmental-scientist.md
│   ├── historian.md
│   ├── political-scientist.md
│   ├── economist.md
│   ├── faction-analyst.md
│   ├── military-strategist.md
│   ├── religious-scholar.md
│   ├── lore-chronicler.md
│   ├── content-creator.md
│   └── technical-director.md
└── README.md                  # This file

doc/plans/
└── narrative-to-entities.md    # Loom orchestration plan

scripts/
├── parse_chapter.py           # Parse chapter text
├── validate_parse_output.py   # Validate parsed data
├── validate_entities.py       # Validate all entities
├── validate_schema.py         # Validate schema compliance
└── verify_sqlite_inserts.py  # Verify database inserts

entities/                       # Generated entity files
├── narrative.json            # 8 entities
├── character.json            # 7 entities
├── quest.json               # 9 entities
├── progression.json         # 10 entities
├── world.json              # 11 entities
├── environment.json         # 6 entities
├── historical.json        # 10 entities
├── political.json        # 13 entities
├── economy.json          # 13 entities
├── faction.json          # 7 entities
├── military.json        # 10 entities
├── religious.json       # 11 entities
├── lore.json            # 8 entities
├── content.json        # 10 entities
└── technical.json     # 193 entities
```

## The 15 Agent Professions

| # | Profession | Entity Types | Count |
|---|------------|--------------|-------|
| 1 | Narrative Specialist | Story, Chapter, Act, Episode, etc. | 8 |
| 2 | Character Architect | Character, Evolution, Relationships, etc. | 7 |
| 3 | Quest Designer | Quest, Chain, Objectives, etc. | 9 |
| 4 | Progression Engineer | Skills, Perks, Attributes, etc. | 10 |
| 5 | World Geographer | Locations, Zones, Dungeons, etc. | 11 |
| 6 | Environmental Scientist | Weather, Atmosphere, Lighting, etc. | 6 |
| 7 | Historian | Eras, Timelines, Festivals, etc. | 10 |
| 8 | Political Scientist | Government, Laws, Courts, etc. | 13 |
| 9 | Economist | Trade, Currency, Markets, etc. | 13 |
| 10 | Faction Analyst | Factions, Ideology, Territory, etc. | 7 |
| 11 | Military Strategist | Armies, Weapons, Fortifications, etc. | 10 |
| 12 | Religious Scholar | Cults, Rituals, Miracles, etc. | 11 |
| 13 | Lore Chronicler | Lore fragments, Bestiary, Secrets, etc. | 8 |
| 14 | Content Creator | Mods, Maps, Localization, etc. | 10 |
| 15 | Technical Director | All remaining technical entities | 193 |
| **TOTAL** | **All loreSystem entities** | **295** |

## Usage

### 1. Initialize Loom Plan

```bash
cd /root/clawd
loom init doc/plans/narrative-to-entities.md
```

### 2. Prepare Chapter Input

```bash
# Create a chapter text file
echo "Chapter 1: The Beginning. Kira stood at the edge of Eldoria..." > chapter_1.txt

# Or use stdin
cat chapter_1.txt | python scripts/parse_chapter.py
```

### 3. Run Orchestration

```bash
# Run with all 15 agents in parallel
loom run --max-parallel 15

# Run with manual control
loom run --manual

# Run with live status monitoring
loom run --max-parallel 15 && loom status --live
```

### 4. Monitor Progress

```bash
# Live status
loom status --live

# Compact status
loom status --compact

# Detailed status
loom status --verbose
```

### 5. Validate Results

```bash
# Validate all entities
python scripts/validate_entities.py --strict

# Validate schema compliance
python scripts/validate_schema.py --all-files
```

### 6. Persist to SQLite

After validation completes, entities are automatically inserted into `lore_system.db`.

```bash
# Verify inserts
python scripts/verify_sqlite_inserts.py lore_system.db entities/
```

## Pipeline Flow

```
Chapter Text
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 1. PARSE CHAPTER                                                 │
│    - Extract entities using regex/NLP                                │
│    - Identify relationships                                         │
│    - Generate chapter ID                                          │
│    Output: parsed_data.json, extracted_entities.json                  │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. PARALLEL AGENT EXECUTION (15 agents)                           │
│    ├─ Narrative Specialist → entities/narrative.json                 │
│    ├─ Character Architect → entities/character.json                 │
│    ├─ Quest Designer → entities/quest.json                         │
│    ├─ Progression Engineer → entities/progression.json             │
│    ├─ World Geographer → entities/world.json                       │
│    ├─ Environmental Scientist → entities/environment.json             │
│    ├─ Historian → entities/historical.json                        │
│    ├─ Political Scientist → entities/political.json                │
│    ├─ Economist → entities/economy.json                          │
│    ├─ Faction Analyst → entities/faction.json                    │
│    ├─ Military Strategist → entities/military.json                 │
│    ├─ Religious Scholar → entities/religious.json                 │
│    ├─ Lore Chronicler → entities/lore.json                      │
│    ├─ Content Creator → entities/content.json                    │
│    └─ Technical Director → entities/technical.json                │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. VALIDATION                                                   │
│    - Validate all entity files                                    │
│    - Check schema compliance                                      │
│    - Verify required fields                                      │
│    Output: validation_report.json, validation_summary.json           │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. PERSIST TO SQLITE                                            │
│    - Insert all entities into lore_system.db                       │
│    - Create database tables if needed                             │
│    - Log insertion results                                        │
│    Output: lore_system.db, insert_log.json, insert_summary.json    │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent Skills

Each `skills/*.md` file defines:

1. **Entity Coverage**: Which entities the agent handles
2. **Expertise**: Domain knowledge and capabilities
3. **Processing Guidelines**: How to analyze text
4. **Output Format**: JSON schema requirements
5. **Key Considerations**: Important notes and edge cases

## Configuration

### Loom Plan Configuration

Edit `doc/plans/narrative-to-entities.md` to customize:

- **Parallelism**: `max_parallel` controls concurrent agents
- **Sandbox**: Filesystem and network restrictions
- **Acceptance Criteria**: Shell commands for stage completion
- **Truths/Artifacts/Wiring**: Goal-backward verification

### Agent Skills Configuration

Edit `agents/skills/*.md` files to:

- Add new entity types
- Modify expertise guidelines
- Change output formats
- Update validation rules

## Troubleshooting

### Stage Stuck?

```bash
loom stage status <stage-id>
loom stage reset <stage-id> --hard
```

### Validation Failed?

```bash
python scripts/validate_entities.py --strict
python scripts/validate_schema.py --all-files
```

### Database Issues?

```bash
sqlite3 lore_system.db ".tables"
sqlite3 lore_system.db "SELECT COUNT(*) FROM story;"
```

## Next Steps

1. **Enhance NLP parsing**: Replace regex with NLP/LLM for better extraction
2. **Add entity linking**: Cross-reference entities between agents
3. **Implement diff tracking**: Track changes between chapters
4. **Add conflict resolution**: Handle entity conflicts between agents
5. **Create agent teams**: Enable collaborative agent work

## License

MIT - See LICENSE file in repository root.
