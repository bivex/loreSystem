"""
Model3d Repository Interface

Port for persisting and retrieving Model3d entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.model3d import Model3d
from ..value_objects.common import TenantId, EntityId


class IModel3dRepository(ABC):
    """
    Repository interface for Model3d entity.
    
    Model3ds belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Model3d) -> Model3d:
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
    ) -> Optional[Model3d]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Model3d]:
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