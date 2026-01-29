"""
Map Entity

A Map represents a visual representation of locations, regions, or layouts in the world.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Map:
    """
    Map entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Must have at least one image or description
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Optional[str]
    image_ids: List[EntityId]  # Images that make up this map
    location_ids: List[EntityId]  # Locations marked on this map
    scale: Optional[str]  # Map scale (e.g., "1 inch = 5 miles")
    is_interactive: bool  # Whether map supports interactive elements
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        if not self.image_ids and not self.description:
            raise InvariantViolation("Map must have at least one image or description")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Optional[str] = None,
        image_ids: Optional[List[EntityId]] = None,
        location_ids: Optional[List[EntityId]] = None,
        scale: Optional[str] = None,
        is_interactive: bool = False,
    ) -> 'Map':
        """
        Factory method for creating a new Map.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            image_ids=image_ids or [],
            location_ids=location_ids or [],
            scale=scale,
            is_interactive=is_interactive,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_image(self, image_id: EntityId) -> None:
        """Add an image to the map."""
        if image_id in self.image_ids:
            return
        self.image_ids.append(image_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_image(self, image_id: EntityId) -> None:
        """Remove an image from the map."""
        if image_id not in self.image_ids:
            return
        self.image_ids.remove(image_id)
        # Check invariant after removal
        if not self.image_ids and not self.description:
            raise InvariantViolation("Map must have at least one image or description")
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_location(self, location_id: EntityId) -> None:
        """Add a location marker to the map."""
        if location_id in self.location_ids:
            return
        self.location_ids.append(location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_location(self, location_id: EntityId) -> None:
        """Remove a location marker from the map."""
        if location_id not in self.location_ids:
            return
        self.location_ids.remove(location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_description(self, new_description: Optional[str]) -> None:
        """Update map description."""
        if self.description == new_description:
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Map({self.name})"
    
    def __repr__(self) -> str:
        return (
            f"Map(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', interactive={self.is_interactive}, version={self.version})"
        )