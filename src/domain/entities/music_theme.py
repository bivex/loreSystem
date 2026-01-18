"""
Music Theme Entity

A MusicTheme represents a musical piece associated with specific lore elements
like worlds, characters, factions, locations, or narrative moments.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    MusicThemeType,
)
from ..exceptions import InvariantViolation


@dataclass
class MusicTheme:
    """
    MusicTheme entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Version increases monotonically
    - Can be associated with character, location, faction, or era
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    theme_type: MusicThemeType
    file_path: Optional[str]  # Path to audio file
    duration_seconds: Optional[float]  # Track duration
    composer: Optional[str]  # Composer/artist name
    
    # Optional associations to other entities
    character_id: Optional[EntityId]  # If this is a character theme
    location_id: Optional[EntityId]  # If this is a location theme
    faction_id: Optional[EntityId]  # If this is a faction theme
    era_id: Optional[EntityId]  # If this is an era theme
    
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
            raise InvariantViolation("Music theme name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Music theme name must be <= 255 characters")
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        theme_type: MusicThemeType,
        file_path: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        composer: Optional[str] = None,
        character_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        era_id: Optional[EntityId] = None,
    ) -> 'MusicTheme':
        """
        Factory method for creating a new MusicTheme.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            theme_type=theme_type,
            file_path=file_path,
            duration_seconds=duration_seconds,
            composer=composer,
            character_id=character_id,
            location_id=location_id,
            faction_id=faction_id,
            era_id=era_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update music theme description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the music theme."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Music theme name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Music theme name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_file_path(self, new_file_path: Optional[str]) -> None:
        """Update the file path for the music theme."""
        if self.file_path == new_file_path:
            return
        
        object.__setattr__(self, 'file_path', new_file_path)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_duration(self, duration_seconds: Optional[float]) -> None:
        """Update the duration of the music theme."""
        if duration_seconds is not None and duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.duration_seconds == duration_seconds:
            return
        
        object.__setattr__(self, 'duration_seconds', duration_seconds)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_character(self, character_id: Optional[EntityId]) -> None:
        """Associate this theme with a character."""
        if self.character_id == character_id:
            return
        
        object.__setattr__(self, 'character_id', character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_location(self, location_id: Optional[EntityId]) -> None:
        """Associate this theme with a location."""
        if self.location_id == location_id:
            return
        
        object.__setattr__(self, 'location_id', location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_faction(self, faction_id: Optional[EntityId]) -> None:
        """Associate this theme with a faction."""
        if self.faction_id == faction_id:
            return
        
        object.__setattr__(self, 'faction_id', faction_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"MusicTheme({self.name}, {self.theme_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"MusicTheme(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.theme_type}, version={self.version})"
        )
