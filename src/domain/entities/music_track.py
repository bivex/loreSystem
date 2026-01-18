"""
Music Track Entity

A MusicTrack represents a technical music component like ambient loops,
dynamic layers, stingers, cues, or leitmotifs used in the music system.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    MusicSystemType,
)
from ..exceptions import InvariantViolation


@dataclass
class MusicTrack:
    """
    MusicTrack entity for system-level music components.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Version increases monotonically
    - Intensity level must be between 0 and 10
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    system_type: MusicSystemType
    file_path: Optional[str]  # Path to audio file
    duration_seconds: Optional[float]  # Track duration
    intensity_level: Optional[int]  # 0-10 intensity scale
    is_loopable: bool  # Whether this track can loop
    loop_start_time: Optional[float]  # Loop start point in seconds
    loop_end_time: Optional[float]  # Loop end point in seconds
    
    # References to related music themes
    music_theme_id: Optional[EntityId]  # Parent theme this track belongs to
    
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
            raise InvariantViolation("Music track name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Music track name must be <= 255 characters")
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.intensity_level is not None:
            if self.intensity_level < 0 or self.intensity_level > 10:
                raise InvariantViolation("Intensity level must be between 0 and 10")
        
        if self.loop_start_time is not None and self.loop_start_time < 0:
            raise InvariantViolation("Loop start time must be non-negative")
        
        if self.loop_end_time is not None and self.loop_end_time < 0:
            raise InvariantViolation("Loop end time must be non-negative")
        
        if (self.loop_start_time is not None and self.loop_end_time is not None 
            and self.loop_start_time >= self.loop_end_time):
            raise InvariantViolation("Loop start time must be less than loop end time")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        system_type: MusicSystemType,
        file_path: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        intensity_level: Optional[int] = None,
        is_loopable: bool = False,
        loop_start_time: Optional[float] = None,
        loop_end_time: Optional[float] = None,
        music_theme_id: Optional[EntityId] = None,
    ) -> 'MusicTrack':
        """
        Factory method for creating a new MusicTrack.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            system_type=system_type,
            file_path=file_path,
            duration_seconds=duration_seconds,
            intensity_level=intensity_level,
            is_loopable=is_loopable,
            loop_start_time=loop_start_time,
            loop_end_time=loop_end_time,
            music_theme_id=music_theme_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update music track description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the music track."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Music track name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Music track name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_intensity(self, intensity_level: Optional[int]) -> None:
        """Update the intensity level."""
        if intensity_level is not None:
            if intensity_level < 0 or intensity_level > 10:
                raise InvariantViolation("Intensity level must be between 0 and 10")
        
        if self.intensity_level == intensity_level:
            return
        
        object.__setattr__(self, 'intensity_level', intensity_level)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_loopable(self, is_loopable: bool) -> None:
        """Set whether this track can loop."""
        if self.is_loopable == is_loopable:
            return
        
        object.__setattr__(self, 'is_loopable', is_loopable)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_loop_points(
        self, 
        loop_start_time: Optional[float], 
        loop_end_time: Optional[float]
    ) -> None:
        """Set the loop start and end points."""
        if loop_start_time is not None and loop_start_time < 0:
            raise InvariantViolation("Loop start time must be non-negative")
        
        if loop_end_time is not None and loop_end_time < 0:
            raise InvariantViolation("Loop end time must be non-negative")
        
        if (loop_start_time is not None and loop_end_time is not None 
            and loop_start_time >= loop_end_time):
            raise InvariantViolation("Loop start time must be less than loop end time")
        
        if self.loop_start_time == loop_start_time and self.loop_end_time == loop_end_time:
            return
        
        object.__setattr__(self, 'loop_start_time', loop_start_time)
        object.__setattr__(self, 'loop_end_time', loop_end_time)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_theme(self, music_theme_id: Optional[EntityId]) -> None:
        """Associate this track with a music theme."""
        if self.music_theme_id == music_theme_id:
            return
        
        object.__setattr__(self, 'music_theme_id', music_theme_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        intensity_str = f", intensity={self.intensity_level}" if self.intensity_level is not None else ""
        return f"MusicTrack({self.name}, {self.system_type.value}{intensity_str})"
    
    def __repr__(self) -> str:
        return (
            f"MusicTrack(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.system_type}, version={self.version})"
        )
