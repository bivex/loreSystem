"""WorldEvent entity for global game events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


VALID_WORLD_EVENT_SEVERITIES = {"low", "moderate", "high", "critical"}


@dataclass
class WorldEvent:
    """Represents a global event that affects a world scope."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    event_type: str
    description: Description
    severity: str
    start_date: Timestamp
    end_date: Timestamp | None
    affected_region_ids: list[EntityId] = field(default_factory=list)
    is_active: bool = True
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("WorldEvent name cannot be empty")
        if not self.event_type or not self.event_type.strip():
            raise InvariantViolation("WorldEvent event_type cannot be empty")
        if self.severity not in VALID_WORLD_EVENT_SEVERITIES:
            raise InvariantViolation(
                f"WorldEvent severity must be one of {sorted(VALID_WORLD_EVENT_SEVERITIES)}"
            )
        if self.end_date is not None and self.end_date.value < self.start_date.value:
            raise InvariantViolation("WorldEvent end_date cannot be before start_date")
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("WorldEvent updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        event_type: str,
        description: str,
        severity: str = "moderate",
        start_date: Timestamp | None = None,
        duration_days: int | None = None,
        affected_region_ids: list[EntityId] | None = None,
        is_active: bool = True,
    ) -> "WorldEvent":
        now = Timestamp.now()
        start = start_date or now
        end = Timestamp(start.value + timedelta(days=duration_days)) if duration_days and duration_days > 0 else None
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            event_type=event_type.strip(),
            description=Description(description.strip()),
            severity=severity,
            start_date=start,
            end_date=end,
            affected_region_ids=list(affected_region_ids or []),
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def validate(self) -> bool:
        try:
            self.__post_init__()
        except InvariantViolation:
            return False
        return True

    def end_event(self) -> None:
        self.is_active = False
        self.end_date = self.end_date or Timestamp.now()
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def __repr__(self) -> str:
        return f"<WorldEvent {self.name}: {self.event_type}, severity={self.severity}>"
