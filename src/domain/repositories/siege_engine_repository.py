"""
Siege_engine Repository Interface

Port for persisting and retrieving Siege_engine entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.siege_engine import Siege_engine
from ..value_objects.common import TenantId, EntityId


class ISiege_engineRepository(ABC):
    """
    Repository interface for Siege_engine entity.
    
    Siege_engines belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Siege_engine) -> Siege_engine:
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
    ) -> Optional[Siege_engine]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Siege_engine]:
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