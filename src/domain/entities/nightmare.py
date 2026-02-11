"""
Nightmare Entity

A Nightmare represents a nightmare or horror sequence.
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
class Nightmare:
    """
    Nightmare entity containing horror sequences and nightmares.
    
    Invariants:
    - Must belong to a character
    - Nightmare content cannot be empty
    - Fear level must be valid
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    character_id: EntityId
    title: str
    content: str
    fear_level: int
    trauma_level: int
    is_lucid: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("Nightmare content cannot be empty")
        
        if self.fear_level < 0 or self.fear_level > 10:
            raise ValueError("Fear level must be between 0 and 10")
        
        if self.trauma_level < 0 or self.trauma_level > 10:
            raise ValueError("Trauma level must be between 0 and 10")
        
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
        fear_level: int = 7,
        trauma_level: int = 3,
        is_lucid: bool = False
    ) -> 'Nightmare':
        """Factory method to create a new Nightmare."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            title=title,
            content=content,
            fear_level=fear_level,
            trauma_level=trauma_level,
            is_lucid=is_lucid,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
