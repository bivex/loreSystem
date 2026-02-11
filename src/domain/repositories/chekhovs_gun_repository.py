"""
ChekhovsGun Repository Interface

Port for persisting and retrieving ChekhovsGun entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.chekhovs_gun import ChekhovsGun
from ..value_objects.common import TenantId, EntityId


class IChekhovsGunRepository(ABC):
    """
    Repository interface for ChekhovsGun entity.
    
    ChekhovsGuns belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: ChekhovsGun) -> ChekhovsGun:
        """
        Save an entity (insert or update).
        
        Args:
            entity: ChekhovsGun to save
        
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
    ) -> Optional[ChekhovsGun]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ChekhovsGun]:
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
