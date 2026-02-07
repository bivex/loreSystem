"""
Research_center Repository Interface

Port for persisting and retrieving Research_center entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.research_center import Research_center
from ..value_objects.common import TenantId, EntityId


class IResearch_centerRepository(ABC):
    """
    Repository interface for Research_center entity.
    
    Research_centers belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Research_center) -> Research_center:
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
    ) -> Optional[Research_center]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Research_center]:
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