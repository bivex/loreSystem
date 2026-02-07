"""
Secret_area Repository Interface

Port for persisting and retrieving Secret_area entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.secret_area import Secret_area
from ..value_objects.common import TenantId, EntityId


class ISecret_areaRepository(ABC):
    """
    Repository interface for Secret_area entity.
    
    Secret_areas belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Secret_area) -> Secret_area:
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
    ) -> Optional[Secret_area]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Secret_area]:
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