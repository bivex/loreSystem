"""Concert entity for musical performances."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Concert:
    """Represents a concert or musical performance."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        venue_id: UUID,
        performers: list[UUID],
        start_time: datetime,
        duration_minutes: int,
        genre: str,
        audience_capacity: int,
        ticket_prices: dict,
        setlist: list[str],
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.venue_id = venue_id
        self.performers = performers
        self.start_time = start_time
        self.duration_minutes = duration_minutes
        self.genre = genre
        self.audience_capacity = audience_capacity
        self.ticket_prices = ticket_prices
        self.setlist = setlist
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        venue_id: UUID,
        performers: list[UUID],
        start_time: datetime,
        duration_minutes: int = 120,
        genre: str = "classical",
        audience_capacity: int = 1000,
    ) -> "Concert":
        """Factory method to create a new concert."""
        if not name or not name.strip():
            raise ValueError("Concert name is required")
        if not performers:
            raise ValueError("At least one performer is required")
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        if audience_capacity <= 0:
            raise ValueError("Capacity must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            venue_id=venue_id,
            performers=performers,
            start_time=start_time,
            duration_minutes=duration_minutes,
            genre=genre,
            audience_capacity=audience_capacity,
            ticket_prices={},
            setlist=[],
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate concert data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.duration_minutes, int) and self.duration_minutes > 0
            and isinstance(self.audience_capacity, int) and self.audience_capacity > 0
        )

    def __repr__(self) -> str:
        return f"<Concert {self.name}: {self.genre}, {self.duration_minutes}min>"
