# MythWeave Chronicles Documentation

**A lore management platform for game developers and storytellers.**

---

## 📚 What is MythWeave?

MythWeave Chronicles is a **structured database for your game's world, characters, events, and storylines.** Whether you're building an RPG, writing a novel, or managing a collaborative world-building project, MythWeave helps you:

✅ **Organize lore** - Keep worlds, characters, and events in one place
✅ **Enforce rules** - Automatic validation prevents broken game mechanics
✅ **Track changes** - Version history and rollback capability
✅ **Collaborate** - Work with teams using Git and database backends
✅ **Validate systems** - Test progression mechanics and gacha rules

---

## 🎯 Who Should Use MythWeave?

### Game Designers
Create and manage consistent game worlds, track character progression, and ensure story continuity.

### Writers
Develop rich character backstories, maintain narrative consistency across multiple storylines, and track character abilities.

### QA Testers
Verify game content matches lore specifications, test progression systems, and validate character abilities.

### Project Managers
Track lore development progress, manage content across teams, and review proposed changes.

---

## 🚀 Quick Start

### New to MythWeave? Start Here:

1. **Read the [User Guide](docs/USER_GUIDE.md)** - Installation, usage, and troubleshooting
2. **Follow the [GUI Quick Start](gui/QUICKSTART_GUI.md)** - 5-minute walkthrough
3. **Check the [FAQ](FAQ.md)** - Common questions answered
4. **Use the [Quick Reference Cards](QUICK_REFERENCE.md)** - Cheat sheets for common tasks

### Already Using MythWeave?

