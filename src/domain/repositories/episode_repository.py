"""
Episode Repository Interface

Port for persisting and retrieving Episode entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.episode import Episode
from ..value_objects.common import TenantId, EntityId


class IEpisodeRepository(ABC):
    """
    Repository interface for Episode entity.
    
    Episodes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Episode) -> Episode:
        """
        Save an entity (insert or update).
        
        Args:
            entity: Episode to save
        
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
    ) -> Optional[Episode]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Episode]:
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
