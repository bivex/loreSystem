"""
Glyph Entity

A Glyph represents a magical glyph that can be inserted into sockets.
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


class GlyphSchool(str, Enum):
    """Schools of magic for glyphs."""
    ELEMENTAL = "elemental"  # Fire, ice, lightning, earth
    CELESTIAL = "celestial"  # Light, stars, moon, sun
    SHADOW = "shadow"  # Darkness, void, necromancy
    NATURE = "nature"  # Plants, animals, life
    ARCANE = "arcane"  # Pure magic, mana, spell power
    DIVINE = "divine"  # Holy, healing, protection
    CHAOS = "chaos"  # Random, unpredictable effects
    ORDER = "order"  # Structure, stability, defense
    TIME = "time"  # Temporal manipulation
    SPACE = "space"  # Teleportation, portals, dimensions
    BLOOD = "blood"  # Sacrificial, life force manipulation
    SOUL = "soul"  # Spirit, possession, soul binding


class GlyphTier(str, Enum):
    """Tier levels for glyphs."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    TRANSCENDENT = "transcendent"


class GlyphCategory(str, Enum):
    """Categories of glyphs based on function."""
    PASSIVE = "passive"  # Constant effects
    TRIGGERED = "triggered"  # Activate on condition
    CHARGED = "charged"  # Require charges to activate
    ACTIVE = "active"  # Must be manually activated
    CURSE = "curse"  # Negative effects
    BLESSING = "blessing"  # Positive temporary effects


@dataclass
class GlyphModifier:
    """Represents a stat modifier provided by a glyph."""
    stat_name: str  # e.g., "spell_power", "mana_regen"
    value: float
    operation: str  # "add", "multiply", "set"
    is_percentage: bool  # True if value is a percentage
    
    def __post_init__(self):
        if self.operation not in ["add", "multiply", "set"]:
            raise ValueError("Operation must be 'add', 'multiply', or 'set'")
        if self.is_percentage and (self.value < -100 or self.value > 100) and self.operation == "add":
            raise ValueError("Percentage value must be between -100 and 100 for add operation")
    
    def __str__(self) -> str:
        suffix = "%" if self.is_percentage else ""
        op_symbols = {"add": "+", "multiply": "×", "set": "="}
        return f"{self.stat_name} {op_symbols[self.operation]} {self.value}{suffix}"


@dataclass
class GlyphAbility:
    """Represents a special ability provided by a glyph."""
    ability_name: str  # e.g., "fireball", "shield", "teleport"
    description: str
    mana_cost: Optional[int]  # Mana cost to activate
    cooldown_seconds: int  # Cooldown between uses
    duration_seconds: Optional[int]  # Duration for effects
    power: float  # Power scaling factor
    requires_target: bool  # True if ability needs a target
    max_charges: Optional[int]  # Maximum charges for charged abilities
    
    def __post_init__(self):
        if self.mana_cost is not None and self.mana_cost < 0:
            raise ValueError("Mana cost cannot be negative")
        if self.cooldown_seconds < 0:
            raise ValueError("Cooldown cannot be negative")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("Duration cannot be negative")
        if self.power < 0:
            raise ValueError("Power cannot be negative")
        if self.max_charges is not None and self.max_charges < 1:
            raise ValueError("Max charges must be positive")


