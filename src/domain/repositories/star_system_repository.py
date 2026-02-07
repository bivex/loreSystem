"""
Star_system Repository Interface

Port for persisting and retrieving Star_system entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.star_system import Star_system
from ..value_objects.common import TenantId, EntityId


class IStar_systemRepository(ABC):
    """
    Repository interface for Star_system entity.
    
    Star_systems belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Star_system) -> Star_system:
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
    ) -> Optional[Star_system]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Star_system]:
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