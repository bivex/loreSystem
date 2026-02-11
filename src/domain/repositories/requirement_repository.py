"""
Requirement Repository Interface

Port for persisting and retrieving Requirement entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.requirement import Requirement
from ..value_objects.common import TenantId, EntityId


class IRequirementRepository(ABC):
    """
    Repository interface for Requirement entity.
    
    Requirements belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Requirement) -> Requirement:
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
    ) -> Optional[Requirement]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Requirement]:
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