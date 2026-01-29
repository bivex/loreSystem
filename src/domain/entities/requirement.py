"""
Requirement Entity

Represents a business rule or invariant that must be preserved.
Used to validate improvements before they are applied.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    EntityType,
    Timestamp,
)


@dataclass
class Requirement:
    """
    Requirement aggregate root.
    
    Represents a formalized business rule that must be checked
    before applying improvements to ensure lore consistency.
    
    Examples:
    - "Character X cannot die before Event Y"
    - "World Z must always have at least 5 active characters"
    - "Backstory length must be >= 100 characters"
    
    Invariants:
    - Description must be clear and actionable
    - Must reference a specific entity or be global
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    entity_type: Optional[EntityType]
    entity_id: Optional[EntityId]
    description: str
    created_at: Timestamp
    
    def __post_init__(self):
        """Validate invariants after construction."""
        if not self.description or len(self.description.strip()) == 0:
            raise ValueError("Requirement description cannot be empty")
        
        # Either both entity_type and entity_id are set, or neither
        if (self.entity_type is None) != (self.entity_id is None):
            raise ValueError(
                "entity_type and entity_id must both be set or both be None"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        description: str,
        entity_type: Optional[EntityType] = None,
        entity_id: Optional[EntityId] = None,
    ) -> 'Requirement':
        """
        Factory method for creating a new Requirement.
        
        Args:
            tenant_id: Tenant this requirement applies to
            description: Human-readable description of the rule
            entity_type: Optional specific entity type
            entity_id: Optional specific entity ID
        
        If entity_type and entity_id are None, this is a global requirement
        applying to all entities in the tenant.
        """
        return cls(
            id=None,
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            created_at=Timestamp.now(),
        )
    
    def is_global(self) -> bool:
        """Check if this is a global requirement (not entity-specific)."""
        return self.entity_type is None and self.entity_id is None
    
    def applies_to_entity(
        self,
        entity_type: EntityType,
        entity_id: EntityId,
    ) -> bool:
        """
        Check if this requirement applies to a specific entity.
        
        Returns True if:
        - Requirement is global, OR
        - Requirement matches the specific entity
        """
        if self.is_global():
            return True
        
        return (
            self.entity_type == entity_type
            and self.entity_id == entity_id
        )
    
    def __str__(self) -> str:
        if self.is_global():
            return f"Requirement(global): {self.description[:50]}..."
        return (
            f"Requirement({self.entity_type}:{self.entity_id}): "
            f"{self.description[:50]}..."
        )
    
    def __repr__(self) -> str:
        return (
            f"Requirement(id={self.id}, entity_type={self.entity_type}, "
            f"entity_id={self.entity_id})"
        )
