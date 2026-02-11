"""
Mastery Entity

A Mastery represents advanced expertise in a particular skill, weapon type, or activity.
Mastery levels unlock new abilities and enhance existing ones.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class MasteryCategory(str, Enum):
    """Category of mastery."""
    WEAPON = "weapon"  # Weapon mastery (sword, bow, etc.)
    MAGIC = "magic"  # Magic school mastery (fire, ice, etc.)
    CRAFTING = "crafting"  # Crafting skill mastery (blacksmith, alchemy, etc.)
    SOCIAL = "social"  # Social interaction mastery
    COMBAT = "combat"  # General combat mastery
    EXPLORATION = "exploration"  # Exploration mastery


class MasteryRank(str, Enum):
    """Mastery rank/tier."""
    NOVICE = "novice"  # Rank 1: Basic understanding
    APPRENTICE = "apprentice"  # Rank 2: Learning the ropes
    JOURNEYMAN = "journeyman"  # Rank 3: Competent
    EXPERT = "expert"  # Rank 4: Highly skilled
    MASTER = "master"  # Rank 5: Master of the craft
    GRANDMASTER = "grandmaster"  # Rank 6: Legendary status
    LEGENDARY = "legendary"  # Rank 7: Unparalleled


class MasteryBonusType(str, Enum):
    """Type of mastery bonus."""
    DAMAGE = "damage"
    CRIT_RATE = "crit_rate"
    CRIT_DAMAGE = "crit_damage"
    SPEED = "speed"
    EFFICIENCY = "efficiency"
    RESOURCE_COST = "resource_cost"
    QUALITY = "quality"
    YIELD = "yield"


@dataclass
class MasteryBonus:
    """A bonus granted at a specific mastery level."""
    level: int  # Mastery level required
    bonus_type: MasteryBonusType
    value: float  # Bonus value
    description: Optional[str]


@dataclass
class Mastery:
    """
    Mastery entity representing skill expertise.
    
    Invariants:
    - Level must be between 0-100
    - Progress must be between 0-100%
    - Version increases monotonically
    - Cannot have empty name
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: EntityId
    name: str
    description: Description
    category: MasteryCategory
    
    # Progression
    level: int  # Current mastery level (0-100)
    max_level: int  # Maximum achievable level
    progress: float  # Progress toward next level (0-100)
    total_experience: int  # Total lifetime experience
    
    # Mastery rank
    current_rank: MasteryRank
    rank_thresholds: Optional[dict]  # Rank name -> level threshold
    
    # Bonuses
    bonuses: Optional[List[MasteryBonus]]  # All available bonuses
    unlocked_bonuses: List[str]  # IDs/types of unlocked bonuses
    
    # Active effects
    active_passive_id: Optional[EntityId]  # ID of active passive ability
    active_ability_ids: Optional[List[EntityId]]  # IDs of active abilities unlocked
    
    # Metadata
    icon_id: Optional[str]
    associated_skill_id: Optional[EntityId]  # Link to related skill
    tags: Optional[List[str]]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
        self._update_rank()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Mastery name cannot be empty")
        
        if self.level < 0 or self.level > self.max_level:
            raise InvariantViolation(
                f"Level must be between 0-{self.max_level}"
            )
        
        if self.max_level < 1:
            raise InvariantViolation("Max level must be at least 1")
        
        if self.progress < 0 or self.progress > 100:
            raise InvariantViolation("Progress must be between 0-100")
        
        if self.total_experience < 0:
            raise InvariantViolation("Total experience cannot be negative")
    
    def _update_rank(self) -> None:
        """Update mastery rank based on level."""
        thresholds = self.rank_thresholds or {
            MasteryRank.NOVICE: 0,
            MasteryRank.APPRENTICE: 10,
            MasteryRank.JOURNEYMAN: 30,
            MasteryRank.EXPERT: 50,
            MasteryRank.MASTER: 70,
            MasteryRank.GRANDMASTER: 85,
            MasteryRank.LEGENDARY: 95,
        }
        
        new_rank = MasteryRank.NOVICE
        for rank, threshold in thresholds.items():
            if self.level >= threshold:
                new_rank = rank
        
        if new_rank != self.current_rank:
            object.__setattr__(self, 'current_rank', new_rank)
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        character_id: EntityId,
        name: str,
        description: Description,
        category: MasteryCategory,
        level: int = 0,
        max_level: int = 100,
        progress: float = 0.0,
        total_experience: int = 0,
        rank_thresholds: Optional[dict] = None,
        bonuses: Optional[List[MasteryBonus]] = None,
        unlocked_bonuses: Optional[List[str]] = None,
        active_passive_id: Optional[EntityId] = None,
        active_ability_ids: Optional[List[EntityId]] = None,
        icon_id: Optional[str] = None,
        associated_skill_id: Optional[EntityId] = None,
        tags: Optional[List[str]] = None,
    ) -> 'Mastery':
        """
        Factory method for creating a new Mastery.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            name=name,
            description=description,
            category=category,
            level=level,
            max_level=max_level,
            progress=progress,
            total_experience=total_experience,
            current_rank=MasteryRank.NOVICE,
            rank_thresholds=rank_thresholds,
            bonuses=bonuses,
            unlocked_bonuses=unlocked_bonuses or [],
            active_passive_id=active_passive_id,
            active_ability_ids=active_ability_ids,
            icon_id=icon_id,
            associated_skill_id=associated_skill_id,
            tags=tags,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_experience(self, amount: int) -> bool:
        """
        Add experience and check for level up.
        
        Returns:
            True if leveled up, False otherwise
        """
        if amount <= 0:
            raise InvariantViolation("Experience amount must be positive")
        
        object.__setattr__(self, 'total_experience', self.total_experience + amount)
        
        # Add progress (simplified: 100 XP = 1% progress)
        progress_gain = amount / 100.0
        new_progress = self.progress + progress_gain
        
        leveled_up = False
        while new_progress >= 100 and self.level < self.max_level:
            new_progress -= 100
            object.__setattr__(self, 'level', self.level + 1)
            leveled_up = True
            self._check_bonuses()
        
        object.__setattr__(self, 'progress', min(new_progress, 100.0))
        self._update_rank()
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        
        return leveled_up
    
    def _check_bonuses(self) -> None:
        """Check for new bonuses at current level."""
        if not self.bonuses:
            return
        
        for bonus in self.bonuses:
            bonus_key = f"{bonus.bonus_type.value}_{bonus.level}"
            if bonus.level <= self.level and bonus_key not in self.unlocked_bonuses:
                self.unlocked_bonuses.append(bonus_key)
    
    def get_total_bonus(self, bonus_type: MasteryBonusType) -> float:
        """Get total bonus for a specific type."""
        if not self.bonuses:
            return 0.0
        
        total = 0.0
        for bonus in self.bonuses:
            if bonus.bonus_type == bonus_type and bonus.level <= self.level:
                total += bonus.value
        
        return total
    
    def is_max_level(self) -> bool:
        """Check if mastery is at maximum level."""
        return self.level >= self.max_level
    
    def is_at_least(self, rank: MasteryRank) -> bool:
        """Check if mastery is at least a certain rank."""
        rank_order = [
            MasteryRank.NOVICE,
            MasteryRank.APPRENTICE,
            MasteryRank.JOURNEYMAN,
            MasteryRank.EXPERT,
            MasteryRank.MASTER,
            MasteryRank.GRANDMASTER,
            MasteryRank.LEGENDARY,
        ]
        return rank_order.index(self.current_rank) >= rank_order.index(rank)
    
    def get_next_rank(self) -> Optional[MasteryRank]:
        """Get the next rank up."""
        rank_order = [
            MasteryRank.NOVICE,
            MasteryRank.APPRENTICE,
            MasteryRank.JOURNEYMAN,
            MasteryRank.EXPERT,
            MasteryRank.MASTER,
            MasteryRank.GRANDMASTER,
            MasteryRank.LEGENDARY,
        ]
        current_index = rank_order.index(self.current_rank)
        if current_index + 1 < len(rank_order):
            return rank_order[current_index + 1]
        return None
    
    def get_progress_to_next_rank(self) -> float:
        """Get percentage progress toward next rank."""
        next_rank = self.get_next_rank()
        if not next_rank:
            return 100.0
        
        thresholds = self.rank_thresholds or {
            MasteryRank.NOVICE: 0,
            MasteryRank.APPRENTICE: 10,
            MasteryRank.JOURNEYMAN: 30,
            MasteryRank.EXPERT: 50,
            MasteryRank.MASTER: 70,
            MasteryRank.GRANDMASTER: 85,
            MasteryRank.LEGENDARY: 95,
        }
        
        current_threshold = thresholds[self.current_rank]
        next_threshold = thresholds[next_rank]
        
        if next_threshold == current_threshold:
            return 100.0
        
        progress = (self.level - current_threshold) / (next_threshold - current_threshold) * 100.0
        return max(0.0, min(100.0, progress))
    
    def __str__(self) -> str:
        return f"Mastery({self.name}: {self.current_rank.value} Lv.{self.level}/{self.max_level})"
    
    def __repr__(self) -> str:
        return (
            f"Mastery(id={self.id}, character_id={self.character_id}, "
            f"name='{self.name}', rank={self.current_rank.value})"
        )
