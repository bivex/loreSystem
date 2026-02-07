"""
Weather_pattern Repository Interface

Port for persisting and retrieving Weather_pattern entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.weather_pattern import Weather_pattern
from ..value_objects.common import TenantId, EntityId


class IWeather_patternRepository(ABC):
    """
    Repository interface for Weather_pattern entity.
    
    Weather_patterns belong to Worlds (aggregate boundary).
    """
    
    @abstractmethod
    def save(self, entity: Weather_pattern) -> Weather_pattern:
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
    ) -> Optional[Weather_pattern]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Weather_pattern]:
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