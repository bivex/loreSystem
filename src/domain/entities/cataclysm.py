"""Cataclysm entity for world-changing events."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Cataclysm:
    """Represents a cataclysmic world-altering event."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        cataclysm_type: str,
        severity: float,
        trigger_event_id: Optional[UUID],
        affected_locations: list[UUID],
        permanent_changes: dict,
        recovery_progress: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.cataclysm_type = cataclysm_type
        self.severity = severity
        self.trigger_event_id = trigger_event_id
        self.affected_locations = affected_locations
        self.permanent_changes = permanent_changes
        self.recovery_progress = recovery_progress
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        cataclysm_type: str,
        severity: float,
        trigger_event_id: Optional[UUID] = None,
        affected_locations: Optional[list[UUID]] = None,
        permanent_changes: Optional[dict] = None,
    ) -> "Cataclysm":
        """Factory method to create a new cataclysm."""
        if not name or not name.strip():
            raise ValueError("Cataclysm name is required")
        if not 0.0 <= severity <= 1.0:
            raise ValueError("Severity must be between 0.0 and 1.0")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            cataclysm_type=cataclysm_type,
            severity=severity,
            trigger_event_id=trigger_event_id,
            affected_locations=affected_locations or [],
            permanent_changes=permanent_changes or {},
            recovery_progress=0.0,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate cataclysm data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.severity, (int, float)) and 0.0 <= self.severity <= 1.0
            and isinstance(self.recovery_progress, (int, float)) and 0.0 <= self.recovery_progress <= 1.0
        )

    def __repr__(self) -> str:
        return f"<Cataclysm {self.name}: {self.cataclysm_type}, severity={self.severity}>"
