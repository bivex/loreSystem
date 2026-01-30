"""
Skybox Entity

A Skybox represents the sky environment for a location.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


@dataclass
class Skybox:
    """
    Skybox entity defining sky appearance.
    
    Invariants:
    - Must have a valid name
    - Must have valid time settings
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    texture_path: str
    has_day_night_cycle: bool
    cloud_density: float
    weather_type: str
    time_of_day: str
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Skybox must have a valid name")
        
        if self.cloud_density < 0 or self.cloud_density > 1:
            raise ValueError("Skybox cloud density must be between 0 and 1")
        
        if self.version.value < 1:
            raise ValueError("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        texture_path: str = "",
        has_day_night_cycle: bool = True,
        cloud_density: float = 0.5,
        weather_type: str = "clear",
        time_of_day: str = "day"
    ) -> 'Skybox':
        """Factory method to create a new Skybox."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            texture_path=texture_path,
            has_day_night_cycle=has_day_night_cycle,
            cloud_density=cloud_density,
            weather_type=weather_type,
            time_of_day=time_of_day,
            created_at=now,
            updated_at=now,
            version=Version(1)
        )
    
    def set_time(self, time_of_day: str) -> 'Skybox':
        """Set the time of day for the skybox."""
        return Skybox(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            name=self.name,
            texture_path=self.texture_path,
            has_day_night_cycle=self.has_day_night_cycle,
            cloud_density=self.cloud_density,
            weather_type=self.weather_type,
            time_of_day=time_of_day,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment()
        )
