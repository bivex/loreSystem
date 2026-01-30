"""WeatherPattern entity for environmental systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class WeatherPattern:
    """Represents a weather pattern affecting game regions."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        pattern_type: str,
        severity: float,
        duration_minutes: int,
        affected_regions: list[UUID],
        conditions: dict,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.pattern_type = pattern_type
        self.severity = severity
        self.duration_minutes = duration_minutes
        self.affected_regions = affected_regions
        self.conditions = conditions
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        pattern_type: str,
        severity: float = 0.5,
        duration_minutes: int = 60,
        affected_regions: Optional[list[UUID]] = None,
        conditions: Optional[dict] = None,
    ) -> "WeatherPattern":
        """Factory method to create a new weather pattern."""
        if not name or not name.strip():
            raise ValueError("Weather pattern name is required")
        if not 0.0 <= severity <= 1.0:
            raise ValueError("Severity must be between 0.0 and 1.0")
        if duration_minutes < 0:
            raise ValueError("Duration cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            pattern_type=pattern_type,
            severity=severity,
            duration_minutes=duration_minutes,
            affected_regions=affected_regions or [],
            conditions=conditions or {},
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate weather pattern data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.severity, (int, float)) and 0.0 <= self.severity <= 1.0
            and isinstance(self.duration_minutes, int) and self.duration_minutes >= 0
        )

    def __repr__(self) -> str:
        return f"<WeatherPattern {self.name}: {self.pattern_type}, severity={self.severity}>"
