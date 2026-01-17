"""
Tests for Choice entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.choice import Choice
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    ChoiceType,
)
from src.domain.exceptions import InvariantViolation


def make_basic_choice():
    """Factory for basic choice."""
    return Choice.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        story_id=EntityId(10),
        prompt="What do you do?",
        choice_type=ChoiceType.BRANCH,
        options=["Go left", "Go right"],
        consequences=["You find treasure", "You encounter a monster"],
        next_story_ids=[EntityId(20), EntityId(21)],
    )


def make_choice_with_none_next_story():
    """Factory for choice with None next story (ending)."""
    return Choice.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        story_id=EntityId(10),
        prompt="Final choice",
        choice_type=ChoiceType.DECISION,
        options=["Accept", "Decline"],
        consequences=["You win", "Game over"],
        next_story_ids=[None, None],
        is_mandatory=False,
    )


class TestChoiceCreation:
    """Test choice creation scenarios."""

    def test_create_basic_choice(self):
        """Test creating a basic choice."""
        choice = make_basic_choice()
        assert choice.prompt == "What do you do?"
        assert choice.choice_type == ChoiceType.BRANCH
        assert len(choice.options) == 2
        assert len(choice.consequences) == 2
        assert len(choice.next_story_ids) == 2
        assert choice.is_mandatory
        assert choice.version.value == 1

    def test_create_choice_with_none_next_story(self):
        """Test creating choice with None next stories."""
        choice = make_choice_with_none_next_story()
        assert choice.next_story_ids == [None, None]
        assert not choice.is_mandatory

    def test_create_choice_insufficient_options_fails(self):
        """Test that choice with < 2 options fails."""
        with pytest.raises(InvariantViolation, match="Choice must have at least 2 options"):
            Choice.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                story_id=EntityId(10),
                prompt="Test",
                choice_type=ChoiceType.BRANCH,
                options=["Only one"],
                consequences=["Consequence"],
                next_story_ids=[EntityId(20)],
            )

    def test_create_choice_mismatched_lengths_fails(self):
        """Test that mismatched option/consequence/next_story lengths fail."""
        with pytest.raises(ValueError, match="Options, consequences, and next_story_ids must have same length"):
            Choice.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                story_id=EntityId(10),
                prompt="Test",
                choice_type=ChoiceType.BRANCH,
                options=["A", "B"],
                consequences=["C1"],  # Different length
                next_story_ids=[EntityId(20), EntityId(21)],
            )

    def test_create_choice_mismatched_consequences_fails(self):
        """Test that mismatched consequences length fails."""
        with pytest.raises(ValueError, match="Options, consequences, and next_story_ids must have same length"):
            Choice.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                story_id=EntityId(10),
                prompt="Test",
                choice_type=ChoiceType.BRANCH,
                options=["A", "B"],
                consequences=["C1", "C2", "C3"],  # Different length
                next_story_ids=[EntityId(20), EntityId(21)],
            )

    def test_create_choice_mismatched_next_stories_fails(self):
        """Test that mismatched next_story_ids length fails."""
        with pytest.raises(ValueError, match="Options, consequences, and next_story_ids must have same length"):
            Choice.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                story_id=EntityId(10),
                prompt="Test",
                choice_type=ChoiceType.BRANCH,
                options=["A", "B"],
                consequences=["C1", "C2"],
                next_story_ids=[EntityId(20)],  # Different length
            )


class TestChoiceOperations:
    """Test choice modification operations."""

    def test_update_options_valid(self):
        """Test updating options with valid data."""
        choice = make_basic_choice()
        old_version = choice.version.value

        new_options = ["Run", "Hide", "Fight"]
        new_consequences = ["You escape", "You hide", "You fight"]
        new_next_stories = [EntityId(30), EntityId(31), EntityId(32)]

        choice.update_options(new_options, new_consequences, new_next_stories)

        assert choice.options == new_options
        assert choice.consequences == new_consequences
        assert choice.next_story_ids == new_next_stories
        assert choice.version.value == old_version + 1

    def test_update_options_insufficient_options_fails(self):
        """Test updating to insufficient options fails."""
        choice = make_basic_choice()
        with pytest.raises(InvariantViolation, match="Choice must have at least 2 options"):
            choice.update_options(
                ["Only one"],
                ["Consequence"],
                [EntityId(20)]
            )

    def test_update_options_mismatched_lengths_fails(self):
        """Test updating with mismatched lengths fails."""
        choice = make_basic_choice()
        with pytest.raises(ValueError, match="Options, consequences, and next_story_ids must have same length"):
            choice.update_options(
                ["A", "B"],
                ["C1"],  # Different length
                [EntityId(20), EntityId(21)]
            )

    def test_update_prompt(self):
        """Test updating choice prompt."""
        choice = make_basic_choice()
        old_version = choice.version.value

        choice.update_prompt("What is your decision?")

        assert choice.prompt == "What is your decision?"
        assert choice.version.value == old_version + 1

    def test_update_prompt_same_no_change(self):
        """Test updating to same prompt doesn't increment version."""
        choice = make_basic_choice()
        old_version = choice.version.value

        choice.update_prompt("What do you do?")

        assert choice.version.value == old_version


