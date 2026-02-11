"""Blessing entity - Supernatural benefit."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Blessing:
    """Represents a supernatural blessing."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    blessing_name: str = ""
    source_id: str = ""  # Deity, shrine, ritual, etc.
    blessing_type: str = ""  # protection, power, wisdom, fortune, health
    power: int = 0  # 0-100
    effects: list[str] = field(default_factory=list)
    duration: str = "permanent"  # temporary, permanent, conditional
    conditions: list[str] = field(default_factory=list)
    loss_conditions: list[str] = field(default_factory=list)
    visible: bool = True

    @classmethod
    def create(
        cls,
        tenant_id: str,
        character_id: str,
        blessing_name: str,
        source_id: str,
        blessing_type: str,
    ) -> Self:
        """Factory method to create a new Blessing."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not character_id:
            raise ValueError("character_id is required")
        if not blessing_name:
            raise ValueError("blessing_name is required")
        if not source_id:
            raise ValueError("source_id is required")
        if not blessing_type:
            raise ValueError("blessing_type is required")

        valid_types = ["protection", "power", "wisdom", "fortune", "health"]
        if blessing_type not in valid_types:
            raise ValueError(f"blessing_type must be one of {valid_types}")

        return cls(
            tenant_id=tenant_id,
            character_id=character_id,
            blessing_name=blessing_name,
            source_id=source_id,
            blessing_type=blessing_type,
        )

    def set_power(self, power: int) -> None:
        """Set blessing power."""
        self.power = max(0, min(100, power))
        self.updated_at = datetime.utcnow()

    def set_duration(self, duration: str) -> None:
        """Set blessing duration."""
        valid_durations = ["temporary", "permanent", "conditional"]
        if duration not in valid_durations:
            raise ValueError(f"duration must be one of {valid_durations}")
        self.duration = duration
        self.updated_at = datetime.utcnow()

    def add_effect(self, effect: str) -> None:
        """Add an effect."""
        if effect and effect not in self.effects:
            self.effects.append(effect)
            self.updated_at = datetime.utcnow()

    def add_condition(self, condition: str) -> None:
        """Add an activation condition."""
        if condition and condition not in self.conditions:
            self.conditions.append(condition)
            self.updated_at = datetime.utcnow()

    def add_loss_condition(self, condition: str) -> None:
        """Add a loss condition."""
        if condition and condition not in self.loss_conditions:
            self.loss_conditions.append(condition)
            self.updated_at = datetime.utcnow()

    def set_visibility(self, visible: bool) -> None:
        """Set blessing visibility."""
        self.visible = visible
        self.updated_at = datetime.utcnow()

    def is_powerful(self) -> bool:
        """Check if blessing is powerful."""
        return self.power >= 70

    def is_permanent(self) -> bool:
        """Check if blessing is permanent."""
        return self.duration == "permanent"

    def is_visible(self) -> bool:
        """Check if blessing is visible."""
        return self.visible

    def is_divine(self) -> bool:
        """Check if blessing is divine (from deity)."""
        return self.source_id.startswith("deity") or "deity" in self.source_id.lower()
