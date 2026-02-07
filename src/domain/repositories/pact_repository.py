"""
Pact Repository Interface

Port for persisting and retrieving Pact entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.pact import Pact
from ..value_objects.common import TenantId, EntityId


class IPactRepository(ABC):
    """
    Repository interface for Pact entity.
    
    Pacts belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Pact) -> Pact:
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
    ) -> Optional[Pact]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Pact]:
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