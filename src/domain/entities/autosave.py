"""Autosave entity - Auto-save system entries."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Autosave:
    """Represents an auto-save entry in the game."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""  # Display name of the autosave
    location_id: str = ""  # Reference to Location entity
    description: str = ""  # Flavor text description
    autosave_type: str = "interval"  # "interval", "event", "zone_change", "custom"
    trigger_condition: str = ""  # Description of trigger condition
    is_active: bool = True  # Whether currently functional
    interval_seconds: int = 0  # Interval for interval-based autosaves
    last_triggered_at: Optional[datetime] = None  # Last trigger timestamp
    max_saves: int = 3  # Maximum number of autosaves to keep
    overwrite_oldest: bool = True  # Overwrite oldest when max reached
    save_on_important_event: bool = False  # Save on important story events
    save_on_zone_change: bool = False  # Save when changing zones
    save_on_combat_end: bool = False  # Save after combat ends
    save_on_pickup: bool = False  # Save on important item pickup
    priority: int = 0  # Higher priority autosaves override lower
    icon_path: str = ""  # UI icon path
    flags: list[str] = field(default_factory=list)  # "temporal", "safe_mode", etc.

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        location_id: str,
        autosave_type: str = "interval",
    ) -> Self:
        """Factory method to create a new Autosave."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not location_id:
            raise ValueError("location_id is required")

        valid_autosave_types = ["interval", "event", "zone_change", "custom"]
        if autosave_type not in valid_autosave_types:
            raise ValueError(f"autosave_type must be one of {valid_autosave_types}")

        return cls(
            tenant_id=tenant_id,
            name=name,
            location_id=location_id,
            autosave_type=autosave_type,
        )

    def trigger(self) -> None:
        """Trigger the autosave."""
        self.last_triggered_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the autosave."""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the autosave."""
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()

    def set_interval(self, seconds: int) -> None:
        """Set the autosave interval."""
        if seconds < 0:
            raise ValueError("interval_seconds must be non-negative")
        self.interval_seconds = seconds
        self.updated_at = datetime.utcnow()

    def add_flag(self, flag: str) -> None:
        """Add a flag to the autosave."""
        if flag not in self.flags:
            self.flags.append(flag)
            self.updated_at = datetime.utcnow()

    def remove_flag(self, flag: str) -> None:
        """Remove a flag from the autosave."""
        if flag in self.flags:
            self.flags.remove(flag)
            self.updated_at = datetime.utcnow()

    def can_trigger(self) -> bool:
        """Check if autosave can trigger."""
        if not self.is_active:
            return False
        if self.autosave_type == "interval" and self.interval_seconds <= 0:
            return False
        return True

    def time_since_last_trigger(self) -> Optional[float]:
        """Get seconds since last trigger, or None if never triggered."""
        if self.last_triggered_at is None:
            return None
        delta = datetime.utcnow() - self.last_triggered_at
        return delta.total_seconds()
