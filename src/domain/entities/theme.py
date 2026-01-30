"""
Theme Entity

A Theme represents a core thematic element in the game - musical, narrative,
or visual - that recurs throughout the experience to create cohesion and
emotional resonance.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    EmotionalTone,
)
from ..exceptions import InvariantViolation


@dataclass
class Theme:
    """
    Theme entity representing core thematic elements.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Version increases monotonically
    - Emotional tone must be valid
    - Can be musical, narrative, or visual in nature
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    theme_category: str  # "musical", "narrative", "visual", "atmospheric"
    emotional_tone: Optional[EmotionalTone]
    
    # Musical associations
    musical_theme_id: Optional[EntityId]  # Reference to MusicTheme
    primary_instrument: Optional[str]  # e.g., "violin", "choir"
    key_signature: Optional[str]  # e.g., "C minor", "D major"
    
    # Narrative/visual associations
    character_id: Optional[EntityId]  # If this is a character theme
    faction_id: Optional[EntityId]  # If this is a faction theme
    location_id: Optional[EntityId]  # If this is a location theme
    
    # Presentation
    color_palette: Optional[str]  # Hex codes for visual themes
    is_recurring: bool  # Whether this theme appears multiple times
    
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
            raise InvariantViolation("Theme name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Theme name must be <= 255 characters")
        
        valid_categories = ["musical", "narrative", "visual", "atmospheric"]
        if self.theme_category not in valid_categories:
            raise InvariantViolation(
                f"Theme category must be one of: {', '.join(valid_categories)}"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        theme_category: str,
        emotional_tone: Optional[EmotionalTone] = None,
        musical_theme_id: Optional[EntityId] = None,
        primary_instrument: Optional[str] = None,
        key_signature: Optional[str] = None,
        character_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        color_palette: Optional[str] = None,
        is_recurring: bool = True,
    ) -> 'Theme':
        """
        Factory method for creating a new Theme.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            theme_category=theme_category,
            emotional_tone=emotional_tone,
            musical_theme_id=musical_theme_id,
            primary_instrument=primary_instrument,
            key_signature=key_signature,
            character_id=character_id,
            faction_id=faction_id,
            location_id=location_id,
            color_palette=color_palette,
            is_recurring=is_recurring,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update theme description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the theme."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Theme name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Theme name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_emotional_tone(self, tone: Optional[EmotionalTone]) -> None:
        """Update the emotional tone of this theme."""
        if self.emotional_tone == tone:
            return
        
        object.__setattr__(self, 'emotional_tone', tone)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_character(self, character_id: Optional[EntityId]) -> None:
        """Associate this theme with a character."""
        if self.character_id == character_id:
            return
        
        object.__setattr__(self, 'character_id', character_id)
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
        tone_str = f", {self.emotional_tone.value}" if self.emotional_tone else ""
        return f"Theme({self.name}, {self.theme_category}{tone_str})"
    
    def __repr__(self) -> str:
        return (
            f"Theme(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', category={self.theme_category}, version={self.version})"
        )
