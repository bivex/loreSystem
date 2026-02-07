"""
Quest_node Repository Interface

Port for persisting and retrieving Quest_node entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.quest_node import Quest_node
from ..value_objects.common import TenantId, EntityId


class IQuest_nodeRepository(ABC):
    """
    Repository interface for Quest_node entity.
    
    Quest_nodes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Quest_node) -> Quest_node:
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
    ) -> Optional[Quest_node]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Quest_node]:
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