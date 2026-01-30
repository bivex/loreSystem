"""Trade entity for world economy systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Trade:
    """Represents a trade agreement or transaction in the world economy."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        seller_id: UUID,
        buyer_id: UUID,
        resource_id: str,
        quantity: int,
        price: float,
        currency: str,
        status: str = "pending",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.resource_id = resource_id
        self.quantity = quantity
        self.price = price
        self.currency = currency
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        seller_id: UUID,
        buyer_id: UUID,
        resource_id: str,
        quantity: int,
        price: float,
        currency: str = "gold",
    ) -> "Trade":
        """Factory method to create a new trade."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price < 0:
            raise ValueError("Price cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            seller_id=seller_id,
            buyer_id=buyer_id,
            resource_id=resource_id,
            quantity=quantity,
            price=price,
            currency=currency,
            status="pending",
        )

    def validate(self) -> bool:
        """Validate trade data."""
        return (
            isinstance(self.quantity, int) and self.quantity > 0
            and isinstance(self.price, (int, float)) and self.price >= 0
            and self.status in ["pending", "completed", "cancelled", "failed"]
        )

    def __repr__(self) -> str:
        return f"<Trade {self.id}: {self.quantity}x {self.resource_id} for {self.price} {self.currency}>"
