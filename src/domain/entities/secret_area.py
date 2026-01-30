"""
SecretArea Entity

A SecretArea represents a hidden location that can only be accessed
through specific means or by solving puzzles.
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
class SecretArea:
    """
    SecretArea entity for hidden locations.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    parent_location_id: Optional[EntityId]
    discovery_method: str  # e.g., "Key", "Code", "Secret Door", "Quest Reward"
    difficulty_level: str  # e.g., "Easy", "Medium", "Hard", "Expert"
    discovery_count: Optional[int]
    is_discovered: bool
    is_active: bool
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
            raise ValueError("SecretArea name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("SecretArea name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        discovery_method: str,
        difficulty_level: str = "Medium",
        is_discovered: bool = False,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        parent_location_id: Optional[EntityId] = None,
    ) -> 'SecretArea':
        """Factory method for creating a new SecretArea."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            parent_location_id=parent_location_id,
            discovery_method=discovery_method,
            difficulty_level=difficulty_level,
            discovery_count=0,
            is_discovered=is_discovered,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update secret area description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def discover(self) -> None:
        """Mark the secret area as discovered."""
        if self.is_discovered:
            return
        object.__setattr__(self, 'is_discovered', True)
        object.__setattr__(self, 'discovery_count', (self.discovery_count or 0) + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def increment_discovery_count(self) -> None:
        """Increment the discovery count."""
        object.__setattr__(self, 'discovery_count', (self.discovery_count or 0) + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
