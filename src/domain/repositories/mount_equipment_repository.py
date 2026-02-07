"""
Mount_equipment Repository Interface

Port for persisting and retrieving Mount_equipment entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.mount_equipment import Mount_equipment
from ..value_objects.common import TenantId, EntityId


class IMount_equipmentRepository(ABC):
    """
    Repository interface for Mount_equipment entity.
    
    Mount_equipments belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Mount_equipment) -> Mount_equipment:
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
    ) -> Optional[Mount_equipment]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Mount_equipment]:
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