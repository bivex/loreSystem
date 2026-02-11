"""Reproduction entity for biological systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Reproduction:
    """Represents reproduction mechanics for species."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        species_id: str,
        reproduction_type: str,
        gestation_period: int,
        offspring_count: int,
        maturity_age: int,
        survival_rate: float,
        breeding_season: Optional[list],
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.species_id = species_id
        self.reproduction_type = reproduction_type
        self.gestation_period = gestation_period
        self.offspring_count = offspring_count
        self.maturity_age = maturity_age
        self.survival_rate = survival_rate
        self.breeding_season = breeding_season
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        species_id: str,
        reproduction_type: str,
        gestation_period: int = 30,
        offspring_count: int = 1,
        maturity_age: int = 365,
        survival_rate: float = 0.7,
        breeding_season: Optional[list] = None,
    ) -> "Reproduction":
        """Factory method to create reproduction mechanics."""
        if not species_id or not species_id.strip():
            raise ValueError("Species ID is required")
        if gestation_period <= 0 or offspring_count < 0 or maturity_age <= 0:
            raise ValueError("Periods and counts must be positive")
        if not (0 <= survival_rate <= 1):
            raise ValueError("Survival rate must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            species_id=species_id.strip(),
            reproduction_type=reproduction_type,
            gestation_period=gestation_period,
            offspring_count=offspring_count,
            maturity_age=maturity_age,
            survival_rate=survival_rate,
            breeding_season=breeding_season,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate reproduction data."""
        return (
            isinstance(self.species_id, str) and len(self.species_id) > 0
            and self.gestation_period > 0
            and self.offspring_count >= 0
            and self.maturity_age > 0
            and 0 <= self.survival_rate <= 1
        )

    def __repr__(self) -> str:
        return f"<Reproduction {self.species_id}: {self.offspring_count} offspring, {self.survival_rate * 100}% survival>"
