# Music System Implementation

## Overview

This document describes the music system entities added to the loreSystem for managing game soundtracks, adaptive music, and narrative-driven audio experiences.

## Architecture

The music system consists of four main entity types that work together to provide a comprehensive music management solution:

### 1. MusicTheme
**Purpose**: Represents thematic musical pieces associated with specific lore elements.

**Key Features**:
- Theme types covering narrative moments (main theme, combat, victory, defeat, etc.)
- Location-based themes (world theme, location theme, era theme)
- Character-specific themes (character theme, faction theme)
- File path management for audio assets
- Duration tracking
- Composer/artist attribution
- Associations with characters, locations, factions, and eras

**Theme Types**:
- Main theme, World theme, Faction theme, Location theme, Era theme, Character theme
- Calm exploration, Mystery ambience, Tension build
- Conflict, Combat, Boss fight
- Victory, Defeat, Loss
- Discovery, Revelation, Lore exposition
- Flashback, Memory, Dream, Prophecy
- Travel, Journey, Transition
- Downtime, Safe zone, Hub
- Crafting, Preparation
- Decision moment, Moral choice
- Betrayal, Tragedy, Sacrifice, Hope, Rebirth
- Climax, Resolution, Epilogue, Credits

### 2. MusicTrack
**Purpose**: Technical music components for the music system implementation.

**Key Features**:
- System component types (ambient loops, dynamic layers, stingers, cues, leitmotifs)
- Intensity levels (0-10 scale) for dynamic music adaptation
- Looping configuration (loop points, seamless loops)
- Integration with parent themes
- Duration and file path management

**System Types**:
- Ambient loop: Background music that seamlessly repeats
- Dynamic layer: Musical layers that can be added/removed
- Intensity level: Different intensity versions of the same theme
- Stinger: Short musical accents for moments
- Cue: Triggered musical snippets
- Leitmotif: Recurring musical motif
- Adaptive state: State-based music variations
- Crossfade rule: Transition definitions
- Silence moment: Intentional musical pauses

### 3. MusicState
**Purpose**: Manages adaptive music states and transition rules.

**Key Features**:
- Silence moment support for dramatic pauses
- Default track assignment per state
- Crossfade duration configuration
- Interrupt behavior (can/cannot be interrupted)
- Priority system for state conflicts
- State transition rules (which states can follow)

**Use Cases**:
- Combat state transitions to exploration state
- Boss battle music that cannot be interrupted
- Silence moments for dramatic reveals
- Priority-based music conflict resolution

### 4. MusicControl
**Purpose**: Developer-controllable parameters ensuring music aligns with narrative.

**Key Features**:
- Lore state tracking (custom game state identifiers)
- Narrative phase awareness (introduction, rising action, climax, etc.)
- Emotional tone control (peaceful, tense, epic, etc.)
- Player context integration (exploration, combat, dialogue, etc.)
- Trigger conditions (JSON-based conditional logic)
- Priority system for conflicting controls
- Fade rules (fade in/out durations)
- Interrupt rules (can interrupt, allow interrupts, priority thresholds)

**Narrative Phases**:
- Introduction, Rising action, Climax, Falling action, Resolution
- Epilogue, Interlude, Flashback

**Emotional Tones**:
- Peaceful, Tense, Joyful, Melancholic, Mysterious
- Epic, Dramatic, Suspenseful, Triumphant, Somber
- Hopeful, Fearful, Aggressive, Calm

**Player Contexts**:
- Exploration, Combat, Dialogue, Cutscene
- Menu, Inventory, Crafting, Trading
- Resting, Traveling

## Entity Relationships

```
World
  ├─ MusicTheme (main theme, location themes, character themes)
  │    └─ MusicTrack (ambient loops, layers, stingers for the theme)
  │
  ├─ MusicState (combat state, exploration state, safe zone state)
  │
  └─ MusicControl (boss fight control, revelation control)
       ├─ References MusicState (target state)
       ├─ References MusicTrack (target track)
       └─ References MusicTheme (target theme)
```

## Example Usage Scenarios

