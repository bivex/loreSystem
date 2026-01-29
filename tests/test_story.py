"""
Tests for Story entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.story import Story
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    StoryName,
    Content,
    StoryType,
)
from src.domain.exceptions import InvariantViolation


def make_basic_story():
    """Factory for basic story."""
    return Story.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=StoryName("The Hero's Journey"),
        description="A classic hero's journey story",
        story_type=StoryType.LINEAR,
        content=Content("Once upon a time..."),
    )


def make_non_linear_story():
    """Factory for non-linear story."""
    return Story.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=StoryName("Choose Your Path"),
        description="Interactive story with choices",
        story_type=StoryType.NON_LINEAR,
        content=Content("You stand at a crossroads..."),
        choice_ids=[EntityId(10), EntityId(11)],
        connected_world_ids=[EntityId(20), EntityId(21)],
        is_active=True,
    )


class TestStoryCreation:
    """Test story creation scenarios."""

    def test_create_basic_story(self):
        """Test creating a basic story."""
        story = make_basic_story()
        assert story.name.value == "The Hero's Journey"
        assert story.description == "A classic hero's journey story"
        assert story.story_type == StoryType.LINEAR
        assert story.choice_ids == []
        assert story.connected_world_ids == []
        assert story.is_active
        assert story.version.value == 1

    def test_create_non_linear_story(self):
        """Test creating non-linear story with choices."""
        story = make_non_linear_story()
        assert story.story_type == StoryType.NON_LINEAR
        assert len(story.choice_ids) == 2
        assert len(story.connected_world_ids) == 2

    def test_create_inactive_story(self):
        """Test creating inactive story."""
        story = Story.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=StoryName("Draft Story"),
            description="Work in progress",
            story_type=StoryType.LINEAR,
            content=Content("Draft content"),
            is_active=False,
        )
        assert not story.is_active

    def test_create_story_empty_content_fails(self):
        """Test that empty content raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Story.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=StoryName("Test"),
                description="Test",
                story_type=StoryType.LINEAR,
                content=Content(""),
            )

    def test_create_story_whitespace_content_fails(self):
        """Test that whitespace-only content raises error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Story.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=StoryName("Test"),
                description="Test",
                story_type=StoryType.LINEAR,
                content=Content("   \n\t   "),
            )


class TestStoryOperations:
    """Test story modification operations."""

    def test_update_content(self):
        """Test updating story content."""
        story = make_basic_story()
        old_version = story.version.value

        new_content = Content("Updated story content.")
        story.update_content(new_content)

        assert story.content == new_content
        assert story.version.value == old_version + 1

    def test_update_content_same_no_change(self):
        """Test updating to same content doesn't increment version."""
        story = make_basic_story()
        old_version = story.version.value

        story.update_content(Content("Once upon a time..."))

        assert story.version.value == old_version


class TestStoryChoices:
    """Test choice management operations."""

    def test_add_choice(self):
        """Test adding a choice."""
        story = make_basic_story()
        old_version = story.version.value

        choice_id = EntityId(10)
        story.add_choice(choice_id)

        assert choice_id in story.choice_ids
        assert story.version.value == old_version + 1

    def test_add_duplicate_choice_no_change(self):
        """Test adding duplicate choice doesn't change anything."""
        story = make_non_linear_story()
        old_version = story.version.value
        old_count = len(story.choice_ids)

        story.add_choice(EntityId(10))  # Already exists

        assert len(story.choice_ids) == old_count
        assert story.version.value == old_version

    def test_remove_choice(self):
        """Test removing a choice."""
        story = make_non_linear_story()
        old_version = story.version.value

        choice_id = EntityId(10)
        story.remove_choice(choice_id)

        assert choice_id not in story.choice_ids
        assert story.version.value == old_version + 1

    def test_remove_nonexistent_choice_no_change(self):
        """Test removing non-existent choice doesn't change anything."""
        story = make_basic_story()
        old_version = story.version.value

        story.remove_choice(EntityId(99))

        assert story.version.value == old_version


