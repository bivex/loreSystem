"""Army entity for military systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Army:
    """Represents a military army."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        faction_id: UUID,
        commander_id: UUID,
        size: int,
        power: float,
        formation: str,
        status: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.faction_id = faction_id
        self.commander_id = commander_id
        self.size = size
        self.power = power
        self.formation = formation
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        faction_id: UUID,
        commander_id: UUID,
        size: int = 1000,
        formation: str = "standard",
        status: str = "ready",
    ) -> "Army":
        """Factory method to create a new army."""
        if not name or not name.strip():
            raise ValueError("Army name is required")
        if size <= 0:
            raise ValueError("Army size must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            faction_id=faction_id,
            commander_id=commander_id,
            size=size,
            power=float(size),
            formation=formation,
            status=status,
        )

    def validate(self) -> bool:
        """Validate army data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.size, int) and self.size > 0
            and self.status in ["ready", "marching", "fighting", "resting", "retreating"]
        )

    def __repr__(self) -> str:
        return f"<Army {self.name}: {self.size} troops, power {self.power}>"
