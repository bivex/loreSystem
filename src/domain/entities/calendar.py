"""
Calendar Entity - Time measurement system
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class CalendarType(str, Enum):
    """Types of calendar systems."""
    LUNAR = "lunar"
    SOLAR = "solar"
    LUNISOLAR = "lunisolar"
    MAGICAL = "magical"
    CELESTIAL = "celestial"
    CUSTOM = "custom"


@dataclass
class Calendar:
    """
    Calendar defines how time is measured in the world.

    Invariants:
    - Name cannot be empty
    - At least one time unit must be defined
    - Months per year must be positive
    """

    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId

    name: str
    description: Description
    calendar_type: CalendarType

    # Names (required)
    day_names: List[str]
    month_names: List[str]
    season_names: List[str]

    # Special dates (required)
    holiday_ids: List[EntityId]

    # Settings (required)
    is_primary_calendar: bool
    is_used_by: List[EntityId]

    # Meta (required)
    created_at: Timestamp
    updated_at: Timestamp
    version: Version

    # Time units (with defaults)
    seconds_per_minute: int = 60
    minutes_per_hour: int = 60
    hours_per_day: int = 24
    days_per_week: int = 7
    weeks_per_month: int = 4
    months_per_year: int = 12

    # Optional fields
    epoch_start: Optional[int] = None
    epoch_name: Optional[str] = None
    moon_phase_names: Optional[List[str]] = None
    days_per_lunar_cycle: Optional[int] = None
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Calendar name cannot be empty")
        
        if self.days_per_week < 1:
            raise InvariantViolation("Days per week must be >= 1")
        
        if self.months_per_year < 1:
            raise InvariantViolation("Months per year must be >= 1")
        
        if self.hours_per_day < 1:
            raise InvariantViolation("Hours per day must be >= 1")
        
        # Validate day names count matches days_per_week
        if self.day_names and len(self.day_names) != self.days_per_week:
            raise InvariantViolation(
                f"Number of day names ({len(self.day_names)}) "
                f"must match days_per_week ({self.days_per_week})"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        calendar_type: CalendarType = CalendarType.SOLAR,
        months_per_year: int = 12,
        days_per_week: int = 7,
        hours_per_day: int = 24,
        is_primary_calendar: bool = False,
    ) -> 'Calendar':
        """
        Factory method for creating a new Calendar.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            calendar_type=calendar_type,
            seconds_per_minute=60,
            minutes_per_hour=60,
            hours_per_day=hours_per_day,
            days_per_week=days_per_week,
            weeks_per_month=4,
            months_per_year=months_per_year,
            day_names=[],
            month_names=[],
            season_names=[],
            holiday_ids=[],
            epoch_start=1,
            epoch_name=None,
            moon_phase_names=None,
            days_per_lunar_cycle=None,
            is_primary_calendar=is_primary_calendar,
            is_used_by=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def set_day_names(self, names: List[str]) -> None:
        """Set the names of days in the week."""
        if len(names) != self.days_per_week:
            raise InvariantViolation(
                f"Must provide exactly {self.days_per_week} day names"
            )
        
        object.__setattr__(self, 'day_names', names)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_month_names(self, names: List[str]) -> None:
        """Set the names of months in the year."""
        if len(names) != self.months_per_year:
            raise InvariantViolation(
                f"Must provide exactly {self.months_per_year} month names"
            )
        
        object.__setattr__(self, 'month_names', names)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
