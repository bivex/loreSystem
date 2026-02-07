"""
Extinction Repository Interface

Port for persisting and retrieving Extinction entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.extinction import Extinction
from ..value_objects.common import TenantId, EntityId


class IExtinctionRepository(ABC):
    """
    Repository interface for Extinction entity.
    
    Extinctions belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Extinction) -> Extinction:
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
    ) -> Optional[Extinction]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Extinction]:
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