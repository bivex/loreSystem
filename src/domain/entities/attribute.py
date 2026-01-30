"""
Attribute Entity

An Attribute is a core stat or property that defines a character's capabilities.
Examples: Strength, Intelligence, Dexterity, Constitution, etc.
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


class AttributeType(str, Enum):
    """Type of attribute."""
    PHYSICAL = "physical"  # STR, DEX, CON, etc.
    MENTAL = "mental"  # INT, WIS, CHA, etc.
    MAGICAL = "magical"  # MAG, FAITH, AURA, etc.
    DERIVED = "derived"  # HP, MP, Attack Power, etc.
    SPECIAL = "special"  # Luck, Perception, etc.


class AttributeScale(str, Enum):
    """Scaling behavior for the attribute."""
    LINEAR = "linear"  # Grows linearly
    EXPONENTIAL = "exponential"  # Grows exponentially
    LOGARITHMIC = "logarithmic"  # Grows logarithmically
    FIXED = "fixed"  # Does not scale


@dataclass
class Attribute:
    """
    Attribute entity representing character stats.
    
    Invariants:
    - Base value must be non-negative
    - Current value cannot exceed maximum
    - Current value cannot be negative
    - Version increases monotonically
    - Cannot have empty name
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: EntityId
    name: str
    description: Description
    attribute_type: AttributeType
    scale_type: AttributeScale
    
    # Attribute values
    base_value: float  # Base value from character level/race
    current_value: float  # Current value (including modifiers)
    maximum_value: Optional[float]  # Maximum possible value (None = unlimited)
    
    # Modifiers
    flat_bonus: float  # Flat additive bonus
    percentage_bonus: float  # Percentage multiplier bonus
    temporary_bonus: Optional[float]  # Temporary bonus (expires over time)
    
    # Attribute properties
    is_derived: bool  # If true, calculated from other attributes
    derivation_formula: Optional[str]  # Formula for derived attributes
    source_attributes: Optional[List[str]]  # Attributes used in derivation
    
    # Constraints
    minimum_value: float  # Minimum possible value (usually 0)
    
    # Metadata
    display_name: Optional[str]  # Human-readable display name
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
            raise InvariantViolation("Attribute name cannot be empty")
        
        if self.base_value < 0:
            raise InvariantViolation("Base value cannot be negative")
        
        if self.current_value < self.minimum_value:
            raise InvariantViolation(
                f"Current value cannot be below minimum ({self.minimum_value})"
            )
        
        if self.maximum_value is not None and self.current_value > self.maximum_value:
            raise InvariantViolation(
                f"Current value cannot exceed maximum ({self.maximum_value})"
            )
        
        if self.is_derived and not self.derivation_formula:
            raise InvariantViolation(
                "Derived attribute must have a derivation formula"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        character_id: EntityId,
        name: str,
        description: Description,
        attribute_type: AttributeType,
        scale_type: AttributeScale,
        base_value: float,
        current_value: Optional[float] = None,
        maximum_value: Optional[float] = None,
        flat_bonus: float = 0.0,
        percentage_bonus: float = 0.0,
        temporary_bonus: Optional[float] = None,
        is_derived: bool = False,
        derivation_formula: Optional[str] = None,
        source_attributes: Optional[List[str]] = None,
        minimum_value: float = 0.0,
        display_name: Optional[str] = None,
        icon_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> 'Attribute':
        """
        Factory method for creating a new Attribute.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            name=name,
            description=description,
            attribute_type=attribute_type,
            scale_type=scale_type,
            base_value=base_value,
            current_value=current_value if current_value is not None else base_value,
            maximum_value=maximum_value,
            flat_bonus=flat_bonus,
            percentage_bonus=percentage_bonus,
            temporary_bonus=temporary_bonus,
            is_derived=is_derived,
            derivation_formula=derivation_formula,
            source_attributes=source_attributes,
            minimum_value=minimum_value,
            display_name=display_name or name.title(),
            icon_id=icon_id,
            tags=tags,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def recalculate(self) -> None:
        """Recalculate current value from base and modifiers."""
        calculated = self.base_value
        calculated += self.flat_bonus
        calculated *= (1.0 + self.percentage_bonus / 100.0)
        
        if self.temporary_bonus is not None:
            calculated += self.temporary_bonus
        
        # Apply constraints
        calculated = max(self.minimum_value, calculated)
        if self.maximum_value is not None:
            calculated = min(self.maximum_value, calculated)
        
        object.__setattr__(self, 'current_value', calculated)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_base_value(self, value: float) -> None:
        """Set the base value of the attribute."""
        if value < 0:
            raise InvariantViolation("Base value cannot be negative")
        
        if self.base_value == value:
            return
        
        object.__setattr__(self, 'base_value', value)
        self.recalculate()
    
    def add_flat_bonus(self, amount: float) -> None:
        """Add a flat bonus to the attribute."""
        if amount == 0:
            return
        
        object.__setattr__(self, 'flat_bonus', self.flat_bonus + amount)
        self.recalculate()
    
    def add_percentage_bonus(self, amount: float) -> None:
        """Add a percentage bonus to the attribute."""
        if amount == 0:
            return
        
        object.__setattr__(self, 'percentage_bonus', self.percentage_bonus + amount)
        self.recalculate()
    
    def set_temporary_bonus(self, amount: Optional[float]) -> None:
        """Set or clear temporary bonus."""
        if self.temporary_bonus == amount:
            return
        
        object.__setattr__(self, 'temporary_bonus', amount)
        self.recalculate()
    
    def get_total_bonus(self) -> float:
        """Get total bonus amount (flat + percentage of base)."""
        total = self.flat_bonus
        total += self.base_value * (self.percentage_bonus / 100.0)
        if self.temporary_bonus is not None:
            total += self.temporary_bonus
        return total
    
    def is_at_maximum(self) -> bool:
        """Check if attribute is at maximum value."""
        return self.maximum_value is not None and self.current_value >= self.maximum_value
    
    def is_at_minimum(self) -> bool:
        """Check if attribute is at minimum value."""
        return self.current_value <= self.minimum_value
    
    def get_percentage_of_max(self) -> Optional[float]:
        """Get current value as percentage of maximum."""
        if self.maximum_value is None:
            return None
        return (self.current_value / self.maximum_value) * 100.0
    
    def __str__(self) -> str:
        bonus = self.get_total_bonus()
        return f"Attribute({self.display_name or self.name}: {self.current_value} (+{bonus:.1f}))"
    
    def __repr__(self) -> str:
        return (
            f"Attribute(id={self.id}, character_id={self.character_id}, "
            f"name='{self.name}', type={self.attribute_type.value})"
        )
