"""
Fleet Repository Interface

Port for persisting and retrieving Fleet entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.fleet import Fleet
from ..value_objects.common import TenantId, EntityId


class IFleetRepository(ABC):
    """
    Repository interface for Fleet entity.
    
    Fleets belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Fleet) -> Fleet:
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
    ) -> Optional[Fleet]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Fleet]:
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