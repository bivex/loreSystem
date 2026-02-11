"""
ShareCode Repository Interface

Port for persisting and retrieving ShareCode entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.share_code import ShareCode
from ..value_objects.common import TenantId, EntityId


class IShareCodeRepository(ABC):
    """
    Repository interface for ShareCode entity.
    
    ShareCodes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: ShareCode) -> ShareCode:
        """
        Save an entity (insert or update).
        
        Args:
            entity: ShareCode to save
        
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
    ) -> Optional[ShareCode]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ShareCode]:
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
