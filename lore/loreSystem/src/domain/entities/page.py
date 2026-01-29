"""
Page Entity

A Page represents a customizable document in the world, using templates and containing content.
Part of the World aggregate.
"""
from dataclasses import dataclass, field
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    PageName,
    Content,
    Version,
    Timestamp,
    TemplateType,
)
from ..exceptions import InvariantViolation


@dataclass
class Page:
    """
    Page entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Content must be non-empty
    - Version increases monotonically
    - Can have hierarchical structure (parent_id)
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: PageName
    content: Content
    template_id: Optional[EntityId]  # Template used for this page
    parent_id: Optional[EntityId]  # For hierarchical structure
    tag_ids: List[EntityId]  # Visual tags
    image_ids: List[EntityId]  # Images in this page
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
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: PageName,
        content: Content,
        template_id: Optional[EntityId] = None,
        parent_id: Optional[EntityId] = None,
        tag_ids: Optional[List[EntityId]] = None,
        image_ids: Optional[List[EntityId]] = None,
    ) -> 'Page':
        """
        Factory method for creating a new Page.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            content=content,
            template_id=template_id,
            parent_id=parent_id,
            tag_ids=tag_ids or [],
            image_ids=image_ids or [],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_content(self, new_content: Content) -> None:
        """Update page content."""
        if str(self.content) == str(new_content):
            return
        
        object.__setattr__(self, 'content', new_content)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_template(self, new_template_id: Optional[EntityId]) -> None:
        """Change the template used by this page."""
        if self.template_id == new_template_id:
            return
        
        object.__setattr__(self, 'template_id', new_template_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_tag(self, tag_id: EntityId) -> None:
        """Add a tag to the page."""
        if tag_id in self.tag_ids:
            return
        self.tag_ids.append(tag_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_tag(self, tag_id: EntityId) -> None:
        """Remove a tag from the page."""
        if tag_id not in self.tag_ids:
            return
        self.tag_ids.remove(tag_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_image(self, image_id: EntityId) -> None:
        """Add an image to the page."""
        if image_id in self.image_ids:
            return
        self.image_ids.append(image_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_image(self, image_id: EntityId) -> None:
        """Remove an image from the page."""
        if image_id not in self.image_ids:
            return
        self.image_ids.remove(image_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def move_to_parent(self, new_parent_id: Optional[EntityId]) -> None:
        """Move page to new parent in hierarchy."""
        if self.parent_id == new_parent_id:
            return
        object.__setattr__(self, 'parent_id', new_parent_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Page({self.name})"
    
    def __repr__(self) -> str:
        return (
            f"Page(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', version={self.version})"
        )