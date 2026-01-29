#!/usr/bin/env python3
"""
Music System Demo

Demonstrates the usage of the new music system entities in the loreSystem.
Shows how to create themes, tracks, states, and controls with proper relationships.
"""

from src.domain.entities.music_theme import MusicTheme
from src.domain.entities.music_track import MusicTrack
from src.domain.entities.music_state import MusicState
from src.domain.entities.music_control import MusicControl
from src.domain.value_objects.common import (
    TenantId,
    EntityId,
    Description,
    MusicThemeType,
    MusicSystemType,
    EmotionalTone,
    NarrativePhase,
    PlayerContext,
)


def demo_character_theme():
    """Demonstrate creating a character theme with leitmotif."""
    print("\n=== Character Theme Demo ===")
    
    # Create a character theme
    hero_theme = MusicTheme.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="The Hero's Journey",
        description=Description("Epic orchestral theme for the main protagonist"),
        theme_type=MusicThemeType.CHARACTER_THEME,
        character_id=EntityId(42),
        file_path="/music/themes/hero_theme.mp3",
        duration_seconds=210.5,
        composer="John Williams Inspired"
    )
    
    print(f"Created: {hero_theme}")
    print(f"  Type: {hero_theme.theme_type.value}")
    print(f"  Associated with Character ID: {hero_theme.character_id}")
    print(f"  Duration: {hero_theme.duration_seconds}s")
    print(f"  Composer: {hero_theme.composer}")
    
    # Create a leitmotif for the hero
    hero_motif = MusicTrack.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Hero's Leitmotif",
        description=Description("Short recurring heroic motif (8 bars)"),
        system_type=MusicSystemType.LEITMOTIF,
        file_path="/music/motifs/hero_leitmotif.mp3",
        duration_seconds=8.0,
        intensity_level=7,
        is_loopable=False,
    )
    
    # Simulate setting IDs after database save
    object.__setattr__(hero_theme, 'id', EntityId(100))
    hero_motif.associate_with_theme(hero_theme.id)
    
    print(f"\nCreated: {hero_motif}")
    print(f"  System Type: {hero_motif.system_type.value}")
    print(f"  Associated with Theme ID: {hero_motif.music_theme_id}")
    print(f"  Intensity: {hero_motif.intensity_level}/10")


def demo_combat_system():
    """Demonstrate adaptive combat music with intensity layers."""
    print("\n=== Combat Music System Demo ===")
    
    # Create base combat theme
    combat_theme = MusicTheme.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Battle Tension",
        description=Description("Dynamic combat music with multiple intensity layers"),
        theme_type=MusicThemeType.COMBAT,
        file_path="/music/combat/battle_base.mp3",
        duration_seconds=120.0,
    )
    
    print(f"Created: {combat_theme}")
    
    # Create intensity layers
    object.__setattr__(combat_theme, 'id', EntityId(200))
    
    for intensity in [3, 5, 7, 9]:
        layer = MusicTrack.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name=f"Combat Layer - Intensity {intensity}",
            description=Description(f"Combat music layer at intensity level {intensity}"),
            system_type=MusicSystemType.DYNAMIC_LAYER,
            music_theme_id=combat_theme.id,
            intensity_level=intensity,
            is_loopable=True,
            file_path=f"/music/combat/layer_{intensity}.mp3",
        )
        print(f"  Created layer: Intensity {layer.intensity_level}/10")
    
    # Create a stinger for hits
    hit_stinger = MusicTrack.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Heavy Hit Stinger",
        description=Description("Musical accent for significant hits"),
        system_type=MusicSystemType.STINGER,
        music_theme_id=combat_theme.id,
        duration_seconds=1.2,
        intensity_level=10,
        is_loopable=False,
    )
    
    print(f"  Created stinger: {hit_stinger.name} ({hit_stinger.duration_seconds}s)")


