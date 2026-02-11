# Loom Agent Orchestration for loreSystem

This directory contains Loom-based agent orchestration system for converting narrative chapters into loreSystem entities.

## Structure

```
agents/
├── skills/                    # 30 specialized agent skills
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
│   ├── achievement-specialist.md
│   ├── audio-director.md
│   ├── visual-effects-artist.md
│   ├── cinematic-director.md
│   ├── media-analyst.md
│   ├── transportation-engineer.md
│   ├── celestial-scientist.md
│   ├── biology-specialist.md
│   ├── urban-architect.md
│   ├── research-education-specialist.md
│   ├── puzzle-secrets-designer.md
│   ├── ui-content-specialist.md
│   ├── analytics-balance-specialist.md
│   ├── legendary-items-specialist.md
│   ├── social-cultural-specialist.md
│   └── game-mechanics-specialist.md
└── README.md                  # This file

doc/plans/
├── narrative-to-entities.md    # Loom orchestration plan (30 agents, 32 stages)

scripts/
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
├── achievement.json         # 6 entities
├── audio.json              # 9 entities
├── visual.json             # 5 entities
├── cinematic.json          # 6 entities
├── media.json              # 7 entities
├── transportation.json      # 9 entities
├── celestial.json          # 9 entities
├── biology.json            # 6 entities
├── urban.json              # 8 entities
├── research.json           # 7 entities
├── puzzle.json             # 7 entities
├── ui_content.json         # 8 entities
├── analytics.json          # 8 entities
├── legendary.json          # 10 entities
├── social_cultural.json    # 11 entities
└── mechanics.json           # 13 entities
```

## The 30 Agent Professions

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
| 15 | Achievement Specialist | Achievements, Trophies, Badges, Titles, Ranks, Leaderboards | 6 |
| 16 | Audio Director | Music, Sound Effects, Ambient, Motifs, Scores | 9 |
| 17 | Visual Effects Artist | Visual Effects, Particles, Shaders, Lighting, Color Palettes | 5 |
| 18 | Cinematic Director | Cutscenes, Cinematics, Camera Paths, Transitions, Fades, Flashbacks | 6 |
| 19 | Media Analyst | Newspapers, Radio, TV, Internet, Social Media, Propaganda, Rumors | 7 |
| 20 | Transportation Engineer | Mounts, Familiars, Vehicles, Airships, Spaceships, Portals, Teleporters | 9 |
| 21 | Celestial Scientist | Galaxies, Nebulae, Black Holes, Wormholes, Star Systems, Moons, Eclipses, Solstices | 9 |
| 22 | Biology Specialist | Food Chains, Migrations, Hibernation, Reproduction, Extinction, Evolution | 6 |
| 23 | Urban Architect | Districts, Wards, Quarters, Plazas, Market Squares, Slums, Noble Districts, Port Districts | 8 |
| 24 | Research & Education Specialist | Academies, Universities, Schools, Libraries, Research Centers, Archives, Museums | 7 |
| 25 | Puzzle & Secrets Designer | Hidden Paths, Easter Eggs, Mysteries, Enigmas, Riddles, Puzzles, Traps | 7 |
| 26 | UI/Content Specialist | Choices, Flowcharts, Handouts, Tokenboards, Tags, Templates, Inspiration, Notes | 8 |
| 27 | Analytics & Balance Specialist | Player Metrics, Session Data, Heatmaps, Drop Rates, Conversion Rates, Difficulty Curves, Loot Table Weights | 8 |
| 28 | Legendary Items Specialist | Legendary Weapons, Mythical Armor, Divine Items, Cursed Items, Artifact Sets, Relic Collections, Glyphs, Runes, Sockets, Enchantments | 10 |
| 29 | Social & Cultural Specialist | Affinity, Disposition, Honor, Karma, Social Classes, Social Mobility, Festivals, Celebrations, Ceremonies, Competitions, Tournaments | 11 |
| 30 | Game Mechanics Specialist | Events, Event Chains, Alternate Realities, Consequences, Endings, Patents, Inventions, Improvements, Requirements, Pulls, Phenomena, Pity, Themes | 13 |
| **TOTAL** | **All loreSystem entities** | **295** |

## Usage

### Prerequisites

**On remote/headless servers:** Loom requires a terminal emulator to spawn agent sessions.

```bash
# Install xterm (simplest terminal emulator)
apt install xterm

# Set TERMINAL environment variable
export TERMINAL=xterm

# Or add to ~/.bashrc for persistence
echo 'export TERMINAL=xterm' >> ~/.bashrc
source ~/.bashrc
```

**Available terminal emulators:** kitty, alacritty, foot, wezterm, gnome-terminal, konsole, xfce4-terminal, xterm

### 1. Initialize Loom Plan

```bash
cd /root/clawd

# Fresh initialization (removes old .work directory)
rm -rf .work && loom init doc/plans/narrative-to-entities.md
```

### 2. Prepare Chapter Input

```bash
# Create a chapter text file (agents will read it directly)
echo "Chapter 1: The Beginning. Kira stood at the edge of Eldoria..." > chapter_1.txt

# Or run the helper script to fix blockers and create sample chapter
bash scripts/fix_loom_blockers.sh
```

### 3. Run Orchestration

```bash
# Quick start with helper script (includes TERMINAL setup)
bash scripts/start_loom.sh

# Or manually:
export TERMINAL=xterm
loom run --max-parallel 30

# Run with manual control
loom run --manual

# Run with live status monitoring
loom run --max-parallel 30 && loom status --live
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
│ PARALLEL AGENT EXECUTION (30 agents)                              │
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
│    ├─ Achievement Specialist → entities/achievement.json             │
│    ├─ Audio Director → entities/audio.json                           │
│    ├─ Visual Effects Artist → entities/visual.json                     │
│    ├─ Cinematic Director → entities/cinematic.json                  │
│    ├─ Media Analyst → entities/media.json                           │
│    ├─ Transportation Engineer → entities/transportation.json       │
│    ├─ Celestial Scientist → entities/celestial.json                   │
│    ├─ Biology Specialist → entities/biology.json                     │
│    ├─ Urban Architect → entities/urban.json                         │
│    ├─ Research & Education Specialist → entities/research.json          │
│    ├─ Puzzle & Secrets Designer → entities/puzzle.json                 │
│    ├─ UI/Content Specialist → entities/ui_content.json             │
│    ├─ Analytics & Balance Specialist → entities/analytics.json          │
│    ├─ Legendary Items Specialist → entities/legendary.json            │
│    ├─ Social & Cultural Specialist → entities/social_cultural.json      │
│    └─ Game Mechanics Specialist → entities/mechanics.json              │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. VALIDATION                                                   │
│    - Validate all entity files                                    │
│    - Check schema compliance                                      │
│    - Verify required fields                                      │
│    Output: validation_report.json, validation_summary.json           │
└─────────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. PERSIST TO SQLITE                                            │
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

1. **Add entity linking**: Cross-reference entities between agents
3. **Implement diff tracking**: Track changes between chapters
4. **Add conflict resolution**: Handle entity conflicts between agents
5. **Create agent teams**: Enable collaborative agent work

## License

MIT - See LICENSE file in repository root.
