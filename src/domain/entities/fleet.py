"""Fleet entity for naval systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Fleet:
    """Represents a naval fleet."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        faction_id: UUID,
        admiral_id: UUID,
        ship_count: int,
        tonnage: float,
        region_id: Optional[UUID],
        status: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.faction_id = faction_id
        self.admiral_id = admiral_id
        self.ship_count = ship_count
        self.tonnage = tonnage
        self.region_id = region_id
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        faction_id: UUID,
        admiral_id: UUID,
        ship_count: int = 10,
        region_id: Optional[UUID] = None,
        status: str = "ready",
    ) -> "Fleet":
        """Factory method to create a new fleet."""
        if not name or not name.strip():
            raise ValueError("Fleet name is required")
        if ship_count <= 0:
            raise ValueError("Ship count must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            faction_id=faction_id,
            admiral_id=admiral_id,
            ship_count=ship_count,
            tonnage=float(ship_count) * 1000.0,
            region_id=region_id,
            status=status,
        )

    def validate(self) -> bool:
        """Validate fleet data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.ship_count, int) and self.ship_count > 0
            and self.status in ["ready", "sailing", "battle", "docked", "repair"]
        )

    def __repr__(self) -> str:
        return f"<Fleet {self.name}: {self.ship_count} ships, {self.tonnage} tons>"
