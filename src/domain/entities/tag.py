"""
Tag Entity

A Tag provides visual organization and categorization for pages and other entities.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    TagName,
    Version,
    Timestamp,
    TagType,
)
from ..exceptions import InvariantViolation


@dataclass
class Tag:
    """
    Tag entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Name must be unique within world and type
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: TagName
    tag_type: TagType
    color: Optional[str]  # Hex color for visual representation
    description: Optional[str]
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
        if self.color and not self._is_valid_hex_color(self.color):
            raise InvariantViolation("Color must be valid hex format")
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Validate hex color format."""
        if not color.startswith('#'):
            return False
        try:
            int(color[1:], 16)
            return len(color) == 7  # #RRGGBB
        except ValueError:
            return False
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: TagName,
        tag_type: TagType,
        color: Optional[str] = None,
        description: Optional[str] = None,
    ) -> 'Tag':
        """
        Factory method for creating a new Tag.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            tag_type=tag_type,
            color=color,
            description=description,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_color(self, new_color: Optional[str]) -> None:
        """Update tag color."""
        if self.color == new_color:
            return
        if new_color and not self._is_valid_hex_color(new_color):
            raise InvariantViolation("Color must be valid hex format")
        
        object.__setattr__(self, 'color', new_color)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_description(self, new_description: Optional[str]) -> None:
        """Update tag description."""
        if self.description == new_description:
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Tag({self.name}, type={self.tag_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Tag(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.tag_type.value}, version={self.version})"
        )