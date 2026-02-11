"""
Perk Entity

A Perk is a passive benefit or bonus that a character possesses.
Perks are typically gained through choices, achievements, or special events.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    Rarity,
)
from ..exceptions import InvariantViolation


class PerkType(str, Enum):
    """Type of perk benefit."""
    STAT_BOOST = "stat_boost"  # Increases a specific stat
    RESISTANCE = "resistance"  # Provides resistance to damage/effects
    ABILITY_MODIFIER = "ability_modifier"  # Modifies abilities
    ECONOMIC = "economic"  # Provides economic benefits (discounts, bonuses)
    SOCIAL = "social"  # Improves social interactions
    UTILITY = "utility"  # General utility benefits


class PerkSource(str, Enum):
    """How the perk was acquired."""
    ACHIEVEMENT = "achievement"
    CHOICE = "choice"  # Selected from a choice pool
    EVENT = "event"
    LEVEL_UP = "level_up"
    QUEST_REWARD = "quest_reward"
    INHERITANCE = "inheritance"  # From parent/lineage


@dataclass
class Perk:
    """
    Perk entity representing passive benefits.
    
    Invariants:
    - Stacking must be between 0-100 (for stacking perks)
    - Version increases monotonically
    - Cannot have empty name
    - Active perks must have valid effect values
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: EntityId
    name: str
    description: Description
    perk_type: PerkType
    source: PerkSource
    rarity: Optional[Rarity]
    
    # Perk effects
    stat_type: Optional[str]  # Which stat this affects (for STAT_BOOST type)
    stat_modifier: Optional[float]  # Flat or percentage modifier
    resistance_type: Optional[str]  # Which damage type resisted (for RESISTANCE type)
    resistance_value: Optional[int]  # Resistance percentage (0-100)
    ability_id: Optional[EntityId]  # Which ability is modified (for ABILITY_MODIFIER type)
    ability_modifier: Optional[str]  # How to modify the ability
    stacking_limit: Optional[int]  # Maximum times this perk can stack (0 = infinite)
    
    # Status
    is_active: bool  # Whether the perk is currently active
    is_hidden: bool  # Whether the perk is hidden from UI
    
    # Metadata
    icon_id: Optional[str]
    source_id: Optional[EntityId]  # ID of achievement, event, etc. that granted this perk
    tags: Optional[List[str]]
    
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
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Perk name cannot be empty")
        
        if self.stacking_limit is not None and self.stacking_limit < 0:
            raise InvariantViolation("Stacking limit cannot be negative")
        
        if self.resistance_value is not None and (self.resistance_value < 0 or self.resistance_value > 100):
            raise InvariantViolation("Resistance value must be between 0-100")
        
        # Validate perk type-specific fields
        if self.perk_type == PerkType.STAT_BOOST and not self.stat_type:
            raise InvariantViolation("STAT_BOOST perk must have stat_type")
        
        if self.perk_type == PerkType.RESISTANCE and not self.resistance_type:
            raise InvariantViolation("RESISTANCE perk must have resistance_type")
        
        if self.perk_type == PerkType.ABILITY_MODIFIER and not self.ability_id:
            raise InvariantViolation("ABILITY_MODIFIER perk must have ability_id")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        character_id: EntityId,
        name: str,
        description: Description,
        perk_type: PerkType,
        source: PerkSource,
        rarity: Optional[Rarity] = None,
        stat_type: Optional[str] = None,
        stat_modifier: Optional[float] = None,
        resistance_type: Optional[str] = None,
        resistance_value: Optional[int] = None,
        ability_id: Optional[EntityId] = None,
        ability_modifier: Optional[str] = None,
        stacking_limit: Optional[int] = None,
        is_active: bool = True,
        is_hidden: bool = False,
        icon_id: Optional[str] = None,
        source_id: Optional[EntityId] = None,
        tags: Optional[List[str]] = None,
    ) -> 'Perk':
        """
        Factory method for creating a new Perk.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            name=name,
            description=description,
            perk_type=perk_type,
            source=source,
            rarity=rarity,
            stat_type=stat_type,
            stat_modifier=stat_modifier,
            resistance_type=resistance_type,
            resistance_value=resistance_value,
            ability_id=ability_id,
            ability_modifier=ability_modifier,
            stacking_limit=stacking_limit,
            is_active=is_active,
            is_hidden=is_hidden,
            icon_id=icon_id,
            source_id=source_id,
            tags=tags,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def activate(self) -> None:
        """Activate the perk."""
        if self.is_active:
            return
        
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Deactivate the perk."""
        if not self.is_active:
            return
        
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def show(self) -> None:
        """Make the perk visible in UI."""
        if not self.is_hidden:
            return
        
        object.__setattr__(self, 'is_hidden', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def hide(self) -> None:
        """Hide the perk from UI."""
        if self.is_hidden:
            return
        
        object.__setattr__(self, 'is_hidden', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def can_stack(self) -> bool:
        """Check if perk can stack (has stacking limit > 1 or no limit)."""
        return self.stacking_limit is None or self.stacking_limit > 1
    
    def get_effective_modifier(self) -> float:
        """
        Calculate the effective stat modifier.
        For complex perk systems, this can be overridden in subclasses.
        """
        return self.stat_modifier if self.stat_modifier is not None else 0.0
    
    def __str__(self) -> str:
        status = "" if self.is_active else " (inactive)"
        hidden = " [HIDDEN]" if self.is_hidden else ""
        return f"Perk({self.name}{status}{hidden}, {self.perk_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Perk(id={self.id}, character_id={self.character_id}, "
            f"name='{self.name}', type={self.perk_type.value})"
        )
