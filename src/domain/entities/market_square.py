"""MarketSquare entity for commercial areas."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class MarketSquare:
    """Represents a market square."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        stall_count: int,
        market_type: str,
        operating_hours: dict,
        trade_goods: list,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.district_id = district_id
        self.stall_count = stall_count
        self.market_type = market_type
        self.operating_hours = operating_hours
        self.trade_goods = trade_goods
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        district_id: UUID,
        stall_count: int = 20,
        market_type: str = "general",
        operating_hours: Optional[dict] = None,
        trade_goods: Optional[list] = None,
    ) -> "MarketSquare":
        """Factory method to create a new market square."""
        if not name or not name.strip():
            raise ValueError("Market square name is required")
        if stall_count < 0:
            raise ValueError("Stall count cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            district_id=district_id,
            stall_count=stall_count,
            market_type=market_type,
            operating_hours=operating_hours or {"open": 6, "close": 20},
            trade_goods=trade_goods or [],
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate market square data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.stall_count, int) and self.stall_count >= 0
        )

    def __repr__(self) -> str:
        return f"<MarketSquare {self.name}: {self.stall_count} stalls, {self.market_type}>"
