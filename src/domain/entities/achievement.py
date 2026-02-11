"""Achievement Entity

An Achievement represents a goal or milestone that players can complete
for rewards and recognition in game. Achievements are often used
for motivation, progression tracking, and bragging rights.
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
class Achievement:
    """An achievement that players can complete."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    achievement_type: str  # "progression", "challenge", "hidden", "collection"
    difficulty: str  # "easy", "medium", "hard", "insane"
    reward_ids: List[EntityId] = field(default_factory=list)  # IDs of rewards (items, titles, etc.)
    is_hidden: bool = False
    is_repeatable: bool = False
    prerequisites: List[EntityId] = field(default_factory=list)  # Requirements to unlock
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
            raise InvariantViolation("Achievement name cannot be empty")
        
        if self.difficulty not in ["easy", "medium", "hard", "insane"]:
            raise InvariantViolation("Invalid difficulty level")
        
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
        achievement_type: str = "progression",
        difficulty: str = "medium",
        reward_ids: Optional[List[EntityId]] = None,
        is_hidden: bool = False,
        is_repeatable: bool = False,
        prerequisites: Optional[List[EntityId]] = None,
        icon: Optional[str] = None,
    ) -> "Achievement":
        """Factory method to create a new Achievement."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            description=Description(description),
            achievement_type=achievement_type,
            difficulty=difficulty,
            reward_ids=reward_ids or [],
            is_hidden=is_hidden,
            is_repeatable=is_repeatable,
            prerequisites=prerequisites or [],
            icon=icon,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def unlock(self) -> "Achievement":
        """Unlock this achievement."""
        self.is_hidden = False
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_minor()
        return self
    
    def add_reward(self, reward_id: EntityId) -> "Achievement":
        """Add a reward to this achievement."""
        if reward_id not in self.reward_ids:
            self.reward_ids.append(reward_id)
            self.updated_at = Timestamp.now()
            self.version = self.version.increment_patch()
        return self
    
    def __str__(self) -> str:
        return f"Achievement({self.name}, type={self.achievement_type}, difficulty={self.difficulty})"
    
    def __repr__(self) -> str:
        return (
            f"Achievement(id={self.id}, name='{self.name}', "
            f"type={self.achievement_type}, difficulty={self.difficulty})"
        )
