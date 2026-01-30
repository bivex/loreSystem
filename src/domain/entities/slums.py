"""Slums entity for impoverished areas."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Slums:
    """Represents slum or impoverished district."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        population: int,
        poverty_level: float,
        crime_rate: float,
        disease_level: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.district_id = district_id
        self.population = population
        self.poverty_level = poverty_level
        self.crime_rate = crime_rate
        self.disease_level = disease_level
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        population: int = 500,
        poverty_level: float = 0.8,
        crime_rate: float = 0.6,
        disease_level: float = 0.4,
    ) -> "Slums":
        """Factory method to create slums."""
        if not name or not name.strip():
            raise ValueError("Slums name is required")
        if population < 0:
            raise ValueError("Population cannot be negative")
        if not (0 <= poverty_level <= 1) or not (0 <= crime_rate <= 1) or not (0 <= disease_level <= 1):
            raise ValueError("Levels must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            district_id=district_id,
            population=population,
            poverty_level=poverty_level,
            crime_rate=crime_rate,
            disease_level=disease_level,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate slums data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.population, int) and self.population >= 0
            and 0 <= self.poverty_level <= 1
            and 0 <= self.crime_rate <= 1
            and 0 <= self.disease_level <= 1
        )

    def __repr__(self) -> str:
        return f"<Slums {self.name}: {self.population} pop, poverty {self.poverty_level}>"
