"""Summon entity - Summoned creature/entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Summon:
    """Represents a summoned creature or entity."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    summoner_id: str = ""
    creature_id: str = ""
    creature_name: str = ""
    power_level: int = 0  # 0-100
    summon_type: str = ""  # familiar, guardian, servant, messenger, deity
    duration_minutes: int = 0
    loyalty: int = 100  # 0-100
    abilities: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    cost: str = ""

    @classmethod
    def create(
        cls,
        tenant_id: str,
        summoner_id: str,
        creature_id: str,
        creature_name: str,
        summon_type: str,
    ) -> Self:
        """Factory method to create a new Summon."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not summoner_id:
            raise ValueError("summoner_id is required")
        if not creature_id:
            raise ValueError("creature_id is required")
        if not creature_name:
            raise ValueError("creature_name is required")
        if not summon_type:
            raise ValueError("summon_type is required")

        valid_types = ["familiar", "guardian", "servant", "messenger", "deity"]
        if summon_type not in valid_types:
            raise ValueError(f"summon_type must be one of {valid_types}")

        return cls(
            tenant_id=tenant_id,
            summoner_id=summoner_id,
            creature_id=creature_id,
            creature_name=creature_name,
            summon_type=summon_type,
        )

    def set_power(self, power: int) -> None:
        """Set power level."""
        self.power_level = max(0, min(100, power))
        self.updated_at = datetime.utcnow()

    def set_duration(self, minutes: int) -> None:
        """Set summon duration."""
        self.duration_minutes = max(0, minutes)
        self.updated_at = datetime.utcnow()

    def modify_loyalty(self, delta: int) -> None:
        """Modify loyalty."""
        self.loyalty = max(0, min(100, self.loyalty + delta))
        self.updated_at = datetime.utcnow()

    def add_ability(self, ability: str) -> None:
        """Add an ability."""
        if ability and ability not in self.abilities:
            self.abilities.append(ability)
            self.updated_at = datetime.utcnow()

    def add_requirement(self, requirement: str) -> None:
        """Add a summon requirement."""
        if requirement and requirement not in self.requirements:
            self.requirements.append(requirement)
            self.updated_at = datetime.utcnow()

    def set_cost(self, cost: str) -> None:
        """Set summon cost."""
        self.cost = cost
        self.updated_at = datetime.utcnow()

    def is_loyal(self) -> bool:
        """Check if summon is loyal."""
        return self.loyalty >= 50

    def is_rebellious(self) -> bool:
        """Check if summon is rebellious."""
        return self.loyalty <= 20

    def is_permanent(self) -> bool:
        """Check if summon is permanent."""
        return self.duration_minutes == 0

    def is_powerful(self) -> bool:
        """Check if summon is powerful."""
        return self.power_level >= 70
