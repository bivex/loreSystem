"""
Social_class Repository Interface

Port for persisting and retrieving Social_class entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.social_class import Social_class
from ..value_objects.common import TenantId, EntityId


class ISocial_classRepository(ABC):
    """
    Repository interface for Social_class entity.
    
    Social_classs belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Social_class) -> Social_class:
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
    ) -> Optional[Social_class]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Social_class]:
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