"""
Ending Entity

An Ending is one of multiple possible conclusions to a campaign.
Based on player choices and actions throughout the game.
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


class EndingType(str, Enum):
    """Types of endings."""
    GOOD = "good"  # Positive outcome
    BAD = "bad"  # Negative outcome
    NEUTRAL = "neutral"  # Mixed outcome
    SECRET = "secret"  # Hidden ending
    CANON = "canon"  # Main story ending
    MULTIPLE = "multiple"  # Different possible endings


class EndingRarity(str, Enum):
    """Rarity of endings."""
    COMMON = "common"  # Easy to achieve
    UNCOMMON = "uncommon"  # Requires some effort
    RARE = "rare"  # Requires significant effort
    EPIC = "epic"  # Major achievement
    MYTHIC = "mythic"  # Extremely hard to find


@dataclass
class Ending:
    """
    Ending entity representing a campaign conclusion.
    
    Invariants:
    - Must have a title and description
    - Must belong to a campaign
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    campaign_id: EntityId
    world_id: EntityId
    title: str
    description: Description
    ending_type: EndingType
    rarity: EndingRarity
    conditions: List[str]  # Requirements to achieve
    is_unlocked: bool  # Default locked
    unlock_count: int  # How many times achieved
    character_endings: Dict[EntityId, str]  # Character-specific endings
    epilogue_id: Optional[EntityId]  # Associated epilogue
    achievement_id: Optional[EntityId]  # Achievement for unlocking
    image_url: Optional[str]
    ending_number: int  # For display (e.g., "Ending 1 of 5")
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.title or len(self.title.strip()) == 0:
            raise InvariantViolation("Ending title cannot be empty")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.unlock_count < 0:
            raise InvariantViolation("Unlock count cannot be negative")
        
        if self.ending_number < 1:
            raise InvariantViolation("Ending number must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        campaign_id: EntityId,
        world_id: EntityId,
        title: str,
        description: Description,
        ending_type: EndingType = EndingType.NEUTRAL,
        rarity: EndingRarity = EndingRarity.COMMON,
        conditions: Optional[List[str]] = None,
        character_endings: Optional[Dict[EntityId, str]] = None,
        epilogue_id: Optional[EntityId] = None,
        achievement_id: Optional[EntityId] = None,
        image_url: Optional[str] = None,
        ending_number: int = 1,
    ) -> 'Ending':
        """Factory method for creating a new Ending."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            world_id=world_id,
            title=title,
            description=description,
            ending_type=ending_type,
            rarity=rarity,
            conditions=conditions or [],
            is_unlocked=False,
            unlock_count=0,
            character_endings=character_endings or {},
            epilogue_id=epilogue_id,
            achievement_id=achievement_id,
            image_url=image_url,
            ending_number=ending_number,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def unlock(self) -> None:
        """Unlock this ending."""
        if self.is_unlocked:
            return
        
        object.__setattr__(self, 'is_unlocked', True)
        object.__setattr__(self, 'unlock_count', self.unlock_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increment_unlock_count(self) -> None:
        """Increment the number of times this ending was achieved."""
        object.__setattr__(self, 'unlock_count', self.unlock_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_condition(self, condition: str) -> None:
        """Add a condition for unlocking this ending."""
        self.conditions.append(condition)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_canon(self) -> bool:
        """Check if this is considered the canon ending."""
        return self.ending_type == EndingType.CANON
    
    def __str__(self) -> str:
        return f"Ending({self.title}, {self.ending_type}, {self.rarity})"
    
    def __repr__(self) -> str:
        return (
            f"Ending(id={self.id}, campaign_id={self.campaign_id}, "
            f"title='{self.title}', type={self.ending_type})"
        )
