"""
Rune Entity

A Rune represents a magical rune that can be inserted into sockets.
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


class RuneType(str, Enum):
    """Types of runes."""
    ELEMENTAL = "elemental"  # Fire, ice, lightning, etc.
    PROTECTIVE = "protective"  # Defense and resistance
    OFFENSIVE = "offensive"  # Attack and damage
    UTILITY = "utility"  # Movement, luck, etc.
    MYSTICAL = "mystical"  # Magic and mana
    CURSED = "cursed"  # Negative effects
    ANCIENT = "ancient"  # Powerful old magic
    DIVINE = "divine"  # Holy magic
    ABYSSAL = "abyssal"  # Dark magic


class RuneRank(str, Enum):
    """Rank tiers for runes."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    ANCIENT = "ancient"
    PRIME = "prime"


@dataclass
class RuneBonus:
    """Represents a bonus stat provided by a rune."""
    stat_name: str  # e.g., "attack_power", "fire_resistance"
    value: float
    is_percentage: bool  # True if value is a percentage
    
    def __post_init__(self):
        if self.is_percentage and (self.value < -100 or self.value > 100):
            raise ValueError("Percentage value must be between -100 and 100")
    
    def __str__(self) -> str:
        suffix = "%" if self.is_percentage else ""
        return f"{self.stat_name} {self.value:+g}{suffix}"


@dataclass
class RuneEffect:
    """Represents a special effect provided by a rune."""
    effect_name: str  # e.g., "on_hit_fire_damage", "on_block_thorns"
    effect_value: float  # Magnitude of the effect
    trigger_chance: Optional[float]  # Chance to trigger (0.0-1.0)
    cooldown_seconds: Optional[int]  # Cooldown between triggers
    
    def __post_init__(self):
        if self.trigger_chance is not None and (self.trigger_chance < 0.0 or self.trigger_chance > 1.0):
            raise ValueError("Trigger chance must be between 0.0-1.0")
        
        if self.cooldown_seconds is not None and self.cooldown_seconds < 0:
            raise ValueError("Cooldown cannot be negative")
    
    def __str__(self) -> str:
        parts = [self.effect_name, f"value={self.effect_value}"]
        if self.trigger_chance is not None:
            parts.append(f"chance={self.trigger_chance * 100:.0f}%")
        if self.cooldown_seconds is not None:
            parts.append(f"cd={self.cooldown_seconds}s")
        return ", ".join(parts)


