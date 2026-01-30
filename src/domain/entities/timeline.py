"""
Timeline Entity - Organized sequence of events and periods
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime, timezone

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class TimelineType(str):
    """Types of timelines."""
    WORLD = "world"  # Main world history
    REGIONAL = "regional"  # Regional timeline
    FACTION = "faction"  # Faction-specific timeline
    CHARACTER = "character"  # Character biography timeline
    CUSTOM = "custom"  # User-defined timeline


@dataclass
class Timeline:
    """
    Timeline organizes events and eras in chronological order.
    
    Invariants:
    - Name cannot be empty
    - Events must be in chronological order
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    name: str
    description: Description
    
    # Timeline type and scope
    timeline_type: str
    scope_entity_id: Optional[EntityId]  # Entity this timeline tracks
    
    # Time period covered
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    
    # Content
    era_ids: List[EntityId]  # Eras in this timeline (ordered)
    event_ids: List[EntityId]  # Events in this timeline (ordered)
    era_transition_ids: List[EntityId]  # Transitions between eras
    
    # Timeline settings
    is_public: bool  # Visible to all players
    is_canonical: bool  # Official timeline vs alternate/fan-made
    
    # Visualization settings
    color_theme: Optional[str]
    display_format: Optional[str]  # e.g., "linear", "spiral", "parallel"
    
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
            raise InvariantViolation("Timeline name cannot be empty")
        
        if len(self.name) > 200:
            raise InvariantViolation("Timeline name must be <= 200 characters")
        
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
        timeline_type: str = TimelineType.WORLD,
        scope_entity_id: Optional[EntityId] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> 'Timeline':
        """
        Factory method for creating a new Timeline.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            timeline_type=timeline_type,
            scope_entity_id=scope_entity_id,
            start_date=start_date,
            end_date=end_date,
            era_ids=[],
            event_ids=[],
            era_transition_ids=[],
            is_public=True,
            is_canonical=True,
            color_theme=None,
            display_format="linear",
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_event(self, event_id: EntityId, position: Optional[int] = None) -> None:
        """Add an event to the timeline."""
        if event_id in self.event_ids:
            return
        
        if position is None:
            self.event_ids.append(event_id)
        else:
            self.event_ids.insert(position, event_id)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def remove_event(self, event_id: EntityId) -> None:
        """Remove an event from the timeline."""
        if event_id in self.event_ids:
            self.event_ids.remove(event_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_era(self, era_id: EntityId, position: Optional[int] = None) -> None:
        """Add an era to the timeline."""
        if era_id in self.era_ids:
            return
        
        if position is None:
            self.era_ids.append(era_id)
        else:
            self.era_ids.insert(position, era_id)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
