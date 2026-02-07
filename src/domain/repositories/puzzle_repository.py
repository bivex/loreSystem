"""
Puzzle Repository Interface

Port for persisting and retrieving Puzzle entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.puzzle import Puzzle
from ..value_objects.common import TenantId, EntityId


class IPuzzleRepository(ABC):
    """
    Repository interface for Puzzle entity.
    
    Puzzles belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Puzzle) -> Puzzle:
        """
        Save an entity (insert or update).
        
        Args:
            entity: Puzzle to save
        
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
    ) -> Optional[Puzzle]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Puzzle]:
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
