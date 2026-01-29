# LoreSystem Project Structure

```
loreSystem/
│
├── 📘 README.md                          # Project overview and quick start
├── 📘 PROJECT_SUMMARY.md                 # Complete implementation summary
├── 🔧 requirements.txt                   # Production dependencies
├── 🔧 requirements-dev.txt               # Development dependencies
├── 🔧 pyproject.toml                     # Project configuration
├── 🔧 alembic.ini                        # Database migration config
├── 🔒 .env.example                       # Environment template
├── 🚫 .gitignore                         # Git ignore rules
│
├── 📁 docs/                              # Documentation
│   ├── 📘 IMPLEMENTATION_GUIDE.md        # Comprehensive guide (500+ lines)
│   └── 📁 adr/                           # Architectural Decision Records
│       ├── 001-hexagonal-architecture.md
│       └── 002-postgresql-primary-database.md
│
├── 📁 config/                            # Configuration files
│   └── 🔧 config.yaml                    # Application configuration
│
├── 📁 migrations/                        # Database migrations
│   ├── 📁 sql/                           # PostgreSQL migrations
│   │   ├── env.py                        # Alembic environment
│   │   ├── script.py.mako                # Migration template
│   │   ├── schema.sql                    # Full schema (350+ lines)
│   │   └── versions/
│   │       └── 001_initial.py            # Initial migration
│   └── 📁 elasticsearch/                 # Elasticsearch setup
│       ├── mappings.py                   # Index mappings (5 indices)
│       └── init_indices.py               # Index initialization script
│
├── 📁 src/                               # Source code
│   ├── __init__.py
│   │
│   ├── 📁 domain/                        # 🎯 DOMAIN LAYER (Pure Business Logic)
│   │   ├── __init__.py
│   │   │
│   │   ├── 📁 entities/                  # Entities with identity
│   │   │   ├── __init__.py
│   │   │   ├── world.py                  # World aggregate root
│   │   │   ├── character.py              # Character entity
│   │   │   ├── event.py                  # Event entity
│   │   │   ├── improvement.py            # Improvement aggregate
│   │   │   └── requirement.py            # Requirement aggregate
│   │   │
│   │   ├── 📁 value_objects/             # Immutable value objects
│   │   │   ├── __init__.py
│   │   │   ├── common.py                 # Common VOs (WorldName, Version, etc.)
│   │   │   └── ability.py                # Ability composite VO
│   │   │
│   │   ├── 📁 repositories/              # Repository interfaces (Ports)
│   │   │   ├── __init__.py
│   │   │   ├── world_repository.py       # IWorldRepository
│   │   │   └── character_repository.py   # ICharacterRepository
│   │   │
│   │   └── exceptions.py                 # Domain exceptions
│   │
│   ├── 📁 application/                   # 📋 APPLICATION LAYER (Use Cases)
│   │   ├── __init__.py
│   │   ├── dto.py                        # Data Transfer Objects
│   │   └── 📁 use_cases/
│   │       ├── __init__.py
│   │       └── create_world.py           # CreateWorldUseCase example
│   │
│   ├── 📁 infrastructure/                # 🔌 INFRASTRUCTURE LAYER (Adapters)
│   │   └── __init__.py                   # (Implementations to be added)
│   │       # Future:
│   │       # ├── persistence/
│   │       # │   ├── sql_world_repository.py
│   │       # │   └── es_world_repository.py
│   │       # ├── git/
│   │       # │   └── git_lore_service.py
│   │       # └── generation/
│   │       #     └── llm_generator.py
│   │
│   └── 📁 presentation/                  # 🖥️ PRESENTATION LAYER (UI)
│       ├── __init__.py
│       └── 📁 gui/                       # PyQt6 GUI
│           ├── __init__.py
│           ├── lore_editor.py            # Main application (800+ lines)
│           └── README.md                 # GUI documentation
│
├── 📁 examples/                          # Example data
│   └── sample_lore.json                  # Sample world, characters, events
│
├── 🚀 run_gui.py                         # GUI launcher script
├── 🚀 sample_demo.py                     # Domain demonstration
│
└── 📁 tests/                             # Tests
    ├── 📁 unit/                          # Unit tests (fast, isolated)
    │   ├── __init__.py
    │   └── test_world_entity.py          # World entity tests (12 tests)
    │
    ├── 📁 integration/                   # Integration tests (with DB)
    │   └── (to be added)
    │
    └── 📁 e2e/                           # End-to-end tests
        └── (to be added)
```

## Key Statistics

### Files Created: 42+

**Domain Layer** (8 files):
- 5 entity modules (World, Character, Event, Improvement, Requirement)
- 2 value object modules (common, ability)
- 2 repository interfaces
- 1 exceptions module

**Application Layer** (3 files):
- 1 DTOs module
- 1 use case implementation
- Supporting __init__ files

**Infrastructure** (4 files):
- 1 SQL schema (350+ lines)
- 1 Alembic migration
- 1 Elasticsearch mappings (5 indices)
- 1 ES initialization script

**Presentation Layer** (3 files):
- 1 PyQt6 GUI application (800+ lines)
- 1 GUI documentation
- 1 launcher script

