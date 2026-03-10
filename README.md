<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/architecture-DDD-green" alt="DDD">
  <img src="https://img.shields.io/badge/entities-200+-purple" alt="200+ entities">
  <img src="https://img.shields.io/badge/MCP-22_tools-orange" alt="MCP Server">
  <img src="https://img.shields.io/badge/agent_teams-5_specialists-red" alt="Agent Teams">
  <img src="https://img.shields.io/badge/repo_coverage-100%25-brightgreen" alt="100% repo coverage">
</p>

# 🧶 MythWeave Chronicles

> Complete lore management system for AAA game development — 200+ entity types, AI-powered extraction, and multi-agent team coordination.

**MythWeave** turns raw narrative text into structured, validated game lore. Feed it a chapter of your game's story, and a team of specialized AI agents will extract characters, locations, quests, factions, items, cinematics — everything — into a clean JSON knowledge base.

## 🔀 How this differs from `MiroFish` technically

This repository is the **canonical lore / world-model layer**. The embedded [`MiroFish/`](MiroFish/) project is a **simulation runtime + interactive report UI**.

| Aspect | `loreSystem` (this repo) | `MiroFish/` subproject |
|--------|---------------------------|------------------------|
| Primary role | Structured lore extraction, validation, storage | Multi-agent social simulation, report generation, graph exploration |
| Backend style | Python-first DDD / repository architecture | Flask API orchestrating simulation and report workflows |
| Frontend | Optional local GUI (`PyQt6`) + CLI + MCP | Web frontend with `Vue 3` + `Vite` + `D3` |
| Core AI pattern | Claude Code agent teams + domain extraction skills | OASIS/CAMEL agent simulation + ReportAgent tool calling |
| Data layer | SQLite / SQLAlchemy / in-memory repositories / Elasticsearch | Zep Cloud + Cognee-style graph memory + runtime action logs |
| Package/runtime tooling | Poetry/pip-style Python workflow | Mixed `npm` + `uv` + Python backend workflow |

