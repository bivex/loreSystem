"""
QuestTracker Entity

A QuestTracker tracks a player's progress through quests and quest chains.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
    QuestStatus,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class QuestTracker:
    """
    QuestTracker entity for player quest progress.
    
    Invariants:
    - Must belong to exactly one player profile
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    player_profile_id: EntityId
    active_quest_chain_ids: List[EntityId]  # Currently active quest chains
    completed_quest_chain_ids: List[EntityId]  # Fully completed chains
    active_quest_node_ids: List[EntityId]  # Currently active quests
    completed_quest_node_ids: List[EntityId]  # Completed quests
    failed_quest_node_ids: List[EntityId]  # Failed quests
    objective_progress: Dict[EntityId, int]  # Objective ID -> current progress
    quest_chain_completions: Dict[EntityId, int]  # Chain ID -> completion count
    last_updated: Timestamp  # When this tracker was last updated
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
        
        # Validate no overlap between quest lists
        active_set = set(self.active_quest_node_ids)
        completed_set = set(self.completed_quest_node_ids)
        failed_set = set(self.failed_quest_node_ids)
        
        overlaps = [
            (active_set & completed_set, "active and completed"),
            (active_set & failed_set, "active and failed"),
            (completed_set & failed_set, "completed and failed"),
        ]
        
        for overlap, desc in overlaps:
            if overlap:
                raise InvariantViolation(
                    f"Quest cannot be in both {desc} lists: {overlap}"
                )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        player_profile_id: EntityId,
    ) -> 'QuestTracker':
        """
        Factory method for creating a new QuestTracker.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            player_profile_id=player_profile_id,
            active_quest_chain_ids=[],
            completed_quest_chain_ids=[],
            active_quest_node_ids=[],
            completed_quest_node_ids=[],
            failed_quest_node_ids=[],
            objective_progress={},
            quest_chain_completions={},
            last_updated=now,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def start_quest_chain(self, quest_chain_id: EntityId) -> None:
        """Start tracking a new quest chain."""
        if quest_chain_id in self.active_quest_chain_ids:
            return
        
        if quest_chain_id in self.completed_quest_chain_ids:
            raise InvalidState(f"Quest chain {quest_chain_id} is already completed")
        
        self.active_quest_chain_ids.append(quest_chain_id)
        object.__setattr__(self, 'last_updated', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def start_quest(self, quest_node_id: EntityId) -> None:
        """Start tracking a new quest."""
        if quest_node_id in self.active_quest_node_ids:
            return
        
        if quest_node_id in self.completed_quest_node_ids:
            raise InvalidState(f"Quest {quest_node_id} is already completed")
        
        if quest_node_id in self.failed_quest_node_ids:
            raise InvalidState(f"Quest {quest_node_id} has failed")
        
        self.active_quest_node_ids.append(quest_node_id)
        object.__setattr__(self, 'last_updated', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete_quest(self, quest_node_id: EntityId) -> None:
        """Mark a quest as completed."""
        if quest_node_id not in self.active_quest_node_ids:
            raise InvalidState(f"Quest {quest_node_id} is not active")
        
        self.active_quest_node_ids.remove(quest_node_id)
        self.completed_quest_node_ids.append(quest_node_id)
        object.__setattr__(self, 'last_updated', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def fail_quest(self, quest_node_id: EntityId) -> None:
        """Mark a quest as failed."""
        if quest_node_id not in self.active_quest_node_ids:
            raise InvalidState(f"Quest {quest_node_id} is not active")
        
        self.active_quest_node_ids.remove(quest_node_id)
        self.failed_quest_node_ids.append(quest_node_id)
        object.__setattr__(self, 'last_updated', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete_quest_chain(self, quest_chain_id: EntityId) -> None:
        """Mark a quest chain as completed."""
        if quest_chain_id not in self.active_quest_chain_ids:
            raise InvalidState(f"Quest chain {quest_chain_id} is not active")
        
        self.active_quest_chain_ids.remove(quest_chain_id)
        self.completed_quest_chain_ids.append(quest_chain_id)
        
        # Track completion count
        self.quest_chain_completions[quest_chain_id] = (
            self.quest_chain_completions.get(quest_chain_id, 0) + 1
        )
        
        object.__setattr__(self, 'last_updated', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_objective_progress(self, objective_id: EntityId, progress: int) -> None:
        """Update progress for a specific objective."""
        if progress < 0:
            raise InvariantViolation("Progress cannot be negative")
        
        self.objective_progress[objective_id] = progress
        object.__setattr__(self, 'last_updated', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def get_objective_progress(self, objective_id: EntityId) -> int:
        """Get progress for a specific objective."""
        return self.objective_progress.get(objective_id, 0)
    
    def get_chain_completion_count(self, quest_chain_id: EntityId) -> int:
        """Get how many times a quest chain has been completed."""
        return self.quest_chain_completions.get(quest_chain_id, 0)
    
    def is_quest_active(self, quest_node_id: EntityId) -> bool:
        """Check if a quest is currently active."""
        return quest_node_id in self.active_quest_node_ids
    
    def is_quest_completed(self, quest_node_id: EntityId) -> bool:
        """Check if a quest is completed."""
        return quest_node_id in self.completed_quest_node_ids
    
    def is_quest_failed(self, quest_node_id: EntityId) -> bool:
        """Check if a quest has failed."""
        return quest_node_id in self.failed_quest_node_ids
    
    def __str__(self) -> str:
        return (
            f"QuestTracker(active={len(self.active_quest_node_ids)}, "
            f"completed={len(self.completed_quest_node_ids)})"
        )
    
    def __repr__(self) -> str:
        return (
            f"QuestTracker(id={self.id}, player_id={self.player_profile_id}, "
            f"active_quests={len(self.active_quest_node_ids)})"
        )
