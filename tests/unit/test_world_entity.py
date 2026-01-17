"""
Unit tests for World entity.

Tests domain logic in isolation without infrastructure dependencies.
"""
import pytest
from datetime import datetime, timezone

from src.domain.entities.world import World
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    Description,
    Version,
    Timestamp,
)
from src.domain.exceptions import InvariantViolation


class TestWorldEntity:
    """Test suite for World aggregate root."""
    
    def test_create_world_with_valid_data(self):
        """Should create a world when all data is valid."""
        # Arrange
        tenant_id = TenantId(1)
        name = WorldName("Eternal Forge")
        description = Description("A vast world of endless creation")
        
        # Act
        world = World.create(
            tenant_id=tenant_id,
            name=name,
            description=description,
        )
        
        # Assert
        assert world.id is None  # Not yet persisted
        assert world.tenant_id == tenant_id
        assert world.name == name
        assert world.description == description
        assert world.version == Version(1)
        assert world.created_at.value <= datetime.now(timezone.utc)
        assert world.updated_at.value <= datetime.now(timezone.utc)
    
    def test_create_world_with_empty_name_raises_error(self):
        """Should raise ValueError when name is empty."""
        tenant_id = TenantId(1)
        description = Description("A description")
        
        with pytest.raises(ValueError, match="World name cannot be empty"):
            WorldName("")
    
    def test_create_world_with_long_name_raises_error(self):
        """Should raise ValueError when name exceeds 255 characters."""
        tenant_id = TenantId(1)
        description = Description("A description")
        
        with pytest.raises(ValueError, match="must be <= 255 characters"):
            WorldName("x" * 256)
    
    def test_update_description(self):
        """Should update description and increment version."""
        # Arrange
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("Original description"),
        )
        original_version = world.version
        original_updated_at = world.updated_at
        
        # Act
        new_description = Description("Updated description")
        world.update_description(new_description)
        
        # Assert
        assert world.description == new_description
        assert world.version == original_version.increment()
        assert world.updated_at.value > original_updated_at.value
    
    def test_rename_world(self):
        """Should rename world and increment version."""
        # Arrange
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Old Name"),
            description=Description("A description"),
        )
        original_version = world.version
        
        # Act
        new_name = WorldName("New Name")
        world.rename(new_name)
        
        # Assert
        assert world.name == new_name
        assert world.version == original_version.increment()
    
    def test_rename_to_same_name_does_not_increment_version(self):
        """Should not change version if name unchanged."""
        # Arrange
        name = WorldName("Same Name")
        world = World.create(
            tenant_id=TenantId(1),
            name=name,
            description=Description("A description"),
        )
        original_version = world.version
        
        # Act
        world.rename(WorldName("Same Name"))
        
        # Assert
        assert world.version == original_version
    
    def test_world_str_representation(self):
        """Should have readable string representation."""
        world = World.create(
            tenant_id=TenantId(1),
            name=WorldName("Test World"),
            description=Description("A description"),
        )
        
        str_repr = str(world)
        assert "Test World" in str_repr
        assert "v1" in str_repr


class TestWorldInvariants:
    """Test invariant enforcement."""
    
    def test_updated_at_cannot_be_before_created_at(self):
        """Should raise InvariantViolation if updated_at < created_at."""
        now = Timestamp.now()
        earlier = Timestamp(datetime(2020, 1, 1, tzinfo=timezone.utc))
        
        with pytest.raises(InvariantViolation, match="Updated timestamp must be"):
            World(
                id=None,
                tenant_id=TenantId(1),
                name=WorldName("Test"),
                description=Description("Test"),
                created_at=now,
                updated_at=earlier,  # Invalid: before created_at
                version=Version(1),
            )
    
    def test_version_must_be_positive(self):
        """Should raise ValueError if version is not positive."""
        with pytest.raises(ValueError, match="Version must be >= 1"):
            Version(0)
        
        with pytest.raises(ValueError, match="Version must be >= 1"):
            Version(-1)
