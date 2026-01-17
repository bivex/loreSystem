"""
Tests for Session entity with edge cases and comprehensive coverage.
"""
import pytest
from datetime import datetime, timedelta, timezone

from src.domain.entities.session import Session
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    SessionName,
    Timestamp,
    SessionStatus,
)
from src.domain.exceptions import InvariantViolation


def make_basic_session():
    """Factory for basic session."""
    return Session.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name=SessionName("Session 1"),
        description="First gaming session",
        player_ids=[EntityId(100), EntityId(101)],
        gm_id=EntityId(99),
        scheduled_start=Timestamp(datetime.now(timezone.utc) + timedelta(hours=1)),
        estimated_duration_hours=3.0,
    )


def make_active_session():
    """Factory for active session."""
    session = make_basic_session()
    session.start_session()
    return session


def make_completed_session():
    """Factory for completed session."""
    session = make_active_session()
    session.end_session("Great session!")
    return session


class TestSessionCreation:
    """Test session creation scenarios."""

    def test_create_basic_session(self):
        """Test creating a basic session."""
        session = make_basic_session()
        assert session.name.value == "Session 1"
        assert session.description == "First gaming session"
        assert len(session.player_ids) == 2
        assert session.gm_id == EntityId(99)
        assert session.status == SessionStatus.SCHEDULED
        assert session.estimated_duration_hours == 3.0
        assert session.actual_duration_hours is None
        assert session.notes == ""
        assert session.version.value == 1

    def test_create_session_with_past_start_fails(self):
        """Test that session with past scheduled start fails."""
        with pytest.raises(InvariantViolation, match="Scheduled start must be in the future"):
            Session.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=SessionName("Past Session"),
                description="This should fail",
                player_ids=[EntityId(100)],
                gm_id=EntityId(99),
                scheduled_start=Timestamp(datetime.now(timezone.utc) - timedelta(hours=1)),
                estimated_duration_hours=2.0,
            )

    def test_create_session_negative_duration_fails(self):
        """Test that session with negative duration fails."""
        with pytest.raises(InvariantViolation, match="Estimated duration must be positive"):
            Session.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=SessionName("Invalid Duration"),
                description="Test",
                player_ids=[EntityId(100)],
                gm_id=EntityId(99),
                scheduled_start=Timestamp(datetime.now(timezone.utc) + timedelta(hours=1)),
                estimated_duration_hours=-1.0,
            )

    def test_create_session_zero_duration_fails(self):
        """Test that session with zero duration fails."""
        with pytest.raises(InvariantViolation, match="Estimated duration must be positive"):
            Session.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=SessionName("Zero Duration"),
                description="Test",
                player_ids=[EntityId(100)],
                gm_id=EntityId(99),
                scheduled_start=Timestamp(datetime.now(timezone.utc) + timedelta(hours=1)),
                estimated_duration_hours=0.0,
            )

    def test_create_session_empty_players_fails(self):
        """Test that session with no players fails."""
        with pytest.raises(InvariantViolation, match="Session must have at least one player"):
            Session.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name=SessionName("No Players"),
                description="Test",
                player_ids=[],
                gm_id=EntityId(99),
                scheduled_start=Timestamp(datetime.now(timezone.utc) + timedelta(hours=1)),
                estimated_duration_hours=2.0,
            )


