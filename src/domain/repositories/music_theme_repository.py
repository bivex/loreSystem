"""
Music_theme Repository Interface

Port for persisting and retrieving Music_theme entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.music_theme import Music_theme
from ..value_objects.common import TenantId, EntityId


class IMusic_themeRepository(ABC):
    """
    Repository interface for Music_theme entity.
    
    Music_themes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Music_theme) -> Music_theme:
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
    ) -> Optional[Music_theme]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Music_theme]:
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