"""
PostgreSQL Database Schema

Following DDD principles:
- Schema reflects domain model
- Normalized to 3NF, conscious denormalization where justified
- Constraints enforce invariants
- Triggers for auditing, not business logic
- Prepared for safe migrations
"""

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Enums for type safety
CREATE TYPE entity_type AS ENUM ('world', 'character', 'event');
CREATE TYPE improvement_status AS ENUM ('proposed', 'approved', 'applied', 'rejected');
CREATE TYPE event_outcome AS ENUM ('success', 'failure', 'ongoing');
CREATE TYPE character_status AS ENUM ('active', 'inactive');

-- =============================================================================
-- TENANTS TABLE
-- =============================================================================
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_tenant_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

CREATE INDEX idx_tenants_name ON tenants(name);

COMMENT ON TABLE tenants IS 'Multi-tenant isolation for different games/campaigns';
COMMENT ON COLUMN tenants.id IS 'Surrogate key for tenant';
COMMENT ON COLUMN tenants.name IS 'Unique tenant identifier';

-- =============================================================================
-- WORLDS TABLE (Aggregate Root)
-- =============================================================================
CREATE TABLE worlds (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    world_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Constraints
    CONSTRAINT chk_world_name_not_empty CHECK (LENGTH(TRIM(world_name)) > 0),
    CONSTRAINT chk_world_description_not_empty CHECK (LENGTH(TRIM(description)) > 0),
    CONSTRAINT chk_world_version_positive CHECK (version > 0),
    CONSTRAINT chk_world_timestamps CHECK (updated_at >= created_at),
    
    -- Unique per tenant
    CONSTRAINT uq_worlds_tenant_name UNIQUE (tenant_id, world_name)
);

CREATE INDEX idx_worlds_tenant_id ON worlds(tenant_id);
CREATE INDEX idx_worlds_created_at ON worlds(tenant_id, created_at);

COMMENT ON TABLE worlds IS 'Game worlds - aggregate roots for lore';
COMMENT ON COLUMN worlds.version IS 'Optimistic concurrency control';

-- =============================================================================
-- CHARACTERS TABLE
-- =============================================================================
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    world_id INTEGER NOT NULL REFERENCES worlds(id) ON DELETE CASCADE,
    character_name VARCHAR(255) NOT NULL,
    backstory TEXT NOT NULL,
    status character_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Domain invariants
    CONSTRAINT chk_character_name_not_empty CHECK (LENGTH(TRIM(character_name)) > 0),
    CONSTRAINT chk_character_backstory_min_length CHECK (LENGTH(backstory) >= 100),
    CONSTRAINT chk_character_version_positive CHECK (version > 0),
    CONSTRAINT chk_character_timestamps CHECK (updated_at >= created_at),
    
    -- Unique per world (not globally)
    CONSTRAINT uq_characters_world_name UNIQUE (tenant_id, world_id, character_name)
);

CREATE INDEX idx_characters_tenant_id ON characters(tenant_id);
CREATE INDEX idx_characters_world_id ON characters(world_id);
CREATE INDEX idx_characters_status ON characters(tenant_id, status);
CREATE INDEX idx_characters_backstory_gin ON characters USING gin (backstory gin_trgm_ops);

COMMENT ON TABLE characters IS 'Characters within worlds';
COMMENT ON CONSTRAINT chk_character_backstory_min_length ON characters 
    IS 'Business rule: Backstory must be at least 100 chars for narrative depth';

-- =============================================================================
-- ABILITIES TABLE (Normalized from character)
-- =============================================================================
CREATE TABLE abilities (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    ability_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    power_level INTEGER NOT NULL,
    
    -- Domain invariants
    CONSTRAINT chk_ability_name_not_empty CHECK (LENGTH(TRIM(ability_name)) > 0),
    CONSTRAINT chk_ability_description_not_empty CHECK (LENGTH(TRIM(description)) > 0),
    CONSTRAINT chk_ability_power_level_range CHECK (power_level BETWEEN 1 AND 10),
    
    -- Unique per character
    CONSTRAINT uq_abilities_character_name UNIQUE (tenant_id, character_id, ability_name)
);

CREATE INDEX idx_abilities_character_id ON abilities(character_id);
CREATE INDEX idx_abilities_power_level ON abilities(tenant_id, power_level);

COMMENT ON TABLE abilities IS 'Character abilities/skills - normalized to avoid duplication';
COMMENT ON CONSTRAINT chk_ability_power_level_range ON abilities 
    IS 'Business rule: Power level 1-10 for game balance';

-- =============================================================================
-- EVENTS TABLE
-- =============================================================================
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    world_id INTEGER NOT NULL REFERENCES worlds(id) ON DELETE CASCADE,
    event_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,  -- NULL if ongoing
    outcome event_outcome NOT NULL DEFAULT 'ongoing',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Domain invariants
    CONSTRAINT chk_event_name_not_empty CHECK (LENGTH(TRIM(event_name)) > 0),
    CONSTRAINT chk_event_description_not_empty CHECK (LENGTH(TRIM(description)) > 0),
    CONSTRAINT chk_event_date_range CHECK (end_date IS NULL OR end_date >= start_date),
    CONSTRAINT chk_event_version_positive CHECK (version > 0),
    CONSTRAINT chk_event_timestamps CHECK (updated_at >= created_at),
    
    -- Unique per world
    CONSTRAINT uq_events_world_name UNIQUE (tenant_id, world_id, event_name)
);

