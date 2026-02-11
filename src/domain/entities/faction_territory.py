"""FactionTerritory entity - Faction controlled territory."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class FactionTerritory:
    """Represents territory controlled by a faction."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    faction_id: str = ""
    territory_type: str = ""  # region, city, dungeon, outpost
    location_id: str = ""  # Reference to Location entity
    level_of_control: int = 0  # 0-100 percentage
    borders_with: list[str] = field(default_factory=list)  # Other faction IDs
    resources: list[str] = field(default_factory=list)
    importance: str = "minor"  # minor, standard, major, capital

    @classmethod
    def create(
        cls,
        tenant_id: str,
        faction_id: str,
        territory_type: str,
        location_id: str,
    ) -> Self:
        """Factory method to create a new FactionTerritory."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not faction_id:
            raise ValueError("faction_id is required")
        if not territory_type:
            raise ValueError("territory_type is required")
        if not location_id:
            raise ValueError("location_id is required")

        valid_types = ["region", "city", "dungeon", "outpost"]
        if territory_type not in valid_types:
            raise ValueError(f"territory_type must be one of {valid_types}")

        return cls(
            tenant_id=tenant_id,
            faction_id=faction_id,
            territory_type=territory_type,
            location_id=location_id,
        )

    def set_control_level(self, level: int) -> None:
        """Set the level of control."""
        self.level_of_control = max(0, min(100, level))
        self.updated_at = datetime.utcnow()

    def add_border(self, faction_id: str) -> None:
        """Add a bordering faction."""
        if faction_id and faction_id not in self.borders_with:
            self.borders_with.append(faction_id)
            self.updated_at = datetime.utcnow()

    def add_resource(self, resource: str) -> None:
        """Add a resource found in territory."""
        if resource and resource not in self.resources:
            self.resources.append(resource)
            self.updated_at = datetime.utcnow()

    def set_importance(self, importance: str) -> None:
        """Set territory importance."""
        valid_levels = ["minor", "standard", "major", "capital"]
        if importance not in valid_levels:
            raise ValueError(f"importance must be one of {valid_levels}")
        self.importance = importance
        self.updated_at = datetime.utcnow()

    def is_under_siege(self) -> bool:
        """Check if territory is under siege (control < 50%)."""
        return self.level_of_control < 50

    def is_stronghold(self) -> bool:
        """Check if territory is a stronghold (control >= 90%)."""
        return self.level_of_control >= 90

    def borders_enemy(self, enemy_faction_id: str) -> bool:
        """Check if borders with specific faction."""
        return enemy_faction_id in self.borders_with
