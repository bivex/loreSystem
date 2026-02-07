"""
Blueprint Repository Interface

Port for persisting and retrieving Blueprint entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.blueprint import Blueprint
from ..value_objects.common import TenantId, EntityId


class IBlueprintRepository(ABC):
    """
    Repository interface for Blueprint entity.
    
    Blueprints belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Blueprint) -> Blueprint:
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
    ) -> Optional[Blueprint]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Blueprint]:
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