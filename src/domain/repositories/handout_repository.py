"""
Handout Repository Interface

Port for persisting and retrieving Handout entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.handout import Handout
from ..value_objects.common import TenantId, EntityId


class IHandoutRepository(ABC):
    """
    Repository interface for Handout entity.
    
    Handouts belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, handout: Handout) -> Handout:
        """
        Save a handout (insert or update).
        
        Args:
            handout: Handout to save
        
        Returns:
            Saved handout with ID populated
        
        Raises:
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world/session doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        handout_id: EntityId,
    ) -> Optional[Handout]:
        """Find handout by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Handout]:
        """List all handouts in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_session(
        self,
        tenant_id: TenantId,
        session_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Handout]:
        """List all handouts for a session."""
        pass
    
    @abstractmethod
    def list_revealed(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Handout]:
        """List all revealed handouts in a world."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        handout_id: EntityId,
    ) -> bool:
        """
        Delete a handout.
        
        Returns:
            True if deleted, False if not found
        """
        pass