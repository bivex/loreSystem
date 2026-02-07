"""
Honor Repository Interface

Port for persisting and retrieving Honor entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.honor import Honor
from ..value_objects.common import TenantId, EntityId


class IHonorRepository(ABC):
    """
    Repository interface for Honor entity.
    
    Honors belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Honor) -> Honor:
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
    ) -> Optional[Honor]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Honor]:
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