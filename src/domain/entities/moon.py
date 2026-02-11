"""Moon entity for astronomical systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Moon:
    """Represents a moon."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        planet_id: UUID,
        diameter_km: float,
        distance_km: float,
        orbital_period_days: float,
        is_habitable: bool,
        has_atmosphere: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.planet_id = planet_id
        self.diameter_km = diameter_km
        self.distance_km = distance_km
        self.orbital_period_days = orbital_period_days
        self.is_habitable = is_habitable
        self.has_atmosphere = has_atmosphere
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        planet_id: UUID,
        diameter_km: float = 3474.0,
        distance_km: float = 384400.0,
        orbital_period_days: float = 27.3,
        is_habitable: bool = False,
        has_atmosphere: bool = False,
    ) -> "Moon":
        """Factory method to create a new moon."""
        if not name or not name.strip():
            raise ValueError("Moon name is required")
        if diameter_km <= 0 or distance_km <= 0 or orbital_period_days <= 0:
            raise ValueError("Diameter, distance and orbital period must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            planet_id=planet_id,
            diameter_km=diameter_km,
            distance_km=distance_km,
            orbital_period_days=orbital_period_days,
            is_habitable=is_habitable,
            has_atmosphere=has_atmosphere,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate moon data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.diameter_km, (int, float)) and self.diameter_km > 0
            and isinstance(self.distance_km, (int, float)) and self.distance_km > 0
            and isinstance(self.orbital_period_days, (int, float)) and self.orbital_period_days > 0
        )

    def __repr__(self) -> str:
        return f"<Moon {self.name}: {self.diameter_km}km, orbit {self.orbital_period_days} days>"
