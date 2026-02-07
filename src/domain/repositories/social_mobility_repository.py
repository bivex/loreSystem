"""
Social_mobility Repository Interface

Port for persisting and retrieving Social_mobility entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.social_mobility import Social_mobility
from ..value_objects.common import TenantId, EntityId


class ISocial_mobilityRepository(ABC):
    """
    Repository interface for Social_mobility entity.
    
    Social_mobilitys belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Social_mobility) -> Social_mobility:
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
    ) -> Optional[Social_mobility]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Social_mobility]:
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