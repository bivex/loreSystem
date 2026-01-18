"""
CharacterRelationship Entity

Represents relationships between characters (friend, enemy, mentor, etc.).
Critical for creating deep, interconnected lore.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class RelationshipType(str, Enum):
    """Types of relationships between characters."""
    FRIEND = "friend"
    ENEMY = "enemy"
    RIVAL = "rival"
    LOVER = "lover"
    FAMILY = "family"  # Parent, sibling, child
    MENTOR = "mentor"  # Teacher -> Student
    STUDENT = "student"  # Student -> Teacher
    ALLY = "ally"  # Political/strategic alliance
    BETRAYER = "betrayer"  # Betrayed this person
    VICTIM = "victim"  # Was betrayed by this person
    SUPERIOR = "superior"  # Boss, commander
    SUBORDINATE = "subordinate"  # Reports to
    NEUTRAL = "neutral"  # No strong feelings
    COMPLICATED = "complicated"  # Mixed feelings


@dataclass
class CharacterRelationship:
    """
    CharacterRelationship entity linking two characters.
    
    Invariants:
    - Characters must be different (no self-relationships)
    - Relationship level must be -100 to 100
    - Both characters must exist in the same world
    - Is_mutual flag determines if relationship is bidirectional
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    
    # Source and target characters
    character_from_id: EntityId  # Subject of the relationship
    character_to_id: EntityId  # Object of the relationship
    
    # Relationship details
    relationship_type: RelationshipType
    description: Description  # How they know each other, history
    relationship_level: int  # -100 (hate) to +100 (love)
    is_mutual: bool  # True = both feel the same way
    
    # Gameplay impact
    combat_bonus_when_together: Optional[float]  # e.g., +10% ATK when in same team
    special_combo_ability_id: Optional[EntityId]  # Unlock special combo move
    dialogue_unlocked: bool  # Has special dialogue when both owned
    
    # Lore tracking
    first_met_event_id: Optional[EntityId]  # Event where they met
    relationship_changed_events: list  # Events that affected relationship
    
    # Meta
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
        
        # Cannot have relationship with self
        if self.character_from_id == self.character_to_id:
            raise InvariantViolation(
                "Character cannot have relationship with themselves"
            )
        
        # Validate relationship level
        if not (-100 <= self.relationship_level <= 100):
            raise InvariantViolation(
                "Relationship level must be between -100 and 100"
            )
        
        # Validate combat bonus
        if self.combat_bonus_when_together is not None:
            if self.combat_bonus_when_together < 0 or self.combat_bonus_when_together > 100:
                raise InvariantViolation(
                    "Combat bonus must be between 0-100%"
                )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        character_from_id: EntityId,
        character_to_id: EntityId,
        relationship_type: RelationshipType,
        description: Description,
        relationship_level: int = 0,
        is_mutual: bool = False,
        combat_bonus_when_together: Optional[float] = None,
        first_met_event_id: Optional[EntityId] = None,
    ) -> 'CharacterRelationship':
        """
        Factory method for creating a new CharacterRelationship.
        
        Example:
            # Lira hates Viktor (he killed her family)
            hatred = CharacterRelationship.create(
                tenant_id=TenantId(1),
                character_from_id=EntityId(3),  # Lira
                character_to_id=EntityId(4),  # Viktor
                relationship_type=RelationshipType.ENEMY,
                description=Description(
                    "Lira swore vengeance against Viktor after he slaughtered her clan "
                    "during the Vampire Purge. Their hatred fuels epic battles."
                ),
                relationship_level=-95,
                is_mutual=True,  # Viktor also hates Lira
                combat_bonus_when_together=15.0,  # +15% damage when fighting each other
                first_met_event_id=EntityId(100),
            )
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_from_id=character_from_id,
            character_to_id=character_to_id,
            relationship_type=relationship_type,
            description=description,
            relationship_level=relationship_level,
            is_mutual=is_mutual,
            combat_bonus_when_together=combat_bonus_when_together,
            special_combo_ability_id=None,
            dialogue_unlocked=False,
            first_met_event_id=first_met_event_id,
            relationship_changed_events=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def is_positive_relationship(self) -> bool:
        """Check if relationship is positive (love, friendship, etc.)."""
        return self.relationship_level > 20
    
    def is_negative_relationship(self) -> bool:
        """Check if relationship is negative (hatred, enmity, etc.)."""
        return self.relationship_level < -20
    
    def is_neutral_relationship(self) -> bool:
        """Check if relationship is neutral."""
        return -20 <= self.relationship_level <= 20
    
    def get_relationship_strength(self) -> str:
        """Get human-readable relationship strength."""
        abs_level = abs(self.relationship_level)
        
        if abs_level >= 80:
            return "extreme"
        elif abs_level >= 60:
            return "strong"
        elif abs_level >= 40:
            return "moderate"
        elif abs_level >= 20:
            return "mild"
        else:
            return "neutral"
    
    def update_relationship_level(self, delta: int, event_id: EntityId):
        """
        Update relationship level based on an event.
        
        Args:
            delta: Change in relationship (-100 to +100)
            event_id: Event that caused the change
        """
        new_level = self.relationship_level + delta
        
        # Clamp to valid range
        new_level = max(-100, min(100, new_level))
        
        object.__setattr__(self, 'relationship_level', new_level)
        self.relationship_changed_events.append({
            'event_id': event_id,
            'delta': delta,
            'timestamp': Timestamp.now().value,
        })
        object.__setattr__(self, 'updated_at', Timestamp.now())