**Documentation** (7 files):
- 1 README (150 lines)
- 1 Implementation Guide (500+ lines)
- 1 Project Summary (400+ lines)
- 1 GUI Quick Start Guide (400+ lines)
- 1 Structure document
- 2 ADRs (architecture decisions)

**Configuration** (6 files):
- requirements.txt (with PyQt6)
- pyproject.toml
- config.yaml
- alembic.ini
- .env.example
- .gitignore

**Tests & Examples** (3 files):
- test_world_entity.py (12 test cases)
- sample_demo.py (demonstration script)
- sample_lore.json (example data)

### Total Lines of Code: ~5,000+

### Test Coverage Targets:
- Domain Layer: 90%+ (critical business logic)
- Application Layer: 80%+
- Infrastructure: 70%+ (integration tests)

## Architecture Layers

### 🎯 Domain Layer (NO external dependencies)
- **Entities**: Objects with identity and lifecycle
- **Value Objects**: Immutable, compared by value
- **Aggregates**: Consistency boundaries
- **Repositories**: Interfaces for persistence
- **Invariants**: Enforced in entity constructors

### 📋 Application Layer (Depends on Domain)
- **Use Cases**: Orchestrate domain operations
- **DTOs**: Transfer data between layers
- **Validation**: Input checks before domain calls
- **Transactions**: Define commit boundaries

### 🔌 Infrastructure Layer (Implements Domain Ports)
- **Repositories**: Concrete implementations (SQL, ES)
- **External Services**: Git, LLM APIs
- **Configuration**: Environment-based settings
- **Logging**: Structured logging

### 🖥️ Presentation Layer (Depends on Application)
- **CLI**: Command-line interface (future)
- **REST API**: HTTP endpoints (future)
- **GraphQL**: Flexible queries (future)

## Dependency Flow

```
┌─────────────────────────────────────────────┐
│           Presentation Layer                │
│  Depends on: Application                    │
└───────────────────┬─────────────────────────┘
                    │ uses
                    ▼
┌─────────────────────────────────────────────┐
│          Application Layer                  │
│  Depends on: Domain abstractions            │
└───────────────────┬─────────────────────────┘
                    │ uses
                    ▼
┌─────────────────────────────────────────────┐
│            Domain Layer                     │
│  Depends on: NOTHING (pure)                 │
└─────────────────────────────────────────────┘
                    ▲
                    │ implements
┌───────────────────┴─────────────────────────┐
│         Infrastructure Layer                │
│  Depends on: Domain interfaces              │
└─────────────────────────────────────────────┘
```

**Rule**: Dependencies point inward only (toward domain).

## Technology Stack

| Layer          | Technologies                               |
|----------------|-------------------------------------------|
| Language       | Python 3.11+                              |
| Database       | PostgreSQL 15+ (ACID, constraints)        |
| Search         | Elasticsearch 8+ (full-text)              |
| VCS            | Git (pygit2)                              |
| Migrations     | Alembic (SQL), custom (ES)                |
| Testing        | Pytest, Testcontainers                    |
| Validation     | Pydantic                                  |
| Logging        | structlog (structured)                    |
| Code Quality   | Black, isort, mypy, pylint                |
| DI             | dependency-injector                       |

## What's Implemented vs. What's Next

### ✅ Implemented (Complete)

1. **Domain Model**: All entities, value objects, invariants
2. **Repository Interfaces**: Ports defined
3. **Database Schema**: PostgreSQL with constraints
4. **Elasticsearch Mappings**: 5 indices with strict schema
5. **Migrations**: Alembic setup with initial migration
6. **Application Layer**: DTOs and example use case
7. **Configuration**: YAML, environment variables
8. **Documentation**: README, guide, ADRs, summary
9. **Tests**: Unit test example structure
10. **Project Setup**: requirements, pyproject.toml

### 🚧 To Be Implemented (Next)

1. **Infrastructure Adapters**:
   - SqlWorldRepository (PostgreSQL implementation)
   - EsWorldRepository (Elasticsearch implementation)
   - SqlCharacterRepository
   - GitLoreService (Git operations)
   - LLMGenerationService (AI improvements)

2. **More Use Cases**:
   - CreateCharacter
   - CreateEvent
   - ProposeImprovement
   - ApplyImprovement
   - ValidateRequirements

3. **Presentation Layer**:
   - CLI with Click
   - REST API with FastAPI
   - GraphQL API (optional)

4. **Additional Tests**:
   - Integration tests for repositories
   - E2E tests for full workflows
   - Load tests for performance

5. **Deployment**:
   - Docker Compose setup
   - Kubernetes manifests
   - CI/CD pipeline (GitHub Actions)

## Quick Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Initialize Elasticsearch
python migrations/elasticsearch/init_indices.py

# Run tests
pytest tests/ -v

# Code quality
black src/ tests/
isort src/ tests/
mypy src/
```

## Notes

- **Pure Domain**: No infrastructure imports in domain layer
- **Immutable VOs**: All value objects frozen dataclasses
- **Type Safety**: Mypy enabled for static checking
- **Test Markers**: @pytest.mark.unit, .integration, .e2e
- **Migration Strategy**: Backward-compatible changes only
- **Multi-tenancy**: tenant_id in all tables
- **Concurrency**: Optimistic locking via version field
