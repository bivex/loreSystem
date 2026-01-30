"""Wormhole entity for astronomical systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Wormhole:
    """Represents a wormhole connection."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        entrance_id: UUID,
        exit_id: UUID,
        diameter_km: float,
        stability: float,
        transit_time_seconds: float,
        is_stable: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.entrance_id = entrance_id
        self.exit_id = exit_id
        self.diameter_km = diameter_km
        self.stability = stability
        self.transit_time_seconds = transit_time_seconds
        self.is_stable = is_stable
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        entrance_id: UUID,
        exit_id: UUID,
        diameter_km: float = 10.0,
        stability: float = 0.8,
        transit_time_seconds: float = 60.0,
        is_stable: bool = True,
    ) -> "Wormhole":
        """Factory method to create a new wormhole."""
        if not name or not name.strip():
            raise ValueError("Wormhole name is required")
        if diameter_km <= 0:
            raise ValueError("Diameter must be positive")
        if not (0 <= stability <= 1):
            raise ValueError("Stability must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            entrance_id=entrance_id,
            exit_id=exit_id,
            diameter_km=diameter_km,
            stability=stability,
            transit_time_seconds=transit_time_seconds,
            is_stable=is_stable,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate wormhole data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.diameter_km, (int, float)) and self.diameter_km > 0
            and 0 <= self.stability <= 1
        )

    def __repr__(self) -> str:
        return f"<Wormhole {self.name}: stability {self.stability}, transit {self.transit_time_seconds}s>"
