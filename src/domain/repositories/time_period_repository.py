"""
Time_period Repository Interface

Port for persisting and retrieving Time_period entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.time_period import Time_period
from ..value_objects.common import TenantId, EntityId


class ITime_periodRepository(ABC):
    """
    Repository interface for Time_period entity.
    
    Time_periods belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Time_period) -> Time_period:
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
    ) -> Optional[Time_period]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Time_period]:
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