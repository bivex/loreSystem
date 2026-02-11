"""
Music_control Repository Interface

Port for persisting and retrieving Music_control entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.music_control import Music_control
from ..value_objects.common import TenantId, EntityId


class IMusic_controlRepository(ABC):
    """
    Repository interface for Music_control entity.
    
    Music_controls belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Music_control) -> Music_control:
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
    ) -> Optional[Music_control]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Music_control]:
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