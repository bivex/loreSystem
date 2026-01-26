"""
Environment Repository Interface

Port for persisting and retrieving Environment entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.environment import Environment
from ..value_objects.common import TenantId, EntityId, TimeOfDay, Weather, Lighting


class IEnvironmentRepository(ABC):
    """
    Repository interface for Environment entity.

    Environments belong to Worlds (aggregate boundary) and describe
    atmospheric conditions for specific Locations.
    """

    @abstractmethod
    def save(self, environment: Environment) -> Environment:
        """
        Save an environment (insert or update).

        Args:
            environment: Environment to save

        Returns:
            Saved environment with ID populated

        Raises:
            DuplicateEntity: If environment name exists for location
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world or location doesn't exist
        """
        pass

    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        environment_id: EntityId,
    ) -> Optional[Environment]:
        """Find environment by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Environment]:
        """List all environments in a world with pagination."""
        pass

    @abstractmethod
    def list_by_location(
        self,
        tenant_id: TenantId,
        location_id: EntityId,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Environment]:
        """List all environments for a specific location with pagination."""
        pass

    @abstractmethod
    def list_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Environment]:
        """List all environments for a tenant with pagination."""
        pass

    @abstractmethod
    def search_by_name(
        self,
        tenant_id: TenantId,
        search_term: str,
        limit: int = 20,
    ) -> List[Environment]:
        """
        Search environments by name.

        Args:
            tenant_id: Tenant to search within
            search_term: Term to search for in environment names
            limit: Maximum results

        Returns:
            List of matching environments
        """
        pass

    @abstractmethod
    def find_by_conditions(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        time_of_day: Optional[TimeOfDay] = None,
        weather: Optional[Weather] = None,
        lighting: Optional[Lighting] = None,
        limit: int = 50,
    ) -> List[Environment]:
        """
        Find environments by atmospheric conditions within a world.

        Args:
            tenant_id: Tenant ID
            world_id: World ID
            time_of_day: Filter by time of day (optional)
            weather: Filter by weather (optional)
            lighting: Filter by lighting (optional)
            limit: Maximum results

        Returns:
            List of environments matching the conditions
        """
        pass

    @abstractmethod
    def find_active_by_location(
        self,
        tenant_id: TenantId,
        location_id: EntityId,
    ) -> Optional[Environment]:
        """
        Find the currently active environment for a location.

        Args:
            tenant_id: Tenant ID
            location_id: Location ID

        Returns:
            Active environment for the location, or None if none active
        """
        pass

    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        environment_id: EntityId,
    ) -> bool:
        """
        Delete an environment.

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        location_id: EntityId,
        name: str,
    ) -> bool:
        """Check if environment with name exists for location."""
        pass