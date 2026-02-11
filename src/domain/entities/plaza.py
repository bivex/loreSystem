"""Plaza entity for public gathering spaces."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Plaza:
    """Represents a public plaza."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        area: float,
        capacity: int,
        features: list,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.district_id = district_id
        self.area = area
        self.capacity = capacity
        self.features = features
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        area: float = 1000.0,
        capacity: int = 500,
        features: Optional[list] = None,
    ) -> "Plaza":
        """Factory method to create a new plaza."""
        if not name or not name.strip():
            raise ValueError("Plaza name is required")
        if area <= 0 or capacity <= 0:
            raise ValueError("Area and capacity must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            district_id=district_id,
            area=area,
            capacity=capacity,
            features=features or [],
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate plaza data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.area, (int, float)) and self.area > 0
            and isinstance(self.capacity, int) and self.capacity > 0
        )

    def __repr__(self) -> str:
        return f"<Plaza {self.name}: {self.area}m², capacity {self.capacity}>"
