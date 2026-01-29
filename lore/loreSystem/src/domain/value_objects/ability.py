"""
Character-specific value objects.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AbilityName:
    """Name of a character ability."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Ability name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Ability name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PowerLevel:
    """
    Numeric power rating for abilities.
    
    Invariant: Must be between 1 and 10 for game balance.
    """
    value: int

    MIN_POWER = 1
    MAX_POWER = 10

    def __post_init__(self):
        if not (self.MIN_POWER <= self.value <= self.MAX_POWER):
            raise ValueError(
                f"Power level must be between {self.MIN_POWER} and {self.MAX_POWER}, "
                f"got {self.value}"
            )

    def __str__(self) -> str:
        return str(self.value)

    def is_weak(self) -> bool:
        """Check if ability is weak (power <= 3)."""
        return self.value <= 3

    def is_strong(self) -> bool:
        """Check if ability is strong (power >= 8)."""
        return self.value >= 8


@dataclass(frozen=True)
class Ability:
    """
    A character's skill or power.
    
    Composite value object containing name, description, and power level.
    """
    name: AbilityName
    description: str
    power_level: PowerLevel

    def __post_init__(self):
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Ability description cannot be empty")

    def __str__(self) -> str:
        return f"{self.name} (Power: {self.power_level})"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": str(self.name),
            "description": self.description,
            "power_level": self.power_level.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Ability':
        """Create from dictionary."""
        return cls(
            name=AbilityName(data["name"]),
            description=data["description"],
            power_level=PowerLevel(data["power_level"]),
        )
