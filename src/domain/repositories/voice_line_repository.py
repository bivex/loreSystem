"""
VoiceLine Repository Interface

Port for persisting and retrieving VoiceLine entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.voice_line import VoiceLine
from ..value_objects.common import TenantId, EntityId


class IVoiceLineRepository(ABC):
    """
    Repository interface for VoiceLine entity.
    
    VoiceLines belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: VoiceLine) -> VoiceLine:
        """
        Save an entity (insert or update).
        
        Args:
            entity: VoiceLine to save
        
        Returns:
            Saved entity with ID populated
        
        Raises:
            DuplicateEntity: If entity name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass
    
    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[VoiceLine]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[VoiceLine]:
        """List all entities in a world with pagination."""
        pass
    
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
