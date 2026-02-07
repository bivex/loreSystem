"""
HolySite Repository Interface

Port for persisting and retrieving HolySite entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.holy_site import HolySite
from ..value_objects.common import TenantId, EntityId


class IHolySiteRepository(ABC):
    """
    Repository interface for HolySite entity.
    
    HolySites belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: HolySite) -> HolySite:
        """
        Save an entity (insert or update).
        
        Args:
            entity: HolySite to save
        
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
    ) -> Optional[HolySite]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[HolySite]:
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
