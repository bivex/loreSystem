"""
Tests for Inspiration entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.inspiration import Inspiration
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
)
from src.domain.exceptions import InvariantViolation


def make_basic_inspiration():
    """Factory for basic inspiration."""
    return Inspiration.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        title="Dragon Concept",
        content="Ancient red dragon with golden scales and emerald eyes.",
        category="Character",
        tags=["dragon", "monster"],
        source="https://example.com/dragon-art",
        is_used=False,
    )


def make_text_only_inspiration():
    """Factory for text-only inspiration."""
    return Inspiration.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        title="Plot Idea",
        content="The hero discovers they are the villain's long-lost sibling.",
        category="Plot",
        tags=["plot", "twist"],
        source=None,
        is_used=True,
    )


class TestInspirationCreation:
    """Test inspiration creation scenarios."""

    def test_create_basic_inspiration(self):
        """Test creating a basic inspiration."""
        inspiration = make_basic_inspiration()
        assert inspiration.title == "Dragon Concept"
        assert inspiration.content == "Ancient red dragon with golden scales and emerald eyes."
        assert inspiration.category == "Character"
        assert inspiration.tags == ["dragon", "monster"]
        assert inspiration.source == "https://example.com/dragon-art"
        assert not inspiration.is_used
        assert inspiration.version.value == 1

    def test_create_text_only_inspiration(self):
        """Test creating text-only inspiration."""
        inspiration = make_text_only_inspiration()
        assert inspiration.source is None
        assert inspiration.is_used


class TestInspirationOperations:
    """Test inspiration modification operations."""

    def test_update_content(self):
        """Test updating inspiration content."""
        inspiration = make_basic_inspiration()
        old_version = inspiration.version.value

        new_content = "Updated dragon description."
        inspiration.update_content(new_content)

        assert inspiration.content == new_content
        assert inspiration.version.value == old_version + 1

    def test_update_content_same_no_change(self):
        """Test updating to same content doesn't increment version."""
        inspiration = make_basic_inspiration()
        old_version = inspiration.version.value

        same_content = "Ancient red dragon with golden scales and emerald eyes."
        inspiration.update_content(same_content)

        assert inspiration.version.value == old_version

    def test_mark_used(self):
        """Test marking inspiration as used."""
        inspiration = make_basic_inspiration()
        old_version = inspiration.version.value

        inspiration.mark_used()

        assert inspiration.is_used
        assert inspiration.version.value == old_version + 1

    def test_add_tag(self):
        """Test adding a tag."""
        inspiration = make_basic_inspiration()
        old_version = inspiration.version.value

        inspiration.add_tag("new-tag")

        assert "new-tag" in inspiration.tags
        assert len(inspiration.tags) == 3
        assert inspiration.version.value == old_version + 1

    def test_add_duplicate_tag_no_change(self):
        """Test adding duplicate tag does nothing."""
        inspiration = make_basic_inspiration()
        old_version = inspiration.version.value

        inspiration.add_tag("dragon")  # Already exists

        assert inspiration.tags.count("dragon") == 1
        assert inspiration.version.value == old_version

    def test_remove_tag(self):
        """Test removing a tag."""
        inspiration = make_basic_inspiration()
        old_version = inspiration.version.value

        inspiration.remove_tag("dragon")

        assert "dragon" not in inspiration.tags
        assert len(inspiration.tags) == 1
        assert inspiration.version.value == old_version + 1

    def test_remove_nonexistent_tag_no_change(self):
        """Test removing nonexistent tag does nothing."""
        inspiration = make_basic_inspiration()
        old_version = inspiration.version.value

        inspiration.remove_tag("nonexistent")

        assert len(inspiration.tags) == 2
        assert inspiration.version.value == old_version


class TestInspirationInvariants:
    """Test invariant enforcement."""

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        inspiration = make_basic_inspiration()
        # Manually set invalid timestamps
        object.__setattr__(inspiration, 'updated_at', Timestamp(inspiration.created_at.value - timedelta(hours=1)))
        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            inspiration._validate_invariants()

    def test_content_cannot_be_empty(self):
        """Test that content cannot be empty."""
        with pytest.raises(InvariantViolation, match="Inspiration content cannot be empty"):
            Inspiration.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                title="Empty Inspiration",
                content="",
                category="Test",
            )

    def test_update_content_cannot_be_empty(self):
        """Test that updating content to empty fails."""
        inspiration = make_basic_inspiration()
        with pytest.raises(InvariantViolation, match="Inspiration content cannot be empty"):
            inspiration.update_content("")

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        inspiration = make_basic_inspiration()
        # Try to set invalid timestamps
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp
        object.__setattr__(inspiration, 'updated_at', Timestamp(inspiration.created_at.value - timedelta(hours=1)))
        with pytest.raises(InvariantViolation):
            inspiration._validate_invariants()


class TestInspirationStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        inspiration = make_basic_inspiration()
        assert str(inspiration) == "Inspiration(Dragon Concept, Character)"

    def test_str_used_inspiration(self):
        """Test __str__ method for used inspiration."""
        inspiration = make_text_only_inspiration()
        assert str(inspiration) == "Inspiration(Plot Idea, Plot)"

    def test_str_long_title(self):
        """Test __str__ method with long title."""
        long_title = "This is a very long inspiration title that should be displayed in full in the string representation"
        inspiration = Inspiration.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            title=long_title,
            content="Test content",
            category="Test",
        )
        str_repr = str(inspiration)
        assert long_title in str_repr
        assert "Test" in str_repr

    def test_repr_representation(self):
        """Test __repr__ method."""
        inspiration = make_basic_inspiration()
        repr_str = repr(inspiration)
        assert "Inspiration(id=None" in repr_str
        assert "world_id=1" in repr_str
        assert "title='Dragon Concept'" in repr_str
        assert "category='Character'" in repr_str
        assert "used=False" in repr_str
        assert "version=v1" in repr_str