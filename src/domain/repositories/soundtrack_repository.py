"""
Soundtrack Repository Interface

Port for persisting and retrieving Soundtrack entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.soundtrack import Soundtrack
from ..value_objects.common import TenantId, EntityId


class ISoundtrackRepository(ABC):
    """
    Repository interface for Soundtrack entity.
    
    Soundtracks belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Soundtrack) -> Soundtrack:
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
    ) -> Optional[Soundtrack]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Soundtrack]:
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