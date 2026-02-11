"""SpawnPoint entity - Locations where entities spawn."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self, List


@dataclass
class SpawnPoint:
    """Represents a spawn point for entities (players, NPCs, monsters, items)."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""  # Display name of the spawn point
    location_id: str = ""  # Reference to Location entity
    description: str = ""  # Flavor text description
    entity_type: str = "npc"  # "player", "npc", "monster", "item", "boss"
    entity_ids: List[str] = field(default_factory=list)  # IDs of entities that can spawn
    spawn_position: dict = field(default_factory=dict)  # {"x": 0, "y": 0, "z": 0}
    spawn_rotation: dict = field(default_factory=dict)  # {"x": 0, "y": 0, "z": 0}
    spawn_radius: float = 0.0  # Random spawn radius (0 = exact position)
    is_active: bool = True  # Whether currently functional
    max_entities: int = 1  # Maximum concurrent entities
    current_count: int = 0  # Current number of spawned entities
    spawn_type: str = "immediate"  # "immediate", "wave", "timed", "conditional"
    spawn_interval: int = 0  # Seconds between spawns (for timed)
    spawn_wave_count: int = 0  # Number of entities per wave
    spawn_wave_delay: int = 0  # Delay between waves
    requires_quest_id: Optional[str] = None  # Quest to activate
    requires_level: int = 0  # Minimum level to spawn
    respawn_time: int = 0  # Seconds before respawn (0 = no respawn)
    conditions: List[str] = field(default_factory=list)  # Spawn conditions
    flags: List[str] = field(default_factory=list)  # "boss_room", "temporal", etc.

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        location_id: str,
        entity_type: str = "npc",
        spawn_type: str = "immediate",
    ) -> Self:
        """Factory method to create a new SpawnPoint."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not location_id:
            raise ValueError("location_id is required")

        valid_entity_types = ["player", "npc", "monster", "item", "boss"]
        if entity_type not in valid_entity_types:
            raise ValueError(f"entity_type must be one of {valid_entity_types}")

        valid_spawn_types = ["immediate", "wave", "timed", "conditional"]
        if spawn_type not in valid_spawn_types:
            raise ValueError(f"spawn_type must be one of {valid_spawn_types}")

        return cls(
            tenant_id=tenant_id,
            name=name,
            location_id=location_id,
            entity_type=entity_type,
            spawn_type=spawn_type,
        )

    def activate(self) -> None:
        """Activate the spawn point."""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate the spawn point."""
        if self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()

    def add_entity(self, entity_id: str) -> None:
        """Add an entity to the spawn list."""
        if entity_id not in self.entity_ids:
            self.entity_ids.append(entity_id)
            self.updated_at = datetime.utcnow()

    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity from the spawn list."""
        if entity_id in self.entity_ids:
            self.entity_ids.remove(entity_id)
            self.updated_at = datetime.utcnow()

    def set_spawn_position(self, x: float, y: float, z: float) -> None:
        """Set the spawn position."""
        self.spawn_position = {"x": x, "y": y, "z": z}
        self.updated_at = datetime.utcnow()

    def set_spawn_rotation(self, x: float, y: float, z: float) -> None:
        """Set the spawn rotation."""
        self.spawn_rotation = {"x": x, "y": y, "z": z}
        self.updated_at = datetime.utcnow()

    def increment_count(self) -> None:
        """Increment the current entity count."""
        self.current_count += 1
        self.updated_at = datetime.utcnow()

    def decrement_count(self) -> None:
        """Decrement the current entity count."""
        if self.current_count > 0:
            self.current_count -= 1
            self.updated_at = datetime.utcnow()

    def add_condition(self, condition: str) -> None:
        """Add a spawn condition."""
        if condition not in self.conditions:
            self.conditions.append(condition)
            self.updated_at = datetime.utcnow()

    def remove_condition(self, condition: str) -> None:
        """Remove a spawn condition."""
        if condition in self.conditions:
            self.conditions.remove(condition)
            self.updated_at = datetime.utcnow()

    def add_flag(self, flag: str) -> None:
        """Add a flag to the spawn point."""
        if flag not in self.flags:
            self.flags.append(flag)
            self.updated_at = datetime.utcnow()

    def remove_flag(self, flag: str) -> None:
        """Remove a flag from the spawn point."""
        if flag in self.flags:
            self.flags.remove(flag)
            self.updated_at = datetime.utcnow()

    def can_spawn(self) -> bool:
        """Check if spawn point can spawn entities."""
        if not self.is_active:
            return False
        if self.max_entities > 0 and self.current_count >= self.max_entities:
            return False
        return True
