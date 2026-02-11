"""Tax entity for world economy."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Tax:
    """Represents a tax imposed by governments or factions."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        rate: float,
        tax_type: str,
        region_id: Optional[UUID],
        payer_type: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.rate = rate
        self.tax_type = tax_type
        self.region_id = region_id
        self.payer_type = payer_type
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        rate: float,
        tax_type: str,
        payer_type: str = "all",
        region_id: Optional[UUID] = None,
    ) -> "Tax":
        """Factory method to create a new tax."""
        if not name or not name.strip():
            raise ValueError("Tax name is required")
        if rate < 0 or rate > 1:
            raise ValueError("Tax rate must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            rate=rate,
            tax_type=tax_type,
            payer_type=payer_type,
            region_id=region_id,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate tax data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.rate, (int, float)) and 0 <= self.rate <= 1
            and isinstance(self.is_active, bool)
        )

    def __repr__(self) -> str:
        return f"<Tax {self.name}: {self.rate * 100}% ({self.tax_type})>"
