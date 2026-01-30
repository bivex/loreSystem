"""Defense entity for military protection."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Defense:
    """Represents a defense system or structure."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        defense_type: str,
        location_id: UUID,
        protection_level: float,
        capacity: int,
        coverage_radius: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.defense_type = defense_type
        self.location_id = location_id
        self.protection_level = protection_level
        self.capacity = capacity
        self.coverage_radius = coverage_radius
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        defense_type: str,
        location_id: UUID,
        protection_level: float = 100.0,
        capacity: int = 1000,
        coverage_radius: float = 10.0,
    ) -> "Defense":
        """Factory method to create a new defense system."""
        if not name or not name.strip():
            raise ValueError("Defense name is required")
        if protection_level < 0:
            raise ValueError("Protection level cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            defense_type=defense_type,
            location_id=location_id,
            protection_level=protection_level,
            capacity=capacity,
            coverage_radius=coverage_radius,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate defense data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.protection_level, (int, float)) and self.protection_level >= 0
            and isinstance(self.capacity, int) and self.capacity > 0
        )

    def __repr__(self) -> str:
        return f"<Defense {self.name}: {self.defense_type}, level {self.protection_level}>"
