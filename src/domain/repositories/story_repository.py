"""
Story Repository Interface

Port for persisting and retrieving Story entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.story import Story
from ..value_objects.common import TenantId, EntityId, StoryName, StoryType


class IStoryRepository(ABC):
    """
    Repository interface for Story entity.
    
    Stories belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, story: Story) -> Story:
        """
        Save a story (insert or update).
        
        Args:
            story: Story to save
        
        Returns:
            Saved story with ID populated
        
        Raises:
            DuplicateEntity: If story name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        story_id: EntityId,
    ) -> Optional[Story]:
        """Find story by ID."""
        pass
    
    @abstractmethod
    def find_by_name(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: StoryName,
    ) -> Optional[Story]:
        """
        Find story by name within a specific world.
        
        Story names are unique per world, not globally.
        """
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Story]:
        """List all stories in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_type(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        story_type: StoryType,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Story]:
        """List stories by type within a world."""
        pass
    
    @abstractmethod
    def list_active(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Story]:
        """List all active stories in a world."""
        pass
    
    @abstractmethod
    def search_by_content(
        self,
        tenant_id: TenantId,
        search_term: str,
        limit: int = 20,
    ) -> List[Story]:
        """
        Search stories by content.
        
        This may be implemented via full-text search.
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        story_id: EntityId,
    ) -> bool:
        """
        Delete a story.
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: StoryName,
    ) -> bool:
        """Check if story with name exists in world."""
        pass