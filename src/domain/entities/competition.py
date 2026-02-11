"""Competition entity for contests and challenges."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Competition:
    """Represents a competition or contest."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        competition_type: str,
        organizer_id: UUID,
        location_id: UUID,
        participants: list[UUID],
        rules: dict,
        rewards: dict,
        start_date: datetime,
        end_date: datetime,
        max_participants: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.competition_type = competition_type
        self.organizer_id = organizer_id
        self.location_id = location_id
        self.participants = participants
        self.rules = rules
        self.rewards = rewards
        self.start_date = start_date
        self.end_date = end_date
        self.max_participants = max_participants
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        competition_type: str,
        organizer_id: UUID,
        location_id: UUID,
        start_date: datetime,
        end_date: datetime,
        max_participants: int = 100,
    ) -> "Competition":
        """Factory method to create a new competition."""
        if not name or not name.strip():
            raise ValueError("Competition name is required")
        if end_date < start_date:
            raise ValueError("End date must be after start date")
        if max_participants <= 0:
            raise ValueError("Max participants must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            competition_type=competition_type,
            organizer_id=organizer_id,
            location_id=location_id,
            participants=[],
            rules={},
            rewards={},
            start_date=start_date,
            end_date=end_date,
            max_participants=max_participants,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate competition data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.start_date <= self.end_date
            and isinstance(self.max_participants, int) and self.max_participants > 0
        )

    def __repr__(self) -> str:
        return f"<Competition {self.name}: {self.competition_type}, {len(self.participants)}/{self.max_participants}>"
