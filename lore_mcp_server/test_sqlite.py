#!/usr/bin/env python3
"""
Test SQLite repositories
"""
import sys
from pathlib import Path

# Add paths
lore_system_root = str(Path(__file__).parent.parent)
if lore_system_root not in sys.path:
    sys.path.insert(0, lore_system_root)

mcp_server_root = str(Path(__file__).parent)
if mcp_server_root not in sys.path:
    sys.path.insert(0, mcp_server_root)

from src.infrastructure.sqlite_repositories import (
    SQLiteDatabase,
    SQLiteWorldRepository,
    SQLiteCharacterRepository,
)
from src.domain.value_objects.common import TenantId, WorldName, CharacterName

# Create test database
db_path = "/tmp/test_lore_system.db"
db = SQLiteDatabase(db_path)
db.initialize_schema()

# Test WorldRepository
print("Testing WorldRepository...")
world_repo = SQLiteWorldRepository(db)

from src.domain.entities.world import World
from src.domain.value_objects.common import Description, Genre, PowerLevel

world = World(
    tenant_id=TenantId(1),
    name=WorldName("TestWorld"),
    description=Description("A test world for SQLite"),
    genre=Genre("Fantasy"),
    power_level=PowerLevel(5)
)

saved_world = world_repo.save(world)
print(f"✓ Created world: {saved_world.name.value} (ID: {saved_world.id.value})")

# Test CharacterRepository
print("\nTesting CharacterRepository...")
char_repo = SQLiteCharacterRepository(db)

from src.domain.entities.character import Character
from src.domain.value_objects.common import Backstory

character = Character(
    tenant_id=TenantId(1),
    world_id=saved_world.id,
    name=CharacterName("TestHero"),
    description=Description("A brave hero"),
    backstory=Backstory("Born in a small village, this hero seeks adventure..."),
    power_level=PowerLevel(3)
)

saved_char = char_repo.save(character)
print(f"✓ Created character: {saved_char.name.value} (ID: {saved_char.id.value})")

# Test listing
print("\nTesting list operations...")
worlds = world_repo.list_by_tenant(TenantId(1))
print(f"✓ Found {len(worlds)} world(s) for tenant 1")

chars = char_repo.list_by_world(TenantId(1), saved_world.id)
print(f"✓ Found {len(chars)} character(s) in world")

# Test retrieval
print("\nTesting retrieval...")
found_world = world_repo.find_by_id(TenantId(1), saved_world.id)
print(f"✓ Retrieved world: {found_world.name.value}")

found_char = char_repo.find_by_id(TenantId(1), saved_char.id)
print(f"✓ Retrieved character: {found_char.name.value}")

# Test database stats
stats = db.get_storage_stats() if hasattr(db, 'get_storage_stats') else {}
print(f"\nDatabase stats: {stats}")

print("\n✅ All tests passed!")
print(f"Database file: {db_path}")
