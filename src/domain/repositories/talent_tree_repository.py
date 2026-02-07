"""
Talent_tree Repository Interface

Port for persisting and retrieving Talent_tree entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.talent_tree import Talent_tree
from ..value_objects.common import TenantId, EntityId


class ITalent_treeRepository(ABC):
    """
    Repository interface for Talent_tree entity.
    
    Talent_trees belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Talent_tree) -> Talent_tree:
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
    ) -> Optional[Talent_tree]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Talent_tree]:
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