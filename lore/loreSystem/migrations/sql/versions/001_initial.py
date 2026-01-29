"""Initial schema creation

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-17 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema with all tables, constraints, and indexes."""
    
    # Create enums
    entity_type_enum = postgresql.ENUM(
        'world', 'character', 'event',
        name='entity_type',
        create_type=True
    )
    entity_type_enum.create(op.get_bind())
    
    improvement_status_enum = postgresql.ENUM(
        'proposed', 'approved', 'applied', 'rejected',
        name='improvement_status',
        create_type=True
    )
    improvement_status_enum.create(op.get_bind())
    
    event_outcome_enum = postgresql.ENUM(
        'success', 'failure', 'ongoing',
        name='event_outcome',
        create_type=True
    )
    event_outcome_enum.create(op.get_bind())
    
    character_status_enum = postgresql.ENUM(
        'active', 'inactive',
        name='character_status',
        create_type=True
    )
    character_status_enum.create(op.get_bind())
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("LENGTH(TRIM(name)) > 0", name='chk_tenant_name_not_empty'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_tenants_name', 'tenants', ['name'])
    
    # Create worlds table
    op.create_table(
        'worlds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('world_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.CheckConstraint("LENGTH(TRIM(world_name)) > 0", name='chk_world_name_not_empty'),
        sa.CheckConstraint("LENGTH(TRIM(description)) > 0", name='chk_world_description_not_empty'),
        sa.CheckConstraint('version > 0', name='chk_world_version_positive'),
        sa.CheckConstraint('updated_at >= created_at', name='chk_world_timestamps'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'world_name', name='uq_worlds_tenant_name')
    )
    op.create_index('idx_worlds_tenant_id', 'worlds', ['tenant_id'])
    op.create_index('idx_worlds_created_at', 'worlds', ['tenant_id', 'created_at'])
    
    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('world_id', sa.Integer(), nullable=False),
        sa.Column('character_name', sa.String(255), nullable=False),
        sa.Column('backstory', sa.Text(), nullable=False),
        sa.Column('status', character_status_enum, server_default='active', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.CheckConstraint("LENGTH(TRIM(character_name)) > 0", name='chk_character_name_not_empty'),
        sa.CheckConstraint('LENGTH(backstory) >= 100', name='chk_character_backstory_min_length'),
        sa.CheckConstraint('version > 0', name='chk_character_version_positive'),
        sa.CheckConstraint('updated_at >= created_at', name='chk_character_timestamps'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'world_id', 'character_name', name='uq_characters_world_name')
    )
    op.create_index('idx_characters_tenant_id', 'characters', ['tenant_id'])
    op.create_index('idx_characters_world_id', 'characters', ['world_id'])
    op.create_index('idx_characters_status', 'characters', ['tenant_id', 'status'])
    
    # Create abilities table
    op.create_table(
        'abilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('ability_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('power_level', sa.Integer(), nullable=False),
        sa.CheckConstraint("LENGTH(TRIM(ability_name)) > 0", name='chk_ability_name_not_empty'),
        sa.CheckConstraint("LENGTH(TRIM(description)) > 0", name='chk_ability_description_not_empty'),
        sa.CheckConstraint('power_level BETWEEN 1 AND 10', name='chk_ability_power_level_range'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'character_id', 'ability_name', name='uq_abilities_character_name')
    )
    op.create_index('idx_abilities_character_id', 'abilities', ['character_id'])
    op.create_index('idx_abilities_power_level', 'abilities', ['tenant_id', 'power_level'])
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('world_id', sa.Integer(), nullable=False),
        sa.Column('event_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('start_date', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('end_date', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('outcome', event_outcome_enum, server_default='ongoing', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.CheckConstraint("LENGTH(TRIM(event_name)) > 0", name='chk_event_name_not_empty'),
        sa.CheckConstraint("LENGTH(TRIM(description)) > 0", name='chk_event_description_not_empty'),
        sa.CheckConstraint('end_date IS NULL OR end_date >= start_date', name='chk_event_date_range'),
        sa.CheckConstraint('version > 0', name='chk_event_version_positive'),
        sa.CheckConstraint('updated_at >= created_at', name='chk_event_timestamps'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['world_id'], ['worlds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'world_id', 'event_name', name='uq_events_world_name')
    )
    op.create_index('idx_events_tenant_id', 'events', ['tenant_id'])
    op.create_index('idx_events_world_id', 'events', ['world_id'])
    op.create_index('idx_events_start_date', 'events', ['tenant_id', 'start_date'])
    op.create_index('idx_events_outcome', 'events', ['tenant_id', 'outcome'])
    
    # Create event_participants table
    op.create_table(
        'event_participants',
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id', 'character_id')
    )
    op.create_index('idx_event_participants_character_id', 'event_participants', ['character_id'])
    
    # Create improvements table
    op.create_table(
        'improvements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', entity_type_enum, nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('suggestion', sa.Text(), nullable=False),
        sa.Column('status', improvement_status_enum, server_default='proposed', nullable=False),
        sa.Column('git_commit_hash', sa.CHAR(40), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("LENGTH(TRIM(suggestion)) > 0", name='chk_improvement_suggestion_not_empty'),
        sa.CheckConstraint("git_commit_hash ~ '^[0-9a-f]{40}$'", name='chk_improvement_git_hash_format'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_improvements_tenant_id', 'improvements', ['tenant_id'])
    op.create_index('idx_improvements_status', 'improvements', ['tenant_id', 'status'])
    op.create_index('idx_improvements_entity', 'improvements', ['tenant_id', 'entity_type', 'entity_id'])
    op.create_index('idx_improvements_git_commit', 'improvements', ['git_commit_hash'])
    
    # Create requirements table
    op.create_table(
        'requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('entity_type', entity_type_enum, nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("LENGTH(TRIM(description)) > 0", name='chk_requirement_description_not_empty'),
        sa.CheckConstraint(
            '(entity_type IS NULL AND entity_id IS NULL) OR (entity_type IS NOT NULL AND entity_id IS NOT NULL)',
            name='chk_requirement_entity_consistency'
        ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_requirements_tenant_id', 'requirements', ['tenant_id'])
    op.create_index('idx_requirements_entity', 'requirements', ['tenant_id', 'entity_type', 'entity_id'])
    
    # Create triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION update_timestamp_and_version()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            NEW.version = OLD.version + 1;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER trig_worlds_update
        BEFORE UPDATE ON worlds
        FOR EACH ROW EXECUTE FUNCTION update_timestamp_and_version();
    """)
    
    op.execute("""
        CREATE TRIGGER trig_characters_update
        BEFORE UPDATE ON characters
        FOR EACH ROW EXECUTE FUNCTION update_timestamp_and_version();
    """)
    
    op.execute("""
        CREATE TRIGGER trig_events_update
        BEFORE UPDATE ON events
        FOR EACH ROW EXECUTE FUNCTION update_timestamp_and_version();
    """)
    
    # Insert default tenant
    op.execute("INSERT INTO tenants (name) VALUES ('default')")


def downgrade() -> None:
    """Drop all tables and enums."""
    
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS trig_events_update ON events")
    op.execute("DROP TRIGGER IF EXISTS trig_characters_update ON characters")
    op.execute("DROP TRIGGER IF EXISTS trig_worlds_update ON worlds")
    op.execute("DROP FUNCTION IF EXISTS update_timestamp_and_version()")
    
    # Drop tables (in reverse dependency order)
    op.drop_table('requirements')
    op.drop_table('improvements')
    op.drop_table('event_participants')
    op.drop_table('events')
    op.drop_table('abilities')
    op.drop_table('characters')
    op.drop_table('worlds')
    op.drop_table('tenants')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS character_status")
    op.execute("DROP TYPE IF EXISTS event_outcome")
    op.execute("DROP TYPE IF EXISTS improvement_status")
    op.execute("DROP TYPE IF EXISTS entity_type")
