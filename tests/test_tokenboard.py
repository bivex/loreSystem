"""
Tests for Tokenboard entity with edge cases and comprehensive coverage.
"""
import pytest

from src.domain.entities.tokenboard import Tokenboard
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
)
from src.domain.exceptions import InvariantViolation


def make_basic_tokenboard():
    """Factory for basic tokenboard."""
    return Tokenboard.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Battle Map",
        description="Current tactical situation.",
        counters={"initiative": 5, "round": 1},
        sticky_notes=["Remember to roll initiative", "Dragon has fire breath"],
        shortcuts={"next_round": "Ctrl+R", "add_token": "Ctrl+T"},
        timers={"combat_timer": 300},
        is_active=True,
    )


def make_empty_tokenboard():
    """Factory for empty tokenboard."""
    return Tokenboard.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Empty Board",
        description="Clean slate for new encounters.",
        counters={},
        sticky_notes=[],
        shortcuts={},
        timers={},
        is_active=False,
    )


class TestTokenboardCreation:
    """Test tokenboard creation scenarios."""

    def test_create_basic_tokenboard(self):
        """Test creating a basic tokenboard."""
        tokenboard = make_basic_tokenboard()
        assert tokenboard.name == "Battle Map"
        assert tokenboard.description == "Current tactical situation."
        assert tokenboard.counters == {"initiative": 5, "round": 1}
        assert tokenboard.sticky_notes == ["Remember to roll initiative", "Dragon has fire breath"]
        assert tokenboard.shortcuts == {"next_round": "Ctrl+R", "add_token": "Ctrl+T"}
        assert tokenboard.timers == {"combat_timer": 300}
        assert tokenboard.is_active
        assert tokenboard.version.value == 1

    def test_create_empty_tokenboard(self):
        """Test creating empty tokenboard."""
        tokenboard = make_empty_tokenboard()
        assert tokenboard.counters == {}
        assert tokenboard.sticky_notes == []
        assert tokenboard.shortcuts == {}
        assert tokenboard.timers == {}
        assert not tokenboard.is_active


class TestTokenboardOperations:
    """Test tokenboard modification operations."""

    def test_increment_counter(self):
        """Test incrementing a counter."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.increment_counter("initiative", 2)

        assert tokenboard.counters["initiative"] == 7
        assert tokenboard.version.value == old_version + 1



    def test_decrement_counter(self):
        """Test decrementing a counter."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.decrement_counter("round", 1)

        assert tokenboard.counters["round"] == 0
        assert tokenboard.version.value == old_version + 1

    def test_set_counter(self):
        """Test setting a counter to a specific value."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.set_counter("initiative", 10)

        assert tokenboard.counters["initiative"] == 10
        assert tokenboard.version.value == old_version + 1

    def test_add_sticky_note(self):
        """Test adding a sticky note."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.add_sticky_note("New note")

        assert "New note" in tokenboard.sticky_notes
        assert tokenboard.version.value == old_version + 1

    def test_remove_sticky_note(self):
        """Test removing a sticky note."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.remove_sticky_note(0)

        assert len(tokenboard.sticky_notes) == 1
        assert tokenboard.version.value == old_version + 1

    def test_add_shortcut(self):
        """Test adding a keyboard shortcut."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.add_shortcut("Ctrl+S", "save")

        assert tokenboard.shortcuts["Ctrl+S"] == "save"
        assert tokenboard.version.value == old_version + 1

    def test_remove_shortcut(self):
        """Test removing a keyboard shortcut."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.remove_shortcut("next_round")

        assert "next_round" not in tokenboard.shortcuts
        assert tokenboard.version.value == old_version + 1

    def test_start_timer(self):
        """Test starting a timer."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.start_timer("new_timer", 120)

        assert tokenboard.timers["new_timer"] == 120
        assert tokenboard.version.value == old_version + 1

    def test_stop_timer(self):
        """Test stopping a timer."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.stop_timer("combat_timer")

        assert "combat_timer" not in tokenboard.timers
        assert tokenboard.version.value == old_version + 1

    def test_activate(self):
        """Test activating the tokenboard."""
        tokenboard = make_empty_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.activate()

        assert tokenboard.is_active
        assert tokenboard.version.value == old_version + 1

    def test_deactivate(self):
        """Test deactivating the tokenboard."""
        tokenboard = make_basic_tokenboard()
        old_version = tokenboard.version.value

        tokenboard.deactivate()

        assert not tokenboard.is_active
        assert tokenboard.version.value == old_version + 1


class TestTokenboardInvariants:
    """Test invariant enforcement."""

    def test_updated_at_not_before_created_at(self):
        """Test that updated_at cannot be before created_at."""
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp

        tokenboard = make_basic_tokenboard()
        # Manually set invalid timestamps
        object.__setattr__(tokenboard, 'updated_at', Timestamp(tokenboard.created_at.value - timedelta(hours=1)))
        with pytest.raises(InvariantViolation, match="Updated timestamp must be >= created timestamp"):
            tokenboard._validate_invariants()

    def test_post_init_validates_invariants(self):
        """Test that invariants are checked after construction."""
        tokenboard = make_basic_tokenboard()
        # Try to set invalid timestamps
        from datetime import timedelta
        from src.domain.value_objects.common import Timestamp
        with pytest.raises(InvariantViolation):
            object.__setattr__(tokenboard, 'updated_at', Timestamp(tokenboard.created_at.value - timedelta(hours=1)))
            tokenboard._validate_invariants()


class TestTokenboardStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        tokenboard = make_basic_tokenboard()
        assert str(tokenboard) == "Tokenboard(Battle Map, active=True)"

    def test_str_inactive_tokenboard(self):
        """Test __str__ method for inactive tokenboard."""
        tokenboard = make_empty_tokenboard()
        assert str(tokenboard) == "Tokenboard(Empty Board, active=False)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        tokenboard = make_basic_tokenboard()
        repr_str = repr(tokenboard)
        assert "Tokenboard(id=None" in repr_str
        assert "world_id=1" in repr_str
        assert "name='Battle Map'" in repr_str
        assert "active=True" in repr_str
        assert "version=v1" in repr_str