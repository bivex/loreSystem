# MythWeave Chronicles - Git-Based Lore Management System

A domain-driven, event-sourced lore management system for games using Git version control, SQL for structured data, and safe improvement generation.

## Domain Overview

### Core Business Value
Manage evolving game lore (worlds, characters, events) with:
- Version-controlled narrative through Git
- Structured querying via SQL/Elasticsearch
- Safe, validated improvements that preserve story integrity
- Multi-tenant support for different games/campaigns

### Ubiquitous Language

**Domain Terms:**
- **Lore**: The collective narrative, world-building, and story elements of a game
- **World**: A game universe containing characters, events, and locations
- **Character**: An actor in the world with backstory, abilities, and relationships
- **Event**: A significant occurrence in the timeline (quests, battles, story beats)
- **Ability**: A character's skill or power with defined mechanics
- **Improvement**: A proposed enhancement to lore that must be validated
- **Requirement**: A business rule or invariant that must never be violated
- **Aggregate**: A consistency boundary for related entities
- **Tenant**: An isolated game or campaign instance

**Invariants:**
- World names must be unique per tenant
- Character backstories must be >= 100 characters
- Events must have at least one participant
- Improvements cannot violate existing requirements
- All dates stored in UTC
- Version numbers monotonically increase

## Architecture

### Bounded Contexts
1. **Lore Management** - Core domain for worlds, characters, events
2. **Improvement Generation** - Procedural/AI enhancement proposals
3. **Validation** - Requirement checking and invariant enforcement
4. **Version Control** - Git integration and synchronization
5. **Search** - Full-text and semantic search via Elasticsearch

### Layers (Hexagonal Architecture)
```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│    (PyQt6 GUI, CLI, API - Future)       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Application Layer (Use Cases)      │
│  - CreateWorld, AddCharacter            │
│  - GenerateImprovements, ApplyChanges   │
│  - SyncWithGit, ValidateRequirements    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Domain Layer (Pure)            │
│  Entities, Value Objects, Aggregates    │
│  Domain Services, Events, Invariants    │
└─────────────────┬───────────────────────┘
                  │ (depends on abstractions)
┌─────────────────▼───────────────────────┐
│    Infrastructure Layer (Adapters)      │
│  - PostgreSQL Repository                │
│  - Elasticsearch Repository             │
│  - Git Service                          │
│  - LLM Generation Service               │
└─────────────────────────────────────────┘
```

## Technology Stack

- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+ (ACID, constraints, JSON support)
- **Search**: Elasticsearch 8+ (full-text, aggregations)
- **Version Control**: Git (libgit2/pygit2)
- **Migrations**: Alembic (SQL), custom scripts (ES)
- **Testing**: Pytest, Testcontainers
- **Validation**: Pydantic for schemas
- **DI**: dependency-injector
- **Logging**: structlog

## Project Structure

```
loreSystem/
├── docs/                      # Documentation and ADRs
│   ├── adr/                   # Architectural Decision Records
│   ├── domain-model.md        # Domain model documentation
│   └── api-contracts.md       # API specifications
├── src/
│   ├── domain/                # Pure domain layer (no dependencies)
│   │   ├── entities/          # Entities and aggregates
│   │   ├── value_objects/     # Immutable value objects
│   │   ├── events/            # Domain events
│   │   ├── services/          # Domain services (pure logic)
│   │   ├── repositories/      # Repository interfaces (ports)
│   │   └── exceptions/        # Domain exceptions
│   ├── application/           # Use cases and orchestration
│   │   ├── use_cases/         # Application use cases
│   │   ├── dto/               # Data transfer objects
│   │   ├── validators/        # Input validation
│   │   └── services/          # Application services
│   ├── infrastructure/        # External concerns (adapters)
│   │   ├── persistence/       # SQL and ES implementations
│   │   ├── git/               # Git integration
│   │   ├── generation/        # AI/procedural generation
│   │   ├── config/            # Configuration management
│   │   └── logging/           # Structured logging
│   └── presentation/          # Entry points (future: API, CLI)
│       └── cli/               # Command-line interface
├── migrations/                # Database migrations
│   ├── sql/                   # Alembic migrations
│   └── elasticsearch/         # ES mapping versions
├── tests/
│   ├── unit/                  # Fast, isolated tests
│   ├── integration/           # Repository and adapter tests
│   └── e2e/                   # End-to-end scenarios
├── config/                    # Configuration files
│   ├── config.yaml            # Application config
│   └── logging.yaml           # Logging configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
└── pyproject.toml            # Project metadata and tools
```

