"""
Session Entity

A Session represents a gaming session in Tome, tracking scheduling, attendance, and progress.
Part of the World aggregate.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import timedelta

from ..value_objects.common import (
    TenantId,
    EntityId,
    SessionName,
    Version,
    Timestamp,
    SessionStatus,
)
from ..exceptions import InvariantViolation


@dataclass
class Session:
    """
    Session entity within a World.

    Invariants:
    - Must belong to exactly one World
    - Scheduled start must be in future for scheduled sessions
    - Actual end must be after actual start if completed
    - Actual duration must be positive if completed
    - Must have at least one player
    - Version increases monotonically
    """

    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: SessionName
    description: str
    gm_id: EntityId
    status: SessionStatus
    scheduled_start: Timestamp
    estimated_duration_hours: float
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    player_ids: List[EntityId] = field(default_factory=list)
    actual_start: Optional[Timestamp] = None
    actual_end: Optional[Timestamp] = None
    actual_duration_hours: Optional[float] = None
    notes: str = ""

    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()

    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )

        if self.status == SessionStatus.SCHEDULED and self.scheduled_start.value <= Timestamp.now().value:
            raise InvariantViolation(
                "Scheduled start must be in the future for scheduled sessions"
            )

        if self.actual_start and self.actual_end:
            if self.actual_end.value < self.actual_start.value:
                raise InvariantViolation(
                    "Actual end must be after actual start"
                )
            if self.actual_duration_hours is not None and self.actual_duration_hours <= 0:
                raise InvariantViolation(
                    "Actual duration must be positive"
                )

        if len(self.player_ids) == 0:
            raise InvariantViolation(
                "Session must have at least one player"
            )

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: SessionName,
        description: str,
        player_ids: List[EntityId],
        gm_id: EntityId,
        scheduled_start: Timestamp,
        estimated_duration_hours: float,
    ) -> 'Session':
        """
        Factory method for creating a new Session.
        """
        if estimated_duration_hours <= 0:
            raise InvariantViolation("Estimated duration must be positive")

        if len(player_ids) == 0:
            raise InvariantViolation("Session must have at least one player")

        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            player_ids=player_ids.copy(),
            gm_id=gm_id,
            status=SessionStatus.SCHEDULED,
            scheduled_start=scheduled_start,
            estimated_duration_hours=estimated_duration_hours,
            actual_start=None,
            actual_end=None,
            actual_duration_hours=None,
            notes="",
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def start_session(self) -> None:
        """Start the session."""
        if self.status != SessionStatus.SCHEDULED:
            raise InvariantViolation("Can only start scheduled sessions")

        now = Timestamp.now()
        object.__setattr__(self, 'status', SessionStatus.ACTIVE)
        object.__setattr__(self, 'actual_start', now)
        object.__setattr__(self, 'actual_end', None)
        object.__setattr__(self, 'updated_at', now)
        object.__setattr__(self, 'version', self.version.increment())

    def end_session(self, notes: Optional[str] = None) -> None:
        """End the active session."""
        if self.status != SessionStatus.ACTIVE:
            raise InvariantViolation("Can only end active sessions")

        now = Timestamp.now()
        duration_hours = None
        if self.actual_start:
            duration = now.value - self.actual_start.value
            duration_hours = duration.total_seconds() / 3600

        object.__setattr__(self, 'status', SessionStatus.COMPLETED)
        object.__setattr__(self, 'actual_end', now)
        object.__setattr__(self, 'actual_duration_hours', duration_hours)
        if notes is not None:
            object.__setattr__(self, 'notes', notes)
        object.__setattr__(self, 'updated_at', now)
        object.__setattr__(self, 'version', self.version.increment())

    def cancel_session(self, reason: Optional[str] = None) -> None:
        """Cancel the scheduled session."""
        if self.status != SessionStatus.SCHEDULED:
            raise InvariantViolation("Can only cancel scheduled sessions")

        notes = f"Cancelled: {reason}" if reason else "Cancelled"
        now = Timestamp.now()

        object.__setattr__(self, 'status', SessionStatus.CANCELLED)
        object.__setattr__(self, 'notes', notes)
        object.__setattr__(self, 'updated_at', now)
        object.__setattr__(self, 'version', self.version.increment())

    def add_player(self, player_id: EntityId) -> None:
        """Add a player to the session."""
        if player_id in self.player_ids:
            raise InvariantViolation("Player already in session")

        self.player_ids.append(player_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())

    def remove_player(self, player_id: EntityId) -> None:
        """Remove a player from the session."""
        if player_id not in self.player_ids:
            raise InvariantViolation("Player not in session")

        if len(self.player_ids) == 1:
            raise InvariantViolation("Session must have at least one player")

        self.player_ids.remove(player_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())

    def update_description(self, description: str) -> None:
        """Update session description."""
        if self.description == description:
            return

        object.__setattr__(self, 'description', description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())

    # Query methods
    def is_scheduled(self) -> bool:
        """Check if session is scheduled."""
        return self.status == SessionStatus.SCHEDULED

    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == SessionStatus.ACTIVE

    def is_completed(self) -> bool:
        """Check if session is completed."""
        return self.status == SessionStatus.COMPLETED

    def is_cancelled(self) -> bool:
        """Check if session is cancelled."""
        return self.status == SessionStatus.CANCELLED

    def player_count(self) -> int:
        """Get number of players."""
        return len(self.player_ids)

    def has_started(self) -> bool:
        """Check if session has started."""
        return self.actual_start is not None

    def has_ended(self) -> bool:
        """Check if session has ended."""
        return self.actual_end is not None

    def __str__(self) -> str:
        return f"Session({self.name.value}, {self.status.value})"

    def __repr__(self) -> str:
        return (
            f"Session(id={self.id}, name={self.name}, "
            f"status={self.status}, version={self.version})"
        )