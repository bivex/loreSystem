# LoreForge System - Comprehensive Implementation Guide

## Quick Start

### Prerequisites

```bash
# Install Python 3.11+
python3 --version

# Install PostgreSQL 15+
brew install postgresql@15  # macOS
# or apt-get install postgresql-15  # Linux

# Install Elasticsearch 8+
brew install elasticsearch  # macOS

# Install Git
git --version
```

### Setup

```bash
# 1. Clone and setup environment
cd /Volumes/External/Code/loreSystem
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 4. Initialize database
createdb lore_system
alembic upgrade head

# 5. Initialize Elasticsearch
elasticsearch  # Start in another terminal
python migrations/elasticsearch/init_indices.py

# 6. Run tests
pytest tests/ -v

# 7. Format code
black src/ tests/
isort src/ tests/
```

## Architecture Overview

### Domain-Driven Design Principles Applied

This system is built following strict DDD and clean architecture principles:

#### 1. **Ubiquitous Language**

All code uses domain terminology:
- `World`: Game universe containing lore
- `Character`: Actor with backstory and abilities
- `Event`: Story occurrence with participants
- `Improvement`: Validated enhancement proposal
- `Requirement`: Business rule that must be preserved

#### 2. **Layered Architecture**

```
┌─────────────────────────────────────┐
│  Presentation (CLI, API - Future)   │  ← Entry points
├─────────────────────────────────────┤
│  Application (Use Cases)            │  ← Orchestration
├─────────────────────────────────────┤
│  Domain (Entities, Value Objects)   │  ← Pure business logic
├─────────────────────────────────────┤
│  Infrastructure (DB, Git, ES)       │  ← Adapters
└─────────────────────────────────────┘
```

**Dependency Rule**: Inner layers never depend on outer layers.

#### 3. **Domain Model**

**Entities** (with identity):
- `World`: Aggregate root for lore
- `Character`: Part of World aggregate
- `Event`: Part of World aggregate
- `Improvement`: Separate aggregate
- `Requirement`: Separate aggregate

**Value Objects** (immutable, compared by value):
- `WorldName`, `CharacterName`: Validated names
- `Backstory`: Minimum 100 chars enforced
- `Ability`: Composite (name, description, power_level)
- `Version`: Optimistic concurrency control
- `Timestamp`: UTC timezone enforcement

**Invariants** (always true):
- World names unique per tenant
- Character backstories ≥ 100 characters
- Events must have ≥ 1 participant
- Versions increase monotonically
- All timestamps in UTC

#### 4. **Repository Pattern**

**Interfaces** (in domain layer):
```python
class IWorldRepository(ABC):
    @abstractmethod
    def save(self, world: World) -> World: ...
    
    @abstractmethod
    def find_by_id(self, tenant_id, world_id) -> Optional[World]: ...
```

**Implementations** (in infrastructure layer):
- `SqlWorldRepository`: PostgreSQL adapter
- `EsWorldRepository`: Elasticsearch adapter (future)

#### 5. **Use Cases**

Each use case is a single application operation:

```python
class CreateWorldUseCase:
    def execute(self, request: CreateWorldDTO) -> WorldDTO:
        # 1. Validate input
        # 2. Check business rules
        # 3. Create domain entity
        # 4. Persist
        # 5. Return DTO
```

## Database Design

### SQL Schema (PostgreSQL)

**Design Principles**:
- Normalized to 3NF (no redundant data)
- Constraints enforce invariants
- Triggers for auditing only (not business logic)
- Optimistic locking via `version` column
- Multi-tenancy via `tenant_id`

**Key Tables**:

```sql
tenants (id, name)
  ↓
worlds (id, tenant_id, world_name, description, version)
  ↓
characters (id, world_id, character_name, backstory, status)
  ↓
abilities (id, character_id, ability_name, power_level)

events (id, world_id, event_name, start_date, end_date, outcome)
  ↓
event_participants (event_id, character_id)  -- Many-to-many
```

**Constraints**:
```sql
CHECK (LENGTH(backstory) >= 100)  -- Domain rule
CHECK (power_level BETWEEN 1 AND 10)  -- Game balance
CHECK (end_date >= start_date)  -- Temporal validity
UNIQUE (tenant_id, world_name)  -- Business uniqueness
```