In short: **`loreSystem` compiles the world canon**, while **`MiroFish` simulates how actors behave inside that world**. They are complementary systems, not the same stack in different folders.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **200+ Entity Types** | 34 categories covering every aspect of AAA game design |
| **Agent Teams** | 5 specialist AI teams extract lore in parallel |
| **33 Domain Skills** | Claude Code skills for entity extraction from text |
| **MCP Server** | Model Context Protocol server with 22 CRUD tools |
| **DDD Architecture** | Clean Domain → Application → Infrastructure layers |
| **Multi-tenant** | Run multiple game projects simultaneously |
| **Dual Storage** | In-Memory and SQLite backends, 100% repository coverage |
| **Validation** | Invariant checks, UUID tracking, version control |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Claude Code](https://code.claude.com) (for agent team features)

### Installation

```bash
git clone https://github.com/bivex/loreSystem && cd loreSystem
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
# Main application
python main.py

# MCP server (standalone)
python lore_mcp_server/run_server.py

# CLI
python -m src --help

# Tests
python -m pytest tests/ -v
```

---

## 🤖 Agent Team System

The core power of MythWeave is **AI-powered lore extraction**. You give it narrative text — it gives you structured entities.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  extraction-lead                     │
│            (orchestrator, delegate mode)             │
├───────────┬───────────┬───────────┬────────┬────────┤
│ narrative │   world   │  society  │systems │  tech  │
│   team    │   team    │   team    │  team  │  team  │
├───────────┼───────────┼───────────┼────────┼────────┤
│ Stories   │ Geography │ Factions  │ Skills │ Cinema │
│ Characters│ Climate   │ Politics  │ Economy│ Audio  │
│ Quests    │ Cities    │ Religion  │ Items  │ VFX    │
│ Lore      │ Dungeons  │ History   │ Combat │ Travel │
└───────────┴───────────┴───────────┴────────┴────────┘
        ↓           ↓           ↓          ↓         ↓
  narrative.json world.json society.json systems.json technical.json
        └───────────┴─────┬─────┴──────────┴─────────┘
                          ↓
                   merged_lore.json
```

### Teams & Skills

| Team | Role | Skills | Output |
|------|------|--------|--------|
| **extraction-lead** | Orchestrate, merge, validate | `lore-extraction`, `entity-validator`, `json-formatter` | `entities/merged_lore.json` |
| **narrative-team** | Stories, characters, quests | `narrative-writing`, `character-design`, `quest-design`, `lore-writing` | `entities/narrative.json` |
| **world-team** | Geography, environments, cities | `world-building`, `environmental-design`, `urban-design` | `entities/world.json` |
| **society-team** | Factions, politics, religion, history | `faction-design`, `political-analysis`, `social-culture`, `religious-lore`, `historical-research` | `entities/society.json` |
| **systems-team** | Progression, economy, items, combat | `progression-design`, `economic-modeling`, `legendary-items`, + 6 more | `entities/systems.json` |
| **technical-team** | Cinematics, audio, VFX, transport | `cinematic-direction`, `audio-direction`, `vfx-design`, + 6 more | `entities/technical.json` |

### How to Use

**Full team extraction** (recommended for chapters / long text):

```
Create an agent team to extract lore from chapter_1.txt.
Use the extraction-lead agent for coordination.
Spawn all 5 domain teammates.
Use delegate mode so the lead only coordinates.
```

**Selective team** (for focused text):

```
Create an agent team for chapter_1.txt.
Use extraction-lead. Spawn only narrative-team and world-team.
```

**Single skill** (quick extraction, no team overhead):

```
/character-design chapter_1.txt
/world-building chapter_1.txt
```

### When to Use What

| Scenario | Approach |
|----------|----------|
| Full chapter (5+ pages) | Agent team with all 5 specialists |
| Character-focused scene | `/character-design` or narrative-team only |
| Battle description | narrative-team + systems-team |
| World/map description | world-team only |
| Quick entity check | Single skill (`/faction-design`, `/quest-design`, etc.) |

### Cross-Reference Protocol

When a teammate finds an entity belonging to another domain, they log a cross-reference:

```json
{
  "cross_references": [
    {
      "domain": "world-team",
      "entity_type": "location",
      "name": "Eldoria Village",
      "note": "Referenced as protagonist's hometown"
    }
  ]
}
```

The lead resolves all cross-references during the merge phase, connecting entities across domains.

---

## 📂 Project Structure

```
loreSystem/
├── src/                          # Main application (DDD)
│   ├── domain/                   #   Entities, value objects, repo interfaces
│   ├── application/              #   Use cases, services
│   ├── infrastructure/           #   SQLite, InMemory implementations
│   └── presentation/             #   CLI, API
│
├── lore_mcp_server/              # Standalone MCP server
│   ├── mcp_server/server.py      #   22 MCP tools
│   └── lore_data/                #   Persistent JSON storage
│
├── .claude/
│   ├── agents/                   # 6 team agent definitions
│   │   ├── extraction-lead.md    #   Orchestrator
│   │   ├── narrative-team.md     #   Stories, characters, quests
│   │   ├── world-team.md         #   Geography, environments
│   │   ├── society-team.md       #   Factions, politics, religion
│   │   ├── systems-team.md       #   Progression, economy, items
│   │   └── technical-team.md     #   Cinema, audio, VFX
│   ├── skills/                   # 33 domain extraction skills
│   └── settings.json             # Agent teams + permissions
│
├── entities/                     # Extracted entity output (JSON)
├── examples/                     # Sample lore JSON files
├── tests/                        # Test suite (unit, integration, e2e)
├── docs/                         # Full documentation
├── CLAUDE.md                     # Project context for AI agents
└── AGENTS.md                     # Agent workflow documentation
```

---

## 🏛️ Architecture

### Domain-Driven Design

```
┌──────────────────────────────────────────┐
│              Presentation                │
│          (CLI, API, MCP Server)          │
├──────────────────────────────────────────┤
│              Application                 │
│        (Services, Use Cases, DTOs)       │
├──────────────────────────────────────────┤
│                Domain                    │
│  (Entities, Value Objects, Repo Interfaces)│
├──────────────────────────────────────────┤
│             Infrastructure               │
│    (SQLite, InMemory, Elasticsearch)     │
└──────────────────────────────────────────┘
```

### Repository Status — 100% Coverage (18/18)

All repository interfaces are fully implemented with In-Memory + SQLite backends.

<details>
<summary><b>Core Lore System (4)</b></summary>

- **WorldRepository** — Create/list/delete worlds
- **CharacterRepository** — Manage characters within worlds
- **StoryRepository** — Create and organize stories
- **PageRepository** — Manage content pages

</details>

<details>
<summary><b>World Building (3)</b></summary>

- **ItemRepository** — Items and inventory
- **LocationRepository** — World locations and areas
- **EnvironmentRepository** — Time, weather, lighting

</details>

<details>
<summary><b>Game Mechanics (8)</b></summary>

- **SessionRepository** — Active game sessions
- **ChoiceRepository** — Interactive story choices
- **FlowchartRepository** — Story branching
- **HandoutRepository** — Player documents
- **ImageRepository** — Asset management
- **InspirationRepository** — Creative prompts
- **MapRepository** — Game maps
- **TokenboardRepository** — Combat boards

</details>

<details>
<summary><b>Content Organization (3)</b></summary>

- **TagRepository** — Tag-based organization
- **NoteRepository** — GM notes and annotations
- **TemplateRepository** — Reusable templates

</details>

> **Note:** Only these 18 entities have repository interfaces and are accessible via the MCP server. The remaining 200+ domain entities exist in the domain model — their business logic is handled within other entities.

---

## 🌍 Domain Model — 200+ Entities across 34 Categories

<details>
<summary><b>Core Game Systems (50 entities)</b></summary>

| Category | Count | Entities |
|----------|-------|----------|
| Campaign & Story | 17 | Act, Chapter, Episode, Prologue, Epilogue, PlotBranch, Consequence, Ending, AlternateReality |
| Characters | 9 | CharacterEvolution, CharacterVariant, CharacterProfileEntry, MotionCapture, VoiceActor |
| Quests | 7 | QuestChain, QuestNode, QuestPrerequisite, QuestObjective, QuestTracker, QuestGiver |
| Skills & Progression | 8 | Skill, Perk, Trait, Attribute, Experience, LevelUp, TalentTree, Mastery |
| Inventory & Crafting | 9 | Inventory, CraftingRecipe, Material, Component, Blueprint, Enchantment, Socket, Rune, Glyph |

</details>

<details>
<summary><b>World Building (39 entities)</b></summary>

| Category | Count | Entities |
|----------|-------|----------|
| Locations | 10 | HubArea, Instance, Dungeon, Raid, Arena, OpenWorldZone, Underground, Skybox, Dimension, PocketDimension |
| Politics & History | 14 | Era, EraTransition, Timeline, Calendar, Holiday, Season, TimePeriod, Treaty, Constitution, Law, LegalSystem, Nation, Kingdom, Empire |
| Economy | 8 | Trade, Barter, Tax, Tariff, Supply, Demand, Price, Inflation |
| Military | 7 | Army, Fleet, WeaponSystem, Defense, Fortification, SiegeEngine, Battalion |

</details>

<details>
<summary><b>Social Systems (22 entities)</b></summary>

| Category | Count | Entities |
|----------|-------|----------|
| Social Relations | 7 | Reputation, Affinity, Disposition, Honor, Karma, SocialClass, SocialMobility |
| Factions | 5 | FactionHierarchy, FactionIdeology, FactionLeader, FactionResource, FactionTerritory |
| Religion & Mysticism | 10 | Cult, Sect, HolySite, Scripture, Ritual, Oath, Summon, Pact, Curse, Blessing |

</details>

<details>
<summary><b>Content & Creativity (25 entities)</b></summary>

| Category | Count | Entities |
|----------|-------|----------|
| Lore System | 8 | LoreFragment, CodexEntry, JournalPage, BestiaryEntry, Memory, Dream, Nightmare, SecretArea |
| Music & Audio | 8 | Theme, Motif, Score, Soundtrack, VoiceLine, SoundEffect, Ambient, Silence |
| Visual Effects | 5 | VisualEffect, Particle, Shader, Lighting, ColorPalette |
| Cinematography | 6 | Cutscene, Cinematic, CameraPath, Transition, Fade, Flashback |

</details>

<details>
<summary><b>Advanced Systems (29 entities)</b></summary>

| Category | Count | Entities |
|----------|-------|----------|
| Architecture | 8 | District, Ward, Quarter, Plaza, MarketSquare, Slums, NobleDistrict, PortDistrict |
| Biology & Ecology | 6 | FoodChain, Migration, Hibernation, Reproduction, Extinction, Evolution |
| Astronomy | 10 | Galaxy, Nebula, BlackHole, Wormhole, StarSystem, Moon, Eclipse, Solstice |
| Weather & Climate | 5 | WeatherPattern, Cataclysm, Disaster, Miracle, Atmosphere |

</details>

<details>
<summary><b>Gameplay, UGC & Analytics (50+ entities)</b></summary>

| Category | Count | Entities |
|----------|-------|----------|
| Narrative Devices | 6 | PlotDevice, DeusExMachina, ChekhovsGun, Foreshadowing, FlashForward, RedHerring |
| Global Events | 7 | WorldEvent, SeasonalEvent, Invasion, Plague, Famine, War, Revolution |
| Travel | 6 | FastTravelPoint, Waypoint, SavePoint, Checkpoint, Autosave, SpawnPoint |
| Achievements | 6 | Achievement, Trophy, Badge, Title, Rank, Leaderboard |
| Legendary Items | 6 | LegendaryWeapon, MythicalArmor, DivineItem, CursedItem, ArtifactSet, RelicCollection |
| Transport | 9 | Pet, Mount, Familiar, MountEquipment, Vehicle, Spaceship, Airship, Portal, Teleporter |
| UGC | 5 | Mod, CustomMap, UserScenario, ShareCode, WorkshopEntry |
| Localization | 5 | Localization, Translation, VoiceOver, Subtitle, Dubbing |
| Analytics | 8 | PlayerMetric, SessionData, Heatmap, DropRate, ConversionRate, DifficultyCurve, LootTableWeight, BalanceEntities |
| Institutions | 7 | Academy, University, School, Library, ResearchCenter, Archive, Museum |
| Media | 7 | Newspaper, Radio, Television, Internet, SocialMedia, Propaganda, Rumor |
| Secrets | 8 | SecretArea, HiddenPath, EasterEgg, Mystery, Enigma, Riddle, Puzzle, Trap |

</details>

---

## 🔧 33 Extraction Skills

All skills live in `.claude/skills/` with YAML frontmatter for auto-discovery by Claude Code.

<details>
<summary><b>Domain Skills (30) — auto-invoked by Claude when relevant</b></summary>

| Skill | Entities | Team |
|-------|----------|------|
| `narrative-writing` | Story, Chapter, Act, Episode, PlotBranch | narrative |
| `character-design` | Character, Relationships, Evolution, Variants | narrative |
| `quest-design` | Quest, QuestChain, Objectives, MoralChoice | narrative |
| `lore-writing` | LoreFragment, Codex, Bestiary, Dreams | narrative |
| `world-building` | Location, Dungeon, Arena, Dimension | world |
| `environmental-design` | Weather, Atmosphere, Lighting, Disasters | world |
| `urban-design` | District, Ward, Market, Plaza | world |
| `faction-design` | Faction, Hierarchy, Territory, Ideology | society |
| `political-analysis` | Government, Law, Court, Treaty | society |
| `social-culture` | SocialClass, Honor, Karma, Festival | society |
| `religious-lore` | Cult, Ritual, Blessing, Curse, Scripture | society |
| `historical-research` | Era, Timeline, Calendar, Ceremony | society |
| `progression-design` | Skill, Perk, Trait, TalentTree, XP | systems |
| `economic-modeling` | Trade, Currency, Shop, Supply/Demand | systems |
| `legendary-items` | Artifacts, Runes, Enchantments, Relics | systems |
| `achievement-design` | Trophy, Badge, Rank, Leaderboard | systems |
| `puzzle-design` | Puzzle, Riddle, Trap, EasterEgg | systems |
| `military-strategy` | Army, Fleet, Fortification, War | systems |
| `biology-design` | Ecosystem, FoodChain, Evolution | systems |
| `celestial-science` | Galaxy, Star, BlackHole, Eclipse | systems |
| `analytics-balance` | DropRate, DifficultyCurve, LootTable | systems |
| `cinematic-direction` | Cutscene, CameraPath, Flashback | technical |
| `audio-direction` | Music, SoundEffect, Motif, Ambient | technical |
| `vfx-design` | Particle, Shader, Lighting, ColorPalette | technical |
| `transport-design` | Mount, Vehicle, Portal, Airship | technical |
| `content-management` | Mod, Localization, UGC, Workshop | technical |
| `media-analysis` | Newspaper, Radio, Propaganda, Rumor | technical |
| `research-design` | Academy, Library, Archive, Museum | technical |
| `ui-design` | Choice, Flowchart, Handout, Tag | technical |
| `technical-systems` | 193 catch-all entity types (safety net) | technical |

</details>

<details>
<summary><b>Base Skills (3) — background knowledge, auto-loaded</b></summary>

| Skill | Purpose |
|-------|---------|
| `lore-extraction` | Base extraction rules for all agents |
| `entity-validator` | Type checking, required fields, deduplication |
| `json-formatter` | Strict JSON output, UUID generation, schema compliance |

</details>

---

## 🔌 MCP Server

The MCP server exposes 22 tools for lore CRUD operations:

```bash
python lore_mcp_server/run_server.py
```

Connect from Claude Code, Claude Desktop, or any MCP client. See [MCP Server docs](lore_mcp_server/docs/) for the full API reference.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/USER_GUIDE.md) | Installation and usage |
| [Documentation Index](docs/README.md) | Full docs navigation |
| [Design & Implementation](docs/design/) | Architecture decisions, ADRs |
| [Validation & Verification](docs/validation/) | Test reports, edge cases |
| [Feature Guides](docs/features/) | Detailed feature docs |
| [CLI Quick Reference](docs/CLI_QUICK_REF.md) | Command-line usage |
| [MCP Server Docs](lore_mcp_server/docs/) | MCP API reference |
| [Gacha Mechanics](docs/GACHA_MECHANICS.md) | Gacha system design |

---

## � Community Standards

This project follows recommended community standards for open-source development:

| Standard | Status | Description |
|----------|--------|-------------|
| **README** | ✅ | Comprehensive project documentation |
| **Code of Conduct** | ✅ [📄](CODE_OF_CONDUCT.md) | Community guidelines and expectations |
| **Contributing** | ✅ [📝](CONTRIBUTING.md) | How to contribute to the project |
| **License** | ✅ [📜](LICENSE) | Project licensing information |
| **Security Policy** | ✅ [🔒](SECURITY.md) | Security vulnerability reporting |
| **Issue Templates** | ✅ [📋](.github/ISSUE_TEMPLATE/) | Standardized issue reporting |
| **Pull Request Template** | ✅ [🔄](.github/PULL_REQUEST_TEMPLATE.md) | Standardized PR submissions |

---

## �🧪 Testing

```bash
# Full test suite with coverage
python -m pytest tests/ -v --cov=src --cov-report=html

# By marker
python -m pytest tests/ -m unit          # Fast, no I/O
python -m pytest tests/ -m integration   # Database tests
python -m pytest tests/ -m e2e           # Full system
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Language** | Python 3.11+ |
| **Architecture** | DDD, Hexagonal, Repository Pattern |
| **Storage** | SQLite, SQLAlchemy, In-Memory |
| **Validation** | Pydantic 2.x |
| **CLI** | Click, Rich |
| **GUI** | PyQt6 |
| **Search** | Elasticsearch |
| **Config** | PyYAML, python-dotenv |
| **DI** | dependency-injector |
| **AI** | Claude Code Agent Teams, 33 Skills, MCP Server |
| **Testing** | pytest, pytest-cov |

---

<p align="center">
  <b>MythWeave Chronicles</b> — built for game developers who take their lore seriously.
</p>
