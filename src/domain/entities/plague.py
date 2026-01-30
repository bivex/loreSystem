"""Plague entity for disease outbreaks and epidemics."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Plague:
    """Represents a plague or disease outbreak affecting populations."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        disease_type: str,
        origin_location_id: UUID,
        virulence: float,
        mortality_rate: float,
        transmission_rate: float,
        infected_count: int,
        death_count: int,
        start_date: datetime,
        end_date: Optional[datetime],
        is_active: bool = True,
        is_contagious: bool = True,
        cure_discovered: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.disease_type = disease_type
        self.origin_location_id = origin_location_id
        self.virulence = virulence
        self.mortality_rate = mortality_rate
        self.transmission_rate = transmission_rate
        self.infected_count = infected_count
        self.death_count = death_count
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
        self.is_contagious = is_contagious
        self.cure_discovered = cure_discovered
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        disease_type: str,
        origin_location_id: UUID,
        virulence: float = 0.5,
        mortality_rate: float = 0.2,
        transmission_rate: float = 0.3,
    ) -> "Plague":
        """Factory method to create a new plague."""
        if not name or not name.strip():
            raise ValueError("Plague name is required")
        if not 0.0 <= virulence <= 1.0:
            raise ValueError("Virulence must be between 0.0 and 1.0")
        if not 0.0 <= mortality_rate <= 1.0:
            raise ValueError("Mortality rate must be between 0.0 and 1.0")
        if not 0.0 <= transmission_rate <= 1.0:
            raise ValueError("Transmission rate must be between 0.0 and 1.0")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            disease_type=disease_type.strip(),
            origin_location_id=origin_location_id,
            virulence=virulence,
            mortality_rate=mortality_rate,
            transmission_rate=transmission_rate,
            infected_count=1,
            death_count=0,
            start_date=datetime.utcnow(),
            end_date=None,
            is_active=True,
            is_contagious=True,
            cure_discovered=False,
        )

    def validate(self) -> bool:
        """Validate plague data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.disease_type, str) and len(self.disease_type) > 0
            and 0.0 <= self.virulence <= 1.0
            and 0.0 <= self.mortality_rate <= 1.0
            and 0.0 <= self.transmission_rate <= 1.0
            and isinstance(self.infected_count, int) and self.infected_count >= 0
            and isinstance(self.death_count, int) and self.death_count >= 0
        )

    def spread(self, new_infections: int) -> None:
        """Record new infections."""
        self.infected_count += max(0, new_infections)
        self.updated_at = datetime.utcnow()

    def add_deaths(self, count: int) -> None:
        """Add death toll."""
        self.death_count += max(0, count)
        self.updated_at = datetime.utcnow()

    def discover_cure(self) -> None:
        """Mark cure as discovered."""
        self.cure_discovered = True
        self.transmission_rate = 0.0
        self.updated_at = datetime.utcnow()

    def end_plague(self) -> None:
        """End the plague outbreak."""
        self.is_active = False
        self.is_contagious = False
        self.end_date = self.end_date or datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Plague {self.name}: {self.infected_count} infected, {self.death_count} deaths>"
