"""
Character_variant Repository Interface

Port for persisting and retrieving Character_variant entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.character_variant import Character_variant
from ..value_objects.common import TenantId, EntityId


class ICharacter_variantRepository(ABC):
    """
    Repository interface for Character_variant entity.
    
    Character_variants belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Character_variant) -> Character_variant:
        """
        Save an entity (insert or update).
        
        Returns:
            Saved entity with ID populated
        """
        pass

    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[Character_variant]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Character_variant]:
        """List all entities in a world with pagination."""
        pass

    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> bool:
        """
        Delete an entity.
        
        Returns:
            True if deleted, False if not found
        """
        pass