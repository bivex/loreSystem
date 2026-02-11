"""SavePoint entity - Places where players can manually save."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class SavePoint:
    """Represents a save point where players can manually save their progress."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""  # Display name of the save point
    location_id: str = ""  # Reference to Location entity
    description: str = ""  # Flavor text description
    is_active: bool = True  # Whether currently usable
    save_type: str = "manual"  # "manual", "limited", "quick"
    uses_remaining: int = -1  # -1 = unlimited
    cooldown_seconds: int = 0  # Cooldown between saves
    requires_quest_id: Optional[str] = None  # Quest to unlock
    restores_health: bool = False  # Full health restore on save
    restores_mana: bool = False  # Full mana restore on save
    restores_resources: bool = False  # Full resource restore on save
    icon_path: str = ""  # UI icon path
    marker_position: dict = field(default_factory=dict)  # {"x": 0, "y": 0, "z": 0}
    interaction_radius: float = 2.0  # Radius to interact
    flags: list[str] = field(default_factory=list)  # "story_lock", "boss_room", etc.

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        location_id: str,
        description: str = "",
        save_type: str = "manual",
    ) -> Self:
        """Factory method to create a new SavePoint."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not location_id:
            raise ValueError("location_id is required")

        valid_save_types = ["manual", "limited", "quick"]
        if save_type not in valid_save_types:
            raise ValueError(f"save_type must be one of {valid_save_types}")

        return cls(
            tenant_id=tenant_id,
            name=name,
            location_id=location_id,
            description=description,
            save_type=save_type,
        )

    def activate(self) -> None:
        """Activate the save point."""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the save point."""
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()

    def use(self) -> None:
        """Use the save point (decrement uses if limited)."""
        if self.save_type == "limited" and self.uses_remaining > 0:
            self.uses_remaining -= 1
            self.updated_at = datetime.utcnow()

    def set_marker_position(self, x: float, y: float, z: float) -> None:
        """Set the marker position."""
        self.marker_position = {"x": x, "y": y, "z": z}
        self.updated_at = datetime.utcnow()

    def add_flag(self, flag: str) -> None:
        """Add a flag to the save point."""
        if flag not in self.flags:
            self.flags.append(flag)
            self.updated_at = datetime.utcnow()

    def remove_flag(self, flag: str) -> None:
        """Remove a flag from the save point."""
        if flag in self.flags:
            self.flags.remove(flag)
            self.updated_at = datetime.utcnow()

    def can_save(self) -> bool:
        """Check if player can save at this point."""
        if not self.is_active:
            return False
        if self.save_type == "limited" and self.uses_remaining <= 0:
            return False
        return True