class TestChoiceQueryMethods:
    """Test choice query methods."""

    def test_option_count(self):
        """Test option_count method."""
        choice = make_basic_choice()
        assert choice.option_count() == 2

    def test_has_consequences(self):
        """Test has_consequences method."""
        choice = make_basic_choice()
        assert choice.has_consequences()

        # Create choice with empty consequences
        choice_no_consequences = Choice.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            story_id=EntityId(10),
            prompt="Test",
            choice_type=ChoiceType.BRANCH,
            options=["A", "B"],
            consequences=["", "   "],  # Empty/whitespace
            next_story_ids=[EntityId(20), EntityId(21)],
        )
        assert not choice_no_consequences.has_consequences()


class TestChoiceInvariants:
    """Test invariant enforcement."""

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        choice = make_basic_choice()
        # Try to set invalid updated_at
        with pytest.raises(InvariantViolation):
            object.__setattr__(choice, 'updated_at', Timestamp(choice.created_at.value - timedelta(hours=1)))
            choice._validate_invariants()

    def test_options_length_invariant(self):
        """Test options length invariant."""
        choice = make_basic_choice()
        # Manually set invalid options
        with pytest.raises(InvariantViolation):
            object.__setattr__(choice, 'options', ["Only one"])
            choice._validate_invariants()

    def test_consequences_length_invariant(self):
        """Test consequences length invariant."""
        choice = make_basic_choice()
        # Manually set invalid consequences
        with pytest.raises(InvariantViolation):
            object.__setattr__(choice, 'consequences', ["Only one"])
            choice._validate_invariants()

    def test_next_story_ids_length_invariant(self):
        """Test next_story_ids length invariant."""
        choice = make_basic_choice()
        # Manually set invalid next_story_ids
        with pytest.raises(InvariantViolation):
            object.__setattr__(choice, 'next_story_ids', [EntityId(20)])
            choice._validate_invariants()


class TestChoiceStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        choice = make_basic_choice()
        assert str(choice) == "Choice(What do you do?..., 2 options)"

    def test_str_long_prompt(self):
        """Test __str__ method with long prompt."""
        choice = Choice.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            story_id=EntityId(10),
            prompt="This is a very long prompt that should be truncated in the string representation",
            choice_type=ChoiceType.BRANCH,
            options=["A", "B"],
            consequences=["C1", "C2"],
            next_story_ids=[EntityId(20), EntityId(21)],
        )
        str_repr = str(choice)
        assert "This is a very long prompt" in str_repr
        assert "..." in str_repr

    def test_repr_representation(self):
        """Test __repr__ method."""
        choice = make_basic_choice()
        repr_str = repr(choice)
        assert "Choice(id=None" in repr_str
        assert "story_id=10" in repr_str
        assert "options=2" in repr_str
        assert "version=v1" in repr_str