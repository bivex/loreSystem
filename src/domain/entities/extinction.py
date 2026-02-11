"""Extinction entity for species loss."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Extinction:
    """Represents extinction events."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        species_id: str,
        extinction_type: str,
        cause: str,
        extinction_year: int,
        population_at_time: int,
        affected_regions: list,
        is_active: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.species_id = species_id
        self.extinction_type = extinction_type
        self.cause = cause
        self.extinction_year = extinction_year
        self.population_at_time = population_at_time
        self.affected_regions = affected_regions
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        species_id: str,
        extinction_type: str,
        cause: str,
        extinction_year: int,
        population_at_time: int = 0,
        affected_regions: Optional[list] = None,
    ) -> "Extinction":
        """Factory method to create an extinction event."""
        if not species_id or not species_id.strip():
            raise ValueError("Species ID is required")
        if not cause or not cause.strip():
            raise ValueError("Cause is required")
        if extinction_year <= 0:
            raise ValueError("Extinction year must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            species_id=species_id.strip(),
            extinction_type=extinction_type,
            cause=cause.strip(),
            extinction_year=extinction_year,
            population_at_time=population_at_time,
            affected_regions=affected_regions or [],
            is_active=False,
        )

    def validate(self) -> bool:
        """Validate extinction data."""
        return (
            isinstance(self.species_id, str) and len(self.species_id) > 0
            and isinstance(self.cause, str) and len(self.cause) > 0
            and isinstance(self.extinction_year, int) and self.extinction_year > 0
        )

    def __repr__(self) -> str:
        return f"<Extinction {self.species_id}: year {self.extinction_year}, {self.cause}>"
