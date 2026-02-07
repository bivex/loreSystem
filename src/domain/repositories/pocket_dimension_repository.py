"""
Pocket_dimension Repository Interface

Port for persisting and retrieving Pocket_dimension entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.pocket_dimension import Pocket_dimension
from ..value_objects.common import TenantId, EntityId


class IPocket_dimensionRepository(ABC):
    """
    Repository interface for Pocket_dimension entity.
    
    Pocket_dimensions belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Pocket_dimension) -> Pocket_dimension:
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
    ) -> Optional[Pocket_dimension]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Pocket_dimension]:
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