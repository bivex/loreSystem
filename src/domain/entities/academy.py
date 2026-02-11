"""
Academy Entity

An Academy represents an educational institution for advanced learning,
specializing in arts, sciences, or magical studies.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


@dataclass
class Academy:
    """
    Academy entity for educational institutions.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    - May belong to a World or Faction
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    faction_id: Optional[EntityId]
    location_id: Optional[EntityId]
    specialization: str  # e.g., "Magic", "Warfare", "Science", "Arts"
    founded_at: Optional[Timestamp]
    dean_name: Optional[str]
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
            raise ValueError("Academy name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Academy name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        specialization: str,
        world_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        dean_name: Optional[str] = None,
    ) -> 'Academy':
        """Factory method for creating a new Academy."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            faction_id=faction_id,
            location_id=location_id,
            specialization=specialization,
            founded_at=None,
            dean_name=dean_name,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update academy description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the academy."""
        if self.name == new_name:
            return
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Academy name cannot be empty")
        if len(new_name) > 255:
            raise ValueError("Academy name must be <= 255 characters")
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def assign_dean(self, new_dean_name: str) -> None:
        """Assign a new dean."""
        if self.dean_name == new_dean_name:
            return
        object.__setattr__(self, 'dean_name', new_dean_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
