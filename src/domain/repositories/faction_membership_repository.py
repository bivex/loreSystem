"""
Faction_membership Repository Interface

Port for persisting and retrieving Faction_membership entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.faction_membership import Faction_membership
from ..value_objects.common import TenantId, EntityId


class IFaction_membershipRepository(ABC):
    """
    Repository interface for Faction_membership entity.
    
    Faction_memberships belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Faction_membership) -> Faction_membership:
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
    ) -> Optional[Faction_membership]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Faction_membership]:
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