"""
LevelUp Repository Interface

Port for persisting and retrieving LevelUp entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.level_up import LevelUp
from ..value_objects.common import TenantId, EntityId


class ILevelUpRepository(ABC):
    """
    Repository interface for LevelUp entity.
    
    LevelUps belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: LevelUp) -> LevelUp:
        """
        Save an entity (insert or update).
        
        Args:
            entity: LevelUp to save
        
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
    ) -> Optional[LevelUp]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[LevelUp]:
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
