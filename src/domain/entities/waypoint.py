"""Waypoint entity - Navigation points on the map."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Waypoint:
    """Represents a waypoint navigation point in the game world."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""  # Display name of the waypoint
    location_id: str = ""  # Reference to Location entity
    description: str = ""  # Flavor text description
    is_discovered: bool = False  # Whether player has discovered it
    is_active: bool = True  # Whether currently usable
    is_primary: bool = False  # Primary quest waypoint
    quest_id: Optional[str] = None  # Associated quest
    waypoint_type: str = "navigation"  # "navigation", "objective", "collection", etc.
    priority: int = 0  # Higher = more important
    marker_type: str = "default"  # "star", "skull", "chest", etc.
    marker_color: str = "white"  # UI marker color
    marker_position: dict = field(default_factory=dict)  # {"x": 0, "y": 0, "z": 0}
    radius: float = 10.0  # Activation radius
    show_on_minimap: bool = True
    show_on_compass: bool = True
    flags: list[str] = field(default_factory=list)  # "temporal", "hidden", etc.

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        location_id: str,
        waypoint_type: str = "navigation",
        quest_id: Optional[str] = None,
    ) -> Self:
        """Factory method to create a new Waypoint."""
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
            waypoint_type=waypoint_type,
            quest_id=quest_id,
        )

    def discover(self) -> None:
        """Mark waypoint as discovered."""
        if not self.is_discovered:
            self.is_discovered = True
            self.updated_at = datetime.utcnow()

    def hide(self) -> None:
        """Hide the waypoint (undiscover)."""
        if self.is_discovered:
            self.is_discovered = False
            self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the waypoint."""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the waypoint."""
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()

    def set_as_primary(self) -> None:
        """Set as primary waypoint."""
        if not self.is_primary:
            self.is_primary = True
            self.updated_at = datetime.utcnow()

    def unset_primary(self) -> None:
        """Unset as primary waypoint."""
        if self.is_primary:
            self.is_primary = False
            self.updated_at = datetime.utcnow()

    def set_marker_position(self, x: float, y: float, z: float) -> None:
        """Set the marker position."""
        self.marker_position = {"x": x, "y": y, "z": z}
        self.updated_at = datetime.utcnow()

    def add_flag(self, flag: str) -> None:
        """Add a flag to the waypoint."""
        if flag not in self.flags:
            self.flags.append(flag)
            self.updated_at = datetime.utcnow()

    def remove_flag(self, flag: str) -> None:
        """Remove a flag from the waypoint."""
        if flag in self.flags:
            self.flags.remove(flag)
            self.updated_at = datetime.utcnow()
