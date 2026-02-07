"""
Quest_tracker Repository Interface

Port for persisting and retrieving Quest_tracker entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.quest_tracker import Quest_tracker
from ..value_objects.common import TenantId, EntityId


class IQuest_trackerRepository(ABC):
    """
    Repository interface for Quest_tracker entity.
    
    Quest_trackers belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Quest_tracker) -> Quest_tracker:
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
    ) -> Optional[Quest_tracker]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Quest_tracker]:
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