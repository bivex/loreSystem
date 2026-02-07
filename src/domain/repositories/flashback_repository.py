"""
Flashback Repository Interface

Port for persisting and retrieving Flashback entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.flashback import Flashback
from ..value_objects.common import TenantId, EntityId


class IFlashbackRepository(ABC):
    """
    Repository interface for Flashback entity.
    
    Flashbacks belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Flashback) -> Flashback:
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
    ) -> Optional[Flashback]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Flashback]:
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