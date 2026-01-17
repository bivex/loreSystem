"""
Note Entity

A Note represents a piece of information, reminder, or annotation in the system.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Note:
    """
    Note entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Content must be non-empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    title: str
    content: str
    tags: list[str]  # Simple string tags for organization
    is_pinned: bool  # Whether note is pinned for quick access
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        if not self.content.strip():
            raise InvariantViolation("Note content cannot be empty")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        title: str,
        content: str,
        tags: Optional[list[str]] = None,
        is_pinned: bool = False,
    ) -> 'Note':
        """
        Factory method for creating a new Note.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            title=title,
            content=content,
            tags=tags or [],
            is_pinned=is_pinned,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_content(self, new_content: str) -> None:
        """Update note content."""
        if not new_content.strip():
            raise InvariantViolation("Note content cannot be empty")
        
        if self.content == new_content:
            return
        
        object.__setattr__(self, 'content', new_content)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_title(self, new_title: str) -> None:
        """Update note title."""
        if self.title == new_title:
            return
        
        object.__setattr__(self, 'title', new_title)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the note."""
        if tag not in self.tags:
            self.tags.append(tag)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note."""
        if tag in self.tags:
            self.tags.remove(tag)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def pin(self) -> None:
        """Pin the note for quick access."""
        if self.is_pinned:
            return
        object.__setattr__(self, 'is_pinned', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def unpin(self) -> None:
        """Unpin the note."""
        if not self.is_pinned:
            return
        object.__setattr__(self, 'is_pinned', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Note({self.title})"
    
    def __repr__(self) -> str:
        return (
            f"Note(id={self.id}, world_id={self.world_id}, "
            f"title='{self.title}', pinned={self.is_pinned}, version={self.version})"
        )