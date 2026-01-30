"""
LoreFragment Entity

A LoreFragment represents a piece of lore that can be discovered by players.
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
class LoreFragment:
    """
    LoreFragment entity containing discoverable lore content.
    
    Invariants:
    - Must have a valid title
    - Content cannot be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    title: str
    content: str
    rarity: str
    is_discoverable: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("LoreFragment must have a valid title")
        
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("LoreFragment content cannot be empty")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        title: str,
        content: str,
        rarity: str = "common",
        is_discoverable: bool = True
    ) -> 'LoreFragment':
        """Factory method to create a new LoreFragment."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            title=title,
            content=content,
            rarity=rarity,
            is_discoverable=is_discoverable,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
