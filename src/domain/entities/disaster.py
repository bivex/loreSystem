"""Disaster entity for catastrophic events."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Disaster:
    """Represents a natural or supernatural disaster."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        disaster_type: str,
        magnitude: float,
        epicenter_id: UUID,
        radius_km: float,
        damage_dealt: int,
        affected_populations: list[UUID],
        warning_time_minutes: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.disaster_type = disaster_type
        self.magnitude = magnitude
        self.epicenter_id = epicenter_id
        self.radius_km = radius_km
        self.damage_dealt = damage_dealt
        self.affected_populations = affected_populations
        self.warning_time_minutes = warning_time_minutes
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        disaster_type: str,
        magnitude: float,
        epicenter_id: UUID,
        radius_km: float,
        warning_time_minutes: int = 0,
    ) -> "Disaster":
        """Factory method to create a new disaster."""
        if not name or not name.strip():
            raise ValueError("Disaster name is required")
        if not 0.0 <= magnitude <= 10.0:
            raise ValueError("Magnitude must be between 0.0 and 10.0")
        if radius_km <= 0:
            raise ValueError("Radius must be positive")
        if warning_time_minutes < 0:
            raise ValueError("Warning time cannot be negative")

        damage_dealt = int(magnitude * 1000)

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            disaster_type=disaster_type,
            magnitude=magnitude,
            epicenter_id=epicenter_id,
            radius_km=radius_km,
            damage_dealt=damage_dealt,
            affected_populations=[],
            warning_time_minutes=warning_time_minutes,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate disaster data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.magnitude, (int, float)) and 0.0 <= self.magnitude <= 10.0
            and isinstance(self.radius_km, (int, float)) and self.radius_km > 0
        )

    def __repr__(self) -> str:
        return f"<Disaster {self.name}: {self.disaster_type}, magnitude={self.magnitude}>"
