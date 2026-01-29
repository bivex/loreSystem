"""
Location Repository Interface

Port for persisting and retrieving Location entities.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.location import Location
from ..value_objects.common import TenantId, EntityId


class ILocationRepository(ABC):
    """
    Repository interface for Location entity.

    Locations belong to Worlds (aggregate boundary).
    """

    @abstractmethod
    def save(self, location: Location) -> Location:
        """
        Save a location (insert or update).

        Args:
            location: Location to save

        Returns:
            Saved location with ID populated

        Raises:
            DuplicateEntity: If location name exists in world
            ConcurrencyConflict: If version mismatch
            EntityNotFound: If referenced world doesn't exist
        """
        pass

    @abstractmethod
    def find_by_id(
        self,
        tenant_id: TenantId,
        location_id: EntityId,
    ) -> Optional[Location]:
        """Find location by ID."""
        pass

    @abstractmethod
    def list_by_world(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Location]:
        """List all locations in a world with pagination."""
        pass

    @abstractmethod
    def list_by_tenant(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Location]:
        """List all locations for a tenant with pagination."""
        pass

    @abstractmethod
    def search_by_name(
        self,
        tenant_id: TenantId,
        search_term: str,
        limit: int = 20,
    ) -> List[Location]:
        """
        Search locations by name.

        Args:
            tenant_id: Tenant to search within
            search_term: Term to search for in location names
            limit: Maximum results

        Returns:
            List of matching locations
        """
        pass

    @abstractmethod
    def find_by_type(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        location_type: str,
        limit: int = 50,
    ) -> List[Location]:
        """
        Find locations by type within a world.

        Args:
            tenant_id: Tenant ID
            world_id: World ID
            location_type: Type of location to find
            limit: Maximum results

        Returns:
            List of locations of the specified type
        """
        pass

    @abstractmethod
    def delete(
        self,
        tenant_id: TenantId,
        location_id: EntityId,
    ) -> bool:
        """
        Delete a location.

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(
        self,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
    ) -> bool:
        """Check if location with name exists in world."""
        pass