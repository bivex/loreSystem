"""Price entity for economic systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Price:
    """Represents the current market price of a resource."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        resource_id: str,
        region_id: UUID,
        amount: float,
        currency: str,
        price_type: str = "market",
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.resource_id = resource_id
        self.region_id = region_id
        self.amount = amount
        self.currency = currency
        self.price_type = price_type
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        resource_id: str,
        region_id: UUID,
        amount: float,
        currency: str = "gold",
        price_type: str = "market",
    ) -> "Price":
        """Factory method to create a new price entry."""
        if not resource_id or not resource_id.strip():
            raise ValueError("Resource ID is required")
        if amount < 0:
            raise ValueError("Price amount cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            resource_id=resource_id.strip(),
            region_id=region_id,
            amount=amount,
            currency=currency,
            price_type=price_type,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate price data."""
        return (
            isinstance(self.resource_id, str) and len(self.resource_id) > 0
            and isinstance(self.amount, (int, float)) and self.amount >= 0
            and isinstance(self.currency, str) and len(self.currency) > 0
        )

    def __repr__(self) -> str:
        return f"<Price {self.resource_id}: {self.amount} {self.currency}>"
