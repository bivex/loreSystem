"""
Progression-related value objects for the lore-based progression simulator.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class CharacterClass(str, Enum):
    """Character classes in the lore."""
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    PALADIN = "paladin"
    NECROMANCER = "necromancer"


class StatType(str, Enum):
    """Types of character stats."""
    STRENGTH = "strength"
    INTELLECT = "intellect"
    AGILITY = "agility"
    VITALITY = "vitality"
    WILLPOWER = "willpower"


class EventType(str, Enum):
    """Types of progression events."""
    LEVEL_UP = "level_up"
    STAT_INCREASE = "stat_increase"
    CLASS_CHANGE = "class_change"
    ABILITY_UNLOCK = "ability_unlock"
    QUEST_COMPLETE = "quest_complete"


@dataclass(frozen=True)
class CharacterLevel:
    """
    Character level with validation.
    
    Invariant: Must be between 1 and 100.
    """
    value: int

    MIN_LEVEL = 1
    MAX_LEVEL = 100

    def __post_init__(self):
        if not (self.MIN_LEVEL <= self.value <= self.MAX_LEVEL):
            raise ValueError(
                f"Level must be between {self.MIN_LEVEL} and {self.MAX_LEVEL}, "
                f"got {self.value}"
            )

    def __str__(self) -> str:
        return str(self.value)

    def next_level(self) -> 'CharacterLevel':
        """Return next level."""
        if self.value >= self.MAX_LEVEL:
            raise ValueError("Already at maximum level")
        return CharacterLevel(self.value + 1)


@dataclass(frozen=True)
class StatValue:
    """
    Stat value with validation.
    
    Invariant: Must be non-negative.
    """
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Stat value must be non-negative")

    def __str__(self) -> str:
        return str(self.value)

    def increase(self, amount: int) -> 'StatValue':
        """Return increased stat value."""
        return StatValue(self.value + amount)


@dataclass(frozen=True)
class ExperiencePoints:
    """
    Experience points with validation.
    
    Invariant: Must be non-negative.
    """
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Experience points must be non-negative")

    def __str__(self) -> str:
        return str(self.value)

    def add(self, amount: int) -> 'ExperiencePoints':
        """Return experience with added points."""
        return ExperiencePoints(self.value + amount)


@dataclass(frozen=True)
class TimePoint:
    """
    Discrete time point for progression simulation.
    
    Time is represented as discrete steps for formal verification.
    """
    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Time point must be non-negative")

    def __str__(self) -> str:
        return f"t{self.value}"

    def next(self) -> 'TimePoint':
        """Return next time point."""
        return TimePoint(self.value + 1)

    def __lt__(self, other: 'TimePoint') -> bool:
        return self.value < other.value

    def __le__(self, other: 'TimePoint') -> bool:
        return self.value <= other.value

    def __gt__(self, other: 'TimePoint') -> bool:
        return self.value > other.value

    def __ge__(self, other: 'TimePoint') -> bool:
        return self.value >= other.value


@dataclass(frozen=True)
class RuleReference:
    """
    Reference to a lore rule.
    
    Used for observability and formal verification.
    """
    rule_id: str
    description: str

    def __post_init__(self):
        if not self.rule_id:
            raise ValueError("Rule ID cannot be empty")
        if not self.description:
            raise ValueError("Rule description cannot be empty")

    def __str__(self) -> str:
        return f"{self.rule_id}: {self.description}"
