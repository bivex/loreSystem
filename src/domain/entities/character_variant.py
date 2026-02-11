"""
CharacterVariant Entity

A CharacterVariant is an alternate version of a character
(costume, age, form, etc.).
"""
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation, InvalidState


class VariantType(str, Enum):
    """Types of character variants."""
    COSTUME = "costume"  # Different outfit
    AGE = "age"  # Different age
    FORM = "form"  # Different physical form
    STATE = "state"  # Injured, transformed, etc.
    ALTERNATE = "alternate"  # AU version
    DLC = "dlc"  # Downloadable content variant
    EVENT = "event"  # Limited time variant
    EVOLUTION = "evolution"  # Evolved form


class VariantRarity(str, Enum):
    """Rarity of character variants."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


@dataclass
class CharacterVariant:
    """
    CharacterVariant entity representing an alternate character version.
    
    Invariants:
    - Must have a name
    - Must belong to a base character
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    base_character_id: EntityId
    name: str
    description: Optional[Description]
    variant_type: VariantType
    rarity: VariantRarity
    is_unlockable: bool
    unlock_condition: Optional[str]
    model_path: Optional[str]  # Path to 3D model
    texture_paths: List[str]  # Texture variants
    animation_overrides: List[str]  # Custom animations
    stat_modifiers: dict  # Stat changes from base
    ability_changes: List[str]  # Modified abilities
    is_seasonal: bool
    season_event_id: Optional[EntityId]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Variant name cannot be empty")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        base_character_id: EntityId,
        name: str,
        variant_type: VariantType = VariantType.COSTUME,
        rarity: VariantRarity = VariantRarity.COMMON,
        description: Optional[Description] = None,
        is_unlockable: bool = False,
        unlock_condition: Optional[str] = None,
        model_path: Optional[str] = None,
        texture_paths: Optional[List[str]] = None,
        animation_overrides: Optional[List[str]] = None,
        stat_modifiers: Optional[dict] = None,
        ability_changes: Optional[List[str]] = None,
        is_seasonal: bool = False,
        season_event_id: Optional[EntityId] = None,
    ) -> 'CharacterVariant':
        """Factory method for creating a new CharacterVariant."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            base_character_id=base_character_id,
            name=name,
            description=description,
            variant_type=variant_type,
            rarity=rarity,
            is_unlockable=is_unlockable,
            unlock_condition=unlock_condition,
            model_path=model_path,
            texture_paths=texture_paths or [],
            animation_overrides=animation_overrides or [],
            stat_modifiers=stat_modifiers or {},
            ability_changes=ability_changes or [],
            is_seasonal=is_seasonal,
            season_event_id=season_event_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def __str__(self) -> str:
        return f"CharacterVariant({self.name}, {self.variant_type})"
    
    def __repr__(self) -> str:
        return (
            f"CharacterVariant(id={self.id}, base_character_id={self.base_character_id}, "
            f"name='{self.name}', type={self.variant_type})"
        )
