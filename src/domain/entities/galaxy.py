"""Galaxy entity for astronomical systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Galaxy:
    """Represents a galaxy."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        galaxy_type: str,
        diameter_light_years: float,
        star_count: int,
        age_billion_years: float,
        mass_solar_masses: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.galaxy_type = galaxy_type
        self.diameter_light_years = diameter_light_years
        self.star_count = star_count
        self.age_billion_years = age_billion_years
        self.mass_solar_masses = mass_solar_masses
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        galaxy_type: str = "spiral",
        diameter_light_years: float = 100000.0,
        star_count: int = 100000000,
        age_billion_years: float = 13.6,
        mass_solar_masses: float = 1000000000000.0,
    ) -> "Galaxy":
        """Factory method to create a new galaxy."""
        if not name or not name.strip():
            raise ValueError("Galaxy name is required")
        if diameter_light_years <= 0 or star_count <= 0 or age_billion_years <= 0:
            raise ValueError("Diameter, star count and age must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            galaxy_type=galaxy_type,
            diameter_light_years=diameter_light_years,
            star_count=star_count,
            age_billion_years=age_billion_years,
            mass_solar_masses=mass_solar_masses,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate galaxy data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.diameter_light_years, (int, float)) and self.diameter_light_years > 0
            and isinstance(self.star_count, int) and self.star_count > 0
            and isinstance(self.age_billion_years, (int, float)) and self.age_billion_years > 0
        )

    def __repr__(self) -> str:
        return f"<Galaxy {self.name}: {self.galaxy_type}, {self.star_count} stars>"
