"""
Music_track Repository Interface

Port for persisting and retrieving Music_track entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.music_track import Music_track
from ..value_objects.common import TenantId, EntityId


class IMusic_trackRepository(ABC):
    """
    Repository interface for Music_track entity.
    
    Music_tracks belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Music_track) -> Music_track:
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
    ) -> Optional[Music_track]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Music_track]:
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