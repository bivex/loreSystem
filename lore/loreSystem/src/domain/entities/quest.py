"""
Quest Entity

A Quest represents a task or mission that characters can undertake.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    QuestStatus,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class Quest:
    """
    Quest entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Must have at least one objective
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    objectives: List[str]
    status: QuestStatus
    participant_ids: List[EntityId]  # Characters involved
    reward_ids: List[EntityId]  # Items rewarded upon completion
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.objectives:
            raise InvariantViolation("Quest must have at least one objective")
        
        if not self.participant_ids:
            raise InvariantViolation("Quest must have at least one participant")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
    
    def complete(self) -> 'Quest':
        """Mark quest as completed."""
        if self.status != QuestStatus.ACTIVE:
            raise InvalidState(f"Cannot complete quest with status {self.status}")
        
        return Quest(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            description=self.description,
            objectives=self.objectives,
            status=QuestStatus.COMPLETED,
            participant_ids=self.participant_ids,
            reward_ids=self.reward_ids,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
    
    def fail(self) -> 'Quest':
        """Mark quest as failed."""
        if self.status != QuestStatus.ACTIVE:
            raise InvalidState(f"Cannot fail quest with status {self.status}")
        
        return Quest(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            description=self.description,
            objectives=self.objectives,
            status=QuestStatus.FAILED,
            participant_ids=self.participant_ids,
            reward_ids=self.reward_ids,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )