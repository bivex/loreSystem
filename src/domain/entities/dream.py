"""
Dream Entity

A Dream represents a dream sequence or vision.
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
class Dream:
    """
    Dream entity containing dream sequences and visions.
    
    Invariants:
    - Must belong to a character
    - Dream content cannot be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    character_id: EntityId
    title: str
    content: str
    dream_type: str
    lucidity_level: int
    is_recurring: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("Dream content cannot be empty")
        
        if self.lucidity_level < 0 or self.lucidity_level > 10:
            raise ValueError("Lucidity level must be between 0 and 10")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        character_id: EntityId,
        title: str,
        content: str,
        dream_type: str = "normal",
        lucidity_level: int = 0,
        is_recurring: bool = False
    ) -> 'Dream':
        """Factory method to create a new Dream."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            title=title,
            content=content,
            dream_type=dream_type,
            lucidity_level=lucidity_level,
            is_recurring=is_recurring,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
