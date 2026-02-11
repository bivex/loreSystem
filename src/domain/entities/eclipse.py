"""Eclipse entity for astronomical events."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Eclipse:
    """Represents an eclipse event."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        eclipse_type: str,
        celestial_body_id: UUID,
        start_time: datetime,
        duration_minutes: float,
        visibility_region: UUID,
        magnitude: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.eclipse_type = eclipse_type
        self.celestial_body_id = celestial_body_id
        self.start_time = start_time
        self.duration_minutes = duration_minutes
        self.visibility_region = visibility_region
        self.magnitude = magnitude
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        eclipse_type: str,
        celestial_body_id: UUID,
        start_time: datetime,
        duration_minutes: float,
        visibility_region: Optional[UUID] = None,
        magnitude: float = 1.0,
    ) -> "Eclipse":
        """Factory method to create an eclipse event."""
        if not name or not name.strip():
            raise ValueError("Eclipse name is required")
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        if not (0 <= magnitude <= 1):
            raise ValueError("Magnitude must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            eclipse_type=eclipse_type,
            celestial_body_id=celestial_body_id,
            start_time=start_time,
            duration_minutes=duration_minutes,
            visibility_region=visibility_region,
            magnitude=magnitude,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate eclipse data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.duration_minutes, (int, float)) and self.duration_minutes > 0
            and 0 <= self.magnitude <= 1
        )

    def __repr__(self) -> str:
        return f"<Eclipse {self.name}: {self.eclipse_type}, magnitude {self.magnitude}>"
