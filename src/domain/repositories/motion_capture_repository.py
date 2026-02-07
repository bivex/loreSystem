"""
Motion_capture Repository Interface

Port for persisting and retrieving Motion_capture entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.motion_capture import Motion_capture
from ..value_objects.common import TenantId, EntityId


class IMotion_captureRepository(ABC):
    """
    Repository interface for Motion_capture entity.
    
    Motion_captures belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Motion_capture) -> Motion_capture:
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
    ) -> Optional[Motion_capture]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Motion_capture]:
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