## Key Design Decisions

### 1. Aggregates and Boundaries
- **World Aggregate**: Root for characters and events (consistency boundary)
- **Improvement Aggregate**: Separate lifecycle from lore entities
- **Requirement Aggregate**: Independent validation rules

### 2. Repository Pattern
- Abstract interfaces in domain layer
- Concrete implementations in infrastructure
- Support for both SQL (transactional) and ES (search)

### 3. Domain Events
- CharacterCreated, EventOccurred, ImprovementProposed
- Eventually consistent updates to Elasticsearch
- Audit trail for all changes

### 4. Validation Strategy
- Domain invariants enforced by entities (e.g., in constructors)
- Business rules checked by domain services
- Requirements validated before applying improvements
- SQL constraints as final safety net

### 5. Git Integration
- Lore stored as structured files (JSON/YAML)
- Sync on merge to main branch (CI/CD webhook)
- Bidirectional sync: Git → SQL ← Application

## Getting Started

```bash
## Getting Started

### Quick Setup (macOS with Homebrew Python)

```bash
# Clone or navigate to the project
cd /path/to/loreSystem

# Create virtual environment (required for externally managed environments)
python3 -m venv venv
source venv/bin/activate

# Install dependencies in virtual environment
pip install "PyQt6>=6.6.1" "pydantic>=2.5.3" dataclasses-json

# Run sample demo (tests domain layer)
python3 sample_demo.py

# Launch GUI Editor
python3 run_gui.py

# OR use the convenience script
./launch_gui.sh
```

### Alternative: Use the Launcher Script

The project includes a convenience script that handles setup automatically:

```bash
# Make script executable (first time only)
chmod +x launch_gui.sh

# Run the launcher (handles venv creation and dependency installation)
./launch_gui.sh
```

### Full Development Setup

For complete development environment with all dependencies:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies (may need to adjust Python version constraints)
# Edit requirements.txt to remove 'python>=3.11,<3.13' if using Python 3.14+
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run database migrations (requires PostgreSQL)
alembic upgrade head

# Initialize Elasticsearch indices (requires Elasticsearch)
python -m src.infrastructure.persistence.elasticsearch.init_indices

# Run tests
pytest tests/

# Run sample demo
python3 sample_demo.py

# Start GUI Editor
python3 run_gui.py
```

### GUI Quick Start

1. **Launch the GUI**:
   ```bash
   ./launch_gui.sh
   ```

2. **Load Sample Data**:
   - Click "Load" button
   - Navigate to `examples/sample_lore.json`
   - Click "Open"

3. **Create Your Own Lore**:
   - **Worlds Tab**: Add game worlds
   - **Characters Tab**: Create characters with abilities
   - **Save**: Use "Save As" to create your lore files

See [GUI Quick Start Guide](QUICKSTART_GUI.md) for detailed tutorial.

## System Capabilities

MythWeave provides comprehensive lore management with:

### Domain Modeling
- **Rich Entity Relationships**: Complex interconnections between worlds, characters, events, and factions
- **Temporal Tracking**: Full timeline management with event sequencing and dependencies
- **Validation Framework**: Domain-driven validation ensuring lore consistency
- **Version Control Integration**: Git-based versioning for collaborative lore development

### Advanced Game Mechanics
- **Gacha Systems**: Complete banner, pity, and pull mechanics for character collection games
- **Economy Simulation**: Multi-currency systems with shops, purchases, and rewards
- **Progression Systems**: Character advancement with state tracking and milestone events
- **Faction Dynamics**: Political systems with reputations, memberships, and relationships

### Content Management
- **Multimedia Support**: Images, audio tracks, and rich text content
- **Template System**: Reusable content templates for consistent world-building
- **Tagging & Organization**: Hierarchical organization with tags and categories
- **Search & Discovery**: Full-text search across all lore content

### Technical Architecture
- **Event Sourcing**: All changes tracked as domain events for audit and replay
- **Multi-tenant Support**: Isolated game worlds and campaigns
- **Scalable Persistence**: SQL for transactions, Elasticsearch for search
- **API-Ready Design**: Clean architecture supporting future API development

## GUI Features

MythWeave includes a comprehensive PyQt6-based graphical editor with modern UI/UX:

