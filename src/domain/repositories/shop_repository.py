"""
Shop Repository Interface

Port for persisting and retrieving Shop entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.shop import Shop
from ..value_objects.common import TenantId, EntityId


class IShopRepository(ABC):
    """
    Repository interface for Shop entity.
    
    Shops belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Shop) -> Shop:
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
    ) -> Optional[Shop]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Shop]:
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