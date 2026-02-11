"""Festival entity for cultural celebrations."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Festival:
    """Represents a festival or cultural celebration."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        festival_type: str,
        location_id: UUID,
        start_date: datetime,
        end_date: datetime,
        organizer_id: UUID,
        participants: list[UUID],
        rewards: dict,
        traditions: list[str],
        is_annual: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.festival_type = festival_type
        self.location_id = location_id
        self.start_date = start_date
        self.end_date = end_date
        self.organizer_id = organizer_id
        self.participants = participants
        self.rewards = rewards
        self.traditions = traditions
        self.is_annual = is_annual
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        festival_type: str,
        location_id: UUID,
        start_date: datetime,
        end_date: datetime,
        organizer_id: UUID,
        is_annual: bool = False,
    ) -> "Festival":
        """Factory method to create a new festival."""
        if not name or not name.strip():
            raise ValueError("Festival name is required")
        if end_date < start_date:
            raise ValueError("End date must be after start date")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            festival_type=festival_type,
            location_id=location_id,
            start_date=start_date,
            end_date=end_date,
            organizer_id=organizer_id,
            participants=[],
            rewards={},
            traditions=[],
            is_annual=is_annual,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate festival data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.start_date <= self.end_date
            and isinstance(self.participants, list)
        )

    def __repr__(self) -> str:
        return f"<Festival {self.name}: {self.festival_type}, {self.start_date.date()}>"
