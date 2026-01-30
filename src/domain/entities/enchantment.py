"""
Enchantment Entity

An Enchantment represents magical properties that can be applied to items.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    Rarity,
)


class EnchantmentType(str, Enum):
    """Types of enchantments."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    SHIELD = "shield"
    HELMET = "helmet"
    CHEST = "chest"
    GLOVES = "gloves"
    BOOTS = "boots"
    RING = "ring"
    AMULET = "amulet"
    BELT = "belt"
    CLOAK = "cloak"
    GENERAL = "general"
    CURSE = "curse"


class EnchantmentEffect(str, Enum):
    """Types of enchantment effects."""
    # Offensive
    ATTACK_POWER = "attack_power"
    CRITICAL_RATE = "critical_rate"
    CRITICAL_DAMAGE = "critical_damage"
    ATTACK_SPEED = "attack_speed"
    ELEMENTAL_DAMAGE = "elemental_damage"
    LIFESTEAL = "lifesteal"
    
    # Defensive
    DEFENSE = "defense"
    MAGIC_RESISTANCE = "magic_resistance"
    HEALTH = "health"
    HEALTH_REGEN = "health_regen"
    DODGE_RATE = "dodge_rate"
    BLOCK_RATE = "block_rate"
    DAMAGE_REDUCTION = "damage_reduction"
    
    # Utility
    MOVEMENT_SPEED = "movement_speed"
    JUMP_HEIGHT = "jump_height"
    CARRY_CAPACITY = "carry_capacity"
    LUCK = "luck"
    GOLD_FIND = "gold_find"
    ITEM_FIND = "item_find"
    EXPERIENCE_GAIN = "experience_gain"
    
    # Magic
    MANA = "mana"
    MANA_REGEN = "mana_regen"
    COOLDOWN_REDUCTION = "cooldown_reduction"
    CAST_SPEED = "cast_speed"
    SPELL_POWER = "spell_power"
    SPELL_DURATION = "spell_duration"
    
    # Special
    PROTECTION = "protection"
    THORNS = "thorns"
    VAMPIRISM = "vampirism"
    TELEPORT = "teleport"
    INVISIBILITY = "invisibility"
    FLIGHT = "flight"
    UNDERWATER_BREATHING = "underwater_breathing"
    
    # Curses
    WEAKNESS = "weakness"
    SLOWNESS = "slowness"
    FRAILTY = "frailty"
    DOOM = "doom"


@dataclass
class EnchantmentEffectValue:
    """Represents an effect and its value."""
    effect: EnchantmentEffect
    value: float
    is_percentage: bool  # True if value is a percentage
    
    def __post_init__(self):
        if self.is_percentage and (self.value < -100 or self.value > 100):
            raise ValueError("Percentage value must be between -100 and 100")
    
    def __str__(self) -> str:
        suffix = "%" if self.is_percentage else ""
        return f"{self.effect.value} {self.value:+g}{suffix}"