CREATE INDEX idx_events_tenant_id ON events(tenant_id);
CREATE INDEX idx_events_world_id ON events(world_id);
CREATE INDEX idx_events_start_date ON events(tenant_id, start_date);
CREATE INDEX idx_events_outcome ON events(tenant_id, outcome);

COMMENT ON TABLE events IS 'Story events/quests within worlds';

-- =============================================================================
-- EVENT_PARTICIPANTS (Many-to-Many)
-- =============================================================================
CREATE TABLE event_participants (
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    
    PRIMARY KEY (event_id, character_id)
);

CREATE INDEX idx_event_participants_character_id ON event_participants(character_id);

COMMENT ON TABLE event_participants IS 'Many-to-many relationship between events and characters';

-- =============================================================================
-- IMPROVEMENTS TABLE (Aggregate Root)
-- =============================================================================
CREATE TABLE improvements (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    entity_type entity_type NOT NULL,
    entity_id INTEGER NOT NULL,  -- Polymorphic reference
    suggestion TEXT NOT NULL,
    status improvement_status NOT NULL DEFAULT 'proposed',
    git_commit_hash CHAR(40) NOT NULL,  -- SHA-1 hash
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Domain invariants
    CONSTRAINT chk_improvement_suggestion_not_empty CHECK (LENGTH(TRIM(suggestion)) > 0),
    CONSTRAINT chk_improvement_git_hash_format CHECK (git_commit_hash ~ '^[0-9a-f]{40}$')
);

CREATE INDEX idx_improvements_tenant_id ON improvements(tenant_id);
CREATE INDEX idx_improvements_status ON improvements(tenant_id, status);
CREATE INDEX idx_improvements_entity ON improvements(tenant_id, entity_type, entity_id);
CREATE INDEX idx_improvements_git_commit ON improvements(git_commit_hash);

COMMENT ON TABLE improvements IS 'Proposed enhancements to lore - must be validated';
COMMENT ON COLUMN improvements.entity_id IS 'Polymorphic FK to world/character/event';

-- =============================================================================
-- REQUIREMENTS TABLE (Aggregate Root)
-- =============================================================================
CREATE TABLE requirements (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE RESTRICT,
    entity_type entity_type,  -- NULL for global requirements
    entity_id INTEGER,  -- NULL for global requirements
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Domain invariants
    CONSTRAINT chk_requirement_description_not_empty CHECK (LENGTH(TRIM(description)) > 0),
    CONSTRAINT chk_requirement_entity_consistency CHECK (
        (entity_type IS NULL AND entity_id IS NULL) OR 
        (entity_type IS NOT NULL AND entity_id IS NOT NULL)
    )
);

CREATE INDEX idx_requirements_tenant_id ON requirements(tenant_id);
CREATE INDEX idx_requirements_entity ON requirements(tenant_id, entity_type, entity_id);

COMMENT ON TABLE requirements IS 'Business rules and invariants to enforce';
COMMENT ON CONSTRAINT chk_requirement_entity_consistency ON requirements 
    IS 'Both entity_type and entity_id must be set or both NULL (global)';

-- =============================================================================
-- TRIGGERS (Infrastructure, not business logic)
-- =============================================================================

-- Trigger function to update timestamp and increment version
CREATE OR REPLACE FUNCTION update_timestamp_and_version()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to versioned tables
CREATE TRIGGER trig_worlds_update
BEFORE UPDATE ON worlds
FOR EACH ROW EXECUTE FUNCTION update_timestamp_and_version();

CREATE TRIGGER trig_characters_update
BEFORE UPDATE ON characters
FOR EACH ROW EXECUTE FUNCTION update_timestamp_and_version();

CREATE TRIGGER trig_events_update
BEFORE UPDATE ON events
FOR EACH ROW EXECUTE FUNCTION update_timestamp_and_version();

-- Trigger to ensure events have at least one participant
CREATE OR REPLACE FUNCTION check_event_has_participants()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM event_participants WHERE event_id = NEW.id
    ) THEN
        RAISE EXCEPTION 'Event must have at least one participant'
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: This trigger fires AFTER INSERT/UPDATE, so the initial insert
-- must be followed by participant inserts in a transaction
CREATE TRIGGER trig_events_check_participants
AFTER INSERT OR UPDATE ON events
FOR EACH ROW EXECUTE FUNCTION check_event_has_participants();

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

CREATE VIEW v_character_summary AS
SELECT 
    c.id,
    c.tenant_id,
    c.world_id,
    w.world_name,
    c.character_name,
    c.status,
    LENGTH(c.backstory) as backstory_length,
    COUNT(a.id) as ability_count,
    COALESCE(AVG(a.power_level), 0) as avg_power_level,
    c.created_at,
    c.version
FROM characters c
JOIN worlds w ON c.world_id = w.id
LEFT JOIN abilities a ON c.id = a.character_id
GROUP BY c.id, w.world_name;

COMMENT ON VIEW v_character_summary IS 'Character summary with aggregated ability stats';

-- =============================================================================
-- SEED DATA (Optional - for testing)
-- =============================================================================

-- Insert default tenant
INSERT INTO tenants (name) VALUES ('default') ON CONFLICT DO NOTHING;
