"""
Television Entity

A Television represents a TV broadcasting station or network that
transmits video and audio content.
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
class Television:
    """
    Television entity for video broadcasting networks.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    faction_id: Optional[EntityId]
    channel_number: Optional[int]
    network_name: Optional[str]
    broadcast_format: str  # e.g., "SD", "HD", "4K"
    content_focus: str  # e.g., "News", "Entertainment", "Sports", "Documentary"
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
            raise ValueError("Television name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Television name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        content_focus: str,
        broadcast_format: str = "HD",
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        channel_number: Optional[int] = None,
        network_name: Optional[str] = None,
    ) -> 'Television':
        """Factory method for creating a new Television."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            faction_id=faction_id,
            channel_number=channel_number,
            network_name=network_name,
            broadcast_format=broadcast_format,
            content_focus=content_focus,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update television description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_active_status(self, is_active: bool) -> None:
        """Set the active status of the TV station."""
        if self.is_active == is_active:
            return
        object.__setattr__(self, 'is_active', is_active)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
