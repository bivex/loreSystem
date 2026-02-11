"""FactionResource entity - Faction resources management."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class FactionResource:
    """Represents resources owned/managed by a faction."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    faction_id: str = ""
    resource_type: str = ""  # gold, food, military, magic, influence, materials
    amount: float = 0.0
    capacity: float = 0.0
    production_rate: float = 0.0  # Per day/week
    consumption_rate: float = 0.0
    trade_allowed: bool = True

    @classmethod
    def create(
        cls,
        tenant_id: str,
        faction_id: str,
        resource_type: str,
        capacity: float = 1000.0,
    ) -> Self:
        """Factory method to create a new FactionResource."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not faction_id:
            raise ValueError("faction_id is required")
        if not resource_type:
            raise ValueError("resource_type is required")

        valid_types = ["gold", "food", "military", "magic", "influence", "materials"]
        if resource_type not in valid_types:
            raise ValueError(f"resource_type must be one of {valid_types}")

        if capacity < 0:
            raise ValueError("capacity cannot be negative")

        return cls(
            tenant_id=tenant_id,
            faction_id=faction_id,
            resource_type=resource_type,
            capacity=capacity,
        )

    def add(self, amount: float) -> None:
        """Add resources."""
        if amount < 0:
            raise ValueError("amount to add cannot be negative")
        self.amount = max(0, min(self.capacity, self.amount + amount))
        self.updated_at = datetime.utcnow()

    def subtract(self, amount: float) -> None:
        """Subtract resources."""
        if amount < 0:
            raise ValueError("amount to subtract cannot be negative")
        self.amount = max(0, self.amount - amount)
        self.updated_at = datetime.utcnow()

    def set_capacity(self, capacity: float) -> None:
        """Set storage capacity."""
        if capacity < 0:
            raise ValueError("capacity cannot be negative")
        self.capacity = capacity
        self.amount = min(self.amount, self.capacity)
        self.updated_at = datetime.utcnow()

    def set_rates(self, production: float, consumption: float) -> None:
        """Set production and consumption rates."""
        self.production_rate = production
        self.consumption_rate = consumption
        self.updated_at = datetime.utcnow()

    def enable_trade(self) -> None:
        """Enable resource trading."""
        self.trade_allowed = True
        self.updated_at = datetime.utcnow()

    def disable_trade(self) -> None:
        """Disable resource trading."""
        self.trade_allowed = False
        self.updated_at = datetime.utcnow()

    def is_full(self) -> bool:
        """Check if resource storage is full."""
        return self.amount >= self.capacity

    def is_empty(self) -> bool:
        """Check if resource storage is empty."""
        return self.amount <= 0

    def net_rate(self) -> float:
        """Calculate net rate (production - consumption)."""
        return self.production_rate - self.consumption_rate

    def fill_percentage(self) -> float:
        """Calculate fill percentage."""
        if self.capacity == 0:
            return 0.0
        return (self.amount / self.capacity) * 100
