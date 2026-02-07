"""
Cursed_item Repository Interface

Port for persisting and retrieving Cursed_item entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.cursed_item import Cursed_item
from ..value_objects.common import TenantId, EntityId


class ICursed_itemRepository(ABC):
    """
    Repository interface for Cursed_item entity.
    
    Cursed_items belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Cursed_item) -> Cursed_item:
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
    ) -> Optional[Cursed_item]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Cursed_item]:
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