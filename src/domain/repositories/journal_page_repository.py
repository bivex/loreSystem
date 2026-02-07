"""
Journal_page Repository Interface

Port for persisting and retrieving Journal_page entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.journal_page import Journal_page
from ..value_objects.common import TenantId, EntityId


class IJournal_pageRepository(ABC):
    """
    Repository interface for Journal_page entity.
    
    Journal_pages belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Journal_page) -> Journal_page:
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
    ) -> Optional[Journal_page]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Journal_page]:
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