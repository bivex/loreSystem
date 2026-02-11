"""
Score Entity

A Score represents a complete orchestral or musical composition for specific
scenes, sequences, or moments in the game. It encompasses the full musical
arrangement including multiple tracks and instruments.
"""
from dataclasses import dataclass
from typing import Optional, List

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
class Score:
    """
    Score entity representing complete musical compositions.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Version increases monotonically
    - Duration must be non-negative
    - Can reference multiple tracks and themes
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    score_type: str  # "cinematic", "gameplay", "cutscene", "boss", "exploration"
    
    # Musical properties
    primary_file_path: Optional[str]  # Path to main score file
    total_duration_seconds: Optional[float]  # Full score duration
    composer: Optional[str]  # Composer name
    orchestrator: Optional[str]  # Orchestrator name
    
    # Structure
    act_count: Optional[int]  # Number of musical acts
    movement_count: Optional[int]  # Number of movements
    has_intro: bool
    has_outro: bool
    
    # Orchestration
    instrument_count: Optional[int]  # Number of instruments
    includes_choir: bool
    includes_orchestra: bool
    includes_synthetics: bool
    
    # Emotional and contextual
    emotional_tone: Optional[EmotionalTone]
    intensity_peak: Optional[int]  # Peak intensity 0-10
    
    # References
    chapter_id: Optional[EntityId]  # If score belongs to a chapter
    quest_id: Optional[EntityId]  # If score belongs to a quest
    scene_id: Optional[EntityId]  # If score belongs to a specific scene
    
    # Technical
    is_adaptive: bool  # Whether this score adapts to gameplay
    stem_count: Optional[int]  # Number of audio stems for mixing
    
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
            raise InvariantViolation("Score name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Score name must be <= 255 characters")
        
        valid_types = ["cinematic", "gameplay", "cutscene", "boss", "exploration"]
        if self.score_type not in valid_types:
            raise InvariantViolation(
                f"Score type must be one of: {', '.join(valid_types)}"
            )
        
        if self.total_duration_seconds is not None and self.total_duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.intensity_peak is not None and (self.intensity_peak < 0 or self.intensity_peak > 10):
            raise InvariantViolation("Intensity peak must be between 0 and 10")
        
        if self.act_count is not None and self.act_count < 1:
            raise InvariantViolation("Act count must be at least 1")
        
        if self.movement_count is not None and self.movement_count < 1:
            raise InvariantViolation("Movement count must be at least 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        score_type: str,
        primary_file_path: Optional[str] = None,
        total_duration_seconds: Optional[float] = None,
        composer: Optional[str] = None,
        orchestrator: Optional[str] = None,
        act_count: Optional[int] = None,
        movement_count: Optional[int] = None,
        has_intro: bool = True,
        has_outro: bool = True,
        instrument_count: Optional[int] = None,
        includes_choir: bool = False,
        includes_orchestra: bool = True,
        includes_synthetics: bool = False,
        emotional_tone: Optional[EmotionalTone] = None,
        intensity_peak: Optional[int] = None,
        chapter_id: Optional[EntityId] = None,
        quest_id: Optional[EntityId] = None,
        scene_id: Optional[EntityId] = None,
        is_adaptive: bool = False,
        stem_count: Optional[int] = None,
    ) -> 'Score':
        """
        Factory method for creating a new Score.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            score_type=score_type,
            primary_file_path=primary_file_path,
            total_duration_seconds=total_duration_seconds,
            composer=composer,
            orchestrator=orchestrator,
            act_count=act_count,
            movement_count=movement_count,
            has_intro=has_intro,
            has_outro=has_outro,
            instrument_count=instrument_count,
            includes_choir=includes_choir,
            includes_orchestra=includes_orchestra,
            includes_synthetics=includes_synthetics,
            emotional_tone=emotional_tone,
            intensity_peak=intensity_peak,
            chapter_id=chapter_id,
            quest_id=quest_id,
            scene_id=scene_id,
            is_adaptive=is_adaptive,
            stem_count=stem_count,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update score description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the score."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Score name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Score name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_duration(self, duration_seconds: Optional[float]) -> None:
        """Update the duration of the score."""
        if duration_seconds is not None and duration_seconds < 0:
            raise InvariantViolation("Duration must be non-negative")
        
        if self.total_duration_seconds == duration_seconds:
            return
        
        object.__setattr__(self, 'total_duration_seconds', duration_seconds)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_emotional_tone(self, tone: Optional[EmotionalTone]) -> None:
        """Update the emotional tone of this score."""
        if self.emotional_tone == tone:
            return
        
        object.__setattr__(self, 'emotional_tone', tone)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        duration = f" ({self.total_duration_seconds}s)" if self.total_duration_seconds else ""
        return f"Score({self.name}, {self.score_type}{duration})"
    
    def __repr__(self) -> str:
        return (
            f"Score(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.score_type}, version={self.version})"
        )