@dataclass
class Glyph:
    """
    Glyph entity for magical socket items.
    
    Invariants:
    - Name cannot be empty
    - Glyph school must be set
    - Glyph tier must be set
    - Tier level must be between 1-10
    - Must have at least one modifier or ability
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    glyph_school: GlyphSchool
    tier: GlyphTier
    category: GlyphCategory
    
    # Power and level
    tier_level: int  # Power level within tier (1-10)
    proficiency: int  # Proficiency with this glyph (1-100)
    
    # Modifiers and abilities
    modifiers: List[GlyphModifier]
    abilities: List[GlyphAbility]
    
    # Socket compatibility
    required_socket_type: Optional[str]  # Specific socket type required
    
    # Upgrade properties
    can_upgrade_tier: bool
    is_max_tier: bool
    max_tier_level: int
    
    # Synergy properties
    synergizes_with_schools: List[GlyphSchool]  # Schools that synergize with this glyph
    synergy_bonus: float  # Bonus when synergized (0.0-1.0)
    
    # Charge properties (for charged glyphs)
    current_charges: int
    max_charges: int
    charge_regen_time: int  # Seconds to regenerate one charge
    
    # Visual representation
    icon_id: Optional[EntityId]
    texture_id: Optional[EntityId]
    symbol: str  # Unicode symbol representing the glyph
    color: str  # Primary color (hex code)
    
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
            raise ValueError("Glyph name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Glyph name must be <= 255 characters")
        
        if self.tier_level < 1 or self.tier_level > self.max_tier_level:
            raise ValueError(f"Tier level must be between 1-{self.max_tier_level}")
        
        if self.proficiency < 0 or self.proficiency > 100:
            raise ValueError("Proficiency must be between 0-100")
        
        if self.max_tier_level < 1:
            raise ValueError("Max tier level must be positive")
        
        if self.synergy_bonus < 0.0 or self.synergy_bonus > 1.0:
            raise ValueError("Synergy bonus must be between 0.0-1.0")
        
        if self.current_charges < 0:
            raise ValueError("Current charges cannot be negative")
        
        if self.max_charges < 0:
            raise ValueError("Max charges cannot be negative")
        
        if self.charge_regen_time < 0:
            raise ValueError("Charge regen time cannot be negative")
        
        if self.base_value < 0:
            raise ValueError("Base value cannot be negative")
        
        if not self.modifiers and not self.abilities:
            raise ValueError("Glyph must have at least one modifier or ability")
        
        # Validate current charges don't exceed max
        if self.current_charges > self.max_charges:
            raise ValueError("Current charges cannot exceed max charges")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        glyph_school: GlyphSchool,
        tier: GlyphTier,
        category: GlyphCategory,
        modifiers: Optional[List[GlyphModifier]] = None,
        abilities: Optional[List[GlyphAbility]] = None,
        tier_level: int = 1,
        proficiency: int = 0,
        required_socket_type: Optional[str] = None,
        can_upgrade_tier: bool = True,
        max_tier_level: int = 10,
        synergizes_with_schools: Optional[List[GlyphSchool]] = None,
        synergy_bonus: float = 0.25,
        current_charges: int = 0,
        max_charges: int = 0,
        charge_regen_time: int = 60,
        icon_id: Optional[EntityId] = None,
        texture_id: Optional[EntityId] = None,
        symbol: str = "✦",
        color: str = "#FFFFFF",
        is_tradeable: bool = True,
        is_sellable: bool = True,
        base_value: int = 0,
    ) -> 'Glyph':
        """
        Factory method for creating a new Glyph.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            glyph_school=glyph_school,
            tier=tier,
            category=category,
            tier_level=tier_level,
            proficiency=proficiency,
            modifiers=modifiers or [],
            abilities=abilities or [],
            required_socket_type=required_socket_type,
            can_upgrade_tier=can_upgrade_tier,
            is_max_tier=tier_level >= max_tier_level,
            max_tier_level=max_tier_level,
            synergizes_with_schools=synergizes_with_schools or [],
            synergy_bonus=synergy_bonus,
            current_charges=current_charges,
            max_charges=max_charges,
            charge_regen_time=charge_regen_time,
            icon_id=icon_id,
            texture_id=texture_id,
            symbol=symbol,
            color=color,
            is_tradeable=is_tradeable,
            is_sellable=is_sellable,
            base_value=base_value,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def has_charges(self) -> bool:
        """Check if glyph has charges (charged glyph category)."""
        return self.category == GlyphCategory.CHARGED and self.max_charges > 0
    
    @property
    def is_charged(self) -> bool:
        """Check if glyph currently has charges available."""
        return self.current_charges > 0
    
    @property
    def proficiency_percentage(self) -> float:
        """Get proficiency as a percentage (0.0-1.0)."""
        return self.proficiency / 100.0
    
    def update_description(self, new_description: Description) -> None:
        """Update glyph description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the glyph."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Glyph name cannot be empty")
        
        if len(new_name) > 255:
            raise ValueError("Glyph name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_school(self, new_school: GlyphSchool) -> None:
        """Set glyph school."""
        if self.glyph_school == new_school:
            return
        
        object.__setattr__(self, 'glyph_school', new_school)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_tier(self, new_tier: GlyphTier) -> None:
        """Set glyph tier."""
        if self.tier == new_tier:
            return
        
        object.__setattr__(self, 'tier', new_tier)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_tier_level(self, level: int) -> None:
        """Set tier level."""
        if level < 1 or level > self.max_tier_level:
            raise ValueError(f"Tier level must be between 1-{self.max_tier_level}")
        
        if self.tier_level == level:
            return
        
        object.__setattr__(self, 'tier_level', level)
        
        # Update max tier status
        object.__setattr__(self, 'is_max_tier', level >= self.max_tier_level)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_proficiency(self, proficiency: int) -> None:
        """Set proficiency (0-100)."""
        if proficiency < 0 or proficiency > 100:
            raise ValueError("Proficiency must be between 0-100")
        
        object.__setattr__(self, 'proficiency', proficiency)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_proficiency(self, amount: int) -> None:
        """Add proficiency (capped at 100)."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        new_proficiency = min(self.proficiency + amount, 100)
        object.__setattr__(self, 'proficiency', new_proficiency)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_modifier(self, modifier: GlyphModifier) -> None:
        """Add a modifier to the glyph."""
        self.modifiers.append(modifier)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_modifier(self, stat_name: str) -> bool:
        """
        Remove a modifier from the glyph.
        
        Returns:
            True if modifier was removed, False if not found.
        """
        for i, modifier in enumerate(self.modifiers):
            if modifier.stat_name == stat_name:
                self.modifiers.pop(i)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False
    
    def add_ability(self, ability: GlyphAbility) -> None:
        """Add an ability to the glyph."""
        self.abilities.append(ability)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_ability(self, ability_name: str) -> bool:
        """
        Remove an ability from the glyph.
        
        Returns:
            True if ability was removed, False if not found.
        """
        for i, ability in enumerate(self.abilities):
            if ability.ability_name == ability_name:
                self.abilities.pop(i)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False
    
    def add_synergy(self, school: GlyphSchool) -> None:
        """Add a synergy school."""
        if school in self.synergizes_with_schools:
            return
        
        self.synergizes_with_schools.append(school)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_synergy(self, school: GlyphSchool) -> bool:
        """
        Remove a synergy school.
        
        Returns:
            True if synergy was removed, False if not found.
        """
        if school in self.synergizes_with_schools:
            self.synergizes_with_schools.remove(school)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
            return True
        
        return False
    
    def has_synergy_with(self, school: GlyphSchool) -> bool:
        """Check if glyph has synergy with a specific school."""
        return school in self.synergizes_with_schools
    
    def consume_charge(self) -> bool:
        """
        Consume one charge.
        
        Returns:
            True if charge was consumed, False if no charges available.
        """
        if not self.has_charges or self.current_charges <= 0:
            return False
        
        object.__setattr__(self, 'current_charges', self.current_charges - 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        return True
    
    def regenerate_charges(self) -> None:
        """Regenerate charges to max."""
        if not self.has_charges or self.current_charges >= self.max_charges:
            return
        
        object.__setattr__(self, 'current_charges', self.max_charges)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def calculate_modifier_value(self, stat_name: str, synergy_active: bool = False) -> Optional[float]:
        """
        Calculate the total modifier for a stat.
        
        Args:
            stat_name: The stat name to calculate
            synergy_active: Whether a synergy is currently active
        
        Returns:
            Total modifier value, or None if stat doesn't exist.
        """
        tier_multiplier = 1.0 + (self.tier_level - 1) * 0.1
        proficiency_multiplier = 1.0 + (self.proficiency / 100.0) * 0.5
        synergy_multiplier = 1.0 + self.synergy_bonus if synergy_active else 1.0
        
        total_multiplier = tier_multiplier * proficiency_multiplier * synergy_multiplier
        
        for modifier in self.modifiers:
            if modifier.stat_name == stat_name:
                return modifier.value * total_multiplier
        
        return None
    
    def calculate_ability_power(self, ability_name: str, synergy_active: bool = False) -> Optional[float]:
        """
        Calculate the total power of an ability.
        
        Args:
            ability_name: The ability name to calculate
            synergy_active: Whether a synergy is currently active
        
        Returns:
            Total ability power, or None if ability doesn't exist.
        """
        tier_multiplier = 1.0 + (self.tier_level - 1) * 0.1
        proficiency_multiplier = 1.0 + (self.proficiency / 100.0) * 0.5
        synergy_multiplier = 1.0 + self.synergy_bonus if synergy_active else 1.0
        
        total_multiplier = tier_multiplier * proficiency_multiplier * synergy_multiplier
        
        for ability in self.abilities:
            if ability.ability_name == ability_name:
                return ability.power * total_multiplier
        
        return None
    
    def set_symbol(self, symbol: str) -> None:
        """Set the unicode symbol."""
        if not symbol or len(symbol) != 1:
            raise ValueError("Symbol must be a single unicode character")
        
        object.__setattr__(self, 'symbol', symbol)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_color(self, color: str) -> None:
        """Set the primary color (hex code)."""
        if not color.startswith("#"):
            color = f"#{color}"
        
        object.__setattr__(self, 'color', color)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        charges_str = f" [{self.current_charges}/{self.max_charges}]" if self.has_charges else ""
        return f"Glyph({self.symbol} {self.name}, {self.glyph_school.value}, Lv{self.tier_level}{charges_str})"
    
    def __repr__(self) -> str:
        return (
            f"Glyph(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', school={self.glyph_school}, tier={self.tier}, level={self.tier_level})"
        )
