"""
Template Entity

A Template defines the structure and layout for pages, with support for runes (sub-templates).
Part of the World aggregate.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from ..value_objects.common import (
    TenantId,
    EntityId,
    TemplateName,
    Content,
    Version,
    Timestamp,
    TemplateType,
)
from ..exceptions import InvariantViolation


@dataclass
class Template:
    """
    Template entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Content defines the template structure
    - Version increases monotonically
    - Runes are sub-templates within templates
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: TemplateName
    description: str
    template_type: TemplateType
    content: Content  # Template structure/layout
    rune_ids: List[EntityId]  # Sub-templates (runes)
    parent_template_id: Optional[EntityId]  # For template hierarchy
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
        name: TemplateName,
        description: str,
        template_type: TemplateType,
        content: Content,
        parent_template_id: Optional[EntityId] = None,
        rune_ids: Optional[List[EntityId]] = None,
    ) -> 'Template':
        """
        Factory method for creating a new Template.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            template_type=template_type,
            content=content,
            rune_ids=rune_ids or [],
            parent_template_id=parent_template_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_content(self, new_content: Content) -> None:
        """Update template content."""
        if str(self.content) == str(new_content):
            return
        
        object.__setattr__(self, 'content', new_content)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_rune(self, rune_id: EntityId) -> None:
        """Add a rune (sub-template) to this template."""
        if rune_id in self.rune_ids:
            return
        self.rune_ids.append(rune_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_rune(self, rune_id: EntityId) -> None:
        """Remove a rune from this template."""
        if rune_id not in self.rune_ids:
            return
        self.rune_ids.remove(rune_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_rune(self) -> bool:
        """Check if this is a rune (sub-template)."""
        return self.template_type == TemplateType.RUNE
    
    def __str__(self) -> str:
        return f"Template({self.name}, type={self.template_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Template(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.template_type.value}, version={self.version})"
        )