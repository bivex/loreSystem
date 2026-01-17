"""
Tag Repository Interface

Port for persisting and retrieving Tag entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.tag import Tag
from ..value_objects.common import TenantId, EntityId, TagName, TagType


class ITagRepository(ABC):
    """
    Repository interface for Tag entity.
    
    Tags belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, tag: Tag) -> Tag:
        """
        Save a tag (insert or update).
        
        Args:
            tag: Tag to save
        
        Returns:
            Saved tag with ID populated
        
        Raises:
            DuplicateEntity: If tag name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        tag_id: EntityId,
    ) -> Optional[Tag]:
        """Find tag by ID."""
        pass
    
    @abstractmethod
    def find_by_name(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: TagName,
    ) -> Optional[Tag]:
        """
        Find tag by name within a specific world.
        
        Tag names are unique per world and type, not globally.
        """
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Tag]:
        """List all tags in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_type(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        tag_type: TagType,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Tag]:
        """List tags by type within a world."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        tag_id: EntityId,
    ) -> bool:
        """
        Delete a tag.
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: TagName,
        tag_type: TagType,
    ) -> bool:
        """Check if tag with name and type exists in world."""
        pass