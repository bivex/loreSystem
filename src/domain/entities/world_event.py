"""WorldEvent entity for global game events."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class WorldEvent:
    """Represents a global event that affects the entire game world."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        event_type: str,
        description: str,
        severity: str,
        start_date: datetime,
        end_date: Optional[datetime],
        affected_regions: list[UUID],
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.event_type = event_type
        self.description = description
        self.severity = severity
        self.start_date = start_date
        self.end_date = end_date
        self.affected_regions = affected_regions
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        event_type: str,
        description: str,
        severity: str = "moderate",
        start_date: Optional[datetime] = None,
        duration_days: Optional[int] = None,
    ) -> "WorldEvent":
        """Factory method to create a new world event."""
        if not name or not name.strip():
            raise ValueError("Event name is required")
        if not event_type or not event_type.strip():
            raise ValueError("Event type is required")
        if severity not in ["minor", "moderate", "major", "catastrophic", "apocalyptic"]:
            raise ValueError("Severity must be one of: minor, moderate, major, catastrophic, apocalyptic")

        start = start_date or datetime.utcnow()
        end = None
        if duration_days and duration_days > 0:
            from datetime import timedelta
            end = start + timedelta(days=duration_days)

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            event_type=event_type.strip(),
            description=description.strip(),
            severity=severity,
            start_date=start,
            end_date=end,
            affected_regions=[],
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate world event data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.event_type, str) and len(self.event_type) > 0
            and self.severity in ["minor", "moderate", "major", "catastrophic", "apocalyptic"]
            and isinstance(self.start_date, datetime)
            and (self.end_date is None or self.end_date > self.start_date)
        )

    def end_event(self) -> None:
        """Mark the event as ended."""
        self.is_active = False
        self.end_date = self.end_date or datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<WorldEvent {self.name}: {self.event_type}, severity={self.severity}>"
