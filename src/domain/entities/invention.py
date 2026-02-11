"""
Invention Entity

Invention represents created technologies, devices, or innovations within the game world.
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


class InventionCategory(str, Enum):
    """Categories of inventions."""
    WEAPON = "weapon"
    ARMOR = "armor"
    TOOL = "tool"
    VEHICLE = "vehicle"
    MACHINE = "machine"
    DEVICE = "device"
    GADGET = "gadget"
    STRUCTURE = "structure"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    OTHER = "other"


class InventionStatus(str, Enum):
    """Status of invention development."""
    CONCEPT = "concept"
    PROTOTYPE = "prototype"
    PRODUCTION = "production"
    OBSOLETE = "obsolete"
    LOST = "lost"


@dataclass
class Invention:
    """
    Invention entity for tracking innovations and technological advances.
    
    Invariants:
    - Name cannot be empty
    - Category must be set
    - Must belong to a world
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    category: InventionCategory
    status: InventionStatus
    rarity: Rarity
    
    # Creator information
    inventor_id: Optional[EntityId]  # Character who invented it
    faction_id: Optional[EntityId]  # Faction that developed it
    invented_at: Optional[Timestamp]
    
    # Technical details
    complexity: int  # 1-10
    durability: int  # 1-100
    efficiency: int  # 1-100
    
    # Production
    production_cost_gold: int
    production_cost_resources: dict  # Resource ID -> quantity
    production_time: int  # Seconds
    
    # Usage
    max_uses: Optional[int]  # None = unlimited
    cooldown_time: int  # Seconds
    
    # Variants
    base_invention_id: Optional[EntityId]
    variant_names: List[str]
    
    # Effects and abilities
    effect_description: Optional[str]
    ability_ids: List[EntityId]  # Abilities granted by this invention
    
    # Market
    is_tradable: bool
    base_value: int
    
    # Restrictions
    required_level: Optional[int]
    required_skill_id: Optional[EntityId]
    required_skill_level: Optional[int]
    
    # Visuals
    icon_id: Optional[EntityId]
    model_id: Optional[EntityId]
    
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
            raise ValueError("Invention name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Invention name must be <= 255 characters")
        
        if self.complexity < 1 or self.complexity > 10:
            raise ValueError("Complexity must be between 1-10")
        
        if self.durability < 1 or self.durability > 100:
            raise ValueError("Durability must be between 1-100")
        
        if self.efficiency < 1 or self.efficiency > 100:
            raise ValueError("Efficiency must be between 1-100")
        
        if self.production_cost_gold < 0:
            raise ValueError("Production cost gold cannot be negative")
        
        if self.production_time < 0:
            raise ValueError("Production time cannot be negative")
        
        if self.max_uses is not None and self.max_uses < 1:
            raise ValueError("Max uses must be positive")
        
        if self.cooldown_time < 0:
            raise ValueError("Cooldown time cannot be negative")
        
        if self.base_value < 0:
            raise ValueError("Base value cannot be negative")
        
        if self.required_level is not None and self.required_level < 1:
            raise ValueError("Required level must be positive")
        
        if self.required_skill_level is not None and self.required_skill_level < 1:
            raise ValueError("Required skill level must be positive")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        category: InventionCategory,
        rarity: Rarity,
        complexity: int = 1,
        durability: int = 100,
        efficiency: int = 50,
        production_cost_gold: int = 0,
        production_cost_resources: Optional[dict] = None,
        production_time: int = 0,
        max_uses: Optional[int] = None,
        cooldown_time: int = 0,
        inventor_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        effect_description: Optional[str] = None,
        ability_ids: Optional[List[EntityId]] = None,
        is_tradable: bool = True,
        base_value: int = 0,
        required_level: Optional[int] = None,
        required_skill_id: Optional[EntityId] = None,
        required_skill_level: Optional[int] = None,
        icon_id: Optional[EntityId] = None,
        model_id: Optional[EntityId] = None,
    ) -> 'Invention':
        """
        Factory method for creating a new Invention.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            category=category,
            status=InventionStatus.PROTOTYPE,
            rarity=rarity,
            inventor_id=inventor_id,
            faction_id=faction_id,
            invented_at=None,
            complexity=complexity,
            durability=durability,
            efficiency=efficiency,
            production_cost_gold=production_cost_gold,
            production_cost_resources=production_cost_resources or {},
            production_time=production_time,
            max_uses=max_uses,
            cooldown_time=cooldown_time,
            base_invention_id=None,
            variant_names=[],
            effect_description=effect_description,
            ability_ids=ability_ids or [],
            is_tradable=is_tradable,
            base_value=base_value,
            required_level=required_level,
            required_skill_id=required_skill_id,
            required_skill_level=required_skill_level,
            icon_id=icon_id,
            model_id=model_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def is_variant(self) -> bool:
        """Check if this is a variant of another invention."""
        return self.base_invention_id is not None
    
    @property
    def in_production(self) -> bool:
        """Check if invention is in production status."""
        return self.status == InventionStatus.PRODUCTION
    
    @property
    def is_obsolete(self) -> bool:
        """Check if invention is obsolete."""
        return self.status == InventionStatus.OBSOLETE
    
    def complete_invention(self) -> None:
        """Mark invention as invented."""
        if self.status != InventionStatus.PROTOTYPE:
            raise ValueError("Can only complete prototype inventions")
        
        now = Timestamp.now()
        object.__setattr__(self, 'status', InventionStatus.PRODUCTION)
        object.__setattr__(self, 'invented_at', now)
        object.__setattr__(self, 'updated_at', now)
        object.__setattr__(self, 'version', self.version.increment())
    
    def mark_obsolete(self) -> None:
        """Mark invention as obsolete."""
        if self.status == InventionStatus.OBSOLETE:
            return
        
        object.__setattr__(self, 'status', InventionStatus.OBSOLETE)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def mark_lost(self) -> None:
        """Mark invention as lost technology."""
        if self.status == InventionStatus.LOST:
            return
        
        object.__setattr__(self, 'status', InventionStatus.LOST)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_durability(self, value: int) -> None:
        """Set invention durability."""
        if value < 1 or value > 100:
            raise ValueError("Durability must be between 1-100")
        
        object.__setattr__(self, 'durability', value)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_efficiency(self, value: int) -> None:
        """Set invention efficiency."""
        if value < 1 or value > 100:
            raise ValueError("Efficiency must be between 1-100")
        
        object.__setattr__(self, 'efficiency', value)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_ability(self, ability_id: EntityId) -> None:
        """Add an ability to the invention."""
        if ability_id not in self.ability_ids:
            self.ability_ids.append(ability_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def remove_ability(self, ability_id: EntityId) -> bool:
        """Remove an ability from the invention."""
        if ability_id in self.ability_ids:
            self.ability_ids.remove(ability_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
            return True
        return False
    
    def can_use(self, player_level: int, skill_levels: Optional[dict] = None) -> bool:
        """Check if player can use this invention."""
        if self.required_level is not None and player_level < self.required_level:
            return False
        
        if self.required_skill_id is not None:
            if skill_levels is None:
                return False
            if self.required_skill_id not in skill_levels:
                return False
            if skill_levels[self.required_skill_id] < self.required_skill_level:
                return False
        
        return True
    
    def __str__(self) -> str:
        return f"Invention({self.name}, {self.category.value}, {self.status.value})"
    
    def __repr__(self) -> str:
        return (
            f"Invention(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', category={self.category}, status={self.status})"
        )