### Elasticsearch Mappings

**Purpose**: Full-text search and analytics (not source of truth).

**Design Principles**:
- Strict mappings (no dynamic fields)
- Denormalized for query performance
- Custom analyzers for lore text
- Nested objects for complex queries

**Indices**:
- `lore_worlds`: World documents
- `lore_characters`: Character documents (with nested abilities)
- `lore_events`: Event documents (with denormalized participant names)
- `lore_improvements`: Improvement proposals
- `lore_requirements`: Business rules

**Denormalization Example**:
```json
{
  "character_name": "Hero",
  "world_name": "Eternal Forge",  // Denormalized from worlds table
  "backstory": "...",
  "abilities": [  // Nested for sub-queries
    {"name": "Flight", "power_level": 8}
  ],
  "avg_power_level": 8.0  // Pre-calculated
}
```

## Git Integration Strategy

### Lore Storage in Git

**Structure**:
```
lore-repo/
├── worlds/
│   └── eternal-forge.json
├── characters/
│   └── eternal-forge/
│       └── hero.json
├── events/
│   └── eternal-forge/
│       └── first-quest.json
└── improvements/
    └── proposed/
        └── hero-new-ability.json
```

**Workflow**:
1. Developer proposes improvement → Creates Git branch
2. CI runs validation tests (checks requirements)
3. On approval → Merge to main
4. Webhook triggers sync to PostgreSQL/ES

**Benefits**:
- Full history of lore evolution
- Code review for narrative changes
- Community contributions via PRs
- Rollback capability (git revert)

## Safe Migrations Without Breaking Requirements

### Strategy

1. **Backward-Compatible Schema Changes**
   ```sql
   -- Good: Add column with default
   ALTER TABLE characters ADD COLUMN power_class VARCHAR(50) DEFAULT 'normal';
   
   -- Bad: Remove column (breaking)
   -- ALTER TABLE characters DROP COLUMN backstory;  -- DON'T DO THIS
   ```

2. **Validation Pipeline**
   ```
   Improvement Proposed
     ↓
   Run Requirement Checks (SQL queries)
     ↓
   If Violations → Reject
     ↓
   If Pass → Stage in separate table
     ↓
   Human Approval
     ↓
   Apply (within transaction)
     ↓
   Re-check Requirements
     ↓
   Commit or Rollback
   ```

3. **Requirement Examples**
   ```sql
   INSERT INTO requirements (description, entity_type, entity_id)
   VALUES (
     'Character "Hero" cannot have backstory changed to less than 200 chars',
     'character',
     123
   );
   ```

4. **Automated Checks**
   ```python
   def validate_improvement(improvement: Improvement) -> List[Violation]:
       # Query requirements for this entity
       requirements = requirement_repo.find_for_entity(
           improvement.entity_type,
           improvement.entity_id
       )
       
       # Apply improvement in test transaction
       with db.transaction() as tx:
           apply_improvement(improvement)
           violations = check_requirements(requirements)
           tx.rollback()  # Always rollback test
       
       return violations
   ```

## Improvement Generation Engine

### Architecture

```python
class ImprovementGenerator:
    def generate(self, context: LoreContext) -> List[Improvement]:
        # 1. Analyze current lore (SQL queries)
        weak_characters = find_characters_with_few_abilities()
        
        # 2. Generate suggestions (LLM or procedural)
        suggestions = []
        for char in weak_characters:
            prompt = f"Suggest new ability for {char.name} in {world.name}"
            suggestion = llm.generate(prompt)
            suggestions.append(suggestion)
        
        # 3. Validate against requirements
        valid_suggestions = []
        for s in suggestions:
            if not violates_requirements(s):
                valid_suggestions.append(s)
        
        return valid_suggestions
```

### Integration Points

1. **Scheduled**: Cron job runs weekly
2. **On-demand**: CLI command `lore generate-improvements`
3. **Event-driven**: After major lore update

## Testing Strategy

### Unit Tests (Fast)

