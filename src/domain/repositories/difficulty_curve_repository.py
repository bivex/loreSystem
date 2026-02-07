"""
Difficulty_curve Repository Interface

Port for persisting and retrieving Difficulty_curve entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.difficulty_curve import Difficulty_curve
from ..value_objects.common import TenantId, EntityId


class IDifficulty_curveRepository(ABC):
    """
    Repository interface for Difficulty_curve entity.
    
    Difficulty_curves belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Difficulty_curve) -> Difficulty_curve:
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
    ) -> Optional[Difficulty_curve]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Difficulty_curve]:
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