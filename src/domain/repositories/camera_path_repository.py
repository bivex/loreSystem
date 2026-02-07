"""
Camera_path Repository Interface

Port for persisting and retrieving Camera_path entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.camera_path import Camera_path
from ..value_objects.common import TenantId, EntityId


class ICamera_pathRepository(ABC):
    """
    Repository interface for Camera_path entity.
    
    Camera_paths belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Camera_path) -> Camera_path:
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
    ) -> Optional[Camera_path]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Camera_path]:
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