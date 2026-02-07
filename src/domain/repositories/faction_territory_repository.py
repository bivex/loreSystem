"""
Faction_territory Repository Interface

Port for persisting and retrieving Faction_territory entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.faction_territory import Faction_territory
from ..value_objects.common import TenantId, EntityId


class IFaction_territoryRepository(ABC):
    """
    Repository interface for Faction_territory entity.
    
    Faction_territorys belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Faction_territory) -> Faction_territory:
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
    ) -> Optional[Faction_territory]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Faction_territory]:
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