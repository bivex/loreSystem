"""
Museum Entity

A Museum represents an institution that collects, preserves, and displays
objects of artistic, cultural, historical, or scientific importance.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


@dataclass
class Museum:
    """
    Museum entity for preserving and displaying important objects.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    location_id: Optional[EntityId]
    curator_name: Optional[str]
    artifact_count: Optional[int]
    museum_type: str  # e.g., "Art", "History", "Science", "Natural History"
    admission_fee: Optional[float]
    is_open: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError("Updated timestamp must be >= created timestamp")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Museum name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Museum name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        museum_type: str,
        is_open: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        curator_name: Optional[str] = None,
        admission_fee: Optional[float] = None,
    ) -> 'Museum':
        """Factory method for creating a new Museum."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            curator_name=curator_name,
            artifact_count=0,
            museum_type=museum_type,
            admission_fee=admission_fee,
            is_open=is_open,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update museum description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_open_status(self, is_open: bool) -> None:
        """Set the open status of the museum."""
        if self.is_open == is_open:
            return
        object.__setattr__(self, 'is_open', is_open)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
