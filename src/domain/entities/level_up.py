"""
LevelUp Entity

A LevelUp represents a character reaching a new level milestone.
Records rewards, choices made, and effects of leveling up.
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


class LevelUpType(str, Enum):
    """Type of level up."""
    NORMAL = "normal"  # Regular level progression
    MASTERY = "mastery"  # Reached mastery level
    PRESTIGE = "prestige"  # Prestige/reset with bonuses
    EVOLUTION = "evolution"  # Character evolution/transformation


class RewardType(str, Enum):
    """Type of reward received."""
    STAT_INCREASE = "stat_increase"
    SKILL_POINT = "skill_point"
    ABILITY_UNLOCK = "ability_unlock"
    PERK_UNLOCK = "perk_unlock"
    TRAIT_CHANGE = "trait_change"
    ITEM_REWARD = "item_reward"
    PASSIVE_BOOST = "passive_boost"


@dataclass
class LevelUp:
    """
    LevelUp entity representing a level milestone.
    
    Invariants:
    - Old level must be < new level
    - Version increases monotonically
    - Must be associated with a character
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: EntityId
    level_up_type: LevelUpType
    
    # Level information
    old_level: int
    new_level: int
    
    # Rewards granted
    reward_ids: Optional[List[EntityId]]  # IDs of reward entities
    stat_increases: Optional[dict]  # Dict of stat_name -> increase_amount
    skill_points_gained: int
    abilities_unlocked: Optional[List[EntityId]]  # Ability IDs unlocked
    
    # Choices made
    choices_made: Optional[List[str]]  # Description of choices player made
    selected_rewards: Optional[List[str]]  # Rewards player selected
    
    # Effects
    health_increase: Optional[int]
    mana_increase: Optional[int]
    attack_increase: Optional[int]
    defense_increase: Optional[int]
    
    # Timestamps
    occurred_at: Timestamp
    
    # Metadata
    location_id: Optional[EntityId]  # Where the level up occurred
    quest_id: Optional[EntityId]  # Quest that caused this level up
    notes: Optional[Description]
    
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
        
        if self.new_level <= self.old_level:
            raise InvariantViolation(
                f"New level ({self.new_level}) must be greater than old level ({self.old_level})"
            )
        
        if self.old_level < 0:
            raise InvariantViolation("Old level cannot be negative")
        
        if self.new_level < 1:
            raise InvariantViolation("New level must be at least 1")
        
        if self.skill_points_gained < 0:
            raise InvariantViolation("Skill points gained cannot be negative")
        
        if self.health_increase is not None and self.health_increase < 0:
            raise InvariantViolation("Health increase cannot be negative")
        
        if self.mana_increase is not None and self.mana_increase < 0:
            raise InvariantViolation("Mana increase cannot be negative")
        
        if self.attack_increase is not None and self.attack_increase < 0:
            raise InvariantViolation("Attack increase cannot be negative")
        
        if self.defense_increase is not None and self.defense_increase < 0:
            raise InvariantViolation("Defense increase cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        character_id: EntityId,
        level_up_type: LevelUpType,
        old_level: int,
        new_level: int,
        reward_ids: Optional[List[EntityId]] = None,
        stat_increases: Optional[dict] = None,
        skill_points_gained: int = 0,
        abilities_unlocked: Optional[List[EntityId]] = None,
        choices_made: Optional[List[str]] = None,
        selected_rewards: Optional[List[str]] = None,
        health_increase: Optional[int] = None,
        mana_increase: Optional[int] = None,
        attack_increase: Optional[int] = None,
        defense_increase: Optional[int] = None,
        occurred_at: Optional[Timestamp] = None,
        location_id: Optional[EntityId] = None,
        quest_id: Optional[EntityId] = None,
        notes: Optional[Description] = None,
    ) -> 'LevelUp':
        """
        Factory method for creating a new LevelUp.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            level_up_type=level_up_type,
            old_level=old_level,
            new_level=new_level,
            reward_ids=reward_ids,
            stat_increases=stat_increases or {},
            skill_points_gained=skill_points_gained,
            abilities_unlocked=abilities_unlocked,
            choices_made=choices_made,
            selected_rewards=selected_rewards,
            health_increase=health_increase,
            mana_increase=mana_increase,
            attack_increase=attack_increase,
            defense_increase=defense_increase,
            occurred_at=occurred_at or now,
            location_id=location_id,
            quest_id=quest_id,
            notes=notes,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_stat_increase(self, stat_name: str, amount: int) -> None:
        """Add a stat increase to this level up."""
        if amount <= 0:
            raise InvariantViolation("Stat increase must be positive")
        
        if not self.stat_increases:
            object.__setattr__(self, 'stat_increases', {})
        
        current = self.stat_increases.get(stat_name, 0)
        self.stat_increases[stat_name] = current + amount
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_choice(self, choice: str) -> None:
        """Record a choice made during level up."""
        if not self.choices_made:
            object.__setattr__(self, 'choices_made', [])
        
        if choice not in self.choices_made:
            self.choices_made.append(choice)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def get_total_stat_increase(self) -> int:
        """Get total stat increase across all stats."""
        if not self.stat_increases:
            return 0
        return sum(self.stat_increases.values())
    
    def get_level_difference(self) -> int:
        """Get the number of levels gained."""
        return self.new_level - self.old_level
    
    def is_milestone_level(self) -> bool:
        """Check if this is a milestone level (e.g., every 10 levels)."""
        return self.new_level % 10 == 0
    
    def is_max_level(self) -> bool:
        """Check if this is a max level achievement."""
        return self.level_up_type == LevelUpType.PRESTIGE
    
    def has_choices(self) -> bool:
        """Check if player made any choices."""
        return bool(self.choices_made)
    
    def get_summary(self) -> str:
        """Get a summary of this level up."""
        parts = [
            f"Level {self.old_level} -> {self.new_level}",
        ]
        
        if self.skill_points_gained > 0:
            parts.append(f"+{self.skill_points_gained} skill points")
        
        if self.stat_increases:
            stat_str = ", ".join(f"{k}: +{v}" for k, v in self.stat_increases.items())
            parts.append(f"Stats: {stat_str}")
        
        return ", ".join(parts)
    
    def __str__(self) -> str:
        return f"LevelUp({self.level_up_type.value}: Lv.{self.old_level} -> {self.new_level})"
    
    def __repr__(self) -> str:
        return (
            f"LevelUp(id={self.id}, character_id={self.character_id}, "
            f"old={self.old_level}, new={self.new_level})"
        )
