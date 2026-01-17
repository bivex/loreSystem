# Changelog

All notable changes to the LoreForge project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - PyQt6 GUI (2024-01-19)

#### Presentation Layer
- **PyQt6 Graphical Editor** (`src/presentation/gui/lore_editor.py`)
  - MainWindow with tabbed interface
  - WorldsTab for world CRUD operations
  - CharactersTab for character management with abilities
  - AbilityDialog for creating/editing abilities
  - LoreData class for in-memory storage with JSON serialization
  - Full integration with domain entities and validation
  - Load/Save functionality for JSON files
  - Real-time validation feedback
  - Status bar with file tracking

#### Features
- **Worlds Management**
  - Create, read, update, delete worlds
  - Table view with selection
  - Form-based editing
  - Version tracking
  
- **Characters Management**
  - Create characters with world assignment
  - Backstory validation (≥100 characters)
  - Multiple abilities per character
  - Power level management (1-10 scale)
  - Status tracking (active/inactive)
  - Dynamic ability list
  
- **Abilities System**
  - Add/remove abilities via dialog
  - Power level constraints (1-10)
  - Duplicate prevention
  - Visual list display
  
- **Data Persistence**
  - Save lore to JSON files
  - Load existing lore projects
  - New file creation
  - Save As functionality

#### Documentation
- **GUI README** (`src/presentation/gui/README.md`)
  - Complete feature documentation
  - Architecture explanation
  - Data format specification
  - Validation rules guide
  - Troubleshooting section
  
- **Quick Start Guide** (`QUICKSTART_GUI.md`)
  - Installation instructions
  - Step-by-step tutorial
  - Common tasks and workflows
  - Tips and tricks
  - Example usage
  
- **Implementation Summary** (`docs/GUI_IMPLEMENTATION_SUMMARY.md`)
  - Technical details
  - Architecture compliance
  - Code quality metrics
  - Testing performed
  - Future enhancements

#### Examples
- **Sample Lore** (`examples/sample_lore.json`)
  - 2 worlds (Eternal Forge, Shadowmere Wastes)
  - 3 characters with rich backstories
  - 9 abilities across characters
  - 2 events (ongoing and completed)

#### Scripts
- **GUI Launcher** (`run_gui.py`)
  - Simple entry point for starting the editor
  - Executable script with proper imports

#### Updates
- **requirements.txt**: Added PyQt6>=6.6.1
- **README.md**: Added GUI section and quick start
- **STRUCTURE.md**: Added presentation layer documentation

## [0.1.0] - 2024-01-18 - Initial Domain Model

### Added - Domain Layer
- **Entities**
  - World aggregate root with factory methods
  - Character entity with abilities
  - Event entity with participants
  - Improvement aggregate with state machine
  - Requirement aggregate for validation rules

- **Value Objects**
  - TenantId, EntityId, WorldName, CharacterName
  - Backstory (≥100 chars), Description
  - Ability composite VO with PowerLevel (1-10)
  - Version, Timestamp, DateRange
  - EntityType, ImprovementStatus, EventOutcome enums

- **Repository Interfaces**
  - IWorldRepository
  - ICharacterRepository
  - Abstract persistence contracts

- **Exceptions**
  - DomainException base
  - InvariantViolation
  - EntityNotFound
  - DuplicateEntity

### Added - Application Layer
- **DTOs**
  - WorldDTO, CreateWorldDTO
  - CharacterDTO, CreateCharacterDTO
  - EventDTO, CreateEventDTO
  - ImprovementDTO, RequirementDTO

- **Use Cases**
  - CreateWorldUseCase with validation and persistence

### Added - Infrastructure Layer
- **PostgreSQL Schema** (`migrations/sql/schema.sql`)
  - 8 tables with constraints and triggers
  - Enums for entity types and statuses
  - Indexes for performance
  - Views for common queries
  - Auto-versioning triggers

- **Alembic Migrations**
  - Initial migration (001_initial.py)
  - Environment configuration
  - Migration templates

- **Elasticsearch Mappings**
  - 5 indices: worlds, characters, events, improvements, requirements
  - Strict schema with analyzers
  - Nested objects for abilities
  - Custom lore_analyzer

- **Initialization Scripts**
  - Elasticsearch index creation
  - Schema validation

### Added - Documentation
- **README.md** - Project overview and quick start
- **PROJECT_SUMMARY.md** - Comprehensive implementation summary
- **IMPLEMENTATION_GUIDE.md** - Detailed guide (500+ lines)
- **STRUCTURE.md** - Visual project structure
- **ADRs**
  - 001: Hexagonal architecture decision
  - 002: PostgreSQL as primary database

### Added - Testing
- **Unit Tests**
  - test_world_entity.py with 12 test cases
  - Invariant validation tests
  - Factory method tests
  - State mutation tests

- **Test Configuration**
  - pytest setup with markers
  - Coverage configuration
  - Test fixtures

### Added - Configuration
- **requirements.txt** - Production dependencies
- **requirements-dev.txt** - Development dependencies
- **pyproject.toml** - Project metadata and tool config
- **config/config.yaml** - Application configuration
- **alembic.ini** - Migration configuration
- **.env.example** - Environment template
- **Makefile** - Common development commands

### Added - Demos
- **sample_demo.py** - Comprehensive domain demonstration
  - World creation
  - Character with abilities
  - Event with participants
  - Improvement workflow
  - Requirement management
  - Validation examples

## Architecture Highlights

### Hexagonal/Ports-and-Adapters
```
Presentation → Application → Domain ← Infrastructure
```

### Key Principles Applied
- Domain-Driven Design
- SOLID principles
- Clean Architecture
- Repository pattern
- Factory pattern
- Value object pattern
- Aggregate roots
- Invariant enforcement

### Technology Stack
- Python 3.11+
- PostgreSQL 15+ with constraints
- Elasticsearch 8+ for search
- Alembic for migrations
- PyQt6 for GUI
- Pytest for testing
- SQLAlchemy 2.0 ORM
- Pydantic for validation
- structlog for logging

## Project Statistics

### Code Volume
- **Total Files**: 42+
- **Lines of Code**: ~5,000+
- **Domain Layer**: 8 modules
- **Application Layer**: 3 modules
- **Infrastructure**: 4 modules
- **Presentation**: 3 modules (GUI)
- **Documentation**: ~2,500+ lines
- **Tests**: 12 test cases

### Coverage Targets
- Domain Layer: 90%+
- Application Layer: 80%+
- Infrastructure: 70%+

## Future Roadmap

### Next Release (0.2.0)
- [ ] Events tab in GUI
- [ ] Improvements workflow UI
- [ ] Requirements management UI
- [ ] Search and filter functionality
- [ ] Concrete repository implementations
- [ ] Integration tests with testcontainers

### Future Releases
- [ ] CLI presentation layer
- [ ] REST API with FastAPI
- [ ] GraphQL endpoint
- [ ] Git integration service
- [ ] LLM improvement generator
- [ ] Elasticsearch integration
- [ ] Multi-tenant authentication
- [ ] Real-time collaboration

## Breaking Changes

None yet - initial release.

## Known Issues

- GUI uses in-memory storage (JSON) instead of database
- Events tab not yet implemented in GUI
- Improvements workflow not yet in GUI
- No search functionality yet
- No undo/redo functionality

## Migration Guide

N/A - initial release.

## Contributors

- Domain modeling and architecture
- PostgreSQL schema design
- Elasticsearch mapping design
- PyQt6 GUI implementation
- Comprehensive documentation

## License

MIT License

---

For detailed information about any release, see the corresponding documentation in the `docs/` directory.
