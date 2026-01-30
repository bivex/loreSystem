"""DropRate Entity

A DropRate represents the percentage of times players receive
specific items from loot tables. Critical for balance tuning
and player satisfaction in loot-based games.
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
class DropRate:
    """Loot drop rate configuration for specific items or item categories."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str  # "Legendary Sword Drop Rate", "Epic Chest Drop Chance"
    category: str  # "weapon", "armor", "material", "currency"
    drop_rate: float  # 0.0 to 1.0 (0% to 100%)
    conditions: List[str]  # ["level >= 50", "world_boss_defeated"]
    affected_items: List[EntityId] = field(default_factory=list)
    player_level_scaling: Dict[str, float] = field(default_factory=dict)  # Per-level adjustments
    is_event_boosted: bool = False  # Limited-time event boosts
    boost_multiplier: float = 1.0  # For event boosts
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("DropRate name cannot be empty")
        
        if not (0.0 <= self.drop_rate <= 1.0):
            raise InvariantViolation("Drop rate must be between 0.0 and 1.0")
        
        if self.player_level_scaling and not self.player_level_scaling:
            raise InvariantViolation("Player level scaling must be a dict")
        
        if self.boost_multiplier <= 0.0:
            raise InvariantViolation("Boost multiplier must be positive")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        category: str,
        drop_rate: float,
        conditions: Optional[List[str]] = None,
        affected_items: Optional[List[EntityId]] = None,
        player_level_scaling: Optional[Dict[str, float]] = None,
        is_event_boosted: bool = False,
        boost_multiplier: float = 1.0,
    ) -> "DropRate":
        """Factory method to create a new DropRate."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            category=category,
            drop_rate=drop_rate,
            conditions=conditions or [],
            affected_items=affected_items or [],
            player_level_scaling=player_level_scaling or {},
            is_event_boosted=is_event_boosted,
            boost_multiplier=boost_multiplier,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def get_effective_rate_for_player(self, player_level: int) -> float:
        """Calculate effective drop rate considering player level."""
        base_rate = self.drop_rate
        if player_level in self.player_level_scaling:
            base_rate *= self.player_level_scaling[player_level]
        return base_rate
    
    def activate_event_boost(self, multiplier: float = 2.0) -> "DropRate":
        """Activate limited-time event boost."""
        self.is_event_boosted = True
        self.boost_multiplier = multiplier
        self.updated_at = Timestamp.now()
        return self
    
    def deactivate_event_boost(self) -> "DropRate":
        """Deactivate event boost."""
        self.is_event_boosted = False
        self.boost_multiplier = 1.0
        self.updated_at = Timestamp.now()
        return self
    
    def __str__(self) -> str:
        return f"DropRate({self.name}, category={self.category}, rate={self.drop_rate * 100}%)"
    
    def __repr__(self) -> str:
        return f"<DropRate {self.name}: {self.category} {self.drop_rate * 100}%>"
