"""
VisualEffect Repository Interface

Port for persisting and retrieving VisualEffect entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.visual_effect import VisualEffect
from ..value_objects.common import TenantId, EntityId


class IVisualEffectRepository(ABC):
    """
    Repository interface for VisualEffect entity.
    
    VisualEffects belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: VisualEffect) -> VisualEffect:
        """
        Save an entity (insert or update).
        
        Args:
            entity: VisualEffect to save
        
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
    ) -> Optional[VisualEffect]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[VisualEffect]:
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
