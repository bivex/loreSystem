"""
Particle Entity

A Particle represents a particle system for AAA game effects (sparks, smoke, debris, etc.).
Part of the World aggregate.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Particle:
    """
    Particle entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Particle count must be non-negative
    - Lifetime must be positive
    - Emission rate must be non-negative
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    particle_type: str  # e.g., "spark", "smoke", "debris", "magic_dust", "water_drop"
    description: Optional[str]
    max_particles: int  # Maximum number of active particles
    lifetime_ms: float  # Average particle lifetime in milliseconds
    emission_rate: float  # Particles per second
    gravity: float  # Gravity effect (negative = up, positive = down)
    initial_velocity: tuple[float, float, float]  # Initial velocity vector (x, y, z)
    velocity_variance: tuple[float, float, float]  # Random velocity variance
    color_start: tuple[float, float, float, float]  # RGBA start color
    color_end: tuple[float, float, float, float]  # RGBA end color
    size_start: float  # Initial particle size
    size_end: float  # Final particle size
    rotation_speed: float  # Degrees per second
    fade_mode: str  # e.g., "linear", "ease_in", "ease_out"
    is_emitting: bool  # Whether particle system is emitting
    loop: bool  # Whether emission loops
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
        if self.max_particles <= 0:
            raise InvariantViolation("Max particles must be positive")
        if self.lifetime_ms <= 0:
            raise InvariantViolation("Lifetime must be positive")
        if self.emission_rate < 0:
            raise InvariantViolation("Emission rate must be non-negative")
        if self.size_start <= 0 or self.size_end <= 0:
            raise InvariantViolation("Particle sizes must be positive")
        if not all(0.0 <= c <= 1.0 for c in self.color_start):
            raise InvariantViolation("Color values must be between 0.0 and 1.0")
        if not all(0.0 <= c <= 1.0 for c in self.color_end):
            raise InvariantViolation("Color values must be between 0.0 and 1.0")
        valid_types = ["spark", "smoke", "debris", "magic_dust", "water_drop", "fire", "snow", "rain", "leaf", "star"]
        if self.particle_type not in valid_types:
            raise InvariantViolation(f"Particle type must be one of: {', '.join(valid_types)}")
        valid_fade = ["linear", "ease_in", "ease_out", "ease_in_out"]
        if self.fade_mode not in valid_fade:
            raise InvariantViolation(f"Fade mode must be one of: {', '.join(valid_fade)}")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        particle_type: str,
        max_particles: int = 1000,
        lifetime_ms: float = 2000.0,
        emission_rate: float = 100.0,
        gravity: float = 0.0,
        initial_velocity: Optional[tuple[float, float, float]] = None,
        velocity_variance: Optional[tuple[float, float, float]] = None,
        color_start: Optional[tuple[float, float, float, float]] = None,
        color_end: Optional[tuple[float, float, float, float]] = None,
        size_start: float = 1.0,
        size_end: float = 0.5,
        rotation_speed: float = 0.0,
        fade_mode: str = "linear",
        loop: bool = True,
        description: Optional[str] = None,
    ) -> 'Particle':
        """
        Factory method for creating a new Particle system.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            particle_type=particle_type,
            description=description,
            max_particles=max_particles,
            lifetime_ms=lifetime_ms,
            emission_rate=emission_rate,
            gravity=gravity,
            initial_velocity=initial_velocity or (0.0, 0.0, 0.0),
            velocity_variance=velocity_variance or (0.0, 0.0, 0.0),
            color_start=color_start or (1.0, 1.0, 1.0, 1.0),
            color_end=color_end or (1.0, 1.0, 1.0, 0.0),
            size_start=size_start,
            size_end=size_end,
            rotation_speed=rotation_speed,
            fade_mode=fade_mode,
            is_emitting=True,
            loop=loop,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def set_emission_rate(self, rate: float) -> None:
        """Update particle emission rate."""
        if rate < 0:
            raise InvariantViolation("Emission rate must be non-negative")
        if self.emission_rate == rate:
            return
        
        object.__setattr__(self, 'emission_rate', rate)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_gravity(self, gravity: float) -> None:
        """Update gravity effect."""
        if self.gravity == gravity:
            return
        
        object.__setattr__(self, 'gravity', gravity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def start_emission(self) -> None:
        """Start particle emission."""
        if self.is_emitting:
            return
        object.__setattr__(self, 'is_emitting', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def stop_emission(self) -> None:
        """Stop particle emission."""
        if not self.is_emitting:
            return
        object.__setattr__(self, 'is_emitting', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Particle({self.name}, {self.particle_type}, max={self.max_particles})"
    
    def __repr__(self) -> str:
        return (
            f"Particle(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.particle_type}, max_particles={self.max_particles}, version={self.version})"
        )
