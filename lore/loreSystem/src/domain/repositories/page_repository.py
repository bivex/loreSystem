"""
Page Repository Interface

Port for persisting and retrieving Page entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.page import Page
from ..value_objects.common import TenantId, EntityId, PageName


class IPageRepository(ABC):
    """
    Repository interface for Page entity.
    
    Pages belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, page: Page) -> Page:
        """
        Save a page (insert or update).
        
        Args:
            page: Page to save
        
        Returns:
            Saved page with ID populated
        
        Raises:
            DuplicateEntity: If page name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world/template doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        page_id: EntityId,
    ) -> Optional[Page]:
        """Find page by ID."""
        pass
    
    @abstractmethod
    def find_by_name(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: PageName,
    ) -> Optional[Page]:
        """
        Find page by name within a specific world.
        
        Page names are unique per world, not globally.
        """
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Page]:
        """List all pages in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_template(
        self,
        tenant_id: TenantId,
        template_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Page]:
        """List all pages using a specific template."""
        pass
    
    @abstractmethod
    def list_by_parent(
        self,
        tenant_id: TenantId,
        parent_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Page]:
        """List all child pages under a parent page."""
        pass
    
    @abstractmethod
    def list_by_tag(
        self,
        tenant_id: TenantId,
        tag_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Page]:
        """List all pages with a specific tag."""
        pass
    
    @abstractmethod
    def search_by_content(
        self,
        tenant_id: TenantId,
        search_term: str,
        limit: int = 20,
    ) -> List[Page]:
        """
        Search pages by content.
        
        This may be implemented via full-text search.
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        page_id: EntityId,
    ) -> bool:
        """
        Delete a page.
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: PageName,
    ) -> bool:
        """Check if page with name exists in world."""
        pass