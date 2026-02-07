# MythWeave Chronicles

Complete lore management system for AAA game development with DDD architecture.

## Features

- **Domain Model**: 200+ AAA game dev entities across 34 categories
- **DDD Architecture**: Clean separation of concerns with domain, application, infrastructure layers
- **Multi-tenant**: Support for multiple projects/tenants
- **Validation**: Comprehensive invariant validation for all entities
- **Factory Methods**: Consistent entity creation pattern
- **Version Control**: Automatic version tracking for all entities
- **Repository Pattern**: Clean data access with In-Memory and SQLite implementations

## What's Working

### ✅ Fully Functional (11 repository interfaces + 3 supporting implementations)

These are accessible via the repository layer with full CRUD operations:

**Core Lore System:**
- **WorldRepository** - Create/list/delete worlds (core of the system)
- **CharacterRepository** - Manage characters within worlds
- **StoryRepository** - Create and organize stories
- **PageRepository** - Manage content pages

**World Building:**
- **ItemRepository** - Items and inventory items
- **LocationRepository** - World locations and areas
- **EnvironmentRepository** - Environmental settings (time, weather, lighting)
- **EventRepository** - Timeline events (no interface, but working)
- **TextureRepository** - 3D textures (no interface, but working)
- **Model3DRepository** - 3D models (no interface, but working)

**Organization:**
- **SessionRepository** - Track active game sessions
- **TagRepository** - Tag-based content organization
- **NoteRepository** - GM notes and annotations
- **TemplateRepository** - Reusable content templates

### ❌ Not Yet Implemented

These interfaces exist in the domain layer but don't have repository implementations:

- ChoiceRepository, FlowchartRepository, HandoutRepository
- ImageRepository, InspirationRepository, MapRepository
- TokenboardRepository

### ⏸️ In Domain Model Only

These 180+ entities exist in `src/domain/entities/` but aren't exposed through repositories yet:

**Quests & Progression:**
- QuestChain, QuestNode, QuestPrerequisite, QuestObjective, QuestTracker, QuestGiver
- Skill, Perk, Trait, Attribute, Experience, LevelUp, TalentTree, Mastery

**Factions & Politics:**
- FactionHierarchy, FactionIdeology, FactionLeader, FactionResource, FactionTerritory
- Era, EraTransition, Timeline, Calendar, Nation, Kingdom, Empire, Government, Alliance

**Economy & Military:**
- Trade, Barter, Tax, Tariff, Supply, Demand, Price, Inflation
- Army, Fleet, WeaponSystem, Defense, Fortification, SiegeEngine, Battalion

**Social & Religion:**
- Reputation, Affinity, Disposition, Honor, Karma, SocialClass, SocialMobility
- Cult, Sect, HolySite, Scripture, Ritual, Oath, Summon, Pact, Curse, Blessing

**Locations & World Building:**
- HubArea, Instance, Dungeon, Raid, Arena, OpenWorldZone, Skybox, Dimension

**UGC & Localization:**
- Mod, CustomMap, UserScenario, ShareCode, WorkshopEntry
- Localization, Translation, VoiceOver, Subtitle, Dubbing

**Analytics & Balance:**
- PlayerMetric, SessionData, Heatmap, DropRate, ConversionRate
- DifficultyCurve, LootTableWeight, BalanceEntities

**And 100+ more...**

Run `python3 check_repositories.py` to see detailed coverage report.

## Coverage

**Repository Interfaces:** 11/18 defined in domain layer = 61.1%
**Domain Entities:** 200+ defined, ~14 exposed through repositories = ~7%

The system is production-ready for core lore management. Additional entities can be exposed by defining repository interfaces and implementing them in both In-Memory and SQLite.

## Quick Start

- [User Guide](docs/USER_GUIDE.md) - Installation and usage instructions
- [Documentation Index](docs/README.md) - Full documentation navigation

## Architecture

- **Domain Layer**: 200+ entities with DDD structure
- **Application Layer**: Services, repositories, DTOs
- **Infrastructure Layer**: Database, caching, messaging
- **Hexagonal Architecture**: Ports and adapters for clean integration

## Documentation

- **[Design & Implementation](docs/design/)** - Architecture decisions, ADRs, technical specs
- **[Validation & Verification](docs/validation/)** - Test reports, edge cases, guarantees
- **[Feature Guides](docs/features/)** - Detailed feature documentation
- **[GUI Documentation](docs/gui/)** - PyQt6 application guides

## Next Steps

1. Implement remaining 7 repository interfaces with In-Memory + SQLite
2. Define repository interfaces for commonly used domain entities (Quests, Skills, Factions)
3. Add repository implementations for newly defined interfaces

## SEO Keywords

AAA game dev, lore management system, worldbuilding software, narrative design tool, RPG campaign manager, DDD architecture, domain-driven design, hexagonal architecture, multi-tenant game system, game data validation, lore version control, collaborative worldbuilding, game content management, RPG toolkit, digital storytelling, game narrative software, lore database, game world editor, player progression tracking, game event timeline, cross-platform game tool, game development utilities