def demo_boss_fight_control():
    """Demonstrate boss fight music control with high priority."""
    print("\n=== Boss Fight Control Demo ===")
    
    # Create boss theme
    boss_theme = MusicTheme.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Ancient Evil Awakens",
        description=Description("Epic boss battle theme with choir and orchestra"),
        theme_type=MusicThemeType.BOSS_FIGHT,
        duration_seconds=360.0,
        composer="Hans Zimmer Inspired"
    )
    
    print(f"Created: {boss_theme}")
    
    # Create music control for the boss fight
    boss_control = MusicControl.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Final Boss Music Control",
        description=Description("Controls music during the final boss encounter"),
        lore_state="final_boss_battle",
        narrative_phase=NarrativePhase.CLIMAX,
        emotional_tone=EmotionalTone.EPIC,
        player_context=PlayerContext.COMBAT,
        priority=20,  # Very high priority
        fade_in_duration_seconds=0.5,
        fade_out_duration_seconds=3.0,
        allow_interrupt=False,  # Cannot be interrupted
        can_interrupt_others=True,  # Can interrupt anything
        interrupt_priority_threshold=15,
    )
    
    print(f"\nCreated: {boss_control}")
    print(f"  Lore State: {boss_control.lore_state}")
    print(f"  Narrative Phase: {boss_control.narrative_phase.value}")
    print(f"  Emotional Tone: {boss_control.emotional_tone.value}")
    print(f"  Player Context: {boss_control.player_context.value}")
    print(f"  Priority: {boss_control.priority}")
    print(f"  Can be interrupted: {boss_control.allow_interrupt}")
    print(f"  Can interrupt others: {boss_control.can_interrupt_others}")
    print(f"  Fade in: {boss_control.fade_in_duration_seconds}s")
    print(f"  Fade out: {boss_control.fade_out_duration_seconds}s")


def demo_exploration_state():
    """Demonstrate exploration music state with ambient loops."""
    print("\n=== Exploration State Demo ===")
    
    # Create exploration theme
    forest_theme = MusicTheme.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Enchanted Forest",
        description=Description("Peaceful forest exploration music"),
        theme_type=MusicThemeType.CALM_EXPLORATION,
        location_id=EntityId(10),  # Forest location
    )
    
    print(f"Created: {forest_theme}")
    
    # Create ambient loop track
    object.__setattr__(forest_theme, 'id', EntityId(300))
    
    ambient_loop = MusicTrack.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Forest Ambience Loop",
        description=Description("Seamless forest ambient loop"),
        system_type=MusicSystemType.AMBIENT_LOOP,
        music_theme_id=forest_theme.id,
        duration_seconds=45.0,
        intensity_level=2,
        is_loopable=True,
        loop_start_time=5.0,
        loop_end_time=40.0,
    )
    
    print(f"  Created: {ambient_loop}")
    print(f"    Loopable: {ambient_loop.is_loopable}")
    print(f"    Loop points: {ambient_loop.loop_start_time}s to {ambient_loop.loop_end_time}s")
    
    # Create music state
    object.__setattr__(ambient_loop, 'id', EntityId(301))
    
    exploration_state = MusicState.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Forest Exploration State",
        description=Description("Music state for peaceful forest exploration"),
        is_silence_moment=False,
        default_track_id=ambient_loop.id,
        crossfade_duration_seconds=3.0,
        allow_interrupts=True,
        priority=5,
    )
    
    print(f"\nCreated: {exploration_state}")
    print(f"  Default Track: {exploration_state.default_track_id}")
    print(f"  Crossfade Duration: {exploration_state.crossfade_duration_seconds}s")
    print(f"  Priority: {exploration_state.priority}")
    print(f"  Can be interrupted: {exploration_state.allow_interrupts}")


def demo_dramatic_silence():
    """Demonstrate silence moment for dramatic effect."""
    print("\n=== Dramatic Silence Demo ===")
    
    # Create a silence state for dramatic moments
    dramatic_silence = MusicState.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Revelation Silence",
        description=Description("Silence before a major story revelation"),
        is_silence_moment=True,
        crossfade_duration_seconds=1.0,
        allow_interrupts=False,
        priority=15,  # High priority - important narrative moment
    )
    
    print(f"Created: {dramatic_silence}")
    print(f"  Is Silence: {dramatic_silence.is_silence_moment}")
    print(f"  Priority: {dramatic_silence.priority}")
    print(f"  Can be interrupted: {dramatic_silence.allow_interrupts}")


def main():
    """Run all demos."""
    print("=" * 60)
    print("MUSIC SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    demo_character_theme()
    demo_combat_system()
    demo_boss_fight_control()
    demo_exploration_state()
    demo_dramatic_silence()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
