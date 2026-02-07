"""
DropRate Repository Interface

Port for persisting and retrieving DropRate entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.drop_rate import DropRate
from ..value_objects.common import TenantId, EntityId


class IDropRateRepository(ABC):
    """
    Repository interface for DropRate entity.
    
    DropRates belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: DropRate) -> DropRate:
        """
        Save an entity (insert or update).
        
        Args:
            entity: DropRate to save
        
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
    ) -> Optional[DropRate]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DropRate]:
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
