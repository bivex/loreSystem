"""
Chekhovs_gun Repository Interface

Port for persisting and retrieving Chekhovs_gun entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.chekhovs_gun import Chekhovs_gun
from ..value_objects.common import TenantId, EntityId


class IChekhovs_gunRepository(ABC):
    """
    Repository interface for Chekhovs_gun entity.
    
    Chekhovs_guns belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Chekhovs_gun) -> Chekhovs_gun:
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
    ) -> Optional[Chekhovs_gun]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Chekhovs_gun]:
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