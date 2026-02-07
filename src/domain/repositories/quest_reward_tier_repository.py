"""
Quest_reward_tier Repository Interface

Port for persisting and retrieving Quest_reward_tier entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.quest_reward_tier import Quest_reward_tier
from ..value_objects.common import TenantId, EntityId


class IQuest_reward_tierRepository(ABC):
    """
    Repository interface for Quest_reward_tier entity.
    
    Quest_reward_tiers belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Quest_reward_tier) -> Quest_reward_tier:
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
    ) -> Optional[Quest_reward_tier]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Quest_reward_tier]:
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