### Core Lore Management
- **Worlds Management**: Create, edit, delete game worlds with descriptions and versioning
- **Characters Management**: Add characters with detailed backstories, abilities, and relationships
- **Events Management**: Create timeline events with participants, outcomes, and story impact
- **Items Management**: Manage game items with rarity levels, types, and properties
- **Quests Management**: Design quests with objectives, rewards, and progression tracking
- **Storylines Management**: Organize narrative arcs connecting events and quests
- **Stories Management**: Write and manage individual story entries with rich content
- **Improvements System**: Propose and manage lore enhancements with validation workflow

### Content Creation Tools
- **Pages Management**: Create structured content pages for documentation
- **Templates Management**: Design reusable templates for consistent content creation
- **Choices Management**: Build interactive choice systems for branching narratives
- **Flowcharts Management**: Visualize complex story flows and decision trees
- **Handouts Management**: Create player handouts and reference materials
- **Inspirations Management**: Collect and organize creative inspiration sources
- **Notes Management**: Maintain organized notes with categorization
- **Tags Management**: Tag and categorize all content for easy searching
- **Images Management**: Manage image assets with metadata and organization

### World Building
- **Locations Management**: Define geographical locations with descriptions and connections
- **World Map Integration**: Visual world mapping with location relationships
- **Factions Management**: Create political factions with reputations and relationships
- **Character Relationships**: Map complex character interactions and alliances
- **Faction Memberships**: Track character affiliations and faction dynamics

### Economy & Gacha Systems
- **Shops Management**: Design in-game shops with inventory and pricing
- **Currencies Management**: Define multiple currency types and exchange rates
- **Banners Management**: Create gacha banners with character pools and rates
- **Pity Systems**: Implement pity timers and guaranteed pulls
- **Pull Systems**: Manage gacha pull mechanics and probabilities
- **Purchases Management**: Track player purchases and transaction history
- **Rewards Management**: Design reward systems and distribution mechanics
- **Player Profiles**: Manage player accounts and progression data

### Event & Progression Systems
- **Event Chains**: Create interconnected event sequences with dependencies
- **Progression Simulator**: Test and simulate player progression paths
- **Progression Events**: Define milestone events and achievements
- **Progression States**: Track character state changes and evolution

### Audio & Media Integration
- **Music Themes**: Organize music by thematic categories and moods
- **Music Tracks**: Manage individual music files with metadata
- **Music Controls**: Real-time music playback and control systems
- **Music States**: Dynamic music state management for adaptive audio

### Advanced Features
- **Lore Axioms**: Define fundamental rules and constraints for your world
- **Requirements Management**: Set up validation rules and business constraints
- **Sessions Management**: Track gaming sessions and campaign progress
- **Tokenboards**: Visual token management for tabletop gaming integration

### Technical Features
- **JSON Persistence**: Load/save complete lore systems as JSON files
- **Real-time Validation**: Immediate feedback on domain rule violations
- **Search & Filter**: Powerful search across all entities with filtering
- **Modern UI**: Dark theme with intuitive navigation and tabbed interface
- **Sample Data**: Pre-loaded examples for quick exploration
- **Export/Import**: Easy data portability and backup capabilities

See [GUI Quick Start Guide](QUICKSTART_GUI.md) for detailed tutorials and [GUI Documentation](src/presentation/gui/README.md) for technical details.

```bash
# Linux/macOS: Launch GUI (easiest way)
./launch_gui.sh

# OR manual setup
python3 -m venv venv
source venv/bin/activate
pip install "PyQt6>=6.6.1" "pydantic>=2.5.3" dataclasses-json
python3 run_gui.py
```

```cmd
REM Windows: Launch GUI (easiest way)
launch_gui.bat

REM Windows: Auto-install Python if missing (requires admin)
launch_gui.bat --auto-install

REM Windows: Manual setup
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python run_gui.py
```

## Safety and Non-Breaking Updates

### Migration Strategy
1. **Backward-compatible schema changes**
   - Add columns with defaults
   - Expand enums, never remove values
   - Use feature flags for new behavior

2. **Zero-downtime deployments**
   - Blue-green database deployment
   - Elasticsearch reindexing with aliases

3. **Validation pipeline**
   - Pre-commit hooks validate lore files
   - CI runs requirement checks
   - Staging environment for integration tests

4. **Rollback capability**
   - Git revert for lore changes
   - Alembic downgrade for schema
   - Elasticsearch snapshots

## Example: MythWeave Chronicles Game

A gacha RPG where:
- Players collect characters through procedurally-generated narratives
- Lore evolves weekly with community input (Git PRs)
- All changes validated against story requirements
- Dynamic worlds generated from SQL data
- AI suggests improvements (new quests, character abilities)

## License

MIT
