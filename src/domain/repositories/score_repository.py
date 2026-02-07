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
        
        Returns:
            Saved entity with ID populated
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