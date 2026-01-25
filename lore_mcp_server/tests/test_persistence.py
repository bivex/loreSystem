#!/usr/bin/env python3
"""
Test JSON persistence functionality
"""

import sys
import json
import shutil
from pathlib import Path

# Add project root to path (loreSystem directory)
# __file__ is mcp/tests/test_persistence.py, so parent.parent.parent is loreSystem/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.src.persistence import JSONPersistence
from src.domain.entities.world import World
from src.domain.entities.character import Character, CharacterElement, CharacterRole
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, CharacterName, Description, Backstory, Rarity
)
from src.infrastructure.in_memory_repositories import (
    InMemoryWorldRepository,
    InMemoryCharacterRepository,
    InMemoryStoryRepository,
    InMemoryEventRepository,
    InMemoryPageRepository,
)


def test_json_persistence():
    """Test saving and loading data to/from JSON."""
    print("Testing JSON Persistence...")

    # Setup
    test_data_dir = "test_lore_data"
    persistence = JSONPersistence(test_data_dir)

    # Create repositories and add test data
    world_repo = InMemoryWorldRepository()
    character_repo = InMemoryCharacterRepository()
    story_repo = InMemoryStoryRepository()
    event_repo = InMemoryEventRepository()
    page_repo = InMemoryPageRepository()

    tenant_id = TenantId(1)
    tenant_id_str = "1"

    # Create test world
    world = World.create(
        tenant_id=tenant_id,
        name=WorldName("Test Realm"),
        description=Description("A realm for testing JSON persistence")
    )
    world_repo.save(world)

    # Create test character
    character = Character.create(
        tenant_id=tenant_id,
        world_id=world.id,
        name=CharacterName("Test Hero"),
        backstory=Backstory("A brave hero created specifically for testing the JSON persistence system. " * 3),
        rarity=Rarity.EPIC,
        element=CharacterElement.FIRE,
        role=CharacterRole.DPS,
        base_hp=1000,
        base_atk=200,
    )
    character_repo.save(character)

    # Save to JSON
    print("\n1. Saving data to JSON files...")
    counts = persistence.save_all(
        world_repo,
        character_repo,
        story_repo,
        event_repo,
        page_repo,
        tenant_id_str
    )

    print(f"   ✓ Saved {counts['worlds']} worlds")
    print(f"   ✓ Saved {counts['characters']} characters")
    print(f"   ✓ Total files: {len(counts['files'])}")

    # List saved files
    print("\n2. Listing saved files...")
    files = persistence.list_saved_files(tenant_id_str)
    print(f"   ✓ Found {len(files['worlds'])} world files")
    print(f"   ✓ Found {len(files['characters'])} character files")

    # Get storage stats
    print("\n3. Getting storage statistics...")
    stats = persistence.get_storage_stats()
    print(f"   ✓ Total files: {stats['total_files']}")
    print(f"   ✓ Total size: {stats['total_size_bytes']} bytes")
    print(f"   ✓ Data directory: {stats['data_directory']}")

    # Export to single file
    print("\n4. Exporting to single file...")
    export_path = persistence.export_tenant(tenant_id_str, "test_export.json")
    print(f"   ✓ Exported to: {export_path}")

    # Verify export file
    with open(export_path, 'r') as f:
        export_data = json.load(f)

    print(f"   ✓ Export contains {export_data['counts']['worlds']} worlds")
    print(f"   ✓ Export contains {export_data['counts']['characters']} characters")

    # Load data back
    print("\n5. Loading data from JSON...")
    loaded_data = persistence.load_all(tenant_id_str)
    print(f"   ✓ Loaded {len(loaded_data['worlds'])} worlds")
    print(f"   ✓ Loaded {len(loaded_data['characters'])} characters")

    # Verify loaded data matches
    assert len(loaded_data['worlds']) == 1, "Should have 1 world"
    assert len(loaded_data['characters']) == 1, "Should have 1 character"

    loaded_world = loaded_data['worlds'][0]
    assert loaded_world['name'] == "Test Realm", "World name should match"

    loaded_char = loaded_data['characters'][0]
    assert loaded_char['name'] == "Test Hero", "Character name should match"
    assert loaded_char['rarity'] == "epic", "Character rarity should match"

    print("\n6. Cleanup...")
    # Clean up test data directory
    if Path(test_data_dir).exists():
        shutil.rmtree(test_data_dir)
        print(f"   ✓ Removed test directory: {test_data_dir}")

    print("\n" + "=" * 60)
    print("✅ All JSON persistence tests passed!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_json_persistence()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
