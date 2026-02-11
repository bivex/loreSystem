"""
DeusExMachina Repository Interface

Port for persisting and retrieving DeusExMachina entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.deus_ex_machina import DeusExMachina
from ..value_objects.common import TenantId, EntityId


class IDeusExMachinaRepository(ABC):
    """
    Repository interface for DeusExMachina entity.
    
    DeusExMachinas belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: DeusExMachina) -> DeusExMachina:
        """
        Save an entity (insert or update).
        
        Args:
            entity: DeusExMachina to save
        
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
    ) -> Optional[DeusExMachina]:
        """Find entity by ID."""
        pass
    
    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DeusExMachina]:
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
