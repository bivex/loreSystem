"""Demand entity for economic systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Demand:
    """Represents the demand for a resource in the market."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        resource_id: str,
        region_id: UUID,
        quantity: float,
        urgency: str,
        demand_type: str,
        max_price: Optional[float] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.resource_id = resource_id
        self.region_id = region_id
        self.quantity = quantity
        self.urgency = urgency
        self.demand_type = demand_type
        self.max_price = max_price
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        resource_id: str,
        region_id: UUID,
        quantity: float,
        urgency: str = "normal",
        demand_type: str = "consumption",
        max_price: Optional[float] = None,
    ) -> "Demand":
        """Factory method to create a new demand entry."""
        if not resource_id or not resource_id.strip():
            raise ValueError("Resource ID is required")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            resource_id=resource_id.strip(),
            region_id=region_id,
            quantity=quantity,
            urgency=urgency,
            demand_type=demand_type,
            max_price=max_price,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate demand data."""
        return (
            isinstance(self.resource_id, str) and len(self.resource_id) > 0
            and isinstance(self.quantity, (int, float)) and self.quantity > 0
            and self.urgency in ["low", "normal", "high", "critical"]
            and (self.max_price is None or self.max_price >= 0)
        )

    def __repr__(self) -> str:
        return f"<Demand {self.resource_id}: {self.quantity} ({self.urgency})>"
