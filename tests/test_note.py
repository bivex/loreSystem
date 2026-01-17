"""
Tests for Note entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.note import Note
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
)
from src.domain.exceptions import InvariantViolation


def make_basic_note():
    """Factory for basic note."""
    return Note.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        title="Important Note",
        content="This is a very important note about the world.",
        tags=["important", "world-building"],
        is_pinned=False,
    )


def make_note_with_empty_tags():
    """Factory for note with no tags."""
    return Note.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        title="Simple Note",
        content="Simple content",
        tags=[],
        is_pinned=True,
    )


class TestNoteCreation:
    """Test note creation scenarios."""

    def test_create_basic_note(self):
        """Test creating a basic note."""
        note = make_basic_note()
        assert note.title == "Important Note"
        assert note.content == "This is a very important note about the world."
        assert note.tags == ["important", "world-building"]
        assert note.version.value == 1

    def test_create_note_with_empty_tags(self):
        """Test creating note with no tags."""
        note = make_note_with_empty_tags()
        assert note.tags == []




class TestNoteOperations:
    """Test note modification operations."""

    def test_update_content(self):
        """Test updating note content."""
        note = make_basic_note()
        old_version = note.version.value

        new_content = "Updated content for this important note."
        note.update_content(new_content)

        assert note.content == new_content
        assert note.version.value == old_version + 1

    def test_update_content_same_no_change(self):
        """Test updating to same content doesn't increment version."""
        note = make_basic_note()
        old_version = note.version.value

        same_content = "This is a very important note about the world."
        note.update_content(same_content)

        assert note.version.value == old_version

    def test_add_tag(self):
        """Test adding a tag."""
        note = make_basic_note()
        old_version = note.version.value

        note.add_tag("new-tag")

        assert "new-tag" in note.tags
        assert len(note.tags) == 3
        assert note.version.value == old_version + 1

    def test_add_duplicate_tag_fails(self):
        """Test adding duplicate tag does nothing."""
        note = make_basic_note()
        old_version = note.version.value

        note.add_tag("important")  # Already exists

        assert note.version.value == old_version  # No change

    def test_remove_tag(self):
        """Test removing a tag."""
        note = make_basic_note()
        old_version = note.version.value

        note.remove_tag("important")

        assert "important" not in note.tags
        assert len(note.tags) == 1
        assert note.version.value == old_version + 1

    def test_remove_nonexistent_tag_fails(self):
        """Test removing nonexistent tag does nothing."""
        note = make_basic_note()
        old_version = note.version.value

        note.remove_tag("nonexistent")

        assert note.version.value == old_version  # No change



    def test_update_title(self):
        """Test updating note title."""
        note = make_basic_note()
        old_version = note.version.value

        new_title = "Updated Title"
        note.update_title(new_title)

        assert note.title == new_title
        assert note.version.value == old_version + 1

    def test_update_title_same_no_change(self):
        """Test updating to same title doesn't increment version."""
        note = make_basic_note()
        old_version = note.version.value

        same_title = "Important Note"
        note.update_title(same_title)

        assert note.version.value == old_version





class TestNoteInvariants:
    """Test invariant enforcement."""

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        note = make_basic_note()
        # Manually set invalid timestamps
        object.__setattr__(note, 'updated_at', Timestamp(note.created_at.value - timedelta(hours=1)))
        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            note._validate_invariants()

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        note = make_basic_note()
        # Try to set invalid content
        with pytest.raises(InvariantViolation):
            object.__setattr__(note, 'content', "")
            note._validate_invariants()


class TestNoteStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        note = make_basic_note()
        assert str(note) == "Note(Important Note)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        note = make_basic_note()
        repr_str = repr(note)
        assert "Note(id=None" in repr_str
        assert "world_id=1" in repr_str
        assert "title='Important Note'" in repr_str
        assert "pinned=False" in repr_str
        assert "version=v1" in repr_str