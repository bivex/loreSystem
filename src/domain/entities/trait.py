"""
Trait Entity

A Trait is a permanent characteristic or personality feature of a character.
Traits define innate abilities, weaknesses, and behavioral patterns.
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
)
from ..exceptions import InvariantViolation


class TraitCategory(str, Enum):
    """Category of trait."""
    PERSONALITY = "personality"
    PHYSICAL = "physical"
    MENTAL = "mental"
    SOCIAL = "social"
    MAGICAL = "magical"
    RACIAL = "racial"


class TraitNature(str, Enum):
    """Whether the trait is positive, negative, or mixed."""
    POSITIVE = "positive"  # Pure benefit
    NEGATIVE = "negative"  # Pure drawback
    MIXED = "mixed"  # Both benefits and drawbacks


@dataclass
class Trait:
    """
    Trait entity representing character characteristics.
    
    Invariants:
    - Must have a valid character_id
    - Impact value must be between -100 and 100
    - Version increases monotonically
    - Cannot have empty name
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: EntityId
    name: str
    description: Description
    category: TraitCategory
    nature: TraitNature
    
    # Trait effects
    impact_value: int  # Overall impact score (-100 to 100)
    positive_effects: Optional[List[str]]  # List of positive effects
    negative_effects: Optional[List[str]]  # List of negative effects
    stat_modifiers: Optional[dict]  # Dict of stat_name -> modifier_value
    
    # Trait relationships
    conflicts_with: Optional[List[str]]  # Trait names that conflict with this one
    synergizes_with: Optional[List[str]]  # Trait names that synergize with this one
    
    # Metadata
    is_inheritable: bool  # Can be passed to offspring
    icon_id: Optional[str]
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
            raise InvariantViolation("Trait name cannot be empty")
        
        if self.impact_value < -100 or self.impact_value > 100:
            raise InvariantViolation("Impact value must be between -100 and 100")
        
        if self.nature == TraitNature.POSITIVE and self.impact_value <= 0:
            raise InvariantViolation("POSITIVE trait must have positive impact")
        
        if self.nature == TraitNature.NEGATIVE and self.impact_value >= 0:
            raise InvariantViolation("NEGATIVE trait must have negative impact")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        character_id: EntityId,
        name: str,
        description: Description,
        category: TraitCategory,
        nature: TraitNature,
        impact_value: int,
        positive_effects: Optional[List[str]] = None,
        negative_effects: Optional[List[str]] = None,
        stat_modifiers: Optional[dict] = None,
        conflicts_with: Optional[List[str]] = None,
        synergizes_with: Optional[List[str]] = None,
        is_inheritable: bool = True,
        icon_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> 'Trait':
        """
        Factory method for creating a new Trait.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            name=name,
            description=description,
            category=category,
            nature=nature,
            impact_value=impact_value,
            positive_effects=positive_effects or [],
            negative_effects=negative_effects or [],
            stat_modifiers=stat_modifiers or {},
            conflicts_with=conflicts_with or [],
            synergizes_with=synergizes_with or [],
            is_inheritable=is_inheritable,
            icon_id=icon_id,
            tags=tags,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def conflicts_with_trait(self, trait_name: str) -> bool:
        """Check if this trait conflicts with another."""
        return trait_name in (self.conflicts_with or [])
    
    def synergizes_with_trait(self, trait_name: str) -> bool:
        """Check if this trait synergizes with another."""
        return trait_name in (self.synergizes_with or [])
    
    def get_stat_modifier(self, stat_name: str) -> Optional[float]:
        """Get modifier for a specific stat."""
        if not self.stat_modifiers:
            return None
        return self.stat_modifiers.get(stat_name)
    
    def has_positive_effect(self, effect: str) -> bool:
        """Check if trait has a specific positive effect."""
        return effect in (self.positive_effects or [])
    
    def has_negative_effect(self, effect: str) -> bool:
        """Check if trait has a specific negative effect."""
        return effect in (self.negative_effects or [])
    
    def add_positive_effect(self, effect: str) -> None:
        """Add a positive effect to the trait."""
        if self.has_positive_effect(effect):
            return
        
        if not self.positive_effects:
            object.__setattr__(self, 'positive_effects', [])
        
        self.positive_effects.append(effect)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_negative_effect(self, effect: str) -> None:
        """Add a negative effect to the trait."""
        if self.has_negative_effect(effect):
            return
        
        if not self.negative_effects:
            object.__setattr__(self, 'negative_effects', [])
        
        self.negative_effects.append(effect)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_stat_modifier(self, stat_name: str, value: float) -> None:
        """Set or update a stat modifier."""
        if not self.stat_modifiers:
            object.__setattr__(self, 'stat_modifiers', {})
        
        self.stat_modifiers[stat_name] = value
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_beneficial(self) -> bool:
        """Check if the trait is overall beneficial."""
        return self.impact_value > 0
    
    def is_detrimental(self) -> bool:
        """Check if the trait is overall detrimental."""
        return self.impact_value < 0
    
    def __str__(self) -> str:
        nature_str = f" [{self.nature.value}]"
        return f"Trait({self.name}{nature_str}, impact={self.impact_value})"
    
    def __repr__(self) -> str:
        return (
            f"Trait(id={self.id}, character_id={self.character_id}, "
            f"name='{self.name}', category={self.category.value})"
        )
