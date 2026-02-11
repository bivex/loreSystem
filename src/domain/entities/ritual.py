"""Ritual entity - Religious ceremonial action."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Ritual:
    """Represents a religious ritual or ceremony."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""
    religion_id: str = ""
    deity_id: str = ""
    ritual_type: str = ""  # blessing, sacrifice, communion, purification, summoning
    difficulty: int = 0  # 0-100
    required_components: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    duration_minutes: int = 0
    participants_required: int = 1
    cooldown_hours: int = 0
    is_secret: bool = False

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        religion_id: str,
        ritual_type: str,
    ) -> Self:
        """Factory method to create a new Ritual."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not religion_id:
            raise ValueError("religion_id is required")
        if not ritual_type:
            raise ValueError("ritual_type is required")

        valid_types = ["blessing", "sacrifice", "communion", "purification", "summoning"]
        if ritual_type not in valid_types:
            raise ValueError(f"ritual_type must be one of {valid_types}")

        return cls(
            tenant_id=tenant_id,
            name=name,
            religion_id=religion_id,
            ritual_type=ritual_type,
        )

    def set_deity(self, deity_id: str) -> None:
        """Set associated deity."""
        self.deity_id = deity_id
        self.updated_at = datetime.utcnow()

    def set_difficulty(self, difficulty: int) -> None:
        """Set difficulty."""
        self.difficulty = max(0, min(100, difficulty))
        self.updated_at = datetime.utcnow()

    def add_component(self, component: str) -> None:
        """Add required component."""
        if component and component not in self.required_components:
            self.required_components.append(component)
            self.updated_at = datetime.utcnow()

    def add_effect(self, effect: str) -> None:
        """Add an effect."""
        if effect and effect not in self.effects:
            self.effects.append(effect)
            self.updated_at = datetime.utcnow()

    def set_duration(self, minutes: int) -> None:
        """Set ritual duration."""
        self.duration_minutes = max(0, minutes)
        self.updated_at = datetime.utcnow()

    def set_participants(self, count: int) -> None:
        """Set required participants."""
        self.participants_required = max(1, count)
        self.updated_at = datetime.utcnow()

    def set_cooldown(self, hours: int) -> None:
        """Set cooldown in hours."""
        self.cooldown_hours = max(0, hours)
        self.updated_at = datetime.utcnow()

    def set_secret(self, secret: bool) -> None:
        """Set as secret ritual."""
        self.is_secret = secret
        self.updated_at = datetime.utcnow()

    def can_be_performed(self, available_components: list[str]) -> bool:
        """Check if ritual can be performed with available components."""
        return all(comp in available_components for comp in self.required_components)

    def is_difficult(self) -> bool:
        """Check if ritual is difficult."""
        return self.difficulty >= 70

    def is_sacrificial(self) -> bool:
        """Check if ritual is a sacrifice."""
        return self.ritual_type == "sacrifice"
