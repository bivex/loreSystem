"""
QuestChain Entity

A QuestChain represents a sequence of related quests that follow each other.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    ChainStatus,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class QuestChain:
    """
    QuestChain entity for organizing sequential quest progression.
    
    Invariants:
    - Must belong to exactly one World
    - Must have at least one quest node
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    quest_node_ids: List[EntityId]  # Ordered sequence of quests
    status: ChainStatus
    required_level: Optional[int]  # Minimum level to start chain
    is_repeatable: bool  # Can the chain be completed multiple times?
    cooldown_hours: Optional[int]  # Cooldown between completions
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.quest_node_ids:
            raise InvariantViolation("QuestChain must have at least one quest node")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
        
        if self.required_level is not None and self.required_level < 1:
            raise InvariantViolation("Required level must be >= 1")
        
        if self.cooldown_hours is not None and self.cooldown_hours < 0:
            raise InvariantViolation("Cooldown hours cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        quest_node_ids: List[EntityId],
        required_level: Optional[int] = None,
        is_repeatable: bool = False,
        cooldown_hours: Optional[int] = None,
    ) -> 'QuestChain':
        """
        Factory method for creating a new QuestChain.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            quest_node_ids=quest_node_ids,
            status=ChainStatus.ACTIVE,
            required_level=required_level,
            is_repeatable=is_repeatable,
            cooldown_hours=cooldown_hours,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_quest_node(self, quest_node_id: EntityId, position: Optional[int] = None) -> None:
        """
        Add a quest node to the chain.
        
        Args:
            quest_node_id: The ID of the quest node to add
            position: Optional position to insert at (None = append to end)
        """
        if position is None:
            self.quest_node_ids.append(quest_node_id)
        else:
            if position < 0 or position > len(self.quest_node_ids):
                raise InvariantViolation(f"Invalid position {position}")
            self.quest_node_ids.insert(position, quest_node_id)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_quest_node(self, quest_node_id: EntityId) -> None:
        """
        Remove a quest node from the chain.
        """
        if quest_node_id not in self.quest_node_ids:
            raise InvalidState(f"Quest node {quest_node_id} not found in chain")
        
        if len(self.quest_node_ids) == 1:
            raise InvariantViolation("Cannot remove the last quest node from chain")
        
        self.quest_node_ids.remove(quest_node_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def get_next_quest(self, completed_quest_ids: List[EntityId]) -> Optional[EntityId]:
        """
        Get the next quest in the chain based on completed quests.
        
        Returns:
            The next quest node ID, or None if chain is complete
        """
        for quest_id in self.quest_node_ids:
            if quest_id not in completed_quest_ids:
                return quest_id
        return None
    
    def is_complete(self, completed_quest_ids: List[EntityId]) -> bool:
        """
        Check if all quests in the chain are completed.
        """
        return all(qid in completed_quest_ids for qid in self.quest_node_ids)
    
    def update_cooldown(self, cooldown_hours: Optional[int]) -> None:
        """Update the cooldown duration."""
        if cooldown_hours is not None and cooldown_hours < 0:
            raise InvariantViolation("Cooldown hours cannot be negative")
        
        object.__setattr__(self, 'cooldown_hours', cooldown_hours)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"QuestChain({self.name}, quests={len(self.quest_node_ids)})"
    
    def __repr__(self) -> str:
        return (
            f"QuestChain(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', status={self.status})"
        )
