"""
Social_media Repository Interface

Port for persisting and retrieving Social_media entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.social_media import Social_media
from ..value_objects.common import TenantId, EntityId


class ISocial_mediaRepository(ABC):
    """
    Repository interface for Social_media entity.
    
    Social_medias belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Social_media) -> Social_media:
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
    ) -> Optional[Social_media]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Social_media]:
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