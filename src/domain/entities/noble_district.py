"""NobleDistrict entity for wealthy residential areas."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class NobleDistrict:
    """Represents a noble or wealthy district."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        population: int,
        wealth_level: float,
        security_level: float,
        prestige: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.district_id = district_id
        self.population = population
        self.wealth_level = wealth_level
        self.security_level = security_level
        self.prestige = prestige
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        population: int = 100,
        wealth_level: float = 1.0,
        security_level: float = 0.9,
        prestige: float = 0.8,
    ) -> "NobleDistrict":
        """Factory method to create a noble district."""
        if not name or not name.strip():
            raise ValueError("Noble district name is required")
        if population < 0:
            raise ValueError("Population cannot be negative")
        if not (0 <= wealth_level <= 1) or not (0 <= security_level <= 1) or not (0 <= prestige <= 1):
            raise ValueError("Levels must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            district_id=district_id,
            population=population,
            wealth_level=wealth_level,
            security_level=security_level,
            prestige=prestige,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate noble district data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.population, int) and self.population >= 0
            and 0 <= self.wealth_level <= 1
            and 0 <= self.security_level <= 1
            and 0 <= self.prestige <= 1
        )

    def __repr__(self) -> str:
        return f"<NobleDistrict {self.name}: {self.population} pop, wealth {self.wealth_level}>"
