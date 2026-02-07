"""
Jury Repository Interface

Port for persisting and retrieving Jury entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.jury import Jury
from ..value_objects.common import TenantId, EntityId


class IJuryRepository(ABC):
    """
    Repository interface for Jury entity.
    
    Jurys belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Jury) -> Jury:
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
    ) -> Optional[Jury]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Jury]:
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