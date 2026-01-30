"""
Internet Entity

An Internet represents a digital network or online platform
for information sharing and communication.
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
class Internet:
    """
    Internet entity for digital networks and platforms.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    network_type: str  # e.g., "Social", "News", "Forum", "Marketplace"
    platform_url: Optional[str]
    user_count: Optional[int]
    moderation_level: str  # e.g., "None", "Light", "Strict", "Full"
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
            raise ValueError("Internet platform name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Internet platform name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        network_type: str,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        platform_url: Optional[str] = None,
        moderation_level: str = "Light",
    ) -> 'Internet':
        """Factory method for creating a new Internet platform."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            network_type=network_type,
            platform_url=platform_url,
            user_count=0,
            moderation_level=moderation_level,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update platform description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_user_count(self, new_count: int) -> None:
        """Update the user count."""
        if new_count < 0:
            raise ValueError("User count cannot be negative")
        if self.user_count == new_count:
            return
        object.__setattr__(self, 'user_count', new_count)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
