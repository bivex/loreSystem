"""SeasonalEvent entity for time-bound recurring events."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class SeasonalEvent:
    """Represents a seasonal or recurring event tied to game calendar."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        season: str,
        year_number: int,
        description: str,
        rewards: list[UUID],
        start_date: datetime,
        end_date: datetime,
        is_recurring: bool = True,
        recurrence_period_days: Optional[int] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.season = season
        self.year_number = year_number
        self.description = description
        self.rewards = rewards
        self.start_date = start_date
        self.end_date = end_date
        self.is_recurring = is_recurring
        self.recurrence_period_days = recurrence_period_days
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        season: str,
        year_number: int,
        description: str,
        duration_days: int = 30,
        is_recurring: bool = True,
        recurrence_period_days: Optional[int] = 365,
    ) -> "SeasonalEvent":
        """Factory method to create a new seasonal event."""
        if not name or not name.strip():
            raise ValueError("Event name is required")
        if season not in ["spring", "summer", "autumn", "winter", "none"]:
            raise ValueError("Season must be one of: spring, summer, autumn, winter, none")
        if year_number < 0:
            raise ValueError("Year number cannot be negative")
        if duration_days <= 0:
            raise ValueError("Duration must be positive")
        if is_recurring and recurrence_period_days and recurrence_period_days <= 0:
            raise ValueError("Recurrence period must be positive")

        start = datetime.utcnow()
        from datetime import timedelta
        end = start + timedelta(days=duration_days)

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            season=season,
            year_number=year_number,
            description=description.strip(),
            rewards=[],
            start_date=start,
            end_date=end,
            is_recurring=is_recurring,
            recurrence_period_days=recurrence_period_days,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate seasonal event data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.season in ["spring", "summer", "autumn", "winter", "none"]
            and isinstance(self.year_number, int) and self.year_number >= 0
            and isinstance(self.start_date, datetime)
            and isinstance(self.end_date, datetime)
            and self.end_date > self.start_date
            and (not self.is_recurring or self.recurrence_period_days is None or self.recurrence_period_days > 0)
        )

    def add_reward(self, reward_id: UUID) -> None:
        """Add a reward to the seasonal event."""
        if reward_id not in self.rewards:
            self.rewards.append(reward_id)
            self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<SeasonalEvent {self.name}: {self.season} Y{self.year_number}>"
