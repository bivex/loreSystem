"""Curse entity - Supernatural affliction."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Curse:
    """Represents a supernatural curse."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    curse_name: str = ""
    source_id: str = ""  # Who/what caused the curse
    severity: int = 0  # 0-100
    effects: list[str] = field(default_factory=list)
    symptoms: list[str] = field(default_factory=list)
    duration: str = "permanent"  # temporary, permanent, until_cured
    removal_conditions: list[str] = field(default_factory=list)
    spread_type: str = "none"  # none, contact, bloodline, area
    cure_methods: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        character_id: str,
        curse_name: str,
        source_id: str,
    ) -> Self:
        """Factory method to create a new Curse."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not character_id:
            raise ValueError("character_id is required")
        if not curse_name:
            raise ValueError("curse_name is required")
        if not source_id:
            raise ValueError("source_id is required")

        return cls(
            tenant_id=tenant_id,
            character_id=character_id,
            curse_name=curse_name,
            source_id=source_id,
        )

    def set_severity(self, severity: int) -> None:
        """Set curse severity."""
        self.severity = max(0, min(100, severity))
        self.updated_at = datetime.utcnow()

    def set_duration(self, duration: str) -> None:
        """Set curse duration."""
        valid_durations = ["temporary", "permanent", "until_cured"]
        if duration not in valid_durations:
            raise ValueError(f"duration must be one of {valid_durations}")
        self.duration = duration
        self.updated_at = datetime.utcnow()

    def add_effect(self, effect: str) -> None:
        """Add an effect."""
        if effect and effect not in self.effects:
            self.effects.append(effect)
            self.updated_at = datetime.utcnow()

    def add_symptom(self, symptom: str) -> None:
        """Add a symptom."""
        if symptom and symptom not in self.symptoms:
            self.symptoms.append(symptom)
            self.updated_at = datetime.utcnow()

    def add_removal_condition(self, condition: str) -> None:
        """Add a removal condition."""
        if condition and condition not in self.removal_conditions:
            self.removal_conditions.append(condition)
            self.updated_at = datetime.utcnow()

    def set_spread_type(self, spread_type: str) -> None:
        """Set spread type."""
        valid_spreads = ["none", "contact", "bloodline", "area"]
        if spread_type not in valid_spreads:
            raise ValueError(f"spread_type must be one of {valid_spreads}")
        self.spread_type = spread_type
        self.updated_at = datetime.utcnow()

    def add_cure_method(self, method: str) -> None:
        """Add a cure method."""
        if method and method not in self.cure_methods:
            self.cure_methods.append(method)
            self.updated_at = datetime.utcnow()

    def is_severe(self) -> bool:
        """Check if curse is severe."""
        return self.severity >= 70

    def is_minor(self) -> bool:
        """Check if curse is minor."""
        return self.severity <= 30

    def is_contagious(self) -> bool:
        """Check if curse spreads."""
        return self.spread_type != "none"

    def is_inheritable(self) -> bool:
        """Check if curse passes to offspring."""
        return self.spread_type == "bloodline"

    def is_permanent(self) -> bool:
        """Check if curse is permanent."""
        return self.duration == "permanent"