class TestStoryWorldConnections:
    """Test world element connection operations."""

    def test_connect_world_element(self):
        """Test connecting a world element."""
        story = make_basic_story()
        old_version = story.version.value

        world_element_id = EntityId(20)
        story.connect_world_element(world_element_id)

        assert world_element_id in story.connected_world_ids
        assert story.version.value == old_version + 1

    def test_connect_duplicate_world_element_no_change(self):
        """Test connecting duplicate world element doesn't change anything."""
        story = make_non_linear_story()
        old_version = story.version.value
        old_count = len(story.connected_world_ids)

        story.connect_world_element(EntityId(20))  # Already exists

        assert len(story.connected_world_ids) == old_count
        assert story.version.value == old_version

    def test_disconnect_world_element(self):
        """Test disconnecting a world element."""
        story = make_non_linear_story()
        old_version = story.version.value

        world_element_id = EntityId(20)
        story.disconnect_world_element(world_element_id)

        assert world_element_id not in story.connected_world_ids
        assert story.version.value == old_version + 1

    def test_disconnect_nonexistent_world_element_no_change(self):
        """Test disconnecting non-existent world element doesn't change anything."""
        story = make_basic_story()
        old_version = story.version.value

        story.disconnect_world_element(EntityId(99))

        assert story.version.value == old_version


class TestStoryActivation:
    """Test story activation/deactivation."""

    def test_activate_story(self):
        """Test activating a story."""
        story = Story.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=StoryName("Inactive Story"),
            description="Inactive",
            story_type=StoryType.LINEAR,
            content=Content("Content"),
            is_active=False,
        )
        old_version = story.version.value

        story.activate()

        assert story.is_active
        assert story.version.value == old_version + 1

    def test_activate_already_active_no_change(self):
        """Test activating already active story doesn't change anything."""
        story = make_basic_story()
        old_version = story.version.value

        story.activate()

        assert story.version.value == old_version

    def test_deactivate_story(self):
        """Test deactivating a story."""
        story = make_basic_story()
        old_version = story.version.value

        story.deactivate()

        assert not story.is_active
        assert story.version.value == old_version + 1

    def test_deactivate_already_inactive_no_change(self):
        """Test deactivating already inactive story doesn't change anything."""
        story = Story.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=StoryName("Inactive Story"),
            description="Inactive",
            story_type=StoryType.LINEAR,
            content=Content("Content"),
            is_active=False,
        )
        old_version = story.version.value

        story.deactivate()

        assert story.version.value == old_version


class TestStoryTypeMethods:
    """Test story type specific methods."""

    def test_is_non_linear_method(self):
        """Test is_non_linear method."""
        linear_story = make_basic_story()
        non_linear_story = make_non_linear_story()
        interactive_story = Story.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=StoryName("Interactive Story"),
            description="Interactive",
            story_type=StoryType.INTERACTIVE,
            content=Content("Interactive content"),
        )

        assert not linear_story.is_non_linear()
        assert non_linear_story.is_non_linear()
        assert interactive_story.is_non_linear()


class TestStoryInvariants:
    """Test invariant enforcement."""

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        story = make_basic_story()
        # Manually set invalid timestamps
        object.__setattr__(story, 'updated_at', Timestamp(story.created_at.value - timedelta(hours=1)))
        # Validation should fail when explicitly called
        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            story._validate_invariants()

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        story = make_basic_story()
        # Try to set invalid updated_at
        with pytest.raises(InvariantViolation):
            object.__setattr__(story, 'updated_at', Timestamp(story.created_at.value - timedelta(hours=1)))
            story._validate_invariants()


class TestStoryStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        story = make_basic_story()
        assert str(story) == "Story(The Hero's Journey, type=linear)"

    def test_non_linear_str_representation(self):
        """Test __str__ method for non-linear story."""
        story = make_non_linear_story()
        assert str(story) == "Story(Choose Your Path, type=non_linear)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        story = make_basic_story()
        repr_str = repr(story)
        assert "Story(id=None" in repr_str
        assert "name='The Hero's Journey'" in repr_str
        assert "type=linear" in repr_str
        assert "version=v1" in repr_str