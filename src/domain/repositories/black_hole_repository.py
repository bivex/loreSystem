"""
Black_hole Repository Interface

Port for persisting and retrieving Black_hole entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.black_hole import Black_hole
from ..value_objects.common import TenantId, EntityId


class IBlack_holeRepository(ABC):
    """
    Repository interface for Black_hole entity.
    
    Black_holes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Black_hole) -> Black_hole:
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
    ) -> Optional[Black_hole]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Black_hole]:
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