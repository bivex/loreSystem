"""
HiddenPath Repository Interface

Port for persisting and retrieving HiddenPath entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.hidden_path import HiddenPath
from ..value_objects.common import TenantId, EntityId


class IHiddenPathRepository(ABC):
    """
    Repository interface for HiddenPath entity.
    
    HiddenPaths belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: HiddenPath) -> HiddenPath:
        """
        Save an entity (insert or update).
        
        Args:
            entity: HiddenPath to save
        
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
    ) -> Optional[HiddenPath]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[HiddenPath]:
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
