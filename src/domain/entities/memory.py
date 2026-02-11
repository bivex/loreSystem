"""
Memory Entity

A Memory represents a stored memory or experience.
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
class Memory:
    """
    Memory entity containing stored experiences.
    
    Invariants:
    - Must belong to a character
    - Memory type must be valid
    - Description cannot be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    character_id: EntityId
    memory_type: str
    description: str
    emotional_intensity: int
    is_replayable: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.memory_type or len(self.memory_type.strip()) == 0:
            raise ValueError("Memory must have a valid memory type")
        
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Memory description cannot be empty")
        
        if self.emotional_intensity < 0 or self.emotional_intensity > 10:
            raise ValueError("Emotional intensity must be between 0 and 10")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        character_id: EntityId,
        memory_type: str,
        description: str,
        emotional_intensity: int = 5,
        is_replayable: bool = True
    ) -> 'Memory':
        """Factory method to create a new Memory."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            memory_type=memory_type,
            description=description,
            emotional_intensity=emotional_intensity,
            is_replayable=is_replayable,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def forget(self) -> 'Memory':
        """Mark the memory as forgotten."""
        return Memory(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            character_id=self.character_id,
            memory_type=f"{self.memory_type}_forgotten",
            description=self.description,
            emotional_intensity=self.emotional_intensity,
            is_replayable=False,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
