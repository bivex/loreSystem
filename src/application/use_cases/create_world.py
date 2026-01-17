"""
Use Case: Create World

Demonstrates clean application layer orchestration.
"""
from typing import Optional

from src.domain.entities.world import World
from src.domain.repositories.world_repository import IWorldRepository
from src.domain.value_objects.common import (
    TenantId,
    WorldName,
    Description,
)
from src.domain.exceptions import DuplicateEntity
from src.application.dto import CreateWorldDTO, WorldDTO


class CreateWorldUseCase:
    """
    Use case for creating a new world.
    
    Responsibilities:
    - Validate input
    - Check business rules (uniqueness)
    - Create domain entity
    - Persist via repository
    - Return DTO
    """
    
    def __init__(self, world_repository: IWorldRepository):
        """
        Dependency injection of repository.
        
        Args:
            world_repository: Repository for persisting worlds
        """
        self._world_repository = world_repository
    
    def execute(self, request: CreateWorldDTO) -> WorldDTO:
        """
        Execute the use case.
        
        Args:
            request: Input data for creating a world
        
        Returns:
            WorldDTO representing the created world
        
        Raises:
            ValueError: If input validation fails
            DuplicateEntity: If world name already exists in tenant
        """
        # Convert primitives to value objects (validates format)
        tenant_id = TenantId(request.tenant_id)
        name = WorldName(request.name)
        description = Description(request.description)
        
        # Check business rule: unique name per tenant
        if self._world_repository.exists(tenant_id, name):
            raise DuplicateEntity(
                f"World '{name}' already exists in tenant {tenant_id}"
            )
        
        # Create domain entity (enforces invariants)
        world = World.create(
            tenant_id=tenant_id,
            name=name,
            description=description,
        )
        
        # Persist (transaction boundary)
        saved_world = self._world_repository.save(world)
        
        # Convert to DTO for response
        return self._to_dto(saved_world)
    
    def _to_dto(self, world: World) -> WorldDTO:
        """Convert domain entity to DTO."""
        return WorldDTO(
            id=world.id.value,
            tenant_id=world.tenant_id.value,
            name=str(world.name),
            description=str(world.description),
            created_at=world.created_at.value,
            updated_at=world.updated_at.value,
            version=world.version.value,
        )
