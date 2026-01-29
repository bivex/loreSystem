"""
Repository Contract Tests

These are shared test mixins that define the expected behavior
for all repository implementations. Each concrete repository
should inherit from these mixins to ensure consistent behavior.

Following the testing strategy:
- Test the contract once (here)
- Test implementations separately
- Mock repositories in higher layers
"""
import pytest
from typing import List

from src.domain.entities.world import World
from src.domain.entities.character import Character
from src.domain.value_objects.ability import Ability, AbilityName, PowerLevel
from src.domain.value_objects.common import (
    TenantId, EntityId, WorldName, CharacterName,
    Backstory, Timestamp, Version, CharacterStatus, Description
)
from src.domain.exceptions import DuplicateEntity, EntityNotFound


class WorldRepositoryContract:
    """
    Contract tests for World repository implementations.

    All concrete World repositories must pass these tests.
    """

    @pytest.fixture
    def sample_world(self):
        """Sample world for testing."""
        return World.create(
            tenant_id=TenantId(100),
            name=WorldName("Test World"),
            description="A test world"
        )

    def test_save_and_find_by_id(self, repo, sample_world):
        """Test basic save and retrieve operations."""
        # Save the world
        saved = repo.save(sample_world)
        assert saved.id == sample_world.id
        assert saved.tenant_id == sample_world.tenant_id

        # Find it back
        found = repo.find_by_id(sample_world.tenant_id, sample_world.id)
        assert found is not None
        assert found.id == sample_world.id
        assert found.name == sample_world.name

    def test_find_by_name(self, repo, sample_world):
        """Test finding world by name."""
        repo.save(sample_world)

        found = repo.find_by_name(sample_world.tenant_id, sample_world.name)
        assert found is not None
        assert found.id == sample_world.id

    def test_find_missing_returns_none(self, repo):
        """Test that missing entities return None."""
        assert repo.find_by_id(TenantId(1), EntityId(999)) is None
        assert repo.find_by_name(TenantId(1), WorldName("Nonexistent")) is None

    def test_list_by_tenant(self, repo, sample_world):
        """Test listing worlds by tenant."""
        repo.save(sample_world)

        worlds = repo.list_by_tenant(sample_world.tenant_id)
        assert len(worlds) == 1
        assert worlds[0].id == sample_world.id

    def test_exists(self, repo, sample_world):
        """Test existence checking."""
        assert not repo.exists(sample_world.tenant_id, sample_world.name)

        repo.save(sample_world)

        assert repo.exists(sample_world.tenant_id, sample_world.name)

    def test_duplicate_name_raises_error(self, repo, sample_world):
        """Test that duplicate names raise errors."""
        repo.save(sample_world)

        # Try to save another world with same name
        duplicate = World(
            id=EntityId(2),
            tenant_id=sample_world.tenant_id,
            name=sample_world.name,  # Same name
            description=Description("Another description"),
            parent_id=None,
            version=Version(1),
            created_at=Timestamp.now(),
            updated_at=Timestamp.now()
        )

        with pytest.raises(DuplicateEntity):
            repo.save(duplicate)


