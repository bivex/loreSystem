"""
Score Repository Interface

Port for persisting and retrieving Score entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.score import Score
from ..value_objects.common import TenantId, EntityId


class IScoreRepository(ABC):
    """
    Repository interface for Score entity.
    
    Scores belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Score) -> Score:
        """
        Save an entity (insert or update).
        
        Args:
            entity: Score to save
        
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
    ) -> Optional[Score]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Score]:
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