@dataclass
class Rune:
    """
    Rune entity for magical socket items.
    
    Invariants:
    - Name cannot be empty
    - Rune type must be set
    - Rune rank must be set
    - Level must be between 1-10
    - Must have at least one bonus or effect
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    rune_type: RuneType
    rank: RuneRank
    
    # Power and level
    level: int  # Rune level (1-10)
    experience: int  # Experience points towards next level
    max_experience: int  # Experience needed for next level
    
    # Bonuses and effects
    bonuses: List[RuneBonus]
    effects: List[RuneEffect]
    
    # Socket compatibility
    required_socket_type: Optional[str]  # Specific socket type required
    
    # Upgrade properties
    can_level_up: bool
    is_max_level: bool
    max_level: int
    
    # Combination properties
    can_combine: bool  # Can combine with same runes to upgrade
    combine_quantity: int  # Number of runes needed to combine
    combine_result_rank: Optional[RuneRank]  # Result rank when combining
    
    # Visual representation
    icon_id: Optional[EntityId]
    texture_id: Optional[EntityId]
    glow_color: Optional[str]  # Hex color code
    particle_effect_id: Optional[EntityId]
    
    # Economic properties
    is_tradeable: bool
    is_sellable: bool
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
            raise ValueError("Rune name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Rune name must be <= 255 characters")
        
        if self.level < 1 or self.level > self.max_level:
            raise ValueError(f"Level must be between 1-{self.max_level}")
        
        if self.experience < 0:
            raise ValueError("Experience cannot be negative")
        
        if self.max_experience < 1:
            raise ValueError("Max experience must be positive")
        
        if self.max_level < 1:
            raise ValueError("Max level must be positive")
        
        if self.combine_quantity < 1:
            raise ValueError("Combine quantity must be positive")
        
        if self.base_value < 0:
            raise ValueError("Base value cannot be negative")
        
        if not self.bonuses and not self.effects:
            raise ValueError("Rune must have at least one bonus or effect")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        rune_type: RuneType,
        rank: RuneRank,
        bonuses: Optional[List[RuneBonus]] = None,
        effects: Optional[List[RuneEffect]] = None,
        level: int = 1,
        experience: int = 0,
        max_experience: int = 100,
        required_socket_type: Optional[str] = None,
        can_level_up: bool = True,
        max_level: int = 10,
        can_combine: bool = True,
        combine_quantity: int = 3,
        combine_result_rank: Optional[RuneRank] = None,
        icon_id: Optional[EntityId] = None,
        texture_id: Optional[EntityId] = None,
        glow_color: Optional[str] = None,
        particle_effect_id: Optional[EntityId] = None,
        is_tradeable: bool = True,
        is_sellable: bool = True,
        base_value: int = 0,
    ) -> 'Rune':
        """
        Factory method for creating a new Rune.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            rune_type=rune_type,
            rank=rank,
            level=level,
            experience=experience,
            max_experience=max_experience,
            bonuses=bonuses or [],
            effects=effects or [],
            required_socket_type=required_socket_type,
            can_level_up=can_level_up,
            is_max_level=level >= max_level,
            max_level=max_level,
            can_combine=can_combine,
            combine_quantity=combine_quantity,
            combine_result_rank=combine_result_rank,
            icon_id=icon_id,
            texture_id=texture_id,
            glow_color=glow_color,
            particle_effect_id=particle_effect_id,
            is_tradeable=is_tradeable,
            is_sellable=is_sellable,
            base_value=base_value,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def level_progress(self) -> float:
        """Get level progress as a percentage (0.0-1.0)."""
        if self.is_max_level:
            return 1.0
        return self.experience / self.max_experience
    
    def update_description(self, new_description: Description) -> None:
        """Update rune description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the rune."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Rune name cannot be empty")
        
        if len(new_name) > 255:
            raise ValueError("Rune name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_rune_type(self, new_type: RuneType) -> None:
        """Set rune type."""
        if self.rune_type == new_type:
            return
        
        object.__setattr__(self, 'rune_type', new_type)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_rank(self, new_rank: RuneRank) -> None:
        """Set rune rank."""
        if self.rank == new_rank:
            return
        
        object.__setattr__(self, 'rank', new_rank)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_bonus(self, bonus: RuneBonus) -> None:
        """Add a bonus to the rune."""
        self.bonuses.append(bonus)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_bonus(self, stat_name: str) -> bool:
        """
        Remove a bonus from the rune.
        
        Returns:
            True if bonus was removed, False if not found.
        """
        for i, bonus in enumerate(self.bonuses):
            if bonus.stat_name == stat_name:
                self.bonuses.pop(i)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False
    
    def add_effect(self, effect: RuneEffect) -> None:
        """Add an effect to the rune."""
        self.effects.append(effect)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_effect(self, effect_name: str) -> bool:
        """
        Remove an effect from the rune.
        
        Returns:
            True if effect was removed, False if not found.
        """
        for i, effect in enumerate(self.effects):
            if effect.effect_name == effect_name:
                self.effects.pop(i)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False
    
    def add_experience(self, amount: int) -> bool:
        """
        Add experience to the rune.
        
        Returns:
            True if rune leveled up.
        """
        if not self.can_level_up or self.is_max_level:
            return False
        
        object.__setattr__(self, 'experience', self.experience + amount)
        
        leveled_up = False
        while self.experience >= self.max_experience and self.level < self.max_level:
            object.__setattr__(self, 'experience', self.experience - self.max_experience)
            object.__setattr__(self, 'level', self.level + 1)
            
            # Scale experience requirement for next level
            new_max_exp = int(self.max_experience * 1.2)
            object.__setattr__(self, 'max_experience', new_max_exp)
            leveled_up = True
        
        # Check if reached max level
        if self.level >= self.max_level:
            object.__setattr__(self, 'is_max_level', True)
            object.__setattr__(self, 'experience', 0)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        
        return leveled_up
    
    def set_level(self, level: int) -> None:
        """Set rune level directly."""
        if level < 1 or level > self.max_level:
            raise ValueError(f"Level must be between 1-{self.max_level}")
        
        if self.level == level:
            return
        
        object.__setattr__(self, 'level', level)
        object.__setattr__(self, 'experience', 0)
        
        # Update max level status
        object.__setattr__(self, 'is_max_level', level >= self.max_level)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def calculate_bonus_value(self, stat_name: str) -> Optional[float]:
        """
        Calculate the total bonus for a stat at current level.
        
        Returns:
            Total bonus value, or None if stat doesn't exist.
        """
        level_multiplier = 1.0 + (self.level - 1) * 0.1
        
        for bonus in self.bonuses:
            if bonus.stat_name == stat_name:
                return bonus.value * level_multiplier
        
        return None
    
    def calculate_effect_value(self, effect_name: str) -> Optional[float]:
        """
        Calculate the total effect value at current level.
        
        Returns:
            Total effect value, or None if effect doesn't exist.
        """
        level_multiplier = 1.0 + (self.level - 1) * 0.1
        
        for effect in self.effects:
            if effect.effect_name == effect_name:
                return effect.effect_value * level_multiplier
        
        return None
    
    def get_all_bonus_values(self) -> Dict[str, float]:
        """Get all bonus values scaled by current level."""
        level_multiplier = 1.0 + (self.level - 1) * 0.1
        return {bonus.stat_name: bonus.value * level_multiplier for bonus in self.bonuses}
    
    def get_all_effect_values(self) -> Dict[str, float]:
        """Get all effect values scaled by current level."""
        level_multiplier = 1.0 + (self.level - 1) * 0.1
        return {effect.effect_name: effect.effect_value * level_multiplier for effect in self.effects}
    
    def set_glow_color(self, color: Optional[str]) -> None:
        """Set the glow color (hex color code)."""
        if color is not None and not color.startswith("#"):
            color = f"#{color}"
        
        object.__setattr__(self, 'glow_color', color)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Rune({self.name}, {self.rank.value}, Lv{self.level})"
    
    def __repr__(self) -> str:
        return (
            f"Rune(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.rune_type}, rank={self.rank}, level={self.level})"
        )
