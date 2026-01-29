"""
Location Entity

A Location represents a place in the world where events occur, items are found,
and characters are present. Locations can be hierarchical (e.g., a chest inside a house).
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    LocationType,
)
from ..exceptions import InvariantViolation


@dataclass
class Location:
    """
    Location entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Version increases monotonically
    - Can have a parent location (for hierarchical locations like "chest in house")
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    location_type: LocationType
    parent_location_id: Optional[EntityId]  # For hierarchical locations (e.g., room in house)
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
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Location name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Location name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        location_type: LocationType,
        parent_location_id: Optional[EntityId] = None,
    ) -> 'Location':
        """
        Factory method for creating a new Location.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            location_type=location_type,
            parent_location_id=parent_location_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update location description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the location."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Location name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Location name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_type(self, new_type: LocationType) -> None:
        """Change location type."""
        if self.location_type == new_type:
            return
        
        object.__setattr__(self, 'location_type', new_type)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def move_to_parent(self, new_parent_id: Optional[EntityId]) -> None:
        """
        Move location to new parent in hierarchy.
        
        Note: Must check for cycles and validity by repository.
        """
        if self.parent_location_id == new_parent_id:
            return
        
        object.__setattr__(self, 'parent_location_id', new_parent_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Location({self.name}, {self.location_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Location(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.location_type}, version={self.version})"
        )
