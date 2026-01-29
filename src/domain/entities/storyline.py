"""
Storyline Entity

A Storyline represents a narrative arc that connects events and quests.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    StorylineType,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class Storyline:
    """
    Storyline entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Must have at least one event or quest
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    storyline_type: StorylineType
    event_ids: List[EntityId]  # Events in this storyline
    quest_ids: List[EntityId]  # Quests in this storyline
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.event_ids and not self.quest_ids:
            raise InvariantViolation("Storyline must have at least one event or quest")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
    
    def add_event(self, event_id: EntityId) -> 'Storyline':
        """Add an event to the storyline."""
        if event_id in self.event_ids:
            raise InvalidState("Event already in storyline")
        
        return Storyline(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            description=self.description,
            storyline_type=self.storyline_type,
            event_ids=self.event_ids + [event_id],
            quest_ids=self.quest_ids,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
    
    def add_quest(self, quest_id: EntityId) -> 'Storyline':
        """Add a quest to the storyline."""
        if quest_id in self.quest_ids:
            raise InvalidState("Quest already in storyline")
        
        return Storyline(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            description=self.description,
            storyline_type=self.storyline_type,
            event_ids=self.event_ids,
            quest_ids=self.quest_ids + [quest_id],
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )