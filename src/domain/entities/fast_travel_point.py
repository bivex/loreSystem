"""FastTravelPoint entity - Points where players can fast travel."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class FastTravelPoint:
    """Represents a fast travel point in the game world."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""  # Display name of the fast travel point
    location_id: str = ""  # Reference to Location entity
    description: str = ""  # Flavor text description
    is_unlocked: bool = False  # Whether player has discovered it
    is_active: bool = True  # Whether currently usable
    requires_quest_id: Optional[str] = None  # Quest to unlock
    requires_level: int = 0  # Minimum level to use
    cost_gold: int = 0  # Gold cost to travel
    cost_resource: str = ""  # Custom resource type
    cost_amount: int = 0  # Custom resource amount
    cooldown_seconds: int = 0  # Cooldown between uses
    icon_path: str = ""  # UI icon path
    marker_position: dict = field(default_factory=dict)  # {"x": 0, "y": 0, "z": 0}
    flags: list[str] = field(default_factory=list)  # "story_lock", "boss_lock", etc.

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        location_id: str,
        description: str = "",
        requires_quest_id: Optional[str] = None,
    ) -> Self:
        """Factory method to create a new FastTravelPoint."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not location_id:
            raise ValueError("location_id is required")

        return cls(
            tenant_id=tenant_id,
            name=name,
            location_id=location_id,
            description=description,
            requires_quest_id=requires_quest_id,
        )

    def unlock(self) -> None:
        """Unlock the fast travel point."""
        if not self.is_unlocked:
            self.is_unlocked = True
            self.updated_at = datetime.utcnow()

    def lock(self) -> None:
        """Lock the fast travel point."""
        if self.is_unlocked:
            self.is_unlocked = False
            self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the fast travel point."""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the fast travel point."""
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()

    def set_marker_position(self, x: float, y: float, z: float) -> None:
        """Set the marker position."""
        self.marker_position = {"x": x, "y": y, "z": z}
        self.updated_at = datetime.utcnow()

    def add_flag(self, flag: str) -> None:
        """Add a flag to the fast travel point."""
        if flag not in self.flags:
            self.flags.append(flag)
            self.updated_at = datetime.utcnow()

    def remove_flag(self, flag: str) -> None:
        """Remove a flag from the fast travel point."""
        if flag in self.flags:
            self.flags.remove(flag)
            self.updated_at = datetime.utcnow()

    def can_use(self, player_level: int, player_gold: int = 0) -> bool:
        """Check if player can use this fast travel point."""
        if not self.is_unlocked or not self.is_active:
            return False
        if player_level < self.requires_level:
            return False
        if player_gold < self.cost_gold:
            return False
        return True
