"""
Spawn_point Repository Interface

Port for persisting and retrieving Spawn_point entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.spawn_point import Spawn_point
from ..value_objects.common import TenantId, EntityId


class ISpawn_pointRepository(ABC):
    """
    Repository interface for Spawn_point entity.
    
    Spawn_points belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Spawn_point) -> Spawn_point:
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
    ) -> Optional[Spawn_point]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Spawn_point]:
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