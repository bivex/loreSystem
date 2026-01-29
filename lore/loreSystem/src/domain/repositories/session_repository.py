"""
Session Repository Interface

Port for persisting and retrieving Session entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.session import Session
from ..value_objects.common import TenantId, EntityId


class ISessionRepository(ABC):
    """
    Repository interface for Session entity.
    
    Sessions belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, session: Session) -> Session:
        """
        Save a session (insert or update).
        
        Args:
            session: Session to save
        
        Returns:
            Saved session with ID populated
        
        Raises:
            DuplicateEntity: If session name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world/story doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        session_id: EntityId,
    ) -> Optional[Session]:
        """Find session by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Session]:
        """List all sessions in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_story(
        self,
        tenant_id: TenantId,
        story_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Session]:
        """List all sessions for a story."""
        pass
    
    @abstractmethod
    def list_active(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Session]:
        """List all active sessions in a world."""
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        session_id: EntityId,
    ) -> bool:
        """
        Delete a session.
        
        Returns:
            True if deleted, False if not found
        """
        pass