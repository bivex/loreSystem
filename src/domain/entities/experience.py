"""
Experience Entity

Experience tracks progress and growth for characters across various activities.
"""
from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class ExperienceType(str, Enum):
    """Type of experience being tracked."""
    CHARACTER_LEVEL = "character_level"  # General character progression
    COMBAT = "combat"  # Combat experience
    CRAFTING = "crafting"  # Crafting experience
    EXPLORATION = "exploration"  # Exploration experience
    SOCIAL = "social"  # Social interaction experience
    QUESTING = "questing"  # Quest completion experience


class ExperienceSource(str, Enum):
    """Source of experience gain."""
    KILL = "kill"
    QUEST = "quest"
    CRAFT = "craft"
    DISCOVER = "discover"
    INTERACT = "interact"
    EVENT = "event"
    ACHIEVEMENT = "achievement"
    BONUS = "bonus"


@dataclass
class Experience:
    """
    Experience entity tracking progression.
    
    Invariants:
    - Total experience cannot be negative
    - Current level must be >= 1
    - Current XP in level must be >= 0
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: EntityId
    experience_type: ExperienceType
    
    # Experience values
    total_experience: int  # Total lifetime experience
    current_level: int  # Current level
    current_xp: int  # XP accumulated toward next level
    xp_to_next_level: int  # XP needed for next level
    
    # Multipliers
    xp_multiplier: float  # Global XP multiplier (e.g., from items, perks)
    
    # Statistics
    total_gains: int  # Number of times experience was gained
    largest_gain: Optional[int]  # Largest single gain
    source_breakdown: Optional[Dict[ExperienceSource, int]]  # XP by source type
    
    # Metadata
    last_gain_at: Optional[Timestamp]  # When last XP was gained
    tags: Optional[list]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if self.total_experience < 0:
            raise InvariantViolation("Total experience cannot be negative")
        
        if self.current_level < 1:
            raise InvariantViolation("Current level must be at least 1")
        
        if self.current_xp < 0:
            raise InvariantViolation("Current XP in level cannot be negative")
        
        if self.xp_multiplier < 0:
            raise InvariantViolation("XP multiplier cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        character_id: EntityId,
        experience_type: ExperienceType,
        total_experience: int = 0,
        current_level: int = 1,
        current_xp: int = 0,
        xp_to_next_level: int = 100,
        xp_multiplier: float = 1.0,
        total_gains: int = 0,
        largest_gain: Optional[int] = None,
        source_breakdown: Optional[Dict[ExperienceSource, int]] = None,
        last_gain_at: Optional[Timestamp] = None,
        tags: Optional[list] = None,
    ) -> 'Experience':
        """
        Factory method for creating a new Experience tracker.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            experience_type=experience_type,
            total_experience=total_experience,
            current_level=current_level,
            current_xp=current_xp,
            xp_to_next_level=xp_to_next_level,
            xp_multiplier=xp_multiplier,
            total_gains=total_gains,
            largest_gain=largest_gain,
            source_breakdown=source_breakdown or {},
            last_gain_at=last_gain_at,
            tags=tags,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_experience(
        self,
        amount: int,
        source: ExperienceSource = ExperienceSource.BONUS
    ) -> bool:
        """
        Add experience and check for level up.
        
        Returns:
            True if leveled up, False otherwise
        
        Raises:
            InvariantViolation: If amount is invalid
        """
        if amount <= 0:
            raise InvariantViolation("Experience amount must be positive")
        
        # Apply multiplier
        final_amount = int(amount * self.xp_multiplier)
        
        # Update statistics
        object.__setattr__(self, 'total_experience', self.total_experience + final_amount)
        object.__setattr__(self, 'current_xp', self.current_xp + final_amount)
        object.__setattr__(self, 'total_gains', self.total_gains + 1)
        
        if self.largest_gain is None or final_amount > self.largest_gain:
            object.__setattr__(self, 'largest_gain', final_amount)
        
        if not self.source_breakdown:
            object.__setattr__(self, 'source_breakdown', {})
        
        self.source_breakdown[source] = self.source_breakdown.get(source, 0) + final_amount
        object.__setattr__(self, 'last_gain_at', Timestamp.now())
        
        # Check for level up
        leveled_up = False
        while self.current_xp >= self.xp_to_next_level:
            self._level_up()
            leveled_up = True
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        
        return leveled_up
    
    def _level_up(self) -> None:
        """Internal method to perform level up logic."""
        object.__setattr__(self, 'current_level', self.current_level + 1)
        object.__setattr__(self, 'current_xp', self.current_xp - self.xp_to_next_level)
        # Scale XP requirement (1.5x per level)
        object.__setattr__(self, 'xp_to_next_level', int(self.xp_to_next_level * 1.5))
    
    def set_xp_multiplier(self, multiplier: float) -> None:
        """Set XP multiplier."""
        if multiplier < 0:
            raise InvariantViolation("XP multiplier cannot be negative")
        
        if self.xp_multiplier == multiplier:
            return
        
        object.__setattr__(self, 'xp_multiplier', multiplier)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def get_progress_percentage(self) -> float:
        """Get progress toward next level as percentage."""
        if self.xp_to_next_level == 0:
            return 100.0
        return (self.current_xp / self.xp_to_next_level) * 100.0
    
    def get_xp_from_source(self, source: ExperienceSource) -> int:
        """Get total XP earned from a specific source."""
        if not self.source_breakdown:
            return 0
        return self.source_breakdown.get(source, 0)
    
    def get_average_gain(self) -> float:
        """Get average XP gain."""
        if self.total_gains == 0:
            return 0.0
        return self.total_experience / self.total_gains
    
    def reset_for_level(self) -> None:
        """Reset XP for current level (e.g., after prestige/special event)."""
        object.__setattr__(self, 'current_xp', 0)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        progress = self.get_progress_percentage()
        return f"Experience({self.experience_type.value} Lv.{self.current_level} - {progress:.1f}%)"
    
    def __repr__(self) -> str:
        return (
            f"Experience(id={self.id}, character_id={self.character_id}, "
            f"type={self.experience_type.value}, level={self.current_level})"
        )
