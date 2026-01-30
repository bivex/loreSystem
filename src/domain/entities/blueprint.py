"""
Blueprint Entity

A Blueprint represents a schematic or plan for crafting items.
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


class BlueprintType(str, Enum):
    """Types of blueprints."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    TOOL = "tool"
    FURNITURE = "furniture"
    STRUCTURE = "structure"
    VEHICLE = "vehicle"
    MACHINE = "machine"
    CONSUMABLE = "consumable"
    SCROLL = "scroll"
    GEM = "gem"
    ENCHANTMENT = "enchantment"
    OTHER = "other"


@dataclass
class BlueprintRequirement:
    """A requirement for using a blueprint."""
    requirement_type: str  # "level", "skill", "quest", etc.
    value: str  # The specific requirement value
    quantity: Optional[int]  # If applicable
    
    def __post_init__(self):
        if not self.requirement_type or len(self.requirement_type.strip()) == 0:
            raise ValueError("Requirement type cannot be empty")
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Requirement value cannot be empty")


@dataclass
class Blueprint:
    """
    Blueprint entity for crafting schematics.
    
    Invariants:
    - Name cannot be empty
    - Blueprint type must be set
    - Complexity must be between 1-10
    - Must belong to a world
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    blueprint_type: BlueprintType
    rarity: Rarity
    
    # Crafting difficulty
    complexity: int  # Complexity level (1-10)
    estimated_crafting_time: int  # Seconds
    
    # Requirements to use blueprint
    requirements: List[BlueprintRequirement]
    required_level: Optional[int]
    required_skill_id: Optional[EntityId]
    required_skill_level: Optional[int]
    
    # Output
    result_item_id: EntityId
    result_quantity: int
    
    # Variants and upgrades
    variant_of_id: Optional[EntityId]  # Parent blueprint if this is a variant
    upgrade_tier: int  # Upgrade tier (1 = base)
    max_upgrade_tier: int
    
    # Discovery and acquisition
    is_discoverable: bool
    discovery_chance: float  # 0.0 - 1.0
    discovery_source_ids: List[EntityId]  # Quests, locations, NPCs where it can be found
    
    # Visual representation
    icon_id: Optional[EntityId]
    texture_id: Optional[EntityId]
    
    # Economic properties
    is_tradable: bool
    base_value: int
    
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
            raise ValueError("Blueprint name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Blueprint name must be <= 255 characters")
        
        if self.complexity < 1 or self.complexity > 10:
            raise ValueError("Complexity must be between 1-10")
        
        if self.estimated_crafting_time < 0:
            raise ValueError("Estimated crafting time cannot be negative")
        
        if self.result_quantity <= 0:
            raise ValueError("Result quantity must be positive")
        
        if self.upgrade_tier < 1:
            raise ValueError("Upgrade tier must be >= 1")
        
        if self.max_upgrade_tier < 1:
            raise ValueError("Max upgrade tier must be >= 1")
        
        if self.upgrade_tier > self.max_upgrade_tier:
            raise ValueError("Upgrade tier cannot exceed max upgrade tier")
        
        if self.discovery_chance < 0.0 or self.discovery_chance > 1.0:
            raise ValueError("Discovery chance must be between 0.0-1.0")
        
        if self.required_level is not None and self.required_level < 1:
            raise ValueError("Required level must be positive")
        
        if self.required_skill_level is not None and self.required_skill_level < 1:
            raise ValueError("Required skill level must be positive")
        
        if self.base_value < 0:
            raise ValueError("Base value cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        blueprint_type: BlueprintType,
        rarity: Rarity,
        result_item_id: EntityId,
        result_quantity: int = 1,
        complexity: int = 1,
        estimated_crafting_time: int = 0,
        requirements: Optional[List[BlueprintRequirement]] = None,
        required_level: Optional[int] = None,
        required_skill_id: Optional[EntityId] = None,
        required_skill_level: Optional[int] = None,
        variant_of_id: Optional[EntityId] = None,
        upgrade_tier: int = 1,
        max_upgrade_tier: int = 1,
        is_discoverable: bool = True,
        discovery_chance: float = 0.0,
        discovery_source_ids: Optional[List[EntityId]] = None,
        icon_id: Optional[EntityId] = None,
        texture_id: Optional[EntityId] = None,
        is_tradable: bool = True,
        base_value: int = 0,
    ) -> 'Blueprint':
        """
        Factory method for creating a new Blueprint.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            blueprint_type=blueprint_type,
            rarity=rarity,
            complexity=complexity,
            estimated_crafting_time=estimated_crafting_time,
            requirements=requirements or [],
            required_level=required_level,
            required_skill_id=required_skill_id,
            required_skill_level=required_skill_level,
            result_item_id=result_item_id,
            result_quantity=result_quantity,
            variant_of_id=variant_of_id,
            upgrade_tier=upgrade_tier,
            max_upgrade_tier=max_upgrade_tier,
            is_discoverable=is_discoverable,
            discovery_chance=discovery_chance,
            discovery_source_ids=discovery_source_ids or [],
            icon_id=icon_id,
            texture_id=texture_id,
            is_tradable=is_tradable,
            base_value=base_value,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def is_max_tier(self) -> bool:
        """Check if this is the maximum upgrade tier."""
        return self.upgrade_tier >= self.max_upgrade_tier
    
    @property
    def is_variant(self) -> bool:
        """Check if this is a variant of another blueprint."""
        return self.variant_of_id is not None
    
    def update_description(self, new_description: Description) -> None:
        """Update blueprint description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the blueprint."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Blueprint name cannot be empty")
        
        if len(new_name) > 255:
            raise ValueError("Blueprint name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_complexity(self, complexity: int) -> None:
        """Set blueprint complexity."""
        if complexity < 1 or complexity > 10:
            raise ValueError("Complexity must be between 1-10")
        
        object.__setattr__(self, 'complexity', complexity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_rarity(self, new_rarity: Rarity) -> None:
        """Set blueprint rarity."""
        if self.rarity == new_rarity:
            return
        
        object.__setattr__(self, 'rarity', new_rarity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_result_item(self, item_id: EntityId, quantity: int = 1) -> None:
        """Set the result item and quantity."""
        if quantity <= 0:
            raise ValueError("Result quantity must be positive")
        
        object.__setattr__(self, 'result_item_id', item_id)
        object.__setattr__(self, 'result_quantity', quantity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_crafting_time(self, seconds: int) -> None:
        """Set the estimated crafting time."""
        if seconds < 0:
            raise ValueError("Estimated crafting time cannot be negative")
        
        object.__setattr__(self, 'estimated_crafting_time', seconds)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_requirement(self, requirement: BlueprintRequirement) -> None:
        """Add a requirement to the blueprint."""
        self.requirements.append(requirement)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_requirement(self, requirement_type: str, value: str) -> bool:
        """
        Remove a requirement from the blueprint.
        
        Returns:
            True if requirement was removed, False if not found.
        """
        for i, req in enumerate(self.requirements):
            if req.requirement_type == requirement_type and req.value == value:
                self.requirements.pop(i)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False
    
    def add_discovery_source(self, source_id: EntityId) -> None:
        """Add a discovery source (quest, location, etc.)."""
        if source_id in self.discovery_source_ids:
            return
        
        self.discovery_source_ids.append(source_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_discovery_source(self, source_id: EntityId) -> bool:
        """
        Remove a discovery source.
        
        Returns:
            True if source was removed, False if not found.
        """
        if source_id in self.discovery_source_ids:
            self.discovery_source_ids.remove(source_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
            return True
        
        return False
    
    def set_discovery_chance(self, chance: float) -> None:
        """Set the discovery chance (0.0 - 1.0)."""
        if chance < 0.0 or chance > 1.0:
            raise ValueError("Discovery chance must be between 0.0-1.0")
        
        object.__setattr__(self, 'discovery_chance', chance)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def can_upgrade(self) -> bool:
        """Check if blueprint can be upgraded further."""
        return not self.is_max_tier
    
    def upgrade(self) -> None:
        """Upgrade blueprint to next tier."""
        if not self.can_upgrade():
            raise ValueError("Blueprint is already at max tier")
        
        object.__setattr__(self, 'upgrade_tier', self.upgrade_tier + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def can_use(self, player_level: int, skill_levels: Optional[dict] = None) -> bool:
        """
        Check if blueprint can be used by player.
        
        Args:
            player_level: Player's current level
            skill_levels: Mapping of skill_id -> skill_level
        
        Returns:
            True if blueprint can be used.
        """
        # Check level requirement
        if self.required_level is not None and player_level < self.required_level:
            return False
        
        # Check skill requirement
        if self.required_skill_id is not None:
            if skill_levels is None:
                return False
            if self.required_skill_id not in skill_levels:
                return False
            if skill_levels[self.required_skill_id] < self.required_skill_level:
                return False
        
        return True
    
    def calculate_crafting_difficulty_modifier(self) -> float:
        """
        Calculate difficulty modifier based on complexity and rarity.
        """
        base_modifier = 1.0
        
        # Complexity bonus
        base_modifier += (self.complexity - 5) * 0.1
        
        # Rarity bonus
        rarity_bonus = {
            Rarity.COMMON: 0.0,
            Rarity.UNCOMMON: 0.2,
            Rarity.RARE: 0.5,
            Rarity.EPIC: 1.0,
            Rarity.LEGENDARY: 1.5,
        }
        base_modifier += rarity_bonus.get(self.rarity, 0.0)
        
        return max(0.5, base_modifier)
    
    def __str__(self) -> str:
        tier_str = f" T{self.upgrade_tier}" if self.upgrade_tier > 1 else ""
        return f"Blueprint({self.name}{tier_str}, {self.rarity.value}, complexity {self.complexity})"
    
    def __repr__(self) -> str:
        return (
            f"Blueprint(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.blueprint_type}, tier={self.upgrade_tier})"
        )
