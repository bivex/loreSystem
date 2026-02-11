"""Ward entity for urban subdivision."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Ward:
    """Represents a ward within a district."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        ward_type: str,
        population: int,
        building_count: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.district_id = district_id
        self.ward_type = ward_type
        self.population = population
        self.building_count = building_count
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        ward_type: str = "mixed",
        population: int = 200,
        building_count: int = 20,
    ) -> "Ward":
        """Factory method to create a new ward."""
        if not name or not name.strip():
            raise ValueError("Ward name is required")
        if population < 0 or building_count < 0:
            raise ValueError("Population and building count cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            district_id=district_id,
            ward_type=ward_type,
            population=population,
            building_count=building_count,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate ward data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.population, int) and self.population >= 0
            and isinstance(self.building_count, int) and self.building_count >= 0
        )

    def __repr__(self) -> str:
        return f"<Ward {self.name}: {self.population} pop, {self.building_count} buildings>"
