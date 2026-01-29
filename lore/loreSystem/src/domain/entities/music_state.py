"""
Music State Entity

A MusicState represents an adaptive music state with crossfade rules
and silence moments for dynamic music transitions.
"""
from dataclasses import dataclass
from typing import Optional, Dict

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class MusicState:
    """
    MusicState entity for adaptive music system states.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Version increases monotonically
    - Crossfade duration must be non-negative
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    
    # State configuration
    is_silence_moment: bool  # Whether this state represents silence
    default_track_id: Optional[EntityId]  # Default track for this state
    crossfade_duration_seconds: float  # Duration for crossfading
    allow_interrupts: bool  # Whether this state can be interrupted
    priority: int  # Priority level (higher = more important)
    
    # Transition configuration
    can_transition_to: Optional[str]  # JSON string of allowed state transitions
    
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
            raise InvariantViolation("Music state name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Music state name must be <= 255 characters")
        
        if self.crossfade_duration_seconds < 0:
            raise InvariantViolation("Crossfade duration must be non-negative")
        
        if self.priority < 0:
            raise InvariantViolation("Priority must be non-negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        is_silence_moment: bool = False,
        default_track_id: Optional[EntityId] = None,
        crossfade_duration_seconds: float = 2.0,
        allow_interrupts: bool = True,
        priority: int = 0,
        can_transition_to: Optional[str] = None,
    ) -> 'MusicState':
        """
        Factory method for creating a new MusicState.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            is_silence_moment=is_silence_moment,
            default_track_id=default_track_id,
            crossfade_duration_seconds=crossfade_duration_seconds,
            allow_interrupts=allow_interrupts,
            priority=priority,
            can_transition_to=can_transition_to,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update music state description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the music state."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Music state name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Music state name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_default_track(self, track_id: Optional[EntityId]) -> None:
        """Set the default track for this state."""
        if self.default_track_id == track_id:
            return
        
        object.__setattr__(self, 'default_track_id', track_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_crossfade_duration(self, duration_seconds: float) -> None:
        """Update the crossfade duration."""
        if duration_seconds < 0:
            raise InvariantViolation("Crossfade duration must be non-negative")
        
        if self.crossfade_duration_seconds == duration_seconds:
            return
        
        object.__setattr__(self, 'crossfade_duration_seconds', duration_seconds)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_interrupt_behavior(self, allow_interrupts: bool) -> None:
        """Set whether this state can be interrupted."""
        if self.allow_interrupts == allow_interrupts:
            return
        
        object.__setattr__(self, 'allow_interrupts', allow_interrupts)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_priority(self, priority: int) -> None:
        """Update the priority level."""
        if priority < 0:
            raise InvariantViolation("Priority must be non-negative")
        
        if self.priority == priority:
            return
        
        object.__setattr__(self, 'priority', priority)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_silence_moment(self, is_silence: bool) -> None:
        """Set whether this state represents a silence moment."""
        if self.is_silence_moment == is_silence:
            return
        
        object.__setattr__(self, 'is_silence_moment', is_silence)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_transitions(self, can_transition_to: Optional[str]) -> None:
        """Update the allowed state transitions."""
        if self.can_transition_to == can_transition_to:
            return
        
        object.__setattr__(self, 'can_transition_to', can_transition_to)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        silence_str = " [SILENCE]" if self.is_silence_moment else ""
        return f"MusicState({self.name}, priority={self.priority}{silence_str})"
    
    def __repr__(self) -> str:
        return (
            f"MusicState(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', priority={self.priority}, version={self.version})"
        )
