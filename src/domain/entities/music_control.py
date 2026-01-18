"""
Music Control Entity

A MusicControl represents developer-controllable music parameters
to ensure music aligns with lore state, narrative phase, and player context.
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
    NarrativePhase,
    PlayerContext,
)
from ..exceptions import InvariantViolation


@dataclass
class MusicControl:
    """
    MusicControl entity for developer control over music behavior.
    
    Invariants:
    - Must belong to exactly one World
    - Name must not be empty
    - Version increases monotonically
    - Priority must be non-negative
    - Fade in/out durations must be non-negative
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    
    # Lore and narrative context
    lore_state: Optional[str]  # Custom lore state identifier
    narrative_phase: Optional[NarrativePhase]  # Current narrative phase
    emotional_tone: Optional[EmotionalTone]  # Desired emotional tone
    player_context: Optional[PlayerContext]  # Current player context
    
    # Trigger configuration
    trigger_conditions: Optional[str]  # JSON string of trigger conditions
    priority: int  # Priority level for conflicting controls
    
    # Fade rules
    fade_in_duration_seconds: float  # Fade in duration
    fade_out_duration_seconds: float  # Fade out duration
    
    # Interrupt rules
    allow_interrupt: bool  # Whether this can be interrupted
    can_interrupt_others: bool  # Whether this can interrupt others
    interrupt_priority_threshold: int  # Minimum priority to interrupt
    
    # Associated music entities
    music_state_id: Optional[EntityId]  # Target music state
    music_track_id: Optional[EntityId]  # Target music track
    music_theme_id: Optional[EntityId]  # Target music theme
    
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
            raise InvariantViolation("Music control name cannot be empty")
        
        if len(self.name) > 255:
            raise InvariantViolation("Music control name must be <= 255 characters")
        
        if self.priority < 0:
            raise InvariantViolation("Priority must be non-negative")
        
        if self.fade_in_duration_seconds < 0:
            raise InvariantViolation("Fade in duration must be non-negative")
        
        if self.fade_out_duration_seconds < 0:
            raise InvariantViolation("Fade out duration must be non-negative")
        
        if self.interrupt_priority_threshold < 0:
            raise InvariantViolation("Interrupt priority threshold must be non-negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        lore_state: Optional[str] = None,
        narrative_phase: Optional[NarrativePhase] = None,
        emotional_tone: Optional[EmotionalTone] = None,
        player_context: Optional[PlayerContext] = None,
        trigger_conditions: Optional[str] = None,
        priority: int = 0,
        fade_in_duration_seconds: float = 1.0,
        fade_out_duration_seconds: float = 1.0,
        allow_interrupt: bool = True,
        can_interrupt_others: bool = False,
        interrupt_priority_threshold: int = 0,
        music_state_id: Optional[EntityId] = None,
        music_track_id: Optional[EntityId] = None,
        music_theme_id: Optional[EntityId] = None,
    ) -> 'MusicControl':
        """
        Factory method for creating a new MusicControl.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            lore_state=lore_state,
            narrative_phase=narrative_phase,
            emotional_tone=emotional_tone,
            player_context=player_context,
            trigger_conditions=trigger_conditions,
            priority=priority,
            fade_in_duration_seconds=fade_in_duration_seconds,
            fade_out_duration_seconds=fade_out_duration_seconds,
            allow_interrupt=allow_interrupt,
            can_interrupt_others=can_interrupt_others,
            interrupt_priority_threshold=interrupt_priority_threshold,
            music_state_id=music_state_id,
            music_track_id=music_track_id,
            music_theme_id=music_theme_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update music control description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the music control."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise InvariantViolation("Music control name cannot be empty")
        
        if len(new_name) > 255:
            raise InvariantViolation("Music control name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_lore_context(
        self,
        lore_state: Optional[str] = None,
        narrative_phase: Optional[NarrativePhase] = None,
        emotional_tone: Optional[EmotionalTone] = None,
        player_context: Optional[PlayerContext] = None,
    ) -> None:
        """Update the lore and narrative context."""
        changed = False
        
        if lore_state is not None and self.lore_state != lore_state:
            object.__setattr__(self, 'lore_state', lore_state)
            changed = True
        
        if narrative_phase is not None and self.narrative_phase != narrative_phase:
            object.__setattr__(self, 'narrative_phase', narrative_phase)
            changed = True
        
        if emotional_tone is not None and self.emotional_tone != emotional_tone:
            object.__setattr__(self, 'emotional_tone', emotional_tone)
            changed = True
        
        if player_context is not None and self.player_context != player_context:
            object.__setattr__(self, 'player_context', player_context)
            changed = True
        
        if changed:
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
    
    def update_fade_rules(
        self,
        fade_in_duration_seconds: Optional[float] = None,
        fade_out_duration_seconds: Optional[float] = None,
    ) -> None:
        """Update fade in/out durations."""
        changed = False
        
        if fade_in_duration_seconds is not None:
            if fade_in_duration_seconds < 0:
                raise InvariantViolation("Fade in duration must be non-negative")
            if self.fade_in_duration_seconds != fade_in_duration_seconds:
                object.__setattr__(self, 'fade_in_duration_seconds', fade_in_duration_seconds)
                changed = True
        
        if fade_out_duration_seconds is not None:
            if fade_out_duration_seconds < 0:
                raise InvariantViolation("Fade out duration must be non-negative")
            if self.fade_out_duration_seconds != fade_out_duration_seconds:
                object.__setattr__(self, 'fade_out_duration_seconds', fade_out_duration_seconds)
                changed = True
        
        if changed:
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def update_interrupt_rules(
        self,
        allow_interrupt: Optional[bool] = None,
        can_interrupt_others: Optional[bool] = None,
        interrupt_priority_threshold: Optional[int] = None,
    ) -> None:
        """Update interrupt behavior rules."""
        changed = False
        
        if allow_interrupt is not None and self.allow_interrupt != allow_interrupt:
            object.__setattr__(self, 'allow_interrupt', allow_interrupt)
            changed = True
        
        if can_interrupt_others is not None and self.can_interrupt_others != can_interrupt_others:
            object.__setattr__(self, 'can_interrupt_others', can_interrupt_others)
            changed = True
        
        if interrupt_priority_threshold is not None:
            if interrupt_priority_threshold < 0:
                raise InvariantViolation("Interrupt priority threshold must be non-negative")
            if self.interrupt_priority_threshold != interrupt_priority_threshold:
                object.__setattr__(self, 'interrupt_priority_threshold', interrupt_priority_threshold)
                changed = True
        
        if changed:
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_music_state(self, music_state_id: Optional[EntityId]) -> None:
        """Associate this control with a music state."""
        if self.music_state_id == music_state_id:
            return
        
        object.__setattr__(self, 'music_state_id', music_state_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_music_track(self, music_track_id: Optional[EntityId]) -> None:
        """Associate this control with a music track."""
        if self.music_track_id == music_track_id:
            return
        
        object.__setattr__(self, 'music_track_id', music_track_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def associate_with_music_theme(self, music_theme_id: Optional[EntityId]) -> None:
        """Associate this control with a music theme."""
        if self.music_theme_id == music_theme_id:
            return
        
        object.__setattr__(self, 'music_theme_id', music_theme_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        context_parts = []
        if self.narrative_phase:
            context_parts.append(f"phase={self.narrative_phase.value}")
        if self.emotional_tone:
            context_parts.append(f"tone={self.emotional_tone.value}")
        context_str = f", {', '.join(context_parts)}" if context_parts else ""
        return f"MusicControl({self.name}, priority={self.priority}{context_str})"
    
    def __repr__(self) -> str:
        return (
            f"MusicControl(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', priority={self.priority}, version={self.version})"
        )
