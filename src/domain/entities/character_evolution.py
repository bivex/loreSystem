"""
CharacterEvolution Entity

A CharacterEvolution tracks how a character develops over time.
Used in games with progression systems.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation, InvalidState


class EvolutionStage(str, Enum):
    """Evolution stages for characters."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"
    LEGENDARY = "legendary"
    TRANSCENDENT = "transcendent"


class EvolutionType(str, Enum):
    """Types of character evolution."""
    LEVEL_UP = "level_up"  # Standard leveling
    TRANSFORMATION = "transformation"  # Form change or awakening
    CLASS_CHANGE = "class_change"  # Job or role change
    SKILL_MASTERY = "skill_mastery"  # Mastering a skill tree
    STORY_UNLOCKED = "story_unlocked"  # Progressed through story
    QUEST_COMPLETED = "quest_completed"  # Finished a quest


@dataclass
class CharacterEvolution:
    """
    CharacterEvolution entity tracking character development.
    
    Invariants:
    - Must belong to a character
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    character_id: EntityId
    evolution_type: EvolutionType
    current_stage: EvolutionStage
    previous_stage: Optional[EvolutionStage]
    requirements: List[str]  # Conditions to evolve
    rewards: Dict[str, str]  # Rewards upon evolution
    evolved_at: Optional[Timestamp]
    variant_ids: List[EntityId]  # Unlocked variants
    new_abilities: List[str]  # Abilities gained
    stat_increases: Dict[str, int]  # Stat boosts
    is_permanent: bool
    can_revert: bool
    
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
        
        if self.evolved_at and self.evolved_at.value < self.created_at.value:
            raise InvariantViolation(
                "Evolved at must be >= created at"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        character_id: EntityId,
        current_stage: EvolutionStage,
        evolution_type: EvolutionType = EvolutionType.LEVEL_UP,
        previous_stage: Optional[EvolutionStage] = None,
        requirements: Optional[List[str]] = None,
        rewards: Optional[Dict[str, str]] = None,
        variant_ids: Optional[List[EntityId]] = None,
        new_abilities: Optional[List[str]] = None,
        stat_increases: Optional[Dict[str, int]] = None,
        is_permanent: bool = True,
        can_revert: bool = False,
    ) -> 'CharacterEvolution':
        """Factory method for creating a new CharacterEvolution."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            evolution_type=evolution_type,
            current_stage=current_stage,
            previous_stage=previous_stage,
            requirements=requirements or [],
            rewards=rewards or {},
            evolved_at=None,
            variant_ids=variant_ids or [],
            new_abilities=new_abilities or [],
            stat_increases=stat_increases or {},
            is_permanent=is_permanent,
            can_revert=can_revert,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def evolve(self) -> None:
        """Mark evolution as complete."""
        if self.evolved_at is not None:
            raise InvalidState("Character has already evolved")
        
        object.__setattr__(self, 'evolved_at', Timestamp.now())
        object.__setattr__(self, 'previous_stage', self.current_stage)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def advance_stage(self, new_stage: EvolutionStage) -> None:
        """Advance to next evolution stage."""
        object.__setattr__(self, 'previous_stage', self.current_stage)
        object.__setattr__(self, 'current_stage', new_stage)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"CharacterEvolution({self.evolution_type}, {self.current_stage})"
    
    def __repr__(self) -> str:
        return (
            f"CharacterEvolution(id={self.id}, character_id={self.character_id}, "
            f"type={self.evolution_type}, stage={self.current_stage})"
        )
