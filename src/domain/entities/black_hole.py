"""BlackHole entity for astronomical systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class BlackHole:
    """Represents a black hole."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        hole_type: str,
        mass_solar_masses: float,
        location_id: UUID,
        event_horizon_km: float,
        accretion_disk: bool,
        singularity_type: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.hole_type = hole_type
        self.mass_solar_masses = mass_solar_masses
        self.location_id = location_id
        self.event_horizon_km = event_horizon_km
        self.accretion_disk = accretion_disk
        self.singularity_type = singularity_type
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        hole_type: str,
        mass_solar_masses: float,
        location_id: UUID,
        accretion_disk: bool = True,
        singularity_type: str = "ring",
    ) -> "BlackHole":
        """Factory method to create a new black hole."""
        if not name or not name.strip():
            raise ValueError("Black hole name is required")
        if mass_solar_masses <= 0:
            raise ValueError("Mass must be positive")

        event_horizon_km = 2.95 * mass_solar_masses

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            hole_type=hole_type,
            mass_solar_masses=mass_solar_masses,
            location_id=location_id,
            event_horizon_km=event_horizon_km,
            accretion_disk=accretion_disk,
            singularity_type=singularity_type,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate black hole data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.mass_solar_masses, (int, float)) and self.mass_solar_masses > 0
            and isinstance(self.event_horizon_km, (int, float)) and self.event_horizon_km > 0
        )

    def __repr__(self) -> str:
        return f"<BlackHole {self.name}: {self.hole_type}, {self.mass_solar_masses} solar masses>"
