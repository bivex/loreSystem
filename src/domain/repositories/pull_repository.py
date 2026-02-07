"""
Pull Repository Interface

Port for persisting and retrieving Pull entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.pull import Pull
from ..value_objects.common import TenantId, EntityId


class IPullRepository(ABC):
    """
    Repository interface for Pull entity.
    
    Pulls belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Pull) -> Pull:
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
    ) -> Optional[Pull]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Pull]:
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