"""Nebula entity for astronomical systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Nebula:
    """Represents a nebula."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        nebula_type: str,
        region_id: UUID,
        diameter_light_years: float,
        composition: list,
        star_formation_rate: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.nebula_type = nebula_type
        self.region_id = region_id
        self.diameter_light_years = diameter_light_years
        self.composition = composition
        self.star_formation_rate = star_formation_rate
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        nebula_type: str,
        region_id: UUID,
        diameter_light_years: float = 10.0,
        star_formation_rate: float = 0.1,
        composition: Optional[list] = None,
    ) -> "Nebula":
        """Factory method to create a new nebula."""
        if not name or not name.strip():
            raise ValueError("Nebula name is required")
        if diameter_light_years <= 0:
            raise ValueError("Diameter must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            nebula_type=nebula_type,
            region_id=region_id,
            diameter_light_years=diameter_light_years,
            composition=composition or [],
            star_formation_rate=star_formation_rate,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate nebula data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.diameter_light_years, (int, float)) and self.diameter_light_years > 0
            and isinstance(self.composition, list)
        )

    def __repr__(self) -> str:
        return f"<Nebula {self.name}: {self.nebula_type}, {self.diameter_light_years} ly>"
