"""
Character Repository Interface

Port for persisting and retrieving Character entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.character import Character
from ..value_objects.common import TenantId, EntityId, CharacterName


class ICharacterRepository(ABC):
    """
    Repository interface for Character entity.
    
    Characters belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, character: Character) -> Character:
        """
        Save a character (insert or update).
        
        Args:
            character: Character to save
        
        Returns:
            Saved character with ID populated
        
        Raises:
            DuplicateEntity: If character name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        character_id: EntityId,
    ) -> Optional[Character]:
        """Find character by ID."""
        pass
    
    @abstractmethod
    def find_by_name(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: CharacterName,
    ) -> Optional[Character]:
        """
        Find character by name within a specific world.
        
        Character names are unique per world, not globally.
        """
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Character]:
        """List all characters in a world with pagination."""
        pass
    
    @abstractmethod
    def list_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Character]:
        """List all characters for a tenant with pagination."""
        pass
    
    @abstractmethod
    def search_by_backstory(
        self,
        tenant_id: TenantId,
        search_term: str,
        limit: int = 20,
    ) -> List[Character]:
        """
        Search characters by backstory content.
        
        This may be implemented via full-text search.
        
        Args:
            tenant_id: Tenant to search within
            search_term: Term to search for in backstories
            limit: Maximum results
        
        Returns:
            List of matching characters
        """
        pass
    
    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        character_id: EntityId,
    ) -> bool:
        """
        Delete a character.
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: CharacterName,
    ) -> bool:
        """Check if character with name exists in world."""
        pass
