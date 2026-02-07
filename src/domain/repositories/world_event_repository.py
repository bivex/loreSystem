"""
World_event Repository Interface

Port for persisting and retrieving World_event entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.world_event import World_event
from ..value_objects.common import TenantId, EntityId


class IWorld_eventRepository(ABC):
    """
    Repository interface for World_event entity.
    
    World_events belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: World_event) -> World_event:
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
    ) -> Optional[World_event]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[World_event]:
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