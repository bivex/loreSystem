"""District entity for urban architecture."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class District:
    """Represents a district within a city."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        city_id: UUID,
        district_type: str,
        population: int,
        safety_level: float,
        prosperity_level: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.city_id = city_id
        self.district_type = district_type
        self.population = population
        self.safety_level = safety_level
        self.prosperity_level = prosperity_level
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        city_id: UUID,
        district_type: str = "residential",
        population: int = 1000,
        safety_level: float = 0.8,
        prosperity_level: float = 0.5,
    ) -> "District":
        """Factory method to create a new district."""
        if not name or not name.strip():
            raise ValueError("District name is required")
        if population < 0:
            raise ValueError("Population cannot be negative")
        if not (0 <= safety_level <= 1) or not (0 <= prosperity_level <= 1):
            raise ValueError("Levels must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            city_id=city_id,
            district_type=district_type,
            population=population,
            safety_level=safety_level,
            prosperity_level=prosperity_level,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate district data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.population, int) and self.population >= 0
            and 0 <= self.safety_level <= 1
            and 0 <= self.prosperity_level <= 1
        )

    def __repr__(self) -> str:
        return f"<District {self.name}: {self.population} pop, {self.district_type}>"
