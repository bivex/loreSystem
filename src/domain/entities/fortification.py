"""Fortification entity for military structures."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Fortification:
    """Represents a fortified structure."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        fort_type: str,
        location_id: UUID,
        health: float,
        max_health: float,
        defense_bonus: float,
        garrison_capacity: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.fort_type = fort_type
        self.location_id = location_id
        self.health = health
        self.max_health = max_health
        self.defense_bonus = defense_bonus
        self.garrison_capacity = garrison_capacity
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        fort_type: str,
        location_id: UUID,
        max_health: float = 1000.0,
        defense_bonus: float = 0.5,
        garrison_capacity: int = 500,
    ) -> "Fortification":
        """Factory method to create a new fortification."""
        if not name or not name.strip():
            raise ValueError("Fortification name is required")
        if max_health <= 0:
            raise ValueError("Max health must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            fort_type=fort_type,
            location_id=location_id,
            health=max_health,
            max_health=max_health,
            defense_bonus=defense_bonus,
            garrison_capacity=garrison_capacity,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate fortification data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.max_health, (int, float)) and self.max_health > 0
            and 0 <= self.health <= self.max_health
            and isinstance(self.garrison_capacity, int) and self.garrison_capacity >= 0
        )

    def __repr__(self) -> str:
        return f"<Fortification {self.name}: {self.health}/{self.max_health} HP, {self.garrison_capacity} garrison>"
