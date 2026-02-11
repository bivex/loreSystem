"""
Foreshadowing Repository Interface

Port for persisting and retrieving Foreshadowing entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.foreshadowing import Foreshadowing
from ..value_objects.common import TenantId, EntityId


class IForeshadowingRepository(ABC):
    """
    Repository interface for Foreshadowing entity.
    
    Foreshadowings belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Foreshadowing) -> Foreshadowing:
        """
        Save an entity (insert or update).
        
        Args:
            entity: Foreshadowing to save
        
        Returns:
            Saved entity with ID populated
        
        Raises:
            DuplicateEntity: If entity name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[Foreshadowing]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Foreshadowing]:
        """List all entities in a world with pagination."""
        pass
    
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
