"""
World Entity - Aggregate Root

A World is the top-level container for game lore, containing characters and events.
It enforces consistency boundaries and invariants.
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone

from ..value_objects.common import (
    TenantId,
    EntityId,
    WorldName,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class World:
    """
    World aggregate root.
    
    Invariants:
    - World name must be unique within tenant
    - Version increases monotonically
    - Updated timestamp >= created timestamp
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: WorldName
    description: Description
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
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: WorldName,
        description: Description,
    ) -> 'World':
        """
        Factory method for creating a new World.
        
        Ensures all required fields are initialized with valid defaults.
        """
        now = Timestamp.now()
        return cls(
            id=None,  # Set by repository on save
            tenant_id=tenant_id,
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """
        Update world description.
        
        This is a domain operation that maintains invariants.
        """
        if str(self.description) == str(new_description):
            return  # No change
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: WorldName) -> None:
        """
        Rename the world.
        
        Note: Uniqueness must be checked by repository before calling this.
        """
        if str(self.name) == str(new_name):
            return
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"World({self.name}, {self.version})"
    
    def __repr__(self) -> str:
        return (
            f"World(id={self.id}, tenant_id={self.tenant_id}, "
            f"name='{self.name}', version={self.version})"
        )
