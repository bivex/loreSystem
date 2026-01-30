"""PortDistrict entity for coastal trade areas."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class PortDistrict:
    """Represents a port district."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        dock_capacity: int,
        trade_volume: float,
        cargo_facilities: list,
        shipyard_level: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.district_id = district_id
        self.dock_capacity = dock_capacity
        self.trade_volume = trade_volume
        self.cargo_facilities = cargo_facilities
        self.shipyard_level = shipyard_level
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        dock_capacity: int = 50,
        trade_volume: float = 10000.0,
        shipyard_level: int = 1,
        cargo_facilities: Optional[list] = None,
    ) -> "PortDistrict":
        """Factory method to create a port district."""
        if not name or not name.strip():
            raise ValueError("Port district name is required")
        if dock_capacity <= 0 or trade_volume < 0:
            raise ValueError("Dock capacity must be positive and trade volume non-negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            district_id=district_id,
            dock_capacity=dock_capacity,
            trade_volume=trade_volume,
            cargo_facilities=cargo_facilities or [],
            shipyard_level=shipyard_level,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate port district data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.dock_capacity, int) and self.dock_capacity > 0
            and isinstance(self.trade_volume, (int, float)) and self.trade_volume >= 0
        )

    def __repr__(self) -> str:
        return f"<PortDistrict {self.name}: {self.dock_capacity} docks, {self.trade_volume} trade>"