Test domain logic in isolation:
```python
def test_character_cannot_have_short_backstory():
    with pytest.raises(ValueError):
        Backstory("Too short")  # < 100 chars
```

### Integration Tests (Medium)

Test repository implementations:
```python
@pytest.mark.integration
def test_world_repository_save_and_find(db_session):
    repo = SqlWorldRepository(db_session)
    world = World.create(...)
    
    saved = repo.save(world)
    found = repo.find_by_id(saved.id)
    
    assert found.name == saved.name
```

### E2E Tests (Slow)

Test full workflows:
```python
@pytest.mark.e2e
def test_create_world_to_elasticsearch_sync():
    # Create world via use case
    use_case = CreateWorldUseCase(...)
    world_dto = use_case.execute(CreateWorldDTO(...))
    
    # Verify in PostgreSQL
    assert db.query(...).count() == 1
    
    # Trigger sync
    sync_service.sync_world_to_es(world_dto.id)
    
    # Verify in Elasticsearch
    result = es.get(index='lore_worlds', id=world_dto.id)
    assert result['_source']['world_name'] == world_dto.name
```

## Example: LoreForge Chronicles Game

### Game Mechanics Integration

```python
# In game code
def player_summons_character(character_id: int):
    # Query lore system
    character = lore_client.get_character(character_id)
    
    # Create game entity from lore
    game_character = GameCharacter(
        name=character.name,
        backstory=character.backstory,
        abilities=[
            GameAbility(a.name, a.power_level)
            for a in character.abilities
        ]
    )
    
    return game_character
```

### Dynamic Lore Updates

```python
# When player completes quest
def on_quest_completed(event_id: int):
    # Mark event as completed in lore system
    event_dto = CompleteEventDTO(
        event_id=event_id,
        outcome='success',
        end_date=datetime.now(UTC)
    )
    use_case.execute(event_dto)
    
    # Generate follow-up improvements
    generator.generate_quest_consequences(event_id)
```

### Community Contributions

1. Player proposes lore change via in-game form
2. System creates Git branch with JSON file
3. Community votes in game
4. If approved → PR merged → Lore updated
5. Next patch: New character/quest appears

## Performance Considerations

### Optimization Strategies

1. **Database**:
   - Connection pooling (10 connections)
   - Prepared statements
   - Composite indexes on (tenant_id, frequently_queried_field)
   - Partitioning by tenant for huge datasets

2. **Elasticsearch**:
   - Bulk indexing (batch 100 documents)
   - Aliases for zero-downtime reindexing
   - Aggregation caching

3. **Application**:
   - DTO projection (don't load full entities for lists)
   - Lazy loading of relationships
   - Cache frequently accessed data (worlds list)

4. **Git**:
   - Shallow clones for CI
   - Batch commits for imports

## Monitoring and Observability

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "world_created",
    world_id=world.id,
    tenant_id=world.tenant_id,
    duration_ms=123
)
```

### Metrics

- World creation rate (per tenant)
- Improvement approval rate
- Requirement violation count
- Query latency (p50, p95, p99)

### Alerts

- Spike in requirement violations → Review recent changes
- Slow queries → Add index
- Elasticsearch sync lag → Scale up

## Security

### Multi-Tenancy Isolation

```sql
-- Row Level Security (PostgreSQL)
CREATE POLICY tenant_isolation ON worlds
    USING (tenant_id = current_setting('app.current_tenant')::int);
```

### Secrets Management

```bash
# Never commit secrets
DATABASE_PASSWORD=secret  # .env file (gitignored)
OPENAI_API_KEY=sk-...     # Environment variable
```

### Audit Log

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER,
    user_id INTEGER,
    action VARCHAR(50),  -- CREATE, UPDATE, DELETE
    entity_type entity_type,
    entity_id INTEGER,
    changes JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Future Enhancements

1. **GraphQL API**: Query lore with flexible schema
2. **Event Sourcing**: Store all changes as events
3. **CQRS**: Separate read/write models
4. **Multi-region**: Deploy PostgreSQL replicas
5. **Vector Search**: Semantic similarity for lore elements
6. **Blockchain**: Immutable lore history (if needed)

## Contributing

See `CONTRIBUTING.md` for guidelines.

## License

MIT
