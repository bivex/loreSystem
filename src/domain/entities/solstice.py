"""Solstice entity for astronomical events."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Solstice:
    """Represents a solstice event."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        solstice_type: str,
        date: datetime,
        hemisphere: str,
        daylight_hours: float,
        solar_declination: float,
        cultural_significance: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.solstice_type = solstice_type
        self.date = date
        self.hemisphere = hemisphere
        self.daylight_hours = daylight_hours
        self.solar_declination = solar_declination
        self.cultural_significance = cultural_significance
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        solstice_type: str,
        date: datetime,
        hemisphere: str = "north",
        daylight_hours: float = 24.0,
        solar_declination: float = 23.5,
        cultural_significance: str = "",
    ) -> "Solstice":
        """Factory method to create a solstice event."""
        if not name or not name.strip():
            raise ValueError("Solstice name is required")
        if solstice_type not in ["summer", "winter"]:
            raise ValueError("Solstice type must be 'summer' or 'winter'")
        if hemisphere not in ["north", "south"]:
            raise ValueError("Hemisphere must be 'north' or 'south'")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            solstice_type=solstice_type,
            date=date,
            hemisphere=hemisphere,
            daylight_hours=daylight_hours,
            solar_declination=solar_declination,
            cultural_significance=cultural_significance,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate solstice data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.solstice_type in ["summer", "winter"]
            and self.hemisphere in ["north", "south"]
        )

    def __repr__(self) -> str:
        return f"<Solstice {self.name}: {self.solstice_type}, {self.daylight_hours}h daylight>"
