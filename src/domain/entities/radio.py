"""
Radio Entity

A Radio represents a broadcasting station that transmits audio content,
including news, music, and entertainment.
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
class Radio:
    """
    Radio entity for audio broadcasting stations.
    
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
    frequency: Optional[str]  # e.g., "98.5 FM", "102.7 FM"
    station_manager: Optional[str]
    broadcast_range: str  # e.g., "Local", "Regional", "National", "International"
    content_type: str  # e.g., "Music", "News", "Talk", "Mixed"
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
            raise ValueError("Radio name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Radio name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        content_type: str,
        broadcast_range: str = "Local",
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        frequency: Optional[str] = None,
        station_manager: Optional[str] = None,
    ) -> 'Radio':
        """Factory method for creating a new Radio."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            faction_id=faction_id,
            frequency=frequency,
            station_manager=station_manager,
            broadcast_range=broadcast_range,
            content_type=content_type,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update radio description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_active_status(self, is_active: bool) -> None:
        """Set the active status of the radio station."""
        if self.is_active == is_active:
            return
        object.__setattr__(self, 'is_active', is_active)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
