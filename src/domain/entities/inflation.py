"""Inflation entity for economic systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Inflation:
    """Represents inflation rate for a region or currency."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        region_id: Optional[UUID],
        currency: str,
        rate: float,
        period: str,
        base_year: int,
        current_year: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.region_id = region_id
        self.currency = currency
        self.rate = rate
        self.period = period
        self.base_year = base_year
        self.current_year = current_year
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        currency: str,
        rate: float,
        base_year: int,
        current_year: int,
        period: str = "yearly",
        region_id: Optional[UUID] = None,
    ) -> "Inflation":
        """Factory method to create a new inflation entry."""
        if not currency or not currency.strip():
            raise ValueError("Currency is required")
        if base_year > current_year:
            raise ValueError("Base year must be before or equal to current year")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            region_id=region_id,
            currency=currency.strip(),
            rate=rate,
            period=period,
            base_year=base_year,
            current_year=current_year,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate inflation data."""
        return (
            isinstance(self.currency, str) and len(self.currency) > 0
            and isinstance(self.rate, (int, float))
            and isinstance(self.base_year, int) and self.base_year > 0
            and isinstance(self.current_year, int) and self.current_year >= self.base_year
        )

    def __repr__(self) -> str:
        return f"<Inflation {self.currency}: {self.rate * 100}% ({self.period})>"
