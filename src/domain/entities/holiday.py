"""
Holiday Entity - Special days in calendar
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


class HolidayType(str, Enum):
    """Types of holidays."""
    RELIGIOUS = "religious"
    CULTURAL = "cultural"
    NATIONAL = "national"
    SEASONAL = "seasonal"
    MAGICAL = "magical"
    HISTORICAL = "historical"
    AGRICULTURAL = "agricultural"


@dataclass
class Holiday:
    """
    Holiday represents a special day or period in the calendar.
    
    Invariants:
    - Name cannot be empty
    - Day must be valid (1-31)
    - Month must be valid (1-12 or based on calendar)
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    calendar_id: EntityId
    
    name: str
    description: Description
    
    # Holiday type
    holiday_type: HolidayType
    
    # Date
    month: int  # Month number (1-indexed)
    day: int  # Day of month
    
    # Duration (for multi-day holidays)
    duration_days: int = 1
    
    # Occurrence
    occurs_every_year: bool = True
    specific_years: Optional[List[int]]  # If not every year
    
    # Origins and meaning
    origin_story: Optional[str]
    associated_deity_ids: List[EntityId]
    associated_event_ids: List[EntityId]
    
    # Celebrations and traditions
    traditions: List[str]
    rituals: List[str]
    foods: List[str]
    activities: List[str]
    
    # Observance
    is_observed_nationwide: bool
    observed_by_ids: List[EntityId]  # Nations/factions that observe this holiday
    
    # Restrictions
    is_work_free: bool
    restrictions: List[str]  # e.g., "No magic use", "No meat consumption"
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
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
            raise InvariantViolation("Holiday name cannot be empty")
        
        if self.month < 1 or self.month > 12:
            raise InvariantViolation("Month must be between 1 and 12")
        
        if self.day < 1 or self.day > 31:
            raise InvariantViolation("Day must be between 1 and 31")
        
        if self.duration_days < 1:
            raise InvariantViolation("Duration must be at least 1 day")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        calendar_id: EntityId,
        name: str,
        description: Description,
        holiday_type: HolidayType,
        month: int,
        day: int,
        duration_days: int = 1,
        is_work_free: bool = False,
        is_observed_nationwide: bool = False,
    ) -> 'Holiday':
        """
        Factory method for creating a new Holiday.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            calendar_id=calendar_id,
            name=name,
            description=description,
            holiday_type=holiday_type,
            month=month,
            day=day,
            duration_days=duration_days,
            occurs_every_year=True,
            specific_years=None,
            origin_story=None,
            associated_deity_ids=[],
            associated_event_ids=[],
            traditions=[],
            rituals=[],
            foods=[],
            activities=[],
            is_observed_nationwide=is_observed_nationwide,
            observed_by_ids=[],
            is_work_free=is_work_free,
            restrictions=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_tradition(self, tradition: str) -> None:
        """Add a tradition to this holiday."""
        if tradition not in self.traditions:
            self.traditions.append(tradition)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_ritual(self, ritual: str) -> None:
        """Add a ritual to this holiday."""
        if ritual not in self.rituals:
            self.rituals.append(ritual)
            object.__setattr__(self, 'updated_at', Timestamp.now())
