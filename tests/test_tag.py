"""
Tests for Tag entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.tag import Tag
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    TagName,
    TagType,
)
from src.domain.exceptions import InvariantViolation


def make_basic_tag():
    """Factory for basic tag."""
    return Tag.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=TagName("Important"),
        tag_type=TagType.CATEGORY,
    )


def make_tag_with_color():
    """Factory for tag with color."""
    return Tag.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=TagName("Priority"),
        tag_type=TagType.STATUS,
        color="#FF0000",
        description="High priority items",
    )


class TestTagCreation:
    """Test tag creation scenarios."""

    def test_create_basic_tag(self):
        """Test creating a basic tag."""
        tag = make_basic_tag()
        assert tag.name.value == "Important"
        assert tag.tag_type == TagType.CATEGORY
        assert tag.color is None
        assert tag.description is None
        assert tag.version.value == 1

    def test_create_tag_with_color_and_description(self):
        """Test creating tag with color and description."""
        tag = make_tag_with_color()
        assert tag.color == "#FF0000"
        assert tag.description == "High priority items"

    def test_create_tag_invalid_color_fails(self):
        """Test that invalid color raises error."""
        with pytest.raises(InvariantViolation, match="Color must be valid hex format"):
            Tag.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=TagName("Test"),
                tag_type=TagType.CATEGORY,
                color="invalid",
            )

    def test_create_tag_short_hex_color_fails(self):
        """Test that short hex color raises error."""
        with pytest.raises(InvariantViolation, match="Color must be valid hex format"):
            Tag.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=TagName("Test"),
                tag_type=TagType.CATEGORY,
                color="#FFF",  # Too short
            )

    def test_create_tag_no_hash_color_fails(self):
        """Test that color without # raises error."""
        with pytest.raises(InvariantViolation, match="Color must be valid hex format"):
            Tag.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=TagName("Test"),
                tag_type=TagType.CATEGORY,
                color="FF0000",
            )

    def test_create_tag_valid_colors(self):
        """Test valid color formats."""
        # Uppercase
        tag1 = Tag.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=TagName("Test1"),
            tag_type=TagType.CATEGORY,
            color="#FF0000",
        )
        assert tag1.color == "#FF0000"

        # Lowercase
        tag2 = Tag.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=TagName("Test2"),
            tag_type=TagType.CATEGORY,
            color="#ff0000",
        )
        assert tag2.color == "#ff0000"

        # Mixed case
        tag3 = Tag.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=TagName("Test3"),
            tag_type=TagType.CATEGORY,
            color="#AbCdEf",
        )
        assert tag3.color == "#AbCdEf"


class TestTagOperations:
    """Test tag modification operations."""

    def test_update_color(self):
        """Test updating tag color."""
        tag = make_basic_tag()
        old_version = tag.version.value

        tag.update_color("#00FF00")

        assert tag.color == "#00FF00"
        assert tag.version.value == old_version + 1

    def test_update_color_to_none(self):
        """Test updating color to None."""
        tag = make_tag_with_color()
        tag.update_color(None)
        assert tag.color is None

    def test_update_color_same_no_change(self):
        """Test updating to same color doesn't increment version."""
        tag = make_tag_with_color()
        old_version = tag.version.value

        tag.update_color("#FF0000")

        assert tag.version.value == old_version

    def test_update_color_invalid_fails(self):
        """Test updating to invalid color fails."""
        tag = make_basic_tag()
        with pytest.raises(InvariantViolation, match="Color must be valid hex format"):
            tag.update_color("invalid")

    def test_update_description(self):
        """Test updating tag description."""
        tag = make_basic_tag()
        old_version = tag.version.value

        tag.update_description("New description")

        assert tag.description == "New description"
        assert tag.version.value == old_version + 1

    def test_update_description_to_none(self):
        """Test updating description to None."""
        tag = make_tag_with_color()
        tag.update_description(None)
        assert tag.description is None

    def test_update_description_same_no_change(self):
        """Test updating to same description doesn't increment version."""
        tag = make_tag_with_color()
        old_version = tag.version.value

        tag.update_description("High priority items")

        assert tag.version.value == old_version


class TestTagInvariants:
    """Test invariant enforcement."""

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        tag = make_basic_tag()
        # Manually set invalid timestamps
        object.__setattr__(tag, 'updated_at', Timestamp(tag.created_at.value - timedelta(hours=1)))
        # Validation should fail when explicitly called
        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            tag._validate_invariants()

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        tag = make_basic_tag()
        # Try to set invalid updated_at
        with pytest.raises(InvariantViolation):
            object.__setattr__(tag, 'updated_at', Timestamp(tag.created_at.value - timedelta(hours=1)))
            tag._validate_invariants()

    def test_color_validation_on_update(self):
        """Test color validation during updates."""
        tag = make_basic_tag()
        # Manually set invalid color
        with pytest.raises(InvariantViolation):
            object.__setattr__(tag, 'color', "invalid")
            tag._validate_invariants()


class TestTagStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        tag = make_basic_tag()
        assert str(tag) == "Tag(Important, type=category)"

    def test_str_with_color(self):
        """Test __str__ method with color."""
        tag = make_tag_with_color()
        assert str(tag) == "Tag(Priority, type=status)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        tag = make_basic_tag()
        repr_str = repr(tag)
        assert "Tag(id=None" in repr_str
        assert "name='Important'" in repr_str
        assert "type=category" in repr_str
        assert "version=v1" in repr_str