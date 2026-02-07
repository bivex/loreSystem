"""
Exhibition Repository Interface

Port for persisting and retrieving Exhibition entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.exhibition import Exhibition
from ..value_objects.common import TenantId, EntityId


class IExhibitionRepository(ABC):
    """
    Repository interface for Exhibition entity.
    
    Exhibitions belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Exhibition) -> Exhibition:
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
    ) -> Optional[Exhibition]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Exhibition]:
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