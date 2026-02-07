"""
Quest_giver Repository Interface

Port for persisting and retrieving Quest_giver entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.quest_giver import Quest_giver
from ..value_objects.common import TenantId, EntityId


class IQuest_giverRepository(ABC):
    """
    Repository interface for Quest_giver entity.
    
    Quest_givers belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Quest_giver) -> Quest_giver:
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
    ) -> Optional[Quest_giver]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Quest_giver]:
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