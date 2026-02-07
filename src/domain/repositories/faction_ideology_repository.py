"""
Faction_ideology Repository Interface

Port for persisting and retrieving Faction_ideology entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.faction_ideology import Faction_ideology
from ..value_objects.common import TenantId, EntityId


class IFaction_ideologyRepository(ABC):
    """
    Repository interface for Faction_ideology entity.
    
    Faction_ideologys belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Faction_ideology) -> Faction_ideology:
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
    ) -> Optional[Faction_ideology]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Faction_ideology]:
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