"""SeasonalEvent entity for time-bound recurring events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from ..exceptions import InvariantViolation
from ..value_objects.common import EntityId, TenantId, Timestamp, Version


VALID_SEASONS = {"spring", "summer", "autumn", "winter", "none"}


@dataclass
class SeasonalEvent:
    """Represents a seasonal or recurring event tied to a world calendar."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    season: str
    year_number: int
    description: str
    start_date: Timestamp
    end_date: Timestamp
    reward_ids: list[EntityId] = field(default_factory=list)
    is_recurring: bool = True
    recurrence_period_days: int | None = None
    is_active: bool = True
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("SeasonalEvent name cannot be empty")
        if self.season not in VALID_SEASONS:
            raise InvariantViolation(
                f"SeasonalEvent season must be one of {sorted(VALID_SEASONS)}"
            )
        if self.year_number < 0:
            raise InvariantViolation("SeasonalEvent year_number cannot be negative")
        if self.end_date.value < self.start_date.value:
            raise InvariantViolation("SeasonalEvent end_date cannot be before start_date")
        if self.is_recurring and self.recurrence_period_days is not None and self.recurrence_period_days <= 0:
            raise InvariantViolation("SeasonalEvent recurrence_period_days must be positive")
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("SeasonalEvent updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        season: str,
        year_number: int,
        description: str,
        duration_days: int = 30,
        reward_ids: list[EntityId] | None = None,
        start_date: Timestamp | None = None,
        is_recurring: bool = True,
        recurrence_period_days: int | None = 365,
        is_active: bool = True,
    ) -> "SeasonalEvent":
        now = Timestamp.now()
        start = start_date or now
        end = Timestamp(start.value + timedelta(days=max(1, duration_days)))
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            season=season,
            year_number=year_number,
            description=description.strip(),
            start_date=start,
            end_date=end,
            reward_ids=list(reward_ids or []),
            is_recurring=is_recurring,
            recurrence_period_days=recurrence_period_days if is_recurring else None,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def validate(self) -> bool:
        try:
            self.__post_init__()
        except InvariantViolation:
            return False
        return True

    def add_reward(self, reward_id: EntityId) -> None:
        if reward_id not in self.reward_ids:
            self.reward_ids.append(reward_id)
            self.updated_at = Timestamp.now()
            self.version = self.version.increment()

    def end_event(self) -> None:
        self.is_active = False
        self.end_date = self.end_date or Timestamp.now()
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def __repr__(self) -> str:
        return f"<SeasonalEvent {self.name}: {self.season} Y{self.year_number}>"