@dataclass
class Enchantment:
    """
    Enchantment entity for magical item properties.
    
    Invariants:
    - Name cannot be empty
    - Enchantment type must be set
    - Must have at least one effect
    - Power level must be between 1-10
    - Maximum stacks must be positive
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    enchantment_type: EnchantmentType
    rarity: Rarity
    
    # Power and scaling
    power_level: int  # Power level (1-10)
    max_stacks: int  # Maximum stacks of this enchantment
    
    # Effects
    effects: List[EnchantmentEffectValue]
    
    # Requirements
    required_item_level: Optional[int]
    required_item_rarity: Optional[Rarity]
    mutually_exclusive_ids: List[EntityId]  # Enchantments that cannot coexist
    
    # Application properties
    is_cursed: bool
    is_permanent: bool  # False = temporary enchantment
    duration_seconds: Optional[int]  # Duration for temporary enchantments
    
    # Cost to apply
    required_material_ids: List[EntityId]
    required_gold: int
    required_skill_id: Optional[EntityId]
    required_skill_level: Optional[int]
    
    # Visual effects
    glow_color: Optional[str]  # Hex color code
    particle_effect_id: Optional[EntityId]
    
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
            raise ValueError("Enchantment name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Enchantment name must be <= 255 characters")
        
        if self.power_level < 1 or self.power_level > 10:
            raise ValueError("Power level must be between 1-10")
        
        if self.max_stacks < 1:
            raise ValueError("Max stacks must be positive")
        
        if not self.effects or len(self.effects) == 0:
            raise ValueError("Enchantment must have at least one effect")
        
        if self.required_item_level is not None and self.required_item_level < 1:
            raise ValueError("Required item level must be positive")
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("Duration cannot be negative")
        
        if self.required_gold < 0:
            raise ValueError("Required gold cannot be negative")
        
        if self.required_skill_level is not None and self.required_skill_level < 1:
            raise ValueError("Required skill level must be positive")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        enchantment_type: EnchantmentType,
        rarity: Rarity,
        effects: List[EnchantmentEffectValue],
        power_level: int = 1,
        max_stacks: int = 1,
        required_item_level: Optional[int] = None,
        required_item_rarity: Optional[Rarity] = None,
        mutually_exclusive_ids: Optional[List[EntityId]] = None,
        is_cursed: bool = False,
        is_permanent: bool = True,
        duration_seconds: Optional[int] = None,
        required_material_ids: Optional[List[EntityId]] = None,
        required_gold: int = 0,
        required_skill_id: Optional[EntityId] = None,
        required_skill_level: Optional[int] = None,
        glow_color: Optional[str] = None,
        particle_effect_id: Optional[EntityId] = None,
    ) -> 'Enchantment':
        """
        Factory method for creating a new Enchantment.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            enchantment_type=enchantment_type,
            rarity=rarity,
            power_level=power_level,
            max_stacks=max_stacks,
            effects=effects,
            required_item_level=required_item_level,
            required_item_rarity=required_item_rarity,
            mutually_exclusive_ids=mutually_exclusive_ids or [],
            is_cursed=is_cursed,
            is_permanent=is_permanent,
            duration_seconds=duration_seconds,
            required_material_ids=required_material_ids or [],
            required_gold=required_gold,
            required_skill_id=required_skill_id,
            required_skill_level=required_skill_level,
            glow_color=glow_color,
            particle_effect_id=particle_effect_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update enchantment description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the enchantment."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Enchantment name cannot be empty")
        
        if len(new_name) > 255:
            raise ValueError("Enchantment name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_rarity(self, new_rarity: Rarity) -> None:
        """Set enchantment rarity."""
        if self.rarity == new_rarity:
            return
        
        object.__setattr__(self, 'rarity', new_rarity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_power_level(self, level: int) -> None:
        """Set power level."""
        if level < 1 or level > 10:
            raise ValueError("Power level must be between 1-10")
        
        object.__setattr__(self, 'power_level', level)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_effect(self, effect: EnchantmentEffectValue) -> None:
        """Add an effect to the enchantment."""
        self.effects.append(effect)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_effect(self, effect: EnchantmentEffect) -> bool:
        """
        Remove an effect from the enchantment.
        
        Returns:
            True if effect was removed, False if not found.
        """
        for i, effect_value in enumerate(self.effects):
            if effect_value.effect == effect:
                self.effects.pop(i)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False
    
    def add_mutually_exclusive(self, enchantment_id: EntityId) -> None:
        """Add an enchantment that is mutually exclusive with this one."""
        if enchantment_id in self.mutually_exclusive_ids:
            return
        
        self.mutually_exclusive_ids.append(enchantment_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_mutually_exclusive(self, enchantment_id: EntityId) -> bool:
        """
        Remove a mutually exclusive enchantment.
        
        Returns:
            True if enchantment was removed, False if not found.
        """
        if enchantment_id in self.mutually_exclusive_ids:
            self.mutually_exclusive_ids.remove(enchantment_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
            return True
        
        return False
    
    def is_compatible_with(self, enchantment_id: EntityId) -> bool:
        """Check if this enchantment is compatible with another."""
        return enchantment_id not in self.mutually_exclusive_ids
    
    def can_apply_to_item(self, item_level: int, item_rarity: Rarity) -> bool:
        """Check if enchantment can be applied to an item."""
        if self.required_item_level is not None and item_level < self.required_item_level:
            return False
        
        if self.required_item_rarity is not None:
            rarity_order = [Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE, Rarity.EPIC, Rarity.LEGENDARY]
            if rarity_order.index(item_rarity) < rarity_order.index(self.required_item_rarity):
                return False
        
        return True
    
    def calculate_total_effect(self, effect: EnchantmentEffect, stacks: int = 1) -> Optional[float]:
        """
        Calculate total value for a specific effect with given stacks.
        
        Returns:
            Total effect value, or None if effect doesn't exist.
        """
        stacks = min(max(stacks, 1), self.max_stacks)
        
        for effect_value in self.effects:
            if effect_value.effect == effect:
                return effect_value.value * stacks
        
        return None
    
    def get_all_effect_values(self, stacks: int = 1) -> Dict[EnchantmentEffect, float]:
        """
        Get all effect values with given stacks.
        
        Returns:
            Dictionary mapping effects to their total values.
        """
        stacks = min(max(stacks, 1), self.max_stacks)
        return {effect_value.effect: effect_value.value * stacks for effect_value in self.effects}
    
    def set_duration(self, seconds: Optional[int]) -> None:
        """Set duration for temporary enchantments (None for permanent)."""
        if seconds is not None and seconds < 0:
            raise ValueError("Duration cannot be negative")
        
        object.__setattr__(self, 'duration_seconds', seconds)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_glow_color(self, color: Optional[str]) -> None:
        """Set the glow color (hex color code)."""
        if color is not None and not color.startswith("#"):
            color = f"#{color}"
        
        object.__setattr__(self, 'glow_color', color)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        cursed_str = " [CURSE]" if self.is_cursed else ""
        effects_str = ", ".join(str(e) for e in self.effects[:3])
        return f"Enchantment({self.name}{cursed_str}, {effects_str})"
    
    def __repr__(self) -> str:
        return (
            f"Enchantment(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.enchantment_type}, power={self.power_level})"
        )
