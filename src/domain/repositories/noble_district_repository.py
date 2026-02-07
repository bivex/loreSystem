"""
Noble_district Repository Interface

Port for persisting and retrieving Noble_district entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.noble_district import Noble_district
from ..value_objects.common import TenantId, EntityId


class INoble_districtRepository(ABC):
    """
    Repository interface for Noble_district entity.
    
    Noble_districts belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Noble_district) -> Noble_district:
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
    ) -> Optional[Noble_district]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Noble_district]:
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