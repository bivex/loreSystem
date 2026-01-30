"""
Consequence Entity

A Consequence is the result of a player choice or action.
Can affect story, characters, world state, etc.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation, InvalidState


class ConsequenceType(str, Enum):
    """Types of consequences."""
    STORY = "story"  # Narrative changes
    CHARACTER = "character"  # Character relationship changes
    WORLD = "world"  # World state changes
    QUEST = "quest"  # Quest availability changes
    REWARD = "reward"  # Item/experience rewards
    PENALTY = "penalty"  # Negative effects
    REPUTATION = "reputation"  # Faction reputation changes
    UNLOCK = "unlock"  # New content unlocked


class ConsequenceSeverity(str, Enum):
    """Severity levels of consequences."""
    TRIVIAL = "trivial"  # Minor cosmetic change
    MINOR = "minor"  # Small effect
    MODERATE = "moderate"  # Noticeable impact
    MAJOR = "major"  # Significant change
    CRITICAL = "critical"  # Story-altering impact


@dataclass
class Consequence:
    """
    Consequence entity representing a result of player actions.
    
    Invariants:
    - Must have a description
    - Must have a type and severity
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    description: Description
    consequence_type: ConsequenceType
    severity: ConsequenceSeverity
    is_permanent: bool
    is_visible_to_player: bool
    trigger_choice_id: Optional[EntityId]  # Choice that triggers this
    trigger_action_id: Optional[EntityId]  # Action that triggers this
    target_entity_id: Optional[EntityId]  # Entity affected
    effect_data: Dict[str, Any]  # Specific effect details
    delay_seconds: Optional[int]  # Delay before applying
    conditions: List[str]  # Conditions for applying
    
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
        
        if self.delay_seconds is not None and self.delay_seconds < 0:
            raise InvariantViolation("Delay cannot be negative")
        
        if self.trigger_choice_id is None and self.trigger_action_id is None:
            raise InvariantViolation(
                "Consequence must have either trigger_choice_id or trigger_action_id"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        description: Description,
        consequence_type: ConsequenceType,
        severity: ConsequenceSeverity,
        is_permanent: bool = True,
        is_visible_to_player: bool = True,
        trigger_choice_id: Optional[EntityId] = None,
        trigger_action_id: Optional[EntityId] = None,
        target_entity_id: Optional[EntityId] = None,
        effect_data: Optional[Dict[str, Any]] = None,
        delay_seconds: Optional[int] = None,
        conditions: Optional[List[str]] = None,
    ) -> 'Consequence':
        """Factory method for creating a new Consequence."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            description=description,
            consequence_type=consequence_type,
            severity=severity,
            is_permanent=is_permanent,
            is_visible_to_player=is_visible_to_player,
            trigger_choice_id=trigger_choice_id,
            trigger_action_id=trigger_action_id,
            target_entity_id=target_entity_id,
            effect_data=effect_data or {},
            delay_seconds=delay_seconds,
            conditions=conditions or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_condition(self, condition: str) -> None:
        """Add a condition for applying the consequence."""
        self.conditions.append(condition)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Consequence({self.consequence_type}, {self.severity})"
    
    def __repr__(self) -> str:
        return (
            f"Consequence(id={self.id}, type={self.consequence_type}, "
            f"severity={self.severity})"
        )
