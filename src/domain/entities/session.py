"""Session entity for scheduled play sessions."""

from dataclasses import dataclass, field
from typing import List, Optional

from ..exceptions import InvariantViolation
from ..value_objects.common import (
    EntityId,
    SessionName,
    SessionStatus,
    TenantId,
    Timestamp,
    Version,
)


@dataclass
class Session:
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: SessionName
    description: str
    player_ids: List[EntityId]
    gm_id: EntityId
    scheduled_start: Timestamp
    estimated_duration_hours: float
    status: SessionStatus
    actual_start: Optional[Timestamp]
    actual_end: Optional[Timestamp]
    actual_duration_hours: Optional[float]
    notes: str
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    story_id: Optional[EntityId] = None
    skip_temporal_validation: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self):
        self._validate_invariants()

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
        story_id: Optional[EntityId] = None,
    ) -> "Session":
        now = Timestamp.now()
        session = cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            player_ids=list(player_ids),
            gm_id=gm_id,
            scheduled_start=scheduled_start,
            estimated_duration_hours=estimated_duration_hours,
            status=SessionStatus.SCHEDULED,
            actual_start=None,
            actual_end=None,
            actual_duration_hours=None,
            notes="",
            created_at=now,
            updated_at=now,
            version=Version(1),
            story_id=story_id,
        )
        if session.scheduled_start.value <= now.value:
            raise InvariantViolation("Scheduled start must be in the future")
        return session

    def _validate_invariants(self) -> None:
        if self.estimated_duration_hours <= 0:
            raise InvariantViolation("Estimated duration must be positive")
        if not self.player_ids:
            raise InvariantViolation("Session must have at least one player")
        if (
            not self.skip_temporal_validation
            and self.status == SessionStatus.SCHEDULED
            and self.scheduled_start.value <= Timestamp.now().value
        ):
            raise InvariantViolation("Scheduled start must be in the future for scheduled sessions")
        if self.actual_start and self.actual_end and self.actual_end.value < self.actual_start.value:
            raise InvariantViolation("Actual end must be after actual start")
        if self.actual_duration_hours is not None and self.actual_duration_hours <= 0:
            raise InvariantViolation("Actual duration must be positive")

    def _touch(self) -> None:
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def start_session(self) -> None:
        if self.status != SessionStatus.SCHEDULED:
            raise InvariantViolation("Can only start scheduled sessions")
        self.status = SessionStatus.ACTIVE
        self.actual_start = Timestamp.now()
        self.actual_end = None
        self.actual_duration_hours = None
        self._touch()

    def end_session(self, notes: str = "") -> None:
        if self.status != SessionStatus.ACTIVE:
            raise InvariantViolation("Can only end active sessions")
        self.status = SessionStatus.COMPLETED
        self.actual_end = Timestamp.now()
        elapsed = self.actual_end.value - self.actual_start.value
        self.actual_duration_hours = max(elapsed.total_seconds() / 3600, 1e-9)
        self.notes = notes
        self._touch()
        self._validate_invariants()

    def cancel_session(self, reason: str = "") -> None:
        if self.status != SessionStatus.SCHEDULED:
            raise InvariantViolation("Can only cancel scheduled sessions")
        self.status = SessionStatus.CANCELLED
        self.notes = f"Cancelled: {reason}" if reason else ""
        self._touch()

    def add_player(self, player_id: EntityId) -> None:
        if player_id in self.player_ids:
            raise InvariantViolation("Player already in session")
        self.player_ids.append(player_id)
        self._touch()

    def remove_player(self, player_id: EntityId) -> None:
        if player_id not in self.player_ids:
            raise InvariantViolation("Player not in session")
        remaining = [pid for pid in self.player_ids if pid != player_id]
        if not remaining:
            raise InvariantViolation("Session must have at least one player")
        self.player_ids = remaining
        self._touch()

    def update_description(self, description: str) -> None:
        if description == self.description:
            return
        self.description = description
        self._touch()

    def is_scheduled(self) -> bool: return self.status == SessionStatus.SCHEDULED
    def is_active(self) -> bool: return self.status == SessionStatus.ACTIVE
    def is_completed(self) -> bool: return self.status == SessionStatus.COMPLETED
    def is_cancelled(self) -> bool: return self.status == SessionStatus.CANCELLED
    def player_count(self) -> int: return len(self.player_ids)
    def has_started(self) -> bool: return self.actual_start is not None
    def has_ended(self) -> bool: return self.actual_end is not None
    def __str__(self) -> str: return f"Session({self.name.value}, {self.status.value})"

    def __repr__(self) -> str:
        return (
            "Session("
            f"id={self.id}, tenant_id={self.tenant_id}, world_id={self.world_id}, "
            f"name={self.name.value}, status=SessionStatus.{self.status.name}, "
            f"players={len(self.player_ids)}, version=v{self.version.value}"
            ")"
        )

