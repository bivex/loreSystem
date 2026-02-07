"""
Sound_effect Repository Interface

Port for persisting and retrieving Sound_effect entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.sound_effect import Sound_effect
from ..value_objects.common import TenantId, EntityId


class ISound_effectRepository(ABC):
    """
    Repository interface for Sound_effect entity.
    
    Sound_effects belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Sound_effect) -> Sound_effect:
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
    ) -> Optional[Sound_effect]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Sound_effect]:
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