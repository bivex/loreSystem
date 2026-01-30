"""
JournalPage Entity

A JournalPage represents a page in a character's journal.
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
class JournalPage:
    """
    JournalPage entity containing player-written journal entries.
    
    Invariants:
    - Must belong to a character
    - Content cannot be empty
    - Page number must be positive
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    character_id: EntityId
    page_number: int
    title: str
    content: str
    is_editable: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.page_number < 1:
            raise ValueError("JournalPage page number must be positive")
        
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("JournalPage content cannot be empty")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        character_id: EntityId,
        page_number: int,
        title: str,
        content: str,
        is_editable: bool = True
    ) -> 'JournalPage':
        """Factory method to create a new JournalPage."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            page_number=page_number,
            title=title,
            content=content,
            is_editable=is_editable,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def update_content(self, content: str) -> 'JournalPage':
        """Update the journal page content."""
        if not self.is_editable:
            raise ValueError("This journal page is not editable")
        
        return JournalPage(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            character_id=self.character_id,
            page_number=self.page_number,
            title=self.title,
            content=content,
            is_editable=self.is_editable,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
