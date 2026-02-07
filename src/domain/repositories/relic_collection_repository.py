"""
Relic_collection Repository Interface

Port for persisting and retrieving Relic_collection entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.relic_collection import Relic_collection
from ..value_objects.common import TenantId, EntityId


class IRelic_collectionRepository(ABC):
    """
    Repository interface for Relic_collection entity.
    
    Relic_collections belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Relic_collection) -> Relic_collection:
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
    ) -> Optional[Relic_collection]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Relic_collection]:
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