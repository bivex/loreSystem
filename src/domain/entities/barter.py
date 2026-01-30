"""Barter entity for direct item exchange without currency."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Barter:
    """Represents a direct exchange of goods or services."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        party_a_id: UUID,
        party_b_id: UUID,
        offered_items: list,
        requested_items: list,
        status: str = "proposed",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.party_a_id = party_a_id
        self.party_b_id = party_b_id
        self.offered_items = offered_items
        self.requested_items = requested_items
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        party_a_id: UUID,
        party_b_id: UUID,
        offered_items: list,
        requested_items: list,
    ) -> "Barter":
        """Factory method to create a new barter proposal."""
        if not offered_items or not requested_items:
            raise ValueError("Both offered and requested items are required")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            party_a_id=party_a_id,
            party_b_id=party_b_id,
            offered_items=offered_items,
            requested_items=requested_items,
            status="proposed",
        )

    def validate(self) -> bool:
        """Validate barter data."""
        return (
            isinstance(self.offered_items, list) and len(self.offered_items) > 0
            and isinstance(self.requested_items, list) and len(self.requested_items) > 0
            and self.status in ["proposed", "accepted", "rejected", "completed"]
        )

    def __repr__(self) -> str:
        return f"<Barter {self.id}: {len(self.offered_items)} items <-> {len(self.requested_items)} items>"
