"""
Tests for Handout entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.handout import Handout
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
)
from src.domain.exceptions import InvariantViolation


def make_basic_handout():
    """Factory for basic handout."""
    return Handout.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        title="Character Sheet",
        content="Name: Hero\nClass: Warrior\nLevel: 5",
        image_ids=[EntityId(200)],
        session_id=EntityId(50),
        reveal_timing="After combat",
        is_revealed=False,
    )


def make_text_only_handout():
    """Factory for text-only handout."""
    return Handout.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        title="Quest Log",
        content="1. Find the lost artifact\n2. Defeat the dragon",
        image_ids=[],
        session_id=None,
        reveal_timing=None,
        is_revealed=False,
    )


class TestHandoutCreation:
    """Test handout creation scenarios."""

    def test_create_basic_handout(self):
        """Test creating a basic handout."""
        handout = make_basic_handout()
        assert handout.title == "Character Sheet"
        assert handout.content == "Name: Hero\nClass: Warrior\nLevel: 5"
        assert handout.image_ids == [EntityId(200)]
        assert handout.session_id == EntityId(50)
        assert handout.reveal_timing == "After combat"
        assert not handout.is_revealed
        assert handout.version.value == 1

    def test_create_text_only_handout(self):
        """Test creating text-only handout."""
        handout = make_text_only_handout()
        assert handout.image_ids == []
        assert not handout.is_revealed


class TestHandoutOperations:
    """Test handout modification operations."""

    def test_update_content(self):
        """Test updating handout content."""
        handout = make_basic_handout()
        old_version = handout.version.value

        new_content = "Updated character information."
        handout.update_content(new_content)

        assert handout.content == new_content
        assert handout.version.value == old_version + 1

    def test_update_content_same_no_change(self):
        """Test updating to same content doesn't increment version."""
        handout = make_basic_handout()
        old_version = handout.version.value

        same_content = "Name: Hero\nClass: Warrior\nLevel: 5"
        handout.update_content(same_content)

        assert handout.version.value == old_version

    def test_add_image(self):
        """Test adding an image to handout."""
        handout = make_text_only_handout()  # Starts with no images
        old_version = handout.version.value

        new_image_id = EntityId(300)
        handout.add_image(new_image_id)

        assert new_image_id in handout.image_ids
        assert handout.version.value == old_version + 1

    def test_add_duplicate_image_no_change(self):
        """Test adding duplicate image doesn't change anything."""
        handout = make_basic_handout()  # Has EntityId(200)
        old_version = handout.version.value

        duplicate_image_id = EntityId(200)
        handout.add_image(duplicate_image_id)

        assert handout.image_ids.count(EntityId(200)) == 1  # Still only one
        assert handout.version.value == old_version


class TestHandoutInvariants:
    """Test invariant enforcement."""

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        handout = make_basic_handout()
        # Manually set invalid timestamps
        object.__setattr__(handout, 'updated_at', Timestamp(handout.created_at.value - timedelta(hours=1)))
        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            handout._validate_invariants()

    def test_content_or_images_required(self):
        """Test that handout must have content or images."""
        with pytest.raises(InvariantViolation, match="Handout must have content or attachments"):
            Handout.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                title="Empty handout",
                content=None,
                image_ids=[],
            )

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        handout = make_basic_handout()
        # Try to set invalid timestamps
        object.__setattr__(handout, 'updated_at', handout.created_at)
        # Should not raise
        handout._validate_invariants()
        
        # Now set invalid
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp
        object.__setattr__(handout, 'updated_at', Timestamp(handout.created_at.value - timedelta(hours=1)))
        with pytest.raises(InvariantViolation):
            handout._validate_invariants()


class TestHandoutStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        handout = make_basic_handout()
        assert str(handout) == "Handout(Character Sheet, revealed=False)"

    def test_str_revealed_handout(self):
        """Test __str__ method for revealed handout."""
        handout = make_text_only_handout()
        handout.reveal()
        assert str(handout) == "Handout(Quest Log, revealed=True)"

    def test_str_long_title(self):
        """Test __str__ method with long title."""
        long_title = "This is a very long handout title that should be displayed in full in the string representation"
        handout = Handout.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            title=long_title,
            content="Test content",
        )
        str_repr = str(handout)
        assert long_title in str_repr
        assert "revealed=False" in str_repr

    def test_repr_representation(self):
        """Test __repr__ method."""
        handout = make_basic_handout()
        repr_str = repr(handout)
        assert "Handout(id=None" in repr_str
        assert "world_id=1" in repr_str
        assert "title='Character Sheet'" in repr_str
        assert "revealed=False" in repr_str
        assert "version=v1" in repr_str