"""Tariff entity for cross-region trade."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Tariff:
    """Represents a tariff on imports/exports between regions."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        from_region_id: UUID,
        to_region_id: UUID,
        resource_type: str,
        rate: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.from_region_id = from_region_id
        self.to_region_id = to_region_id
        self.resource_type = resource_type
        self.rate = rate
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        from_region_id: UUID,
        to_region_id: UUID,
        resource_type: str,
        rate: float,
    ) -> "Tariff":
        """Factory method to create a new tariff."""
        if not resource_type or not resource_type.strip():
            raise ValueError("Resource type is required")
        if rate < 0 or rate > 1:
            raise ValueError("Tariff rate must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            from_region_id=from_region_id,
            to_region_id=to_region_id,
            resource_type=resource_type.strip(),
            rate=rate,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate tariff data."""
        return (
            isinstance(self.resource_type, str) and len(self.resource_type) > 0
            and isinstance(self.rate, (int, float)) and 0 <= self.rate <= 1
            and isinstance(self.is_active, bool)
        )

    def __repr__(self) -> str:
        return f"<Tariff {self.from_region_id} -> {self.to_region_id}: {self.rate * 100}% on {self.resource_type}>"
