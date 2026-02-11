"""
QuestNode Entity

A QuestNode represents a single quest within a QuestChain.
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
class QuestNode:
    """
    QuestNode entity representing a quest in a chain.
    
    Invariants:
    - Must belong to exactly one QuestChain
    - Must have at least one objective
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    quest_chain_id: EntityId
    name: str
    description: Description
    objective_ids: List[EntityId]  # Objectives that must be completed
    prerequisite_ids: List[EntityId]  # Prerequisites before this quest
    reward_tier_ids: List[EntityId]  # Reward tiers for completion
    status: QuestStatus
    is_optional: bool  # Can this quest be skipped?
    auto_complete: bool  # Auto-complete when objectives done?
    position: int  # Position within the chain
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.objective_ids:
            raise InvariantViolation("QuestNode must have at least one objective")
        
        if self.position < 0:
            raise InvariantViolation("Position cannot be negative")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        quest_chain_id: EntityId,
        name: str,
        description: Description,
        objective_ids: List[EntityId],
        prerequisite_ids: Optional[List[EntityId]] = None,
        reward_tier_ids: Optional[List[EntityId]] = None,
        is_optional: bool = False,
        auto_complete: bool = False,
        position: int = 0,
    ) -> 'QuestNode':
        """
        Factory method for creating a new QuestNode.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            quest_chain_id=quest_chain_id,
            name=name,
            description=description,
            objective_ids=objective_ids,
            prerequisite_ids=prerequisite_ids or [],
            reward_tier_ids=reward_tier_ids or [],
            status=QuestStatus.ACTIVE,
            is_optional=is_optional,
            auto_complete=auto_complete,
            position=position,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_objective(self, objective_id: EntityId) -> None:
        """Add an objective to this quest node."""
        if objective_id in self.objective_ids:
            raise InvariantViolation(f"Objective {objective_id} already exists in quest")
        
        self.objective_ids.append(objective_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_objective(self, objective_id: EntityId) -> None:
        """Remove an objective from this quest node."""
        if objective_id not in self.objective_ids:
            raise InvalidState(f"Objective {objective_id} not found in quest")
        
        if len(self.objective_ids) == 1:
            raise InvariantViolation("Cannot remove the last objective from quest")
        
        self.objective_ids.remove(objective_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_prerequisite(self, prerequisite_id: EntityId) -> None:
        """Add a prerequisite to this quest."""
        if prerequisite_id in self.prerequisite_ids:
            return
        
        self.prerequisite_ids.append(prerequisite_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_reward_tier(self, reward_tier_id: EntityId) -> None:
        """Add a reward tier to this quest."""
        if reward_tier_id in self.reward_tier_ids:
            return
        
        self.reward_tier_ids.append(reward_tier_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(self) -> 'QuestNode':
        """Mark quest node as completed."""
        if self.status != QuestStatus.ACTIVE:
            raise InvalidState(f"Cannot complete quest with status {self.status}")
        
        return QuestNode(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            quest_chain_id=self.quest_chain_id,
            name=self.name,
            description=self.description,
            objective_ids=self.objective_ids,
            prerequisite_ids=self.prerequisite_ids,
            reward_tier_ids=self.reward_tier_ids,
            status=QuestStatus.COMPLETED,
            is_optional=self.is_optional,
            auto_complete=self.auto_complete,
            position=self.position,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment(),
        )
    
    def fail(self) -> 'QuestNode':
        """Mark quest node as failed."""
        if self.status != QuestStatus.ACTIVE:
            raise InvalidState(f"Cannot fail quest with status {self.status}")
        
        return QuestNode(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            quest_chain_id=self.quest_chain_id,
            name=self.name,
            description=self.description,
            objective_ids=self.objective_ids,
            prerequisite_ids=self.prerequisite_ids,
            reward_tier_ids=self.reward_tier_ids,
            status=QuestStatus.FAILED,
            is_optional=self.is_optional,
            auto_complete=self.auto_complete,
            position=self.position,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment(),
        )
    
    def update_position(self, new_position: int) -> None:
        """Update the position of this quest within the chain."""
        if new_position < 0:
            raise InvariantViolation("Position cannot be negative")
        
        object.__setattr__(self, 'position', new_position)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"QuestNode({self.name}, objectives={len(self.objective_ids)})"
    
    def __repr__(self) -> str:
        return (
            f"QuestNode(id={self.id}, quest_chain_id={self.quest_chain_id}, "
            f"name='{self.name}', status={self.status})"
        )
