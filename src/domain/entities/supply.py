"""Supply entity for economic systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Supply:
    """Represents the supply of a resource in the market."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        resource_id: str,
        region_id: UUID,
        quantity: float,
        available_quantity: float,
        source_type: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.resource_id = resource_id
        self.region_id = region_id
        self.quantity = quantity
        self.available_quantity = available_quantity
        self.source_type = source_type
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
        source_type: str = "production",
    ) -> "Supply":
        """Factory method to create a new supply entry."""
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
            available_quantity=quantity,
            source_type=source_type,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate supply data."""
        return (
            isinstance(self.resource_id, str) and len(self.resource_id) > 0
            and isinstance(self.quantity, (int, float)) and self.quantity > 0
            and isinstance(self.available_quantity, (int, float)) and 0 <= self.available_quantity <= self.quantity
        )

    def __repr__(self) -> str:
        return f"<Supply {self.resource_id}: {self.available_quantity}/{self.quantity} available>"
