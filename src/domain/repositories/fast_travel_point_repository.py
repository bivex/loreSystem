"""
Fast_travel_point Repository Interface

Port for persisting and retrieving Fast_travel_point entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.fast_travel_point import Fast_travel_point
from ..value_objects.common import TenantId, EntityId


class IFast_travel_pointRepository(ABC):
    """
    Repository interface for Fast_travel_point entity.
    
    Fast_travel_points belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Fast_travel_point) -> Fast_travel_point:
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
    ) -> Optional[Fast_travel_point]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Fast_travel_point]:
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