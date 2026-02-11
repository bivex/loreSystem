"""
CodexEntry Entity

A CodexEntry represents an organized knowledge entry in a game's codex.
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
class CodexEntry:
    """
    CodexEntry entity containing structured knowledge.
    
    Invariants:
    - Must have a valid title and category
    - Content cannot be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    title: str
    category: str
    content: str
    unlock_condition: str
    is_unlocked: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("CodexEntry must have a valid title")
        
        if not self.category or len(self.category.strip()) == 0:
            raise ValueError("CodexEntry must have a valid category")
        
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("CodexEntry content cannot be empty")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        title: str,
        category: str,
        content: str,
        unlock_condition: str = ""
    ) -> 'CodexEntry':
        """Factory method to create a new CodexEntry."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            title=title,
            category=category,
            content=content,
            unlock_condition=unlock_condition,
            is_unlocked=False,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def unlock(self) -> 'CodexEntry':
        """Unlock the codex entry."""
        if self.is_unlocked:
            return self
        
        return CodexEntry(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            title=self.title,
            category=self.category,
            content=self.content,
            unlock_condition=self.unlock_condition,
            is_unlocked=True,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