- **Need help?** Check the [FAQ](FAQ.md) or [Glossary](GLOSSARY.md)
- **Want to upgrade?** See [Advanced Configuration](USER_GUIDE.md#advanced-configuration)
- **Building a game?** Read [Validation Quick Reference](validation/VALIDATION_QUICK_REFERENCE.md)
- **Testing progression?** See [Progression Simulator Guide](features/PROGRESSION_SIMULATOR_README.md)

---

## 🏗️ Architecture

### Domain Model Overview

The domain model includes **200+ AAA game dev entities** organized into **34 major categories**:

#### Core Game Systems
- **Campaign & Story** (17): Act, Chapter, Episode, Prologue, Epilogue, PlotBranch, Consequence, Ending, AlternateReality
- **Characters** (9): CharacterEvolution, CharacterVariant, CharacterProfileEntry, MotionCapture, VoiceActor
- **Quests** (7): QuestChain, QuestNode, QuestPrerequisite, QuestObjective, QuestTracker, QuestGiver, QuestRewardTier
- **Skills & Progression** (8): Skill, Perk, Trait, Attribute, Experience, LevelUp, TalentTree, Mastery
- **Inventory & Crafting** (9): Inventory, CraftingRecipe, Material, Component, Blueprint, Enchantment, Socket, Rune, Glyph

#### World Building
- **Locations** (10): HubArea, Instance, Dungeon, Raid, Arena, OpenWorldZone, Underground, Skybox, Dimension, PocketDimension
- **Politics & History** (14): Era, EraTransition, Timeline, Calendar, Holiday, Season, TimePeriod, Treaty, Constitution, Law, LegalSystem, Nation, Kingdom, Empire, Government, Alliance
- **Economy** (8): Trade, Barter, Tax, Tariff, Supply, Demand, Price, Inflation
- **Military** (7): Army, Fleet, WeaponSystem, Defense, Fortification, SiegeEngine, Battalion

#### Social Systems
- **Social Relations** (7): Reputation, Affinity, Disposition, Honor, Karma, SocialClass, SocialMobility
- **Factions** (5): FactionHierarchy, FactionIdeology, FactionLeader, FactionResource, FactionTerritory
- **Religion & Mysticism** (10): Cult, Sect, HolySite, Scripture, Ritual, Oath, Summon, Pact, Curse, Blessing

#### Content & Creativity
- **Lore System** (7): LoreFragment, CodexEntry, JournalPage, BestiaryEntry, CharacterProfileEntry, Memory, Dream, Nightmare
- **Music & Audio** (7): Theme, Motif, Score, Soundtrack, VoiceLine, SoundEffect, Ambient, Silence
- **Visual Effects** (5): VisualEffect, Particle, Shader, Lighting, ColorPalette
- **Cinematography** (6): Cutscene, Cinematic, CameraPath, Transition, Fade, Flashback

#### Advanced Systems
- **Architecture** (8): District, Ward, Quarter, Plaza, MarketSquare, Slums, NobleDistrict, PortDistrict
- **Biology & Ecology** (6): FoodChain, Migration, Hibernation, Reproduction, Extinction, Evolution
- **Astronomy** (10): Galaxy, Nebula, BlackHole, Wormhole, StarSystem, Moon, Eclipse, Solstice
- **Weather & Climate** (5): WeatherPattern, Cataclysm, Disaster, Miracle, Phenomenon, Atmosphere

#### Gameplay Mechanics
- **Narrative Devices** (6): PlotDevice, DeusExMachina, ChekhovsGun, Foreshadowing, FlashForward, RedHerring
- **Global Events** (7): WorldEvent, SeasonalEvent, Invasion, Plague, Famine, War, Revolution
- **Travel & Progression** (6): FastTravelPoint, Waypoint, SavePoint, Checkpoint, Autosave, SpawnPoint
- **Legal System** (9): Court, Crime, Judge, Jury, Lawyer, Punishment, Evidence, Witness
- **Achievements** (5): Achievement, Trophy, Badge, Title, Rank, Leaderboard

#### User Generated Content
- **UGC** (5): Mod, CustomMap, UserScenario, ShareCode, WorkshopEntry
- **Localization** (5): Localization, Translation, VoiceOver, Subtitle, Dubbing
- **Analytics** (5): PlayerMetric, SessionData, Heatmap, DropRate, ConversionRate
- **Balance** (3): DifficultyCurve, LootTableWeight, BalanceEntities

#### Item Systems
- **Legendary Items** (6): LegendaryWeapon, MythicalArmor, DivineItem, CursedItem, ArtifactSet, RelicCollection
- **Companions & Transport** (9): Pet, Mount, Familiar, MountEquipment, Vehicle, Spaceship, Airship, Portal, Teleporter

#### Architecture & Infrastructure
- **Institutions** (6): Academy, University, School, Library, ResearchCenter, Archive, Museum
- **Media** (7): Newspaper, Radio, Television, Internet, SocialMedia, Propaganda, Rumor
- **Secrets** (8): SecretArea, HiddenPath, EasterEgg, Mystery, Enigma, Riddle, Puzzle, Trap
- **Art & Culture** (6): Festival, Celebration, Ceremony, Concert, Exhibition, Competition, Tournament

### DDD Architecture

- **Domain Layer** (200+ entities): Clean separation of concerns with tenant multi-tenancy
- **Application Layer** (Services, repositories, DTOs): Business logic and use cases
- **Infrastructure Layer** (Database, caching, messaging): Technical implementation
- **Hexagonal Architecture**: Ports and adapters for clean integration with game engines (Unreal, Unity, Godot)

### Multi-Tenant Support
- Separate databases per tenant
- Shared infrastructure with tenant isolation
- Tenant-specific configurations and templates

---

## 🎯 Use Cases

Detailed documentation of how AAA game dev studios and professionals can use of loreSystem domain model.

### Game Designers

**[UC1: Campaign Management](docs/use_cases/uc1_campaign_management.md)**
Creating and managing branching story campaigns with multiple endings, dependent on player choices.

**[UC2: Quest System](docs/use_cases/uc2_quest_system.md)**
Creating and managing complex quest chains with prerequisites, rewards, and progress tracking.

**[UC3: Faction & Reputation](docs/use_cases/uc3_faction_systems.md)**
Creating and managing faction systems with hierarchies, ideologies, and reputation mechanics.

**[UC4: Economy & Trade](docs/use_cases/uc4_economy_system.md)**
Creating and managing economic systems with trade routes, taxes, inflation, and supply/demand.

**[UC5: Validation & Export](docs/use_cases/uc5_validation_and_export.md)**
Validating lore data and exporting to game engines (Unreal, Unity, Godot) with proper formats.

### Developers

**[UC6: Import/Export](docs/use_cases/uc5_validation_and_export.md)**
Exporting campaigns, quests, factions to JSON/XML for game engines.
Version control and hotfix support for live games.

**[UC7: Engine Integration](docs/use_cases/uc5_validation_and_export.md)**
Generating C#/C++ classes from domain model for game engines.
Converting lore data to engine assets (Blueprints, Prefabs).

### Producers & Stakeholders

**[UC8: Progress Monitoring](docs/use_cases/uc5_validation_and_export.md)**
Tracking campaign, quest, and faction creation progress.
Generating heatmaps for spatial analysis.
Conversion rate analysis for player retention and optimization.

**[UC9: Game Balance](docs/use_cases/uc5_validation_and_export.md)**
Analyzing drop rates of legendary items and optimizing loot tables.
Balancing PvP, PvE, and economy based on player metrics.
Fine-tuning difficulty curves for optimal player experience.

**[UC10: Support & Analytics](docs/use_cases/uc5_validation_and_export.md)**
Processing player complaints about balance and bugs.
Reviewing version history for hotfix opportunities.
Analyzing player behavior metrics and session data for improvement.

---

## 📊 Statistics

- **Total Entity Files**: 288 (including __init__.py)
- **Total Use Cases**: 10
- **Total Documentation Pages**: 15+
- **Supported Formats**: JSON, XML, CSV, SQLite
- **Game Engines**: Unreal Engine, Unity, Godot
- **DDD Patterns**: Repository, Factory, Aggregate, ValueObject, Specification

---

## 🎯 Key Features

### Domain-Driven Design
- **Rich Domain Model**: 200+ AAA game dev entities with full DDD structure
- **Automatic Validation**: Invariant checking prevents broken game mechanics
- **Version Control**: Built-in version tracking for all entities
- **Factory Methods**: Consistent entity creation patterns
- **Clean Separation**: Clear boundaries between domain, application, infrastructure layers

### Multi-Tenant Architecture
- **Tenant Isolation**: Separate data per project/tenant
- **Shared Services**: Reusable application layer across tenants
- **Tenant-Specific Configuration**: Customizable per tenant

### Validation & Quality
- **Invariant Validation**: All entities validate their own rules
- **Dependency Checking**: Quest prerequisites, level requirements, etc.
- **Type Safety**: Strong typing for all entities
- **Error Handling**: Clear exception hierarchy (InvariantViolation, InvalidState)

### Import/Export
- **Multiple Formats**: JSON, XML, CSV, SQLite
- **Engine Support**: Unreal Engine, Unity, Godot
- **Hotfix Ready**: Version tracking for live game patches
- **Batch Operations**: Import/export all tenant data

---

## 📚 Documentation Structure

### Core Documentation
- **[User Guide](docs/USER_GUIDE.md)** - Installation, usage, troubleshooting
- **[README](README.md)** - This file (project overview)

### Domain Documentation
- **[Design & Implementation](docs/design/)** - Architecture decisions, ADRs, technical specs

### Validation & Verification
- **[Validation Quick Reference](validation/VALIDATION_QUICK_REFERENCE.md)** - Testing patterns
- **[Edge Cases](validation/DOMAIN_EDGE_CASES.md)** - Known limitations and workarounds
- **[Player Guarantees](validation/PLAYER_GUARANTEES.md)** - System guarantees

### Feature Guides
- **[Progression Simulator](features/PROGRESSION_SIMULATOR_README.md)** - Character progression system
- **[Music System](features/MUSIC_SYSTEM.md)** - Audio and music features

### GUI Documentation
- **[GUI Quick Start](gui/QUICKSTART_GUI.md)** - 5-minute PyQt6 walkthrough
- **[Implementation Summary](gui/GUI_IMPLEMENTATION_SUMMARY.md)** - Architecture overview

### Platform-Specific
- **[Windows Setup](platform/WINDOWS_SETUP.md)** - Installation on Windows

---

## 🔍 SEO Keywords

AAA game dev, lore management system, worldbuilding software, narrative design tool, RPG campaign manager, DDD architecture, domain-driven design, hexagonal architecture, multi-tenant game system, game data validation, lore version control, collaborative worldbuilding, game content management, RPG toolkit, digital storytelling, game narrative software, lore database, game world editor, player progression tracking, game event timeline, cross-platform game tool, game development utilities, creative writing software, campaign planning tool, adventure game editor, game lore backup, lore import export, game design workflow, story-driven game tools, quest management, character progression, skill trees, inventory system, crafting mechanics, economy simulation, faction system, reputation system, karma system, social class system, legendary items, epic loot, quest rewards, achievements system, leaderboards, PvP balance, PvE balance, difficulty scaling, loot tables, economy balance, drop rates, conversion rates, heatmaps, player metrics, session data, difficulty curves, loot table weights, campaign management, quest chains, faction hierarchies, reputation tracking, honor system, karma system, social class system, diplomatic system, trade routes, market squares, trade nodes, supply chains, demand systems, tax collection, tariffs, economic balance, inflation control, currency management, item trading, barter systems, military hierarchies, army management, fleet management, weapon systems, defense fortifications, siege engines, battalions, city management, district organization, ward systems, architecture details, plaza management, market management, port management, slums management, noble district management, biological systems, food chains, migration patterns, hibernation cycles, reproduction mechanics, extinction events, evolution systems, genetic mutation, astronomical bodies, star systems, black holes, wormholes, galactic clusters, nebulae, solar systems, planetary bodies, lunar cycles, eclipses, solstices, weather patterns, catastrophic events, natural disasters, miracles, divine interventions, atmospheric systems, environmental effects, visual effects, particle systems, shader programming, lighting setups, color palettes, cinematographic elements, cutscenes, cinematic events, camera movements, transitions, fades, flashbacks, narrative plot devices, deus ex machina, chekhov's gun, foreshadowing, flash forwards, red herrings, world events, seasonal events, invasions, plagues, famines, wars, revolutions, fast travel points, waypoints, save points, checkpoints, autosaves, spawn points, trophy system, badge system, title system, rank progression, UGC support, modding API, custom scenario editor, share codes, workshop entries, localization tools, translation workflows, voice-over management, subtitle synchronization, dubbing quality assurance, player behavior tracking, session duration analysis, heatmaps, spatial analytics, drop rate optimization, conversion rate analysis, difficulty curves, loot table weights, economy balance, PvP balance, PvE balance, educational institutions, academies, universities, schools, libraries, research centers, archives, museums, media outlets, newspapers, radio stations, television channels, internet platforms, social media networks, propaganda systems, rumor mills, secret areas, hidden paths, easter eggs, mysteries, enigmas, riddles, puzzles, traps, legendary weapons, mythical armor, divine items, cursed artifacts, artifact sets, relic collections, musical themes, motifs, scores, soundtracks, voice lines, sound effects, ambient audio, silence control, visual effect particles, shaders, lighting setups, color palettes, cinematographic elements, cutscenes, cinematic events, camera paths, transitions, fades, flashbacks, narrative plot devices, deus ex machina, chekhov's gun, foreshadowing, flash forwards, red herrings, world events, seasonal events, invasions, plagues, famines, wars, revolutions, fast travel, waymarks, save points, checkpoints, autosaves, spawn points, achievements, trophies, badges, titles, ranks, leaderboards, mods, custom maps, user scenarios, share codes, workshop entries, localizations, translations, voice overs, subtitles, dubbings, player metrics, session data, heatmaps, drop rates, conversion rates, difficulty curves, loot table weights, economy balance, PvP balance, PvE balance

---

## 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python scripts/init_database.py
   ```

3. **Start Application**
   ```bash
   python -m src.application.main
   ```

4. **Import Sample Data** (Optional)
   ```bash
   python scripts/import_sample_lore.py
   ```

---

## 🎯 Target Users

### Narrative Designers
Create complex branching stories with moral choices and multiple endings.

### Game Designers
Implement balanced progression systems, craft engaging economies, and design fair combat mechanics.

### World Builders
Develop rich worlds with consistent lore, geography, history, and cultures.

### Quest Writers
Create engaging quest chains with clear objectives, interesting rewards, and meaningful player choices.

### QA Engineers
Test progression systems, validate game mechanics, and ensure bug-free releases.

---

## 🛡 Technical Architecture

### Hexagonal Architecture

```
┌─────────────────────────────────────────┐
│           GUI (Presentation)        │
├───────────────────┬──────────────────┤
│   Application Layer  (Business Logic)│
├───────────────────┼──────────────────┤
│      Domain Layer    (Domain Model)│
├───────────────────┼──────────────────┤
│   Infrastructure Layer (Database/Messaging)│
└───────────────────┴───────────────────┘
```

**Each layer depends only on the layer immediately below it.** This enables clean testing, independent deployment, and technology substitution.

### Domain Model Highlights

- **200+ Entities**: Covering all major AAA game dev categories
- **DDD Principles**: Repository, Factory, Aggregate, ValueObject patterns
- **Validation**: Invariant checking for all entities
- **Versioning**: Built-in version tracking (major.minor.patch)
- **Factory Methods**: Consistent `create()` pattern across all entities
- **Type Safety**: Strong typing with pydantic-like validation

---

## 📈 Roadmap

### Version 1.0 (Current) ✅
- **Domain Model**: 200+ AAA game dev entities
- **DDD Architecture**: Clean separation of concerns
- **Multi-Tenant**: Support for multiple projects
- **Validation**: Comprehensive invariant checking
- **Use Cases**: 10 documented scenarios

### Version 1.1 (Planned)
- **Real-time Collaboration**: WebSocket-based multi-user editing
- **Asset Pipeline**: Integration with game engine asset workflows
- **Live Game Support**: Hotfix deployment and version management
- **Analytics Dashboard**: Player behavior tracking and heatmaps

### Version 2.0 (Future)
- **AI-Assisted Creation**: LLM-powered lore and quest generation
- **Procedural Generation**: Automatic world and quest creation
- **Cross-Engine Support**: Unified asset pipeline for Unreal, Unity, Godot
- **VR Support**: Virtual reality world editing and exploration

---

## 🔒 Security & Privacy

### Multi-Tenant Isolation
- **Tenant Data Separation**: Each tenant's data is isolated
- **Authentication**: JWT-based authentication with role-based access
- **Authorization**: Fine-grained permissions for read/write operations
- **Audit Logging**: All changes tracked with timestamps and user IDs

### Data Protection
- **Encryption at Rest**: All sensitive data encrypted in database
- **Secure Communication**: HTTPS/TLS for all API calls
- **Input Validation**: Strict validation on all user inputs
- **SQL Injection Prevention**: Parameterized queries and input sanitization

---

## 🤝 Contributing

### Code of Conduct
- **Respect**: Treat all contributors and users with respect
- **Inclusion**: Welcome contributions from diverse backgrounds
- **Quality**: Maintain high code standards and documentation

### Development Workflow
1. Fork the repository
2. Create a feature branch (`feature/amazing-new-entity`)
3. Make your changes with tests
4. Submit a pull request
5. Wait for review and merge

### Commit Message Standards
```
feat: Add [category] entity for [purpose]

Added [EntityName] to domain model with:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Updated docs/ and added import to __init__.py.
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with ❤️ for the AAA game development community.
