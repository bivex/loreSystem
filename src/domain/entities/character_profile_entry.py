"""
CharacterProfileEntry Entity

A CharacterProfileEntry represents detailed information about a character.
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
class CharacterProfileEntry:
    """
    CharacterProfileEntry entity containing character profile details.
    
    Invariants:
    - Must belong to a character
    - Must have at least one profile field
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    character_id: EntityId
    field_name: str
    field_value: str
    is_public: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.field_name or len(self.field_name.strip()) == 0:
            raise ValueError("CharacterProfileEntry must have a valid field name")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        character_id: EntityId,
        field_name: str,
        field_value: str,
        is_public: bool = False
    ) -> 'CharacterProfileEntry':
        """Factory method to create a new CharacterProfileEntry."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            character_id=character_id,
            field_name=field_name,
            field_value=field_value,
            is_public=is_public,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def update_value(self, field_value: str) -> 'CharacterProfileEntry':
        """Update the profile field value."""
        return CharacterProfileEntry(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            character_id=self.character_id,
            field_name=self.field_name,
            field_value=field_value,
            is_public=self.is_public,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
