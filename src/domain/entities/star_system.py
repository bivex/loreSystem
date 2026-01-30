"""StarSystem entity for astronomical systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class StarSystem:
    """Represents a star system."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        star_type: str,
        galaxy_id: UUID,
        star_count: int,
        planet_count: int,
        age_billion_years: float,
        habitable_planets: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.star_type = star_type
        self.galaxy_id = galaxy_id
        self.star_count = star_count
        self.planet_count = planet_count
        self.age_billion_years = age_billion_years
        self.habitable_planets = habitable_planets
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        star_type: str = "g_type",
        galaxy_id: Optional[UUID] = None,
        star_count: int = 1,
        planet_count: int = 8,
        age_billion_years: float = 4.6,
        habitable_planets: int = 1,
    ) -> "StarSystem":
        """Factory method to create a new star system."""
        if not name or not name.strip():
            raise ValueError("Star system name is required")
        if star_count <= 0 or planet_count < 0 or age_billion_years <= 0:
            raise ValueError("Star count and age must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            star_type=star_type,
            galaxy_id=galaxy_id,
            star_count=star_count,
            planet_count=planet_count,
            age_billion_years=age_billion_years,
            habitable_planets=habitable_planets,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate star system data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.star_count, int) and self.star_count > 0
            and isinstance(self.planet_count, int) and self.planet_count >= 0
            and isinstance(self.age_billion_years, (int, float)) and self.age_billion_years > 0
        )

    def __repr__(self) -> str:
        return f"<StarSystem {self.name}: {self.star_count} stars, {self.planet_count} planets>"
