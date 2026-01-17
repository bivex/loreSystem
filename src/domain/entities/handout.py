"""
Handout Entity

A Handout represents documents or materials given to players during sessions.
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
class Handout:
    """
    Handout entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Must have content or attachments
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    title: str
    content: Optional[str]  # Text content
    image_ids: List[EntityId]  # Attached images
    session_id: Optional[EntityId]  # Session this handout was given in
    is_revealed: bool  # Whether handout has been given to players
    reveal_timing: Optional[str]  # When/how to reveal the handout
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
        if not self.content and not self.image_ids:
            raise InvariantViolation("Handout must have content or attachments")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        title: str,
        content: Optional[str] = None,
        image_ids: Optional[List[EntityId]] = None,
        session_id: Optional[EntityId] = None,
        reveal_timing: Optional[str] = None,
        is_revealed: bool = False,
    ) -> 'Handout':
        """
        Factory method for creating a new Handout.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            title=title,
            content=content,
            image_ids=image_ids or [],
            session_id=session_id,
            is_revealed=is_revealed,
            reveal_timing=reveal_timing,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_content(self, new_content: Optional[str]) -> None:
        """Update handout content."""
        if self.content == new_content:
            return
        
        object.__setattr__(self, 'content', new_content)
        # Check invariant after update
        if not self.content and not self.image_ids:
            raise InvariantViolation("Handout must have content or attachments")
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_image(self, image_id: EntityId) -> None:
        """Add an image attachment."""
        if image_id in self.image_ids:
            return
        self.image_ids.append(image_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_image(self, image_id: EntityId) -> None:
        """Remove an image attachment."""
        if image_id not in self.image_ids:
            return
        self.image_ids.remove(image_id)
        # Check invariant after removal
        if not self.content and not self.image_ids:
            raise InvariantViolation("Handout must have content or attachments")
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def reveal(self) -> None:
        """Mark handout as revealed to players."""
        if self.is_revealed:
            return
        object.__setattr__(self, 'is_revealed', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def unreveal(self) -> None:
        """Mark handout as not yet revealed."""
        if not self.is_revealed:
            return
        object.__setattr__(self, 'is_revealed', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Handout({self.title}, revealed={self.is_revealed})"
    
    def __repr__(self) -> str:
        return (
            f"Handout(id={self.id}, world_id={self.world_id}, "
            f"title='{self.title}', revealed={self.is_revealed}, version={self.version})"
        )