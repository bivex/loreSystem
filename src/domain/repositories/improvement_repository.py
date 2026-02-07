"""
Improvement Repository Interface

Port for persisting and retrieving Improvement entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.improvement import Improvement
from ..value_objects.common import TenantId, EntityId


class IImprovementRepository(ABC):
    """
    Repository interface for Improvement entity.
    
    Improvements belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Improvement) -> Improvement:
        """
        Save an entity (insert or update).
        
        Returns:
            Saved entity with ID populated
        """
        pass

    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[Improvement]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Improvement]:
        """List all entities in a world with pagination."""
        pass

    @abstractmethod
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