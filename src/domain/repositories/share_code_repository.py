"""
Share_code Repository Interface

Port for persisting and retrieving Share_code entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.share_code import Share_code
from ..value_objects.common import TenantId, EntityId


class IShare_codeRepository(ABC):
    """
    Repository interface for Share_code entity.
    
    Share_codes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Share_code) -> Share_code:
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
    ) -> Optional[Share_code]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Share_code]:
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