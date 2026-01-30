"""
Skill Entity

A Skill represents an ability or capability that a character can learn and improve.
Skills can be active (used in combat) or passive (always active).
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
    Rarity,
)
from ..exceptions import InvariantViolation


class SkillType(str, Enum):
    """Skill type classification."""
    ACTIVE = "active"  # Must be activated (combat abilities, spells)
    PASSIVE = "passive"  # Always active (stat boosts, modifiers)
    TRIGGERED = "triggered"  # Activates under specific conditions


class SkillCategory(str, Enum):
    """Skill category for organization."""
    COMBAT = "combat"
    MAGIC = "magic"
    CRAFTING = "crafting"
    SOCIAL = "social"
    STEALTH = "stealth"
    SURVIVAL = "survival"


@dataclass
class Skill:
    """
    Skill entity that defines learnable abilities.
    
    Invariants:
    - Level must be between 1-10
    - Version increases monotonically
    - Max level must be >= current level
    - Mastery must be between 0-100%
    - Cooldown must be non-negative (for active skills)
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: Optional[EntityId]  # Character that learned this skill (None = base skill definition)
    name: str
    description: Description
    skill_type: SkillType
    category: SkillCategory
    rarity: Optional[Rarity]
    
    # Skill progression
    level: int  # Current skill level (1-10)
    max_level: int  # Maximum achievable level
    experience: int  # Experience points toward next level
    experience_to_next: int  # XP needed to reach next level
    
    # Skill stats
    power: float  # Skill power multiplier
    mastery: int  # Mastery percentage (0-100)
    cooldown_seconds: Optional[int]  # Cooldown for active skills
    mana_cost: Optional[int]  # Resource cost to use
    
    # Prerequisites
    prerequisite_skill_ids: Optional[List[EntityId]]  # Skills required before learning this one
    minimum_level: int  # Minimum character level to learn
    
    # Optional metadata
    icon_id: Optional[str]  # Reference to icon asset
    tags: Optional[List[str]]  # Searchable tags
    
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
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Skill name cannot be empty")
        
        if self.level < 1 or self.level > self.max_level:
            raise InvariantViolation(
                f"Level must be between 1-{self.max_level}"
            )
        
        if self.max_level < 1:
            raise InvariantViolation("Max level must be at least 1")
        
        if self.level > self.max_level:
            raise InvariantViolation("Level cannot exceed max level")
        
        if self.mastery < 0 or self.mastery > 100:
            raise InvariantViolation("Mastery must be between 0-100")
        
        if self.cooldown_seconds is not None and self.cooldown_seconds < 0:
            raise InvariantViolation("Cooldown cannot be negative")
        
        if self.mana_cost is not None and self.mana_cost < 0:
            raise InvariantViolation("Mana cost cannot be negative")
        
        if self.minimum_level < 1:
            raise InvariantViolation("Minimum level must be at least 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        skill_type: SkillType,
        category: SkillCategory,
        character_id: Optional[EntityId] = None,
        rarity: Optional[Rarity] = None,
        level: int = 1,
        max_level: int = 10,
        experience: int = 0,
        experience_to_next: int = 100,
        power: float = 1.0,
        mastery: int = 0,
        cooldown_seconds: Optional[int] = None,
        mana_cost: Optional[int] = None,
        prerequisite_skill_ids: Optional[List[EntityId]] = None,
        minimum_level: int = 1,
        icon_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> 'Skill':
        """
        Factory method for creating a new Skill.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            name=name,
            description=description,
            skill_type=skill_type,
            category=category,
            rarity=rarity,
            level=level,
            max_level=max_level,
            experience=experience,
            experience_to_next=experience_to_next,
            power=power,
            mastery=mastery,
            cooldown_seconds=cooldown_seconds,
            mana_cost=mana_cost,
            prerequisite_skill_ids=prerequisite_skill_ids,
            minimum_level=minimum_level,
            icon_id=icon_id,
            tags=tags,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_experience(self, amount: int) -> None:
        """
        Add experience to the skill.
        
        Raises:
            InvariantViolation: If experience amount is invalid
        """
        if amount <= 0:
            raise InvariantViolation("Experience amount must be positive")
        
        self.experience += amount
        
        # Check for level up
        while self.experience >= self.experience_to_next and self.level < self.max_level:
            self.level_up()
    
    def level_up(self) -> None:
        """
        Increase skill level.
        
        Raises:
            InvariantViolation: If already at max level
        """
        if self.level >= self.max_level:
            raise InvariantViolation("Skill is already at max level")
        
        object.__setattr__(self, 'level', self.level + 1)
        object.__setattr__(self, 'experience', 0)
        object.__setattr__(self, 'experience_to_next', int(self.experience_to_next * 1.5))
        object.__setattr__(self, 'power', self.power * 1.1)  # 10% power increase per level
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increase_mastery(self, amount: int) -> None:
        """
        Increase skill mastery.
        
        Raises:
            InvariantViolation: If amount is invalid or would exceed 100%
        """
        if amount <= 0:
            raise InvariantViolation("Mastery amount must be positive")
        
        if self.mastery + amount > 100:
            raise InvariantViolation("Mastery cannot exceed 100")
        
        object.__setattr__(self, 'mastery', self.mastery + amount)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_mastered(self) -> bool:
        """Check if skill is fully mastered."""
        return self.mastery >= 100
    
    def is_max_level(self) -> bool:
        """Check if skill is at maximum level."""
        return self.level >= self.max_level
    
    def get_effective_power(self) -> float:
        """Calculate effective power including mastery bonus."""
        mastery_bonus = 1.0 + (self.mastery / 100.0 * 0.5)  # Max 50% bonus from mastery
        return self.power * mastery_bonus
    
    def __str__(self) -> str:
        return f"Skill({self.name} Lv.{self.level}/{self.max_level}, {self.skill_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Skill(id={self.id}, name='{self.name}', "
            f"level={self.level}, type={self.skill_type.value})"
        )
