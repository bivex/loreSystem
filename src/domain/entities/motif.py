"""
Motif Entity

A Motif represents a short, recurring musical idea, phrase, or melody
that serves as a signature for characters, concepts, or emotions throughout
the game (leitmotif system).
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
class Motif:
    """
    Motif entity representing leitmotifs and recurring musical phrases.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Version increases monotonically
    - Duration must be non-negative
    - Can vary in intensity and presentation
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    motif_type: str  # "leitmotif", "rhythmic", "harmonic", "melodic", "textural"
    
    # Musical properties
    file_path: Optional[str]  # Path to motif audio file
    duration_seconds: Optional[float]  # Motif length
    key_signature: Optional[str]  # e.g., "C minor"
    tempo_bpm: Optional[int]  # Tempo in beats per minute
    
    # Emotional and contextual
    emotional_tone: Optional[EmotionalTone]
    primary_association: str  # What this motif represents (e.g., "hero", "danger")
    
    # Adaptation properties
    has_variants: bool  # Whether this motif has different versions
    is_transformable: bool  # Whether this motif can be harmonically transformed
    can_be_inverted: bool  # Whether this motif can be melodically inverted
    
    # References
    parent_theme_id: Optional[EntityId]  # Parent Theme this motif belongs to
    character_id: Optional[EntityId]  # If this is a character's motif
    item_id: Optional[EntityId]  # If this is associated with an item
    
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
            raise InvariantViolation("Motif name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Motif name must be <= 255 characters")
        
        valid_types = ["leitmotif", "rhythmic", "harmonic", "melodic", "textural"]
        if self.motif_type not in valid_types:
            raise InvariantViolation(
                f"Motif type must be one of: {', '.join(valid_types)}"
            )
        
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.tempo_bpm is not None and (self.tempo_bpm < 20 or self.tempo_bpm > 300):
            raise InvariantViolation("Tempo must be between 20 and 300 BPM")
        
        if not self.primary_association or len(self.primary_association.strip()) == 0:
            raise InvariantViolation("Primary association cannot be empty")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        motif_type: str,
        primary_association: str,
        file_path: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        key_signature: Optional[str] = None,
        tempo_bpm: Optional[int] = None,
        emotional_tone: Optional[EmotionalTone] = None,
        has_variants: bool = False,
        is_transformable: bool = True,
        can_be_inverted: bool = True,
        parent_theme_id: Optional[EntityId] = None,
        character_id: Optional[EntityId] = None,
        item_id: Optional[EntityId] = None,
    ) -> 'Motif':
        """
        Factory method for creating a new Motif.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            motif_type=motif_type,
            file_path=file_path,
            duration_seconds=duration_seconds,
            key_signature=key_signature,
            tempo_bpm=tempo_bpm,
            emotional_tone=emotional_tone,
            primary_association=primary_association,
            has_variants=has_variants,
            is_transformable=is_transformable,
            can_be_inverted=can_be_inverted,
            parent_theme_id=parent_theme_id,
            character_id=character_id,
            item_id=item_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update motif description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the motif."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Motif name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Motif name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_duration(self, duration_seconds: Optional[float]) -> None:
        """Update the duration of the motif."""
        if duration_seconds is not None and duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.duration_seconds == duration_seconds:
            return
        
        object.__setattr__(self, 'duration_seconds', duration_seconds)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_emotional_tone(self, tone: Optional[EmotionalTone]) -> None:
        """Update the emotional tone of this motif."""
        if self.emotional_tone == tone:
            return
        
        object.__setattr__(self, 'emotional_tone', tone)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        assoc = f" ({self.primary_association})"
        return f"Motif({self.name}, {self.motif_type}{assoc})"
    
    def __repr__(self) -> str:
        return (
            f"Motif(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.motif_type}, version={self.version})"
        )
