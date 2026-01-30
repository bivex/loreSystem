"""Phenomenon entity for natural supernatural occurrences."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Phenomenon:
    """Represents a mysterious or supernatural phenomenon."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        phenomenon_type: str,
        location_id: UUID,
        duration_minutes: int,
        repeat_interval_days: Optional[int],
        effects: dict,
        is_mystical: bool,
        discovery_count: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.phenomenon_type = phenomenon_type
        self.location_id = location_id
        self.duration_minutes = duration_minutes
        self.repeat_interval_days = repeat_interval_days
        self.effects = effects
        self.is_mystical = is_mystical
        self.discovery_count = discovery_count
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        phenomenon_type: str,
        location_id: UUID,
        duration_minutes: int = 60,
        repeat_interval_days: Optional[int] = None,
        is_mystical: bool = False,
    ) -> "Phenomenon":
        """Factory method to create a new phenomenon."""
        if not name or not name.strip():
            raise ValueError("Phenomenon name is required")
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        if repeat_interval_days is not None and repeat_interval_days <= 0:
            raise ValueError("Repeat interval must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            phenomenon_type=phenomenon_type,
            location_id=location_id,
            duration_minutes=duration_minutes,
            repeat_interval_days=repeat_interval_days,
            effects={},
            is_mystical=is_mystical,
            discovery_count=0,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate phenomenon data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.duration_minutes, int) and self.duration_minutes > 0
            and isinstance(self.discovery_count, int) and self.discovery_count >= 0
        )

    def __repr__(self) -> str:
        return f"<Phenomenon {self.name}: {self.phenomenon_type}, mystical={self.is_mystical}>"
