"""
Level_up Repository Interface

Port for persisting and retrieving Level_up entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.level_up import Level_up
from ..value_objects.common import TenantId, EntityId


class ILevel_upRepository(ABC):
    """
    Repository interface for Level_up entity.
    
    Level_ups belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Level_up) -> Level_up:
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
    ) -> Optional[Level_up]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Level_up]:
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