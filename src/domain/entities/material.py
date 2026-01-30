"""
Material Entity

A Material represents a resource used in crafting and upgrading.
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
    Rarity,
)


class MaterialType(str, Enum):
    """Types of crafting materials."""
    ORE = "ore"
    GEM = "gem"
    HERB = "herb"
    WOOD = "wood"
    LEATHER = "leather"
    CLOTH = "cloth"
    ESSENCE = "essence"
    CRYSTAL = "crystal"
    BONE = "bone"
    SCALE = "scale"
    INGOT = "ingot"
    PLATE = "plate"
    THREAD = "thread"
    DUST = "dust"
    SHARD = "shard"
    FRAGMENT = "fragment"
    OTHER = "other"


@dataclass
class Material:
    """
    Material entity for crafting resources.
    
    Invariants:
    - Name cannot be empty
    - Rarity must be set
    - Stack size must be positive (for stackable materials)
    - Material type must be valid
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    material_type: MaterialType
    rarity: Rarity
    stack_size: int  # Maximum quantity per stack
    
    # Visual representation
    icon_id: Optional[EntityId]
    texture_id: Optional[EntityId]
    model_3d_id: Optional[EntityId]
    
    # Economic properties
    base_value: int  # Base gold value per unit
    is_tradeable: bool
    is_sellable: bool
    
    # Material properties
    durability: Optional[int]  # For materials that degrade
    conductivity: Optional[int]  # For magic-related materials
    hardness: Optional[int]  # For crafting quality
    magic_affinity: Optional[str]  # Element or school of magic
    
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
            raise ValueError("Material name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Material name must be <= 255 characters")
        
        if self.stack_size <= 0:
            raise ValueError("Stack size must be positive")
        
        if self.base_value < 0:
            raise ValueError("Base value cannot be negative")
        
        if self.durability is not None and self.durability < 0:
            raise ValueError("Durability cannot be negative")
        
        if self.conductivity is not None and (self.conductivity < 0 or self.conductivity > 100):
            raise ValueError("Conductivity must be between 0-100")
        
        if self.hardness is not None and (self.hardness < 0 or self.hardness > 100):
            raise ValueError("Hardness must be between 0-100")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        material_type: MaterialType,
        rarity: Rarity,
        stack_size: int = 99,
        icon_id: Optional[EntityId] = None,
        texture_id: Optional[EntityId] = None,
        model_3d_id: Optional[EntityId] = None,
        base_value: int = 0,
        is_tradeable: bool = True,
        is_sellable: bool = True,
        durability: Optional[int] = None,
        conductivity: Optional[int] = None,
        hardness: Optional[int] = None,
        magic_affinity: Optional[str] = None,
    ) -> 'Material':
        """
        Factory method for creating a new Material.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            material_type=material_type,
            rarity=rarity,
            stack_size=stack_size,
            icon_id=icon_id,
            texture_id=texture_id,
            model_3d_id=model_3d_id,
            base_value=base_value,
            is_tradeable=is_tradeable,
            is_sellable=is_sellable,
            durability=durability,
            conductivity=conductivity,
            hardness=hardness,
            magic_affinity=magic_affinity,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update material description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the material."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Material name cannot be empty")
        
        if len(new_name) > 255:
            raise ValueError("Material name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_type(self, new_type: MaterialType) -> None:
        """Change material type."""
        if self.material_type == new_type:
            return
        
        object.__setattr__(self, 'material_type', new_type)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_rarity(self, new_rarity: Rarity) -> None:
        """Set material rarity."""
        if self.rarity == new_rarity:
            return
        
        object.__setattr__(self, 'rarity', new_rarity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_stack_size(self, size: int) -> None:
        """Set the stack size."""
        if size <= 0:
            raise ValueError("Stack size must be positive")
        
        object.__setattr__(self, 'stack_size', size)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_base_value(self, value: int) -> None:
        """Set the base gold value."""
        if value < 0:
            raise ValueError("Base value cannot be negative")
        
        object.__setattr__(self, 'base_value', value)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_tradeable(self, tradeable: bool) -> None:
        """Set whether the material is tradeable."""
        if self.is_tradeable == tradeable:
            return
        
        object.__setattr__(self, 'is_tradeable', tradeable)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_sellable(self, sellable: bool) -> None:
        """Set whether the material is sellable."""
        if self.is_sellable == sellable:
            return
        
        object.__setattr__(self, 'is_sellable', sellable)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_properties(
        self,
        durability: Optional[int] = None,
        conductivity: Optional[int] = None,
        hardness: Optional[int] = None,
        magic_affinity: Optional[str] = None,
    ) -> None:
        """Update material properties."""
        changed = False
        
        if durability is not None and durability != self.durability:
            if durability < 0:
                raise ValueError("Durability cannot be negative")
            object.__setattr__(self, 'durability', durability)
            changed = True
        
        if conductivity is not None and conductivity != self.conductivity:
            if conductivity < 0 or conductivity > 100:
                raise ValueError("Conductivity must be between 0-100")
            object.__setattr__(self, 'conductivity', conductivity)
            changed = True
        
        if hardness is not None and hardness != self.hardness:
            if hardness < 0 or hardness > 100:
                raise ValueError("Hardness must be between 0-100")
            object.__setattr__(self, 'hardness', hardness)
            changed = True
        
        if magic_affinity is not None and magic_affinity != self.magic_affinity:
            object.__setattr__(self, 'magic_affinity', magic_affinity)
            changed = True
        
        if changed:
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def calculate_quality_multiplier(self) -> float:
        """
        Calculate quality multiplier based on material properties.
        Higher hardness and conductivity can improve crafting quality.
        """
        multiplier = 1.0
        
        if self.hardness is not None:
            multiplier += (self.hardness - 50) / 100.0
        
        if self.conductivity is not None:
            multiplier += (self.conductivity - 50) / 200.0
        
        # Rarity bonus
        rarity_bonus = {
            Rarity.COMMON: 0.0,
            Rarity.UNCOMMON: 0.1,
            Rarity.RARE: 0.25,
            Rarity.EPIC: 0.5,
            Rarity.LEGENDARY: 1.0,
        }
        multiplier += rarity_bonus.get(self.rarity, 0.0)
        
        return max(0.5, min(2.0, multiplier))
    
    def __str__(self) -> str:
        return f"Material({self.name}, {self.rarity.value}, {self.material_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Material(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.material_type}, rarity={self.rarity})"
        )
