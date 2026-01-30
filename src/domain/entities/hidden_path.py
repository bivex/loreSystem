"""
HiddenPath Entity

A HiddenPath represents a concealed route or passage that connects
two locations, often requiring special actions to reveal.
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
class HiddenPath:
    """
    HiddenPath entity for concealed routes.
    
    Invariants:
    - Name must not be empty
    - Both endpoints must be specified
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    start_location_id: EntityId
    end_location_id: EntityId
    reveal_method: str  # e.g., "Switch", "Key Item", "Spell", "Time of Day"
    path_type: str  # e.g., "Tunnel", "Teleporter", "Secret Door", "Underground"
    is_one_way: bool
    is_revealed: bool
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
            raise ValueError("HiddenPath name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("HiddenPath name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        start_location_id: EntityId,
        end_location_id: EntityId,
        reveal_method: str,
        path_type: str = "Secret Door",
        is_one_way: bool = False,
        is_revealed: bool = False,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
    ) -> 'HiddenPath':
        """Factory method for creating a new HiddenPath."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            start_location_id=start_location_id,
            end_location_id=end_location_id,
            reveal_method=reveal_method,
            path_type=path_type,
            is_one_way=is_one_way,
            is_revealed=is_revealed,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update hidden path description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def reveal(self) -> None:
        """Reveal the hidden path."""
        if self.is_revealed:
            return
        object.__setattr__(self, 'is_revealed', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def hide(self) -> None:
        """Hide the path again."""
        if not self.is_revealed:
            return
        object.__setattr__(self, 'is_revealed', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
