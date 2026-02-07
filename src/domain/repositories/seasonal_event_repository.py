"""
Seasonal_event Repository Interface

Port for persisting and retrieving Seasonal_event entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.seasonal_event import Seasonal_event
from ..value_objects.common import TenantId, EntityId


class ISeasonal_eventRepository(ABC):
    """
    Repository interface for Seasonal_event entity.
    
    Seasonal_events belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Seasonal_event) -> Seasonal_event:
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
    ) -> Optional[Seasonal_event]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Seasonal_event]:
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