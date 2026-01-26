"""
Environment Entity

An Environment represents the atmospheric conditions and sensory details
of a location, including time of day, weather, lighting, and other ambient factors.
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    TimeOfDay,
    Weather,
    Lighting,
)
from ..exceptions import InvariantViolation


@dataclass
class Environment:
    """
    Environment entity within a World.

    Describes the atmospheric conditions of a location including:
    - Time of day (day/night/dawn/dusk)
    - Weather conditions (clear/rainy/stormy/foggy)
    - Lighting conditions (bright/dim/dark/magical)

    Invariants:
    - Must belong to exactly one World
    - Must be associated with exactly one Location
    - Version increases monotonically
    """

    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    location_id: EntityId  # The location this environment describes
    name: str  # Environment preset name (e.g., "Stormy Night", "Sunny Day")
    description: Optional[Description]  # Detailed description of the environment
    time_of_day: TimeOfDay
    weather: Weather
    lighting: Lighting
    temperature: Optional[str]  # Free-form temperature description (e.g., "chilly", "sweltering")
    sounds: Optional[str]  # Ambient sounds description
    smells: Optional[str]  # Ambient smells description
    is_active: bool  # Whether this environment is currently active for the location
    created_at: Timestamp
    updated_at: Timestamp
    version: Version

    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()

    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )

        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Environment name cannot be empty")

        if len(self.name) > 255:
            raise InvariantViolation("Environment name must be <= 255 characters")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        location_id: EntityId,
        name: str,
        time_of_day: TimeOfDay,
        weather: Weather,
        lighting: Lighting,
        description: Optional[Description] = None,
        temperature: Optional[str] = None,
        sounds: Optional[str] = None,
        smells: Optional[str] = None,
        is_active: bool = True,
    ) -> 'Environment':
        """
        Factory method for creating a new Environment.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            location_id=location_id,
            name=name,
            description=description,
            time_of_day=time_of_day,
            weather=weather,
            lighting=lighting,
            temperature=temperature,
            sounds=sounds,
            smells=smells,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def update_description(self, new_description: Optional[Description]) -> None:
        """Update environment description."""
        if str(self.description) == str(new_description):
            return

        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())

    def rename(self, new_name: str) -> None:
        """Rename the environment."""
        if self.name == new_name:
            return

        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Environment name cannot be empty")

        if len(new_name) > 255:
            raise InvariantViolation("Environment name must be <= 255 characters")

        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())

    def change_conditions(
        self,
        time_of_day: Optional[TimeOfDay] = None,
        weather: Optional[Weather] = None,
        lighting: Optional[Lighting] = None,
        temperature: Optional[str] = None,
        sounds: Optional[str] = None,
        smells: Optional[str] = None,
    ) -> None:
        """Change environmental conditions."""
        changed = False

        if time_of_day is not None and self.time_of_day != time_of_day:
            object.__setattr__(self, 'time_of_day', time_of_day)
            changed = True

        if weather is not None and self.weather != weather:
            object.__setattr__(self, 'weather', weather)
            changed = True

        if lighting is not None and self.lighting != lighting:
            object.__setattr__(self, 'lighting', lighting)
            changed = True

        if temperature != self.temperature:
            object.__setattr__(self, 'temperature', temperature)
            changed = True

        if sounds != self.sounds:
            object.__setattr__(self, 'sounds', sounds)
            changed = True

        if smells != self.smells:
            object.__setattr__(self, 'smells', smells)
            changed = True

        if changed:
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())

    def activate(self) -> None:
        """Make this environment active for its location."""
        if self.is_active:
            return

        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())

    def deactivate(self) -> None:
        """Make this environment inactive for its location."""
        if not self.is_active:
            return

        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())

    def __str__(self) -> str:
        active_str = " (active)" if self.is_active else ""
        return f"Environment({self.name}: {self.time_of_day.value}, {self.weather.value}, {self.lighting.value}{active_str})"

    def __repr__(self) -> str:
        return (
            f"Environment(id={self.id}, location_id={self.location_id}, "
            f"name='{self.name}', active={self.is_active})"
        )