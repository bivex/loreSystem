"""
Voice_line Repository Interface

Port for persisting and retrieving Voice_line entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.voice_line import Voice_line
from ..value_objects.common import TenantId, EntityId


class IVoice_lineRepository(ABC):
    """
    Repository interface for Voice_line entity.
    
    Voice_lines belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Voice_line) -> Voice_line:
        """
        Save an entity (insert or update).
        
        Returns:
            Saved entity with ID populated
        """
        pass

    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        entity_id: EntityId,
    ) -> Optional[Voice_line]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Voice_line]:
        """List all entities in a world with pagination."""
        pass

    @abstractmethod
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