"""
Tests for Map entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.map import Map
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
)
from src.domain.exceptions import InvariantViolation


def make_basic_map():
    """Factory for basic map."""
    return Map.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="World Map",
        description="A detailed map of the fantasy world.",
        image_ids=[EntityId(200)],
        location_ids=[EntityId(100), EntityId(101)],
        scale="1:1000",
        is_interactive=False,
    )


def make_map_without_image():
    """Factory for map without image."""
    return Map.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Text Map",
        description="A text-based map description.",
        image_ids=[],
        location_ids=[],
        scale=None,
        is_interactive=True,
    )


class TestMapCreation:
    """Test map creation scenarios."""

    def test_create_basic_map(self):
        """Test creating a basic map."""
        map_obj = make_basic_map()
        assert map_obj.name == "World Map"
        assert map_obj.description == "A detailed map of the fantasy world."
        assert map_obj.image_ids == [EntityId(200)]
        assert map_obj.location_ids == [EntityId(100), EntityId(101)]
        assert map_obj.scale == "1:1000"
        assert map_obj.is_interactive == False
        assert map_obj.version.value == 1

    def test_create_map_without_image(self):
        """Test creating map without image."""
        map_obj = make_map_without_image()
        assert map_obj.image_ids == []
        assert map_obj.description == "A text-based map description."
        assert map_obj.scale is None
        assert map_obj.is_interactive == True

    def test_create_map_without_image_or_description_fails(self):
        """Test that map without image or description fails."""
        with pytest.raises(InvariantViolation, match="Map must have at least one image or description"):
            Map.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name="Invalid Map",
                description=None,
                image_ids=[],
                location_ids=[],
                scale=None,
                is_interactive=False,
            )







class TestMapOperations:
    """Test map modification operations."""

    def test_update_description(self):
        """Test updating map description."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        new_description = "Updated map description."
        map_obj.update_description(new_description)

        assert map_obj.description == new_description
        assert map_obj.version.value == old_version + 1

    def test_update_description_same_no_change(self):
        """Test updating to same description doesn't increment version."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        same_description = "A detailed map of the fantasy world."
        map_obj.update_description(same_description)

        assert map_obj.version.value == old_version

    def test_add_image(self):
        """Test adding an image to the map."""
        map_obj = make_map_without_image()
        old_version = map_obj.version.value

        new_image_id = EntityId(300)
        map_obj.add_image(new_image_id)

        assert new_image_id in map_obj.image_ids
        assert map_obj.version.value == old_version + 1

    def test_add_duplicate_image_no_change(self):
        """Test adding duplicate image does nothing."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        existing_image_id = EntityId(200)
        map_obj.add_image(existing_image_id)

        assert map_obj.version.value == old_version  # No change

    def test_remove_image(self):
        """Test removing an image from the map."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        image_id_to_remove = EntityId(200)
        map_obj.remove_image(image_id_to_remove)

        assert image_id_to_remove not in map_obj.image_ids
        assert map_obj.version.value == old_version + 1

    def test_remove_nonexistent_image_no_change(self):
        """Test removing nonexistent image does nothing."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        nonexistent_image_id = EntityId(999)
        map_obj.remove_image(nonexistent_image_id)

        assert map_obj.version.value == old_version  # No change

    def test_add_location(self):
        """Test adding a location to the map."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        new_location_id = EntityId(300)
        map_obj.add_location(new_location_id)

        assert new_location_id in map_obj.location_ids
        assert map_obj.version.value == old_version + 1

    def test_add_duplicate_location_no_change(self):
        """Test adding duplicate location does nothing."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        existing_location_id = EntityId(100)
        map_obj.add_location(existing_location_id)

        assert map_obj.version.value == old_version  # No change

    def test_remove_location(self):
        """Test removing a location from the map."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        location_id_to_remove = EntityId(100)
        map_obj.remove_location(location_id_to_remove)

        assert location_id_to_remove not in map_obj.location_ids
        assert map_obj.version.value == old_version + 1

    def test_remove_nonexistent_location_no_change(self):
        """Test removing nonexistent location does nothing."""
        map_obj = make_basic_map()
        old_version = map_obj.version.value

        nonexistent_location_id = EntityId(999)
        map_obj.remove_location(nonexistent_location_id)

        assert map_obj.version.value == old_version  # No change











class TestMapInvariants:
    """Test invariant enforcement."""

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        map_obj = make_basic_map()
        # Manually set invalid timestamps
        object.__setattr__(map_obj, 'updated_at', Timestamp(map_obj.created_at.value - timedelta(hours=1)))
        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            map_obj._validate_invariants()

    def test_remove_last_image_without_description_fails(self):
        """Test that removing the last image without description fails."""
        map_obj = Map.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Image Only Map",
            description=None,
            image_ids=[EntityId(200)],
            location_ids=[],
            scale=None,
            is_interactive=False,
        )
        with pytest.raises(InvariantViolation, match="Map must have at least one image or description"):
            map_obj.remove_image(EntityId(200))


class TestMapStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        map_obj = make_basic_map()
        assert str(map_obj) == "Map(World Map)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        map_obj = make_basic_map()
        repr_str = repr(map_obj)
        assert "Map(id=None" in repr_str
        assert "world_id=1" in repr_str
        assert "name='World Map'" in repr_str
        assert "interactive=False" in repr_str
        assert "version=v1" in repr_str