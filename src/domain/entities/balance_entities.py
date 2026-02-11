"""EconomyBalance, PvPBalance, PvEBalance Entities

These entities represent balance and tuning configurations
for game economy and combat systems. Critical for maintaining
fair gameplay and monetization balance.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class EconomyBalance:
    """Overall economic balance for the game."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    gold_generation_rate: float  # Gold per hour
    item_drop_rate: float  # Item rarity multiplier
    vendor_price_modifier: float  # Vendor discount/markup
    crafting_cost_modifier: float  # Crafting material cost
    daily_currency_cap: Optional[int] = None  # Max daily currency earned
    total_currency_cap: Optional[int] = None  # Max total currency in economy
    is_balanced: bool = True  # Overall health flag
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("EconomyBalance name cannot be empty")
        if self.gold_generation_rate <= 0:
            raise InvariantViolation("Gold generation rate must be positive")
        if not (0.0 <= self.item_drop_rate <= 5.0):
            raise InvariantViolation("Item drop rate must be 0.0-5.0x")
    
    @classmethod
    def create(cls, tenant_id: TenantId, name: str, description: str,
                 gold_generation_rate: float = 100.0, item_drop_rate: float = 1.0,
                 vendor_price_modifier: float = 1.0, crafting_cost_modifier: float = 1.0,
                 daily_currency_cap: Optional[int] = None, total_currency_cap: Optional[int] = None) -> "EconomyBalance":
        now = Timestamp.now()
        return cls(tenant_id=tenant_id, name=name.strip(), description=Description(description),
                   gold_generation_rate=gold_generation_rate, item_drop_rate=item_drop_rate,
                   vendor_price_modifier=vendor_price_modifier, crafting_cost_modifier=crafting_cost_modifier,
                   daily_currency_cap=daily_currency_cap, total_currency_cap=total_currency_cap,
                   is_balanced=True, created_at=now, updated_at=now, version=Version(1))
    
    def update_balance(self, is_balanced: bool) -> "EconomyBalance":
        self.is_balanced = is_balanced
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_patch()
        return self
    
    def get_economy_health(self) -> str:
        if self.is_balanced:
            return "balanced"
        return "unbalanced"


@dataclass
class PvPBalance:
    """Player vs Player combat balance configuration."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    damage_multiplier: float  # Damage output multiplier
    health_multiplier: float  # HP multiplier
    is_ranked: bool = True  # Whether ranked PvP is enabled
    mmr_skill: Optional[str] = None  # Matchmaking skill rating
    mmr_range: Dict[str, int] = field(default_factory=dict)  # Skill tier ranges
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("PvPBalance name cannot be empty")
        if self.damage_multiplier <= 0 or self.health_multiplier <= 0:
            raise InvariantViolation("Multipliers must be positive")
    
    @classmethod
    def create(cls, tenant_id: TenantId, name: str, description: str,
                 damage_multiplier: float = 1.0, health_multiplier: float = 1.0,
                 mmr_skill: Optional[str] = None) -> "PvPBalance":
        now = Timestamp.now()
        return cls(tenant_id=tenant_id, name=name.strip(), description=Description(description),
                   damage_multiplier=damage_multiplier, health_multiplier=health_multiplier,
                   is_ranked=True, mmr_skill=mmr_skill,
                   mmr_range={"bronze": (800, 1200), "silver": (1200, 1600), "gold": (1600, 2000)},
                   created_at=now, updated_at=now, version=Version(1))
    
    def adjust_multipliers(self, damage_mult: float, health_mult: float) -> "PvPBalance":
        self.damage_multiplier = damage_mult
        self.health_multiplier = health_mult
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_patch()
        return self
    
    def update_mmr(self, new_mmr: str, range: Tuple[int, int]) -> None:
        self.mmr_skill = new_mmr
        self.mmr_range[new_mmr] = range
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_patch()
    
    def __str__(self) -> str:
        return f"PvPBalance({self.name}, dmg={self.damage_multiplier:.1f}, hp={self.health_multiplier:.1f})"
    
    def __repr__(self) -> str:
        return f"<PvPBalance {self.name}: dmg {self.damage_multiplier:.1f}x hp {self.health_multiplier:.1f}x>"


@dataclass
class PvEBalance:
    """Player vs Environment combat balance configuration."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    mob_damage_multiplier: float  # PvE damage multiplier
    mob_health_multiplier: float  # PvE health multiplier
    mob_ai_level: str  # "easy", "medium", "hard"
    drop_rate_modifier: float  # PvE drop rate modifier
    environmental_hazard_multiplier: float  # Trap/lava/etc damage
    is_hardcore: bool = False  # Hardcore mode toggle
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("PvEBalance name cannot be empty")
        if self.mob_damage_multiplier <= 0 or self.mob_health_multiplier <= 0:
            raise InvariantViolation("Multipliers must be positive")
    
    @classmethod
    def create(cls, tenant_id: TenantId, name: str, description: str,
                 mob_damage_mult: float = 1.0, mob_health_mult: float = 1.0,
                 mob_ai_level: str = "medium", drop_rate_mod: float = 1.0,
                 environmental_hazard_mult: float = 1.0, is_hardcore: bool = False) -> "PvEBalance":
        now = Timestamp.now()
        return cls(tenant_id=tenant_id, name=name.strip(), description=Description(description),
                   mob_damage_mult=mob_damage_mult, mob_health_mult=mob_health_mult,
                   mob_ai_level=mob_ai_level, drop_rate_mod=drop_rate_mod,
                   environmental_hazard_mod=environmental_hazard_mult, is_hardcore=is_hardcore,
                   created_at=now, updated_at=now, version=Version(1))
    
    def set_hardcore_mode(self, is_hardcore: bool) -> "PvEBalance":
        self.is_hardcore = is_hardcore
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_patch()
        return self
    
    def adjust_mobs(self, damage_mod: float, health_mod: float) -> "PvEBalance":
        self.mob_damage_multiplier = damage_mod
        self.mob_health_multiplier = health_mod
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_patch()
        return self
    
    def get_difficulty_rating(self) -> str:
        if self.is_hardcore:
            return "hardcore"
        rating = self.mob_damage_multiplier * self.mob_health_multiplier
        if rating < 0.5:
            return "easy"
        elif rating < 1.0:
            return "medium"
        return "hard"
    
    def __str__(self) -> str:
        return f"PvEBalance({self.name}, ai={self.mob_ai_level}, dmg={self.mob_damage_mult:.1f}x hp={self.mob_health_mult:.1f}x)"
    
    def __repr__(self) -> str:
        return f"<PvEBalance {self.name}: {self.mob_ai_level} {self.mob_damage_mult:.1f}x {self.mob_health_mult:.1f}x>"
