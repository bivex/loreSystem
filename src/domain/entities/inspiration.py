"""
Inspiration Entity

An Inspiration represents creative ideas, prompts, or resources for storytelling.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Inspiration:
    """
    Inspiration entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Must have content or tags
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    title: str
    content: str  # The inspiration content/prompt
    category: str  # Category like "Plot", "Character", "Setting", etc.
    tags: List[str]  # Tags for organization
    source: Optional[str]  # Where this inspiration came from
    is_used: bool  # Whether this inspiration has been used
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
            raise InvariantViolation("Inspiration content cannot be empty")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        title: str,
        content: str,
        category: str,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        is_used: bool = False,
    ) -> 'Inspiration':
        """
        Factory method for creating a new Inspiration.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            source=source,
            is_used=is_used,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_content(self, new_content: str) -> None:
        """Update inspiration content."""
        if not new_content.strip():
            raise InvariantViolation("Inspiration content cannot be empty")
        
        if self.content == new_content:
            return
        
        object.__setattr__(self, 'content', new_content)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def mark_used(self) -> None:
        """Mark inspiration as used."""
        if self.is_used:
            return
        object.__setattr__(self, 'is_used', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def mark_unused(self) -> None:
        """Mark inspiration as unused."""
        if not self.is_used:
            return
        object.__setattr__(self, 'is_used', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the inspiration."""
        if tag not in self.tags:
            self.tags.append(tag)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the inspiration."""
        if tag in self.tags:
            self.tags.remove(tag)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Inspiration({self.title}, {self.category})"
    
    def __repr__(self) -> str:
        return (
            f"Inspiration(id={self.id}, world_id={self.world_id}, "
            f"title='{self.title}', category='{self.category}', used={self.is_used}, version={self.version})"
        )