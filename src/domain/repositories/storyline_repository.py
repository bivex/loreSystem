"""
Storyline Repository Interface

Port for persisting and retrieving Storyline entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.storyline import Storyline
from ..value_objects.common import TenantId, EntityId


class IStorylineRepository(ABC):
    """
    Repository interface for Storyline entity.
    
    Storylines belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Storyline) -> Storyline:
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
    ) -> Optional[Storyline]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Storyline]:
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