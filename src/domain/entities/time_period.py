"""
TimePeriod Entity - Generic time period
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


class PeriodType(str):
    """Types of time periods."""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    DECADE = "decade"
    CENTURY = "century"
    MILLENNIUM = "millennium"
    CUSTOM = "custom"


@dataclass
class TimePeriod:
    """
    TimePeriod represents a named period of time (not necessarily historical era).
    
    Invariants:
    - Name cannot be empty
    - End date must be after start date
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    name: str
    description: Description
    
    # Time period type
    period_type: str
    
    # Duration
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    
    # Relationships
    parent_period_id: Optional[EntityId]
    child_period_ids: List[EntityId]
    
    # Period characteristics
    significance: Optional[str]  # Why this period is notable
    key_events: List[EntityId]  # Events in this period
    
    # Tags and categorization
    tags: List[str]
    
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
            raise InvariantViolation("TimePeriod name cannot be empty")
        
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
        period_type: str = PeriodType.CUSTOM,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        parent_period_id: Optional[EntityId] = None,
    ) -> 'TimePeriod':
        """
        Factory method for creating a new TimePeriod.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            parent_period_id=parent_period_id,
            child_period_ids=[],
            significance=None,
            key_events=[],
            tags=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_key_event(self, event_id: EntityId) -> None:
        """Add a key event to this period."""
        if event_id not in self.key_events:
            self.key_events.append(event_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to this period."""
        if tag not in self.tags:
            self.tags.append(tag)
            object.__setattr__(self, 'updated_at', Timestamp.now())
