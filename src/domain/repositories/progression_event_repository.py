"""
Progression_event Repository Interface

Port for persisting and retrieving Progression_event entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.progression_event import Progression_event
from ..value_objects.common import TenantId, EntityId


class IProgression_eventRepository(ABC):
    """
    Repository interface for Progression_event entity.
    
    Progression_events belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Progression_event) -> Progression_event:
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
    ) -> Optional[Progression_event]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Progression_event]:
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