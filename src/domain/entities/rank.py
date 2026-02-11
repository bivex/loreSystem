"""Rank Entity

A Rank represents a hierarchical position or title
that players earn through progression, achievements, or reputation.
Ranks are often used for skill-based matchmaking or prestige systems.
"""

from dataclasses import dataclass, field
from typing import Optional, List
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
class Rank:
    """A hierarchical position or title for players."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    rank_type: str  # "skill", "prestige", "faction", "pvp"
    tier: int  # 1-10 or 1-100
    required_level: int
    required_xp: int
    perks: List[str]  # Perks unlocked at this rank
    is_permanent: bool = False
    icon: Optional[str] = None
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Rank name cannot be empty")
        
        if self.tier < 1:
            raise InvariantViolation("Tier must be >= 1")
        
        if self.required_level < 0:
            raise InvariantViolation("Required level must be >= 0")
        
        if self.required_xp < 0:
            raise InvariantViolation("Required XP must be >= 0")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: str,
        rank_type: str = "prestige",
        tier: int = 1,
        required_level: int = 1,
        required_xp: int = 0,
        perks: Optional[List[str]] = None,
        is_permanent: bool = False,
        icon: Optional[str] = None,
    ) -> "Rank":
        """Factory method to create a new Rank."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            description=Description(description),
            rank_type=rank_type,
            tier=tier,
            required_level=required_level,
            required_xp=required_xp,
            perks=perks or [],
            is_permanent=is_permanent,
            icon=icon,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def promote(self) -> "Rank":
        """Promote to next tier."""
        self.tier += 1
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_minor()
        return self
    
    def __str__(self) -> str:
        return f"Rank({self.name}, tier={self.tier}, type={self.rank_type})"
    
    def __repr__(self) -> str:
        return f"<Rank {self.name}: tier {self.tier}, type {self.rank_type}>"
