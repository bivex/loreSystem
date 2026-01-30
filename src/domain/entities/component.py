"""
Component Entity

A Component represents a part used in crafting larger items.
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


class ComponentCategory(str, Enum):
    """Categories of components."""
    BLADE = "blade"
    HILT = "hilt"
    GUARD = "guard"
    POMMEL = "pommel"
    HANDLE = "handle"
    HEAD = "head"
    SHAFT = "shaft"
    SOCKET = "socket"
    BINDING = "binding"
    LENS = "lens"
    FRAME = "frame"
    CORE = "core"
    HOUSING = "housing"
    MECHANISM = "mechanism"
    WIRING = "wiring"
    PLATING = "plating"
    JOINT = "joint"
    OTHER = "other"


@dataclass
class Component:
    """
    Component entity for crafting parts.
    
    Invariants:
    - Name cannot be empty
    - Category must be set
    - Quality must be between 1-100
    - Must belong to a world
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    category: ComponentCategory
    rarity: Rarity
    
    # Quality attributes
    quality: int  # Quality score (1-100)
    durability: int  # Durability points
    max_durability: int  # Maximum durability
    
    # Component stats
    weight: float  # Weight in kg
    size: str  # Size category (small, medium, large, huge)
    
    # Crafting properties
    is_craftable: bool  # Can be crafted by players
    required_skill_id: Optional[EntityId]  # Skill needed to craft
    required_skill_level: Optional[int]  # Minimum skill level
    
    # Visual representation
    model_3d_id: Optional[EntityId]
    texture_ids: Optional[List[EntityId]]
    
    # Materials used in this component
    material_ids: List[EntityId]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Component name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Component name must be <= 255 characters")
        
        if self.quality < 1 or self.quality > 100:
            raise ValueError("Quality must be between 1-100")
        
        if self.durability < 0:
            raise ValueError("Durability cannot be negative")
        
        if self.max_durability < 1:
            raise ValueError("Max durability must be positive")
        
        if self.durability > self.max_durability:
            raise ValueError("Durability cannot exceed max durability")
        
        if self.weight < 0:
            raise ValueError("Weight cannot be negative")
        
        if self.required_skill_level is not None and self.required_skill_level <= 0:
            raise ValueError("Required skill level must be positive")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        category: ComponentCategory,
        rarity: Rarity,
        quality: int = 50,
        durability: int = 100,
        max_durability: int = 100,
        weight: float = 1.0,
        size: str = "medium",
        is_craftable: bool = True,
        required_skill_id: Optional[EntityId] = None,
        required_skill_level: Optional[int] = None,
        model_3d_id: Optional[EntityId] = None,
        texture_ids: Optional[List[EntityId]] = None,
        material_ids: Optional[List[EntityId]] = None,
    ) -> 'Component':
        """
        Factory method for creating a new Component.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            category=category,
            rarity=rarity,
            quality=quality,
            durability=durability,
            max_durability=max_durability,
            weight=weight,
            size=size,
            is_craftable=is_craftable,
            required_skill_id=required_skill_id,
            required_skill_level=required_skill_level,
            model_3d_id=model_3d_id,
            texture_ids=texture_ids or [],
            material_ids=material_ids or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def durability_percentage(self) -> float:
        """Get durability as a percentage."""
        return (self.durability / self.max_durability) * 100
    
    @property
    def is_broken(self) -> bool:
        """Check if component is broken."""
        return self.durability <= 0
    
    def update_description(self, new_description: Description) -> None:
        """Update component description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the component."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Component name cannot be empty")
        
        if len(new_name) > 255:
            raise ValueError("Component name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_category(self, new_category: ComponentCategory) -> None:
        """Change component category."""
        if self.category == new_category:
            return
        
        object.__setattr__(self, 'category', new_category)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_rarity(self, new_rarity: Rarity) -> None:
        """Set component rarity."""
        if self.rarity == new_rarity:
            return
        
        object.__setattr__(self, 'rarity', new_rarity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_quality(self, quality: int) -> None:
        """Set component quality."""
        if quality < 1 or quality > 100:
            raise ValueError("Quality must be between 1-100")
        
        object.__setattr__(self, 'quality', quality)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_max_durability(self, max_durability: int) -> None:
        """Set maximum durability."""
        if max_durability < 1:
            raise ValueError("Max durability must be positive")
        
        object.__setattr__(self, 'max_durability', max_durability)
        
        # Adjust current durability if needed
        if self.durability > max_durability:
            object.__setattr__(self, 'durability', max_durability)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def repair(self, amount: int) -> None:
        """Repair component by specified amount."""
        if amount < 0:
            raise ValueError("Repair amount cannot be negative")
        
        new_durability = min(self.durability + amount, self.max_durability)
        object.__setattr__(self, 'durability', new_durability)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def fully_repair(self) -> None:
        """Fully repair component."""
        if self.durability == self.max_durability:
            return
        
        object.__setattr__(self, 'durability', self.max_durability)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def damage(self, amount: int) -> None:
        """Apply damage to component."""
        if amount < 0:
            raise ValueError("Damage amount cannot be negative")
        
        new_durability = max(self.durability - amount, 0)
        object.__setattr__(self, 'durability', new_durability)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_weight(self, weight: float) -> None:
        """Set component weight."""
        if weight < 0:
            raise ValueError("Weight cannot be negative")
        
        object.__setattr__(self, 'weight', weight)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_size(self, size: str) -> None:
        """Set component size."""
        valid_sizes = ["tiny", "small", "medium", "large", "huge", "colossal"]
        if size.lower() not in valid_sizes:
            raise ValueError(f"Size must be one of: {', '.join(valid_sizes)}")
        
        object.__setattr__(self, 'size', size.lower())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_material(self, material_id: EntityId) -> None:
        """Add a material to the component."""
        if material_id in self.material_ids:
            return
        
        self.material_ids.append(material_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_material(self, material_id: EntityId) -> bool:
        """
        Remove a material from the component.
        
        Returns:
            True if material was removed, False if not found.
        """
        if material_id in self.material_ids:
            self.material_ids.remove(material_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
            return True
        
        return False
    
    def calculate_effectiveness(self) -> float:
        """
        Calculate component effectiveness based on quality and durability.
        """
        quality_factor = self.quality / 100.0
        durability_factor = self.durability_percentage / 100.0
        return quality_factor * durability_factor
    
    def can_craft(self, skill_level: Optional[int] = None) -> bool:
        """Check if component can be crafted with given skill level."""
        if not self.is_craftable:
            return False
        
        if self.required_skill_level is not None:
            if skill_level is None or skill_level < self.required_skill_level:
                return False
        
        return True
    
    def __str__(self) -> str:
        return f"Component({self.name}, {self.category.value}, {self.rarity.value}, Q{self.quality})"
    
    def __repr__(self) -> str:
        return (
            f"Component(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', category={self.category}, quality={self.quality})"
        )
