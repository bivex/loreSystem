"""Trophy Entity

A Trophy represents a prestigious award given for achieving
major milestones, completing difficult content, or winning competitions.
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
class Trophy:
    """A prestigious award for major achievements."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    trophy_type: str  # "world_first", "pvp_champion", "event_winner"
    rarity: str  # "common", "rare", "epic", "legendary"
    icon: Optional[str] = None
    achievement_ids: List[EntityId] = field(default_factory=list)
    is_held: bool = False
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Trophy name cannot be empty")
        
        if self.trophy_type not in ["world_first", "pvp_champion", "event_winner"]:
            raise InvariantViolation("Invalid trophy type")
        
        if self.rarity not in ["common", "rare", "epic", "legendary"]:
            raise InvariantViolation("Invalid rarity level")
        
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
        trophy_type: str = "event_winner",
        rarity: str = "rare",
        icon: Optional[str] = None,
        achievement_ids: Optional[List[EntityId]] = None,
    ) -> "Trophy":
        """Factory method to create a new Trophy."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            description=Description(description),
            trophy_type=trophy_type,
            rarity=rarity,
            icon=icon,
            achievement_ids=achievement_ids or [],
            is_held=False,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def award(self) -> "Trophy":
        """Mark this trophy as awarded/held."""
        self.is_held = True
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_minor()
        return self
    
    def add_achievement(self, achievement_id: EntityId) -> None:
        """Add an achievement to this trophy."""
        if achievement_id not in self.achievement_ids:
            self.achievement_ids.append(achievement_id)
            self.updated_at = Timestamp.now()
        return None
    
    def __str__(self) -> str:
        return f"Trophy({self.name}, rarity={self.rarity})"
    
    def __repr__(self) -> str:
        return f"<Trophy {self.name}: {self.trophy_type} {self.rarity}>"