### 1. Character Theme System
```python
# Create a character theme
hero_theme = MusicTheme.create(
    tenant_id=TenantId(1),
    world_id=EntityId(1),
    name="Hero's Journey",
    description=Description("The protagonist's personal theme"),
    theme_type=MusicThemeType.CHARACTER_THEME,
    character_id=EntityId(42),  # Link to hero character
    file_path="/music/hero_theme.mp3",
    duration_seconds=180.0,
    composer="John Williams"
)

# Create a leitmotif track for the theme
hero_motif = MusicTrack.create(
    tenant_id=TenantId(1),
    world_id=EntityId(1),
    name="Hero Leitmotif",
    description=Description("Short heroic motif"),
    system_type=MusicSystemType.LEITMOTIF,
    music_theme_id=hero_theme.id,
    duration_seconds=8.0,
    intensity_level=7
)
```

### 2. Boss Fight Music Control
```python
# Create a music control for boss battles
boss_control = MusicControl.create(
    tenant_id=TenantId(1),
    world_id=EntityId(1),
    name="Final Boss Music Control",
    description=Description("Controls music during the final boss fight"),
    lore_state="final_boss_battle",
    narrative_phase=NarrativePhase.CLIMAX,
    emotional_tone=EmotionalTone.EPIC,
    player_context=PlayerContext.COMBAT,
    priority=20,  # High priority
    fade_in_duration_seconds=0.5,
    fade_out_duration_seconds=2.0,
    allow_interrupt=False,  # Cannot be interrupted
    can_interrupt_others=True,  # Can interrupt other music
    interrupt_priority_threshold=15
)
```

### 3. Adaptive Music State
```python
# Create an exploration state with crossfade
exploration_state = MusicState.create(
    tenant_id=TenantId(1),
    world_id=EntityId(1),
    name="Forest Exploration State",
    description=Description("Music state for forest exploration"),
    is_silence_moment=False,
    default_track_id=EntityId(100),  # Default forest ambience track
    crossfade_duration_seconds=3.0,
    allow_interrupts=True,
    priority=5
)

# Create a silence moment state
dramatic_pause = MusicState.create(
    tenant_id=TenantId(1),
    world_id=EntityId(1),
    name="Dramatic Revelation Silence",
    description=Description("Silence before a major revelation"),
    is_silence_moment=True,
    crossfade_duration_seconds=1.0,
    allow_interrupts=False,
    priority=15
)
```

## Domain Invariants

### MusicTheme Invariants
- Name must not be empty and ≤ 255 characters
- Duration must be non-negative if specified
- Must belong to exactly one World
- Version increases monotonically
- Updated timestamp ≥ created timestamp

### MusicTrack Invariants
- Name must not be empty and ≤ 255 characters
- Intensity level must be 0-10 if specified
- Duration must be non-negative
- Loop start time < loop end time if both specified
- Loop times must be non-negative

### MusicState Invariants
- Name must not be empty and ≤ 255 characters
- Crossfade duration must be non-negative
- Priority must be non-negative
- Version increases monotonically

### MusicControl Invariants
- Name must not be empty and ≤ 255 characters
- Priority must be non-negative
- Fade in/out durations must be non-negative
- Interrupt priority threshold must be non-negative
- Version increases monotonically

## Testing

All music entities have comprehensive unit tests covering:
- Entity creation and factory methods
- Invariant validation
- Update operations and version tracking
- Association management
- Edge cases and error conditions
- Integration between entities

Test file: `tests/test_music_entities.py` (36 tests, all passing)

## Integration with Existing System

The music entities integrate seamlessly with the existing lore system:
- Follow the same domain-driven design patterns
- Use existing value objects (TenantId, EntityId, Description, etc.)
- Maintain version tracking and timestamp management
- Respect tenant isolation
- Support hierarchical relationships with World entities

## Future Enhancements

Potential future additions:
1. Repository implementations for persistence (SQL, Elasticsearch)
2. GUI tabs for music management
3. Audio file validation and metadata extraction
4. Music preview and playback in the editor
5. Automatic intensity level detection
6. Music generation integration (AI-based composition)
7. Export to game engine formats (Unity, Unreal, etc.)
