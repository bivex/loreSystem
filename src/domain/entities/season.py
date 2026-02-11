"""
Season Entity - Seasonal period in calendar
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Season:
    """
    Season represents a seasonal period in the calendar.
    
    Invariants:
    - Name cannot be empty
    - Months must be unique across seasons in same calendar
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    calendar_id: EntityId
    
    name: str
    description: Description
    
    # Months in this season
    months: List[int]  # Month numbers (1-indexed)
    
    # Climate characteristics
    typical_weather: Optional[str]
    average_temperature: Optional[str]  # e.g., "10-20°C", "Cold"
    precipitation: Optional[str]  # e.g., "Heavy rain", "Dry"
    
    # Cultural associations
    activities: List[str]
    festivals: List[EntityId]  # Holiday IDs
    
    # Agriculture and nature
    crops_planted: List[str]
    crops_harvested: List[str]
    animal_behaviors: Optional[str]  # e.g., "Migration", "Hibernation"
    
    # Magical aspects (if applicable)
    magical_phenomena: List[str]
    
    # Visual
    color_palette: Optional[str]  # Dominant colors
    icon_path: Optional[str]
    
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
            raise InvariantViolation("Season name cannot be empty")
        
        # Validate months
        if not self.months:
            raise InvariantViolation("Season must have at least one month")
        
        for month in self.months:
            if month < 1 or month > 12:
                raise InvariantViolation(
                    f"Month must be between 1 and 12, got {month}"
                )
        
        # Check for duplicate months
        if len(self.months) != len(set(self.months)):
            raise InvariantViolation("Season cannot have duplicate months")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        calendar_id: EntityId,
        name: str,
        description: Description,
        months: List[int],
    ) -> 'Season':
        """
        Factory method for creating a new Season.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            calendar_id=calendar_id,
            name=name,
            description=description,
            months=months,
            typical_weather=None,
            average_temperature=None,
            precipitation=None,
            activities=[],
            festivals=[],
            crops_planted=[],
            crops_harvested=[],
            animal_behaviors=None,
            magical_phenomena=[],
            color_palette=None,
            icon_path=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_activity(self, activity: str) -> None:
        """Add an activity to this season."""
        if activity not in self.activities:
            self.activities.append(activity)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_festival(self, holiday_id: EntityId) -> None:
        """Add a festival/holiday to this season."""
        if holiday_id not in self.festivals:
            self.festivals.append(holiday_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
