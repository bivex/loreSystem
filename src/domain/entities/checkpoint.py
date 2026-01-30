"""Checkpoint entity - Auto-save points during gameplay."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Checkpoint:
    """Represents an auto-save checkpoint in the game."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""  # Display name of the checkpoint
    location_id: str = ""  # Reference to Location entity
    description: str = ""  # Flavor text description
    quest_id: Optional[str] = None  # Associated quest
    checkpoint_type: str = "story"  # "story", "combat", "exploration", "custom"
    trigger_type: str = "proximity"  # "proximity", "event", "manual", "trigger"
    trigger_position: dict = field(default_factory=dict)  # {"x": 0, "y": 0, "z": 0}
    trigger_radius: float = 5.0  # Activation radius
    is_active: bool = True  # Whether currently functional
    is_triggered: bool = False  # Whether player has passed it
    one_time_only: bool = False  # If True, triggers once per playthrough
    restores_on_trigger: bool = False  # Restore health/mana when triggered
    restore_percentage: float = 0.0  # Percentage to restore (0.0-1.0)
    spawn_on_death: bool = True  # Player respawns here on death
    icon_path: str = ""  # UI icon path
    flags: list[str] = field(default_factory=list)  # "boss_room", "temporal", etc.

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        location_id: str,
        checkpoint_type: str = "story",
        trigger_type: str = "proximity",
    ) -> Self:
        """Factory method to create a new Checkpoint."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not location_id:
            raise ValueError("location_id is required")

        valid_checkpoint_types = ["story", "combat", "exploration", "custom"]
        if checkpoint_type not in valid_checkpoint_types:
            raise ValueError(f"checkpoint_type must be one of {valid_checkpoint_types}")

        valid_trigger_types = ["proximity", "event", "manual", "trigger"]
        if trigger_type not in valid_trigger_types:
            raise ValueError(f"trigger_type must be one of {valid_trigger_types}")

        return cls(
            tenant_id=tenant_id,
            name=name,
            location_id=location_id,
            checkpoint_type=checkpoint_type,
            trigger_type=trigger_type,
        )

    def trigger(self) -> None:
        """Trigger the checkpoint (auto-save)."""
        if not self.is_triggered:
            self.is_triggered = True
            self.updated_at = datetime.utcnow()

    def reset(self) -> None:
        """Reset the checkpoint (allow re-triggering)."""
        if self.is_triggered:
            self.is_triggered = False
            self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the checkpoint."""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the checkpoint."""
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()

    def set_trigger_position(self, x: float, y: float, z: float) -> None:
        """Set the trigger position."""
        self.trigger_position = {"x": x, "y": y, "z": z}
        self.updated_at = datetime.utcnow()

    def add_flag(self, flag: str) -> None:
        """Add a flag to the checkpoint."""
        if flag not in self.flags:
            self.flags.append(flag)
            self.updated_at = datetime.utcnow()

    def remove_flag(self, flag: str) -> None:
        """Remove a flag from the checkpoint."""
        if flag in self.flags:
            self.flags.remove(flag)
            self.updated_at = datetime.utcnow()

    def can_trigger(self) -> bool:
        """Check if checkpoint can be triggered."""
        if not self.is_active:
            return False
        if self.one_time_only and self.is_triggered:
            return False
        return True
