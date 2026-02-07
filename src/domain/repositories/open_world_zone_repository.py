"""
Open_world_zone Repository Interface

Port for persisting and retrieving Open_world_zone entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.open_world_zone import Open_world_zone
from ..value_objects.common import TenantId, EntityId


class IOpen_world_zoneRepository(ABC):
    """
    Repository interface for Open_world_zone entity.
    
    Open_world_zones belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Open_world_zone) -> Open_world_zone:
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
    ) -> Optional[Open_world_zone]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Open_world_zone]:
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