"""
Note Repository Interface

Port for persisting and retrieving Note entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.note import Note
from ..value_objects.common import TenantId, EntityId


class INoteRepository(ABC):
    """
    Repository interface for Note entity.
    
    Notes belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, note: Note) -> Note:
        """
        Save a note (insert or update).
        
        Args:
            note: Note to save
        
        Returns:
            Saved note with ID populated
        
        Raises:
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        note_id: EntityId,
    ) -> Optional[Note]:
        """Find note by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Note]:
        """List all notes in a world with pagination."""
        pass
    
    @abstractmethod
    def list_pinned(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Note]:
        """List all pinned notes in a world."""
        pass
    
    @abstractmethod
    def search_by_content(
        self,
        tenant_id: TenantId,
        search_term: str,
        limit: int = 20,
    ) -> List[Note]:
        """
        Search notes by content.
        
        This may be implemented via full-text search.
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        note_id: EntityId,
    ) -> bool:
        """
        Delete a note.
        
        Returns:
            True if deleted, False if not found
        """
        pass