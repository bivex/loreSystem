"""
EraTransition Entity - Transition between historical eras
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


class TransitionType(str):
    """Types of era transitions."""
    CATASTROPHIC = "catastrophic"
    GRADUAL = "gradual"
    REVOLUTIONARY = "revolutionary"
    PEACEFUL = "peaceful"
    MAGICAL = "magical"
    NATURAL = "natural"
    DIVINE = "divine"
    TECHNOLOGICAL = "technological"


@dataclass
class EraTransition:
    """
    EraTransition represents the transition point between two eras.
    
    Invariants:
    - Transition date must be specified
    - Source and target eras must be different
    - Transition type must be valid
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    name: str
    description: Description
    
    # The eras involved
    from_era_id: EntityId
    to_era_id: EntityId
    
    # Transition details
    transition_date: datetime
    transition_type: str
    
    # Key events and causes
    trigger_events: List[str]  # Events that caused the transition
    key_figures: List[EntityId]  # Characters involved in transition
    
    # Impact
    social_impact: Optional[str]
    economic_impact: Optional[str]
    political_impact: Optional[str]
    magical_impact: Optional[str]
    
    # Narrative elements
    stories_and_legends: List[str]  # Stories about this transition
    artifacts: List[EntityId]  # Items from this transition period
    
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
            raise InvariantViolation("EraTransition name cannot be empty")
        
        if self.from_era_id == self.to_era_id:
            raise InvariantViolation(
                "Source and target eras must be different"
            )
        
        valid_types = [
            "catastrophic", "gradual", "revolutionary", "peaceful",
            "magical", "natural", "divine", "technological"
        ]
        if self.transition_type not in valid_types:
            raise InvariantViolation(
                f"Invalid transition type: {self.transition_type}"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        from_era_id: EntityId,
        to_era_id: EntityId,
        transition_date: datetime,
        transition_type: str = "gradual",
    ) -> 'EraTransition':
        """
        Factory method for creating a new EraTransition.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            from_era_id=from_era_id,
            to_era_id=to_era_id,
            transition_date=transition_date,
            transition_type=transition_type,
            trigger_events=[],
            key_figures=[],
            social_impact=None,
            economic_impact=None,
            political_impact=None,
            magical_impact=None,
            stories_and_legends=[],
            artifacts=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_trigger_event(self, event: str) -> None:
        """Add a trigger event for the transition."""
        if event not in self.trigger_events:
            self.trigger_events.append(event)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_key_figure(self, character_id: EntityId) -> None:
        """Add a key figure involved in the transition."""
        if character_id not in self.key_figures:
            self.key_figures.append(character_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
