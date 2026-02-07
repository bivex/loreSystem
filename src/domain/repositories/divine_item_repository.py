"""
Divine_item Repository Interface

Port for persisting and retrieving Divine_item entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.divine_item import Divine_item
from ..value_objects.common import TenantId, EntityId


class IDivine_itemRepository(ABC):
    """
    Repository interface for Divine_item entity.
    
    Divine_items belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Divine_item) -> Divine_item:
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
    ) -> Optional[Divine_item]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Divine_item]:
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