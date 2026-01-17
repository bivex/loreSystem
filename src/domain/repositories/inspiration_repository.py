"""
Inspiration Repository Interface

Port for persisting and retrieving Inspiration entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.inspiration import Inspiration
from ..value_objects.common import TenantId, EntityId


class IInspirationRepository(ABC):
    """
    Repository interface for Inspiration entity.
    
    Inspirations belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, inspiration: Inspiration) -> Inspiration:
        """
        Save an inspiration (insert or update).
        
        Args:
            inspiration: Inspiration to save
        
        Returns:
            Saved inspiration with ID populated
        
        Raises:
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        inspiration_id: EntityId,
    ) -> Optional[Inspiration]:
        """Find inspiration by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Inspiration]:
        """List all inspirations in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_category(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        category: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Inspiration]:
        """List inspirations by category within a world."""
        pass
    
    @abstractmethod
    def list_unused(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Inspiration]:
        """List all unused inspirations in a world."""
        pass
    
    @abstractmethod
    def search_by_content(
        self,
        tenant_id: TenantId,
        search_term: str,
        limit: int = 20,
    ) -> List[Inspiration]:
        """
        Search inspirations by content.
        
        This may be implemented via full-text search.
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        inspiration_id: EntityId,
    ) -> bool:
        """
        Delete an inspiration.
        
        Returns:
            True if deleted, False if not found
        """
        pass