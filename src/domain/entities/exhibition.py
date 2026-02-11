"""Exhibition entity for displays and showcases."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Exhibition:
    """Represents an exhibition or showcase."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        exhibition_type: str,
        venue_id: UUID,
        curator_id: Optional[UUID],
        exhibits: list[UUID],
        start_date: datetime,
        end_date: datetime,
        entry_fee: int,
        visitor_count: int,
        rating: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.exhibition_type = exhibition_type
        self.venue_id = venue_id
        self.curator_id = curator_id
        self.exhibits = exhibits
        self.start_date = start_date
        self.end_date = end_date
        self.entry_fee = entry_fee
        self.visitor_count = visitor_count
        self.rating = rating
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        exhibition_type: str,
        venue_id: UUID,
        start_date: datetime,
        end_date: datetime,
        curator_id: Optional[UUID] = None,
        entry_fee: int = 0,
    ) -> "Exhibition":
        """Factory method to create a new exhibition."""
        if not name or not name.strip():
            raise ValueError("Exhibition name is required")
        if end_date < start_date:
            raise ValueError("End date must be after start date")
        if entry_fee < 0:
            raise ValueError("Entry fee cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            exhibition_type=exhibition_type,
            venue_id=venue_id,
            curator_id=curator_id,
            exhibits=[],
            start_date=start_date,
            end_date=end_date,
            entry_fee=entry_fee,
            visitor_count=0,
            rating=0.0,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate exhibition data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.start_date <= self.end_date
            and isinstance(self.entry_fee, int) and self.entry_fee >= 0
        )

    def __repr__(self) -> str:
        return f"<Exhibition {self.name}: {self.exhibition_type}, rating={self.rating}>"
