"""
Era Entity - Historical period in world history
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, timezone

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Era:
    """
    Era represents a distinct historical period in the world's timeline.
    
    Invariants:
    - Name cannot be empty
    - End date must be after start date (if both specified)
    - Updated timestamp >= created timestamp
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    name: str
    description: Description
    
    # Time period
    start_date: Optional[datetime]  # Era start date
    end_date: Optional[datetime]  # Era end date (None for ongoing)
    
    # Parent/child relationships for nested eras
    parent_era_id: Optional[EntityId]
    child_era_ids: List[EntityId]
    
    # Characteristics
    major_events: List[str]  # Brief descriptions of major events
    cultural_notes: Optional[str]  # Cultural aspects of this era
    technological_level: Optional[str]  # e.g., "Bronze Age", "Medieval"
    
    # Metadata
    is_ongoing: bool
    color_code: Optional[str]  # For timeline visualization
    
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
            raise InvariantViolation("Era name cannot be empty")
        
        if len(self.name) > 200:
            raise InvariantViolation("Era name must be <= 200 characters")
        
        # Validate date range
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise InvariantViolation(
                    "End date must be after start date"
                )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        parent_era_id: Optional[EntityId] = None,
        is_ongoing: bool = False,
    ) -> 'Era':
        """
        Factory method for creating a new Era.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            parent_era_id=parent_era_id,
            child_era_ids=[],
            major_events=[],
            cultural_notes=None,
            technological_level=None,
            is_ongoing=is_ongoing,
            color_code=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_major_event(self, event_description: str) -> None:
        """Add a major event to this era."""
        if event_description not in self.major_events:
            self.major_events.append(event_description)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def end_era(self, end_date: Optional[datetime] = None) -> None:
        """Mark era as ended."""
        if not self.is_ongoing:
            return
        
        date = end_date or datetime.now(timezone.utc)
        
        if self.start_date and date < self.start_date:
            raise InvariantViolation(
                "End date cannot be before start date"
            )
        
        object.__setattr__(self, 'end_date', date)
        object.__setattr__(self, 'is_ongoing', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
