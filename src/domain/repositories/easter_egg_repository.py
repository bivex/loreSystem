"""
Easter_egg Repository Interface

Port for persisting and retrieving Easter_egg entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.easter_egg import Easter_egg
from ..value_objects.common import TenantId, EntityId


class IEaster_eggRepository(ABC):
    """
    Repository interface for Easter_egg entity.
    
    Easter_eggs belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Easter_egg) -> Easter_egg:
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
    ) -> Optional[Easter_egg]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Easter_egg]:
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