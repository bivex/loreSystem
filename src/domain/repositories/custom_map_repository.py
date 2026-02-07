"""
Custom_map Repository Interface

Port for persisting and retrieving Custom_map entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.custom_map import Custom_map
from ..value_objects.common import TenantId, EntityId


class ICustom_mapRepository(ABC):
    """
    Repository interface for Custom_map entity.
    
    Custom_maps belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Custom_map) -> Custom_map:
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
    ) -> Optional[Custom_map]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Custom_map]:
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