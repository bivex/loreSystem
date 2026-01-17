"""
Choice Repository Interface

Port for persisting and retrieving Choice entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.choice import Choice
from ..value_objects.common import TenantId, EntityId, ChoiceType


class IChoiceRepository(ABC):
    """
    Repository interface for Choice entity.
    
    Choices belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, choice: Choice) -> Choice:
        """
        Save a choice (insert or update).
        
        Args:
            choice: Choice to save
        
        Returns:
            Saved choice with ID populated
        
        Raises:
            DuplicateEntity: If choice prompt exists in story
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world/story doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        choice_id: EntityId,
    ) -> Optional[Choice]:
        """Find choice by ID."""
        pass
    
    @abstractmethod
    def list_by_story(
        self,
        tenant_id: TenantId,
        story_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Choice]:
        """List all choices in a story with pagination."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Choice]:
        """List all choices in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_type(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        choice_type: ChoiceType,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Choice]:
        """List choices by type within a world."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        choice_id: EntityId,
    ) -> bool:
        """
        Delete a choice.
        
        Returns:
            True if deleted, False if not found
        """
        pass