class TestSessionOperations:
    """Test session state transitions and operations."""

    def test_start_session(self):
        """Test starting a scheduled session."""
        session = make_basic_session()
        old_version = session.version.value

        session.start_session()

        assert session.status == SessionStatus.ACTIVE
        assert session.actual_start is not None
        assert session.actual_end is None
        assert session.version.value == old_version + 1

    def test_start_already_active_fails(self):
        """Test starting an already active session fails."""
        session = make_active_session()
        with pytest.raises(InvariantViolation, match="Can only start scheduled sessions"):
            session.start_session()

    def test_start_completed_session_fails(self):
        """Test starting a completed session fails."""
        session = make_completed_session()
        with pytest.raises(InvariantViolation, match="Can only start scheduled sessions"):
            session.start_session()

    def test_end_session(self):
        """Test ending an active session."""
        session = make_active_session()
        old_version = session.version.value

        session.end_session("Session completed successfully")

        assert session.status == SessionStatus.COMPLETED
        assert session.actual_end is not None
        assert session.actual_duration_hours is not None
        assert session.actual_duration_hours > 0
        assert session.notes == "Session completed successfully"
        assert session.version.value == old_version + 1

    def test_end_session_without_notes(self):
        """Test ending session without notes."""
        session = make_active_session()
        session.end_session()

        assert session.status == SessionStatus.COMPLETED
        assert session.notes == ""

    def test_end_scheduled_session_fails(self):
        """Test ending a scheduled session fails."""
        session = make_basic_session()
        with pytest.raises(InvariantViolation, match="Can only end active sessions"):
            session.end_session()

    def test_end_completed_session_fails(self):
        """Test ending an already completed session fails."""
        session = make_completed_session()
        with pytest.raises(InvariantViolation, match="Can only end active sessions"):
            session.end_session()

    def test_cancel_session(self):
        """Test canceling a scheduled session."""
        session = make_basic_session()
        old_version = session.version.value

        session.cancel_session("Weather issues")

        assert session.status == SessionStatus.CANCELLED
        assert session.notes == "Cancelled: Weather issues"
        assert session.version.value == old_version + 1

    def test_cancel_active_session_fails(self):
        """Test canceling an active session fails."""
        session = make_active_session()
        with pytest.raises(InvariantViolation, match="Can only cancel scheduled sessions"):
            session.cancel_session()

    def test_cancel_completed_session_fails(self):
        """Test canceling a completed session fails."""
        session = make_completed_session()
        with pytest.raises(InvariantViolation, match="Can only cancel scheduled sessions"):
            session.cancel_session()

    def test_add_player(self):
        """Test adding a player to session."""
        session = make_basic_session()
        old_version = session.version.value

        new_player = EntityId(102)
        session.add_player(new_player)

        assert new_player in session.player_ids
        assert len(session.player_ids) == 3
        assert session.version.value == old_version + 1

    def test_add_duplicate_player_fails(self):
        """Test adding duplicate player fails."""
        session = make_basic_session()
        existing_player = session.player_ids[0]

        with pytest.raises(InvariantViolation, match="Player already in session"):
            session.add_player(existing_player)

    def test_remove_player(self):
        """Test removing a player from session."""
        session = make_basic_session()
        old_version = session.version.value

        player_to_remove = session.player_ids[0]
        session.remove_player(player_to_remove)

        assert player_to_remove not in session.player_ids
        assert len(session.player_ids) == 1
        assert session.version.value == old_version + 1

    def test_remove_nonexistent_player_fails(self):
        """Test removing nonexistent player fails."""
        session = make_basic_session()
        nonexistent_player = EntityId(999)

        with pytest.raises(InvariantViolation, match="Player not in session"):
            session.remove_player(nonexistent_player)

    def test_remove_last_player_fails(self):
        """Test removing the last player fails."""
        session = make_basic_session()
        session.player_ids = [EntityId(100)]  # Manually set to one player

        with pytest.raises(InvariantViolation, match="Session must have at least one player"):
            session.remove_player(EntityId(100))

    def test_update_description(self):
        """Test updating session description."""
        session = make_basic_session()
        old_version = session.version.value

        session.update_description("Updated description")

        assert session.description == "Updated description"
        assert session.version.value == old_version + 1

    def test_update_description_same_no_change(self):
        """Test updating to same description doesn't increment version."""
        session = make_basic_session()
        old_version = session.version.value

        session.update_description("First gaming session")

        assert session.version.value == old_version


class TestSessionQueryMethods:
    """Test session query methods."""

    def test_is_scheduled(self):
        """Test is_scheduled method."""
        session = make_basic_session()
        assert session.is_scheduled()

        active_session = make_active_session()
        assert not active_session.is_scheduled()

    def test_is_active(self):
        """Test is_active method."""
        session = make_basic_session()
        assert not session.is_active()

        active_session = make_active_session()
        assert active_session.is_active()

    def test_is_completed(self):
        """Test is_completed method."""
        session = make_basic_session()
        assert not session.is_completed()

        completed_session = make_completed_session()
        assert completed_session.is_completed()

    def test_is_cancelled(self):
        """Test is_cancelled method."""
        session = make_basic_session()
        assert not session.is_cancelled()

        session.cancel_session()
        assert session.is_cancelled()

    def test_player_count(self):
        """Test player_count method."""
        session = make_basic_session()
        assert session.player_count() == 2

    def test_has_started(self):
        """Test has_started method."""
        session = make_basic_session()
        assert not session.has_started()

        active_session = make_active_session()
        assert active_session.has_started()

    def test_has_ended(self):
        """Test has_ended method."""
        session = make_basic_session()
        assert not session.has_ended()

        completed_session = make_completed_session()
        assert completed_session.has_ended()


class TestSessionInvariants:
    """Test invariant enforcement."""

    def test_actual_start_before_end(self):
        """Test that actual_end cannot be before actual_start."""
        session = make_active_session()
        # Manually set invalid end time
        with pytest.raises(InvariantViolation, match="Actual end must be after actual start"):
            object.__setattr__(session, 'actual_end', Timestamp(session.actual_start.value - timedelta(hours=1)))
            session._validate_invariants()

    def test_actual_duration_positive(self):
        """Test that actual duration must be positive."""
        session = make_completed_session()
        # Manually set invalid duration
        with pytest.raises(InvariantViolation, match="Actual duration must be positive"):
            object.__setattr__(session, 'actual_duration_hours', -1.0)
            session._validate_invariants()

    def test_scheduled_start_future_for_scheduled(self):
        """Test that scheduled start must be future for scheduled sessions."""
        session = make_basic_session()
        # Manually set past start
        with pytest.raises(InvariantViolation, match="Scheduled start must be in the future for scheduled sessions"):
            object.__setattr__(session, 'scheduled_start', Timestamp(datetime.now(timezone.utc) - timedelta(hours=1)))
            session._validate_invariants()

    def test_at_least_one_player(self):
        """Test that session must have at least one player."""
        session = make_basic_session()
        # Manually set empty players
        with pytest.raises(InvariantViolation, match="Session must have at least one player"):
            object.__setattr__(session, 'player_ids', [])
            session._validate_invariants()


class TestSessionStringRepresentations:
    """Test string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        session = make_basic_session()
        assert str(session) == "Session(Session 1, scheduled)"

    def test_repr_representation(self):
        """Test __repr__ method."""
        session = make_basic_session()
        repr_str = repr(session)
        assert "Session(id=None" in repr_str
        assert "name=Session 1" in repr_str
        assert "status=SessionStatus.SCHEDULED" in repr_str
        assert "version=v1" in repr_str