#!/usr/bin/env python3
"""
Simple test script to verify MCP server setup

This tests basic functionality without needing an MCP client.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        from src.domain.entities.world import World
        from src.domain.entities.character import Character
        from src.domain.entities.story import Story
        from src.domain.entities.event import Event
        from src.domain.entities.page import Page
        from src.domain.value_objects.common import (
            TenantId, EntityId, WorldName, CharacterName, Description,
            Backstory, StoryName, PageName, Content, Timestamp
        )
        from src.infrastructure.in_memory_repositories import (
            InMemoryWorldRepository,
            InMemoryCharacterRepository,
            InMemoryStoryRepository,
            InMemoryEventRepository,
            InMemoryPageRepository,
        )
        print("✓ All domain imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_repositories():
    """Test basic repository operations."""
    print("\nTesting repositories...")

    try:
        from src.domain.entities.world import World
        from src.domain.value_objects.common import TenantId, WorldName, Description
        from src.infrastructure.in_memory_repositories import InMemoryWorldRepository

        # Create repository
        repo = InMemoryWorldRepository()

        # Create world
        tenant_id = TenantId(1)
        world = World.create(
            tenant_id=tenant_id,
            name=WorldName("Test World"),
            description=Description("A test world for verification")
        )

        # Save world
        saved_world = repo.save(world)
        assert saved_world.id is not None, "World ID should be assigned"

        # Retrieve world
        found_world = repo.find_by_id(tenant_id, saved_world.id)
        assert found_world is not None, "World should be found"
        assert str(found_world.name) == "Test World", "World name should match"

        print("✓ Repository operations successful")
        return True
    except Exception as e:
        print(f"✗ Repository test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_character_creation():
    """Test character with abilities."""
    print("\nTesting character creation...")

    try:
        from src.domain.entities.world import World
        from src.domain.entities.character import Character, CharacterElement, CharacterRole
        from src.domain.value_objects.common import (
            TenantId, EntityId, WorldName, CharacterName, Description, Backstory, Rarity
        )
        from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel
        from src.infrastructure.in_memory_repositories import (
            InMemoryWorldRepository,
            InMemoryCharacterRepository,
        )

        # Create repositories
        world_repo = InMemoryWorldRepository()
        char_repo = InMemoryCharacterRepository()

        # Create world
        tenant_id = TenantId(1)
        world = World.create(
            tenant_id=tenant_id,
            name=WorldName("Fantasy Realm"),
            description=Description("A magical fantasy world")
        )
        world_repo.save(world)

        # Create character
        character = Character.create(
            tenant_id=tenant_id,
            world_id=world.id,
            name=CharacterName("Hero"),
            backstory=Backstory("A brave hero who embarked on a quest to save the kingdom from an ancient evil. " * 3),
            rarity=Rarity.LEGENDARY,
            element=CharacterElement.FIRE,
            role=CharacterRole.DPS,
            base_hp=1000,
            base_atk=250,
        )

        # Add ability
        ability = Ability(
            name=AbilityName("Fireball"),
            description="A powerful fire spell that deals massive damage to enemies",
            power_level=PowerLevel(9),
        )
        character.add_ability(ability)

        # Save character
        char_repo.save(character)

        # Verify
        found_char = char_repo.find_by_id(tenant_id, character.id)
        assert found_char is not None, "Character should be found"
        assert found_char.ability_count() == 1, "Character should have 1 ability"

        print("✓ Character creation successful")
        return True
    except Exception as e:
        print(f"✗ Character test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Lore System MCP Server - Component Tests")
    print("=" * 60)

    tests = [
        test_imports,
        test_repositories,
        test_character_creation,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("=" * 60)
        print("\nThe MCP server is ready to use!")
        print("Run: python server.py")
        return 0
    else:
        print(f"✗ Some tests failed ({passed}/{total} passed)")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
