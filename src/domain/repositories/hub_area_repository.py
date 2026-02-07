"""
Hub_area Repository Interface

Port for persisting and retrieving Hub_area entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.hub_area import Hub_area
from ..value_objects.common import TenantId, EntityId


class IHub_areaRepository(ABC):
    """
    Repository interface for Hub_area entity.
    
    Hub_areas belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Hub_area) -> Hub_area:
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
    ) -> Optional[Hub_area]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Hub_area]:
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