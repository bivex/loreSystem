"""Badge Entity

A Badge is a visual indicator or collectible that players earn
by completing achievements, participating in events, or reaching milestones.
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
class Badge:
    """A visual collectible indicator for achievements."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    badge_type: str  # "progression", "event", "collection"
    rarity: str  # "common", "uncommon", "rare"
    icon: Optional[str] = None
    achievement_ids: List[EntityId] = field(default_factory=list)
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Badge name cannot be empty")
        
        if self.badge_type not in ["progression", "event", "collection"]:
            raise InvariantViolation("Invalid badge type")
        
        if self.rarity not in ["common", "uncommon", "rare"]:
            raise InvariantViolation("Invalid rarity")
        
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
        badge_type: str = "progression",
        rarity: str = "common",
        icon: Optional[str] = None,
        achievement_ids: Optional[List[EntityId]] = None,
    ) -> "Badge":
        """Factory method to create a new Badge."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            description=Description(description),
            badge_type=badge_type,
            rarity=rarity,
            icon=icon,
            achievement_ids=achievement_ids or [],
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def unlock(self) -> "Badge":
        """Unlock this badge for player."""
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_minor()
        return self
    
    def add_achievement(self, achievement_id: EntityId) -> None:
        """Associate an achievement with this badge."""
        if achievement_id not in self.achievement_ids:
            self.achievement_ids.append(achievement_id)
            self.updated_at = Timestamp.now()
    
    def __str__(self) -> str:
        return f"Badge({self.name}, type={self.badge_type}, rarity={self.rarity})"
    
    def __repr__(self) -> str:
        return f"<Badge {self.name}: {self.badge_type} {self.rarity}>"