class CharacterRepositoryContract:
    """
    Contract tests for Character repository implementations.

    All concrete Character repositories must pass these tests.
    """

    @pytest.fixture
    def sample_character(self):
        """Sample character for testing."""
        return Character.create(
            tenant_id=TenantId(100),
            world_id=EntityId(1),
            name=CharacterName("Test Character"),
            backstory=Backstory("A test character backstory" * 20),  # Meet min length
            abilities=[
                Ability(
                    name=AbilityName("Strength"),
                    power_level=PowerLevel(5),
                    description="Physical strength"
                )
            ]
        )

    def test_save_and_find_by_id(self, repo, sample_character):
        """Test basic save and retrieve operations."""
        saved = repo.save(sample_character)
        assert saved.id == sample_character.id

        found = repo.find_by_id(sample_character.tenant_id, sample_character.id)
        assert found is not None
        assert found.name == sample_character.name

    def test_find_by_name_in_world(self, repo, sample_character):
        """Test finding character by name within a world."""
        repo.save(sample_character)

        found = repo.find_by_name(
            sample_character.tenant_id,
            sample_character.world_id,
            sample_character.name
        )
        assert found is not None
        assert found.id == sample_character.id

    def test_find_missing_returns_none(self, repo):
        """Test that missing entities return None."""
        assert repo.find_by_id(TenantId(1), EntityId(999)) is None

    def test_list_by_world(self, repo, sample_character):
        """Test listing characters by world."""
        repo.save(sample_character)

        characters = repo.list_by_world(
            sample_character.tenant_id,
            sample_character.world_id
        )
        assert len(characters) == 1
        assert characters[0].id == sample_character.id

    def test_exists(self, repo, sample_character):
        """Test existence checking."""
        assert not repo.exists(
            sample_character.tenant_id,
            sample_character.world_id,
            sample_character.name
        )

        repo.save(sample_character)

        assert repo.exists(
            sample_character.tenant_id,
            sample_character.world_id,
            sample_character.name
        )

    def test_delete(self, repo, sample_character):
        """Test character deletion."""
        repo.save(sample_character)

        # Verify it exists
        assert repo.exists(
            sample_character.tenant_id,
            sample_character.world_id,
            sample_character.name
        )

        # Delete it
        deleted = repo.delete(sample_character.tenant_id, sample_character.id)
        assert deleted is True

        # Verify it's gone
        assert repo.find_by_id(sample_character.tenant_id, sample_character.id) is None

    def test_delete_missing_returns_false(self, repo):
        """Test deleting non-existent character returns False."""
        deleted = repo.delete(TenantId(1), EntityId(999))
        assert deleted is False

    def test_duplicate_name_in_world_raises_error(self, repo, sample_character):
        """Test that duplicate names in same world raise errors."""
        repo.save(sample_character)

        # Try to save another character with same name in same world
        duplicate = Character(
            id=EntityId(2),
            tenant_id=sample_character.tenant_id,
            world_id=sample_character.world_id,  # Same world
            name=sample_character.name,  # Same name
            backstory=Backstory("Different backstory" * 20),
            status=CharacterStatus.ACTIVE,
            abilities=[
                Ability(
                    name=AbilityName("Magic"),
                    power_level=PowerLevel(3),
                    description="Magical ability"
                )
            ],
            parent_id=None,
            location_id=None,
            rarity=None,
            element=None,
            role=None,
            base_hp=None,
            base_atk=None,
            base_def=None,
            base_speed=None,
            energy_cost=None,
            version=Version(1),
            created_at=Timestamp.now(),
            updated_at=Timestamp.now()
        )

        with pytest.raises(DuplicateEntity):
            repo.save(duplicate)

    def test_same_name_different_world_allowed(self, repo, sample_character):
        """Test that same name in different worlds is allowed."""
        repo.save(sample_character)

        # Save character with same name but different world - should work
        different_world = Character(
            id=EntityId(2),
            tenant_id=sample_character.tenant_id,
            world_id=EntityId(2),  # Different world
            name=sample_character.name,  # Same name
            backstory=Backstory("Different backstory" * 20),
            status=CharacterStatus.ACTIVE,
            abilities=[
                Ability(
                    name=AbilityName("Agility"),
                    power_level=PowerLevel(4),
                    description="Speed and dexterity"
                )
            ],
            parent_id=None,
            location_id=None,
            rarity=None,
            element=None,
            role=None,
            base_hp=None,
            base_atk=None,
            base_def=None,
            base_speed=None,
            energy_cost=None,
            version=Version(1),
            created_at=Timestamp.now(),
            updated_at=Timestamp.now()
        )

        # This should not raise an error
        saved = repo.save(different_world)
        assert saved.id == different_world.id