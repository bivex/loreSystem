"""Celebration entity for joyous occasions."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Celebration:
    """Represents a celebration event."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        celebration_type: str,
        location_id: UUID,
        trigger_id: UUID,
        participants: list[UUID],
        activities: list[dict],
        mood_modifier: float,
        duration_minutes: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.celebration_type = celebration_type
        self.location_id = location_id
        self.trigger_id = trigger_id
        self.participants = participants
        self.activities = activities
        self.mood_modifier = mood_modifier
        self.duration_minutes = duration_minutes
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        celebration_type: str,
        location_id: UUID,
        trigger_id: UUID,
        mood_modifier: float = 0.2,
        duration_minutes: int = 120,
    ) -> "Celebration":
        """Factory method to create a new celebration."""
        if not name or not name.strip():
            raise ValueError("Celebration name is required")
        if not -1.0 <= mood_modifier <= 1.0:
            raise ValueError("Mood modifier must be between -1.0 and 1.0")
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            celebration_type=celebration_type,
            location_id=location_id,
            trigger_id=trigger_id,
            participants=[],
            activities=[],
            mood_modifier=mood_modifier,
            duration_minutes=duration_minutes,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate celebration data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.mood_modifier, (int, float)) and -1.0 <= self.mood_modifier <= 1.0
            and isinstance(self.duration_minutes, int) and self.duration_minutes > 0
        )

    def __repr__(self) -> str:
        return f"<Celebration {self.name}: {self.celebration_type}, mood+{self.mood_modifier}>"
