"""
Tests for Music System Entities

Tests for MusicTheme, MusicTrack, MusicState, and MusicControl entities.
"""
import pytest
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
from src.domain.exceptions import InvariantViolation


# Test fixtures
def make_basic_music_theme():
    """Create a basic music theme for testing."""
    return MusicTheme.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Epic Battle Theme",
        description=Description("A thrilling combat theme"),
        theme_type=MusicThemeType.COMBAT,
    )


def make_basic_music_track():
    """Create a basic music track for testing."""
    return MusicTrack.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Ambient Forest Loop",
        description=Description("Peaceful forest ambience"),
        system_type=MusicSystemType.AMBIENT_LOOP,
        is_loopable=True,
    )


def make_basic_music_state():
    """Create a basic music state for testing."""
    return MusicState.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Combat State",
        description=Description("State for combat music"),
        priority=5,
    )


def make_basic_music_control():
    """Create a basic music control for testing."""
    return MusicControl.create(
        tenant_id=TenantId(1),
        world_id=EntityId(1),
        name="Boss Fight Control",
        description=Description("Controls music for boss fights"),
        priority=10,
    )


# MusicTheme Tests
class TestMusicTheme:
    def test_create_music_theme(self):
        """Test creating a basic music theme."""
        theme = make_basic_music_theme()
        assert theme.name == "Epic Battle Theme"
        assert theme.theme_type == MusicThemeType.COMBAT
        assert theme.version.value == 1
    
    def test_music_theme_rename(self):
        """Test renaming a music theme."""
        theme = make_basic_music_theme()
        theme.rename("Ultimate Battle Theme")
        assert theme.name == "Ultimate Battle Theme"
        assert theme.version.value == 2
    
    def test_music_theme_empty_name_raises(self):
        """Test that empty name raises error."""
        with pytest.raises(InvariantViolation):
            MusicTheme.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name="",
                description=Description("Test"),
                theme_type=MusicThemeType.MAIN_THEME,
            )
    
    def test_music_theme_update_file_path(self):
        """Test updating file path."""
        theme = make_basic_music_theme()
        theme.update_file_path("/music/combat_theme.mp3")
        assert theme.file_path == "/music/combat_theme.mp3"
        assert theme.version.value == 2
    
    def test_music_theme_update_duration(self):
        """Test updating duration."""
        theme = make_basic_music_theme()
        theme.update_duration(180.5)
        assert theme.duration_seconds == 180.5
        assert theme.version.value == 2
    
    def test_music_theme_negative_duration_raises(self):
        """Test that negative duration raises error."""
        theme = make_basic_music_theme()
        with pytest.raises(InvariantViolation):
            theme.update_duration(-10.0)
    
    def test_music_theme_associate_with_character(self):
        """Test associating theme with character."""
        theme = make_basic_music_theme()
        theme.associate_with_character(EntityId(42))
        assert theme.character_id.value == 42
        assert theme.version.value == 2
    
    def test_music_theme_associate_with_location(self):
        """Test associating theme with location."""
        theme = make_basic_music_theme()
        theme.associate_with_location(EntityId(99))
        assert theme.location_id.value == 99
        assert theme.version.value == 2


# MusicTrack Tests
class TestMusicTrack:
    def test_create_music_track(self):
        """Test creating a basic music track."""
        track = make_basic_music_track()
        assert track.name == "Ambient Forest Loop"
        assert track.system_type == MusicSystemType.AMBIENT_LOOP
        assert track.is_loopable is True
        assert track.version.value == 1
    
    def test_music_track_update_intensity(self):
        """Test updating intensity level."""
        track = make_basic_music_track()
        track.update_intensity(7)
        assert track.intensity_level == 7
        assert track.version.value == 2
    
    def test_music_track_intensity_out_of_range_raises(self):
        """Test that intensity out of range raises error."""
        track = make_basic_music_track()
        with pytest.raises(InvariantViolation):
            track.update_intensity(11)
        with pytest.raises(InvariantViolation):
            track.update_intensity(-1)
    
    def test_music_track_set_loopable(self):
        """Test setting loopable flag."""
        track = make_basic_music_track()
        track.set_loopable(False)
        assert track.is_loopable is False
        assert track.version.value == 2
    
    def test_music_track_set_loop_points(self):
        """Test setting loop start and end points."""
        track = make_basic_music_track()
        track.set_loop_points(10.5, 45.2)
        assert track.loop_start_time == 10.5
        assert track.loop_end_time == 45.2
        assert track.version.value == 2
    
    def test_music_track_invalid_loop_points_raises(self):
        """Test that invalid loop points raise error."""
        track = make_basic_music_track()
        with pytest.raises(InvariantViolation):
            track.set_loop_points(50.0, 30.0)  # Start after end
        with pytest.raises(InvariantViolation):
            track.set_loop_points(-5.0, 30.0)  # Negative start
    
    def test_music_track_associate_with_theme(self):
        """Test associating track with theme."""
        track = make_basic_music_track()
        track.associate_with_theme(EntityId(123))
        assert track.music_theme_id.value == 123
        assert track.version.value == 2


# MusicState Tests
class TestMusicState:
    def test_create_music_state(self):
        """Test creating a basic music state."""
        state = make_basic_music_state()
        assert state.name == "Combat State"
        assert state.priority == 5
        assert state.is_silence_moment is False
        assert state.version.value == 1
    
    def test_music_state_update_priority(self):
        """Test updating priority."""
        state = make_basic_music_state()
        state.update_priority(8)
        assert state.priority == 8
        assert state.version.value == 2
    
    def test_music_state_negative_priority_raises(self):
        """Test that negative priority raises error."""
        state = make_basic_music_state()
        with pytest.raises(InvariantViolation):
            state.update_priority(-1)
    
    def test_music_state_update_crossfade_duration(self):
        """Test updating crossfade duration."""
        state = make_basic_music_state()
        state.update_crossfade_duration(5.0)
        assert state.crossfade_duration_seconds == 5.0
        assert state.version.value == 2
    
    def test_music_state_negative_crossfade_raises(self):
        """Test that negative crossfade duration raises error."""
        state = make_basic_music_state()
        with pytest.raises(InvariantViolation):
            state.update_crossfade_duration(-1.0)
    
    def test_music_state_set_silence_moment(self):
        """Test setting silence moment flag."""
        state = make_basic_music_state()
        state.set_silence_moment(True)
        assert state.is_silence_moment is True
        assert state.version.value == 2
    
    def test_music_state_set_interrupt_behavior(self):
        """Test setting interrupt behavior."""
        state = make_basic_music_state()
        state.set_interrupt_behavior(False)
        assert state.allow_interrupts is False
        assert state.version.value == 2
    
    def test_music_state_set_default_track(self):
        """Test setting default track."""
        state = make_basic_music_state()
        state.set_default_track(EntityId(55))
        assert state.default_track_id.value == 55
        assert state.version.value == 2


# MusicControl Tests
class TestMusicControl:
    def test_create_music_control(self):
        """Test creating a basic music control."""
        control = make_basic_music_control()
        assert control.name == "Boss Fight Control"
        assert control.priority == 10
        assert control.version.value == 1
    
    def test_music_control_update_lore_context(self):
        """Test updating lore context."""
        control = make_basic_music_control()
        control.update_lore_context(
            narrative_phase=NarrativePhase.CLIMAX,
            emotional_tone=EmotionalTone.EPIC,
            player_context=PlayerContext.COMBAT,
        )
        assert control.narrative_phase == NarrativePhase.CLIMAX
        assert control.emotional_tone == EmotionalTone.EPIC
        assert control.player_context == PlayerContext.COMBAT
        assert control.version.value == 2
    
    def test_music_control_update_priority(self):
        """Test updating priority."""
        control = make_basic_music_control()
        control.update_priority(15)
        assert control.priority == 15
        assert control.version.value == 2
    
    def test_music_control_update_fade_rules(self):
        """Test updating fade rules."""
        control = make_basic_music_control()
        control.update_fade_rules(fade_in_duration_seconds=2.5, fade_out_duration_seconds=3.0)
        assert control.fade_in_duration_seconds == 2.5
        assert control.fade_out_duration_seconds == 3.0
        assert control.version.value == 2
    
    def test_music_control_negative_fade_raises(self):
        """Test that negative fade durations raise error."""
        control = make_basic_music_control()
        with pytest.raises(InvariantViolation):
            control.update_fade_rules(fade_in_duration_seconds=-1.0)
    
    def test_music_control_update_interrupt_rules(self):
        """Test updating interrupt rules."""
        control = make_basic_music_control()
        control.update_interrupt_rules(
            allow_interrupt=False,
            can_interrupt_others=True,
            interrupt_priority_threshold=5,
        )
        assert control.allow_interrupt is False
        assert control.can_interrupt_others is True
        assert control.interrupt_priority_threshold == 5
        assert control.version.value == 2
    
    def test_music_control_associate_with_music_state(self):
        """Test associating control with music state."""
        control = make_basic_music_control()
        control.associate_with_music_state(EntityId(77))
        assert control.music_state_id.value == 77
        assert control.version.value == 2
    
    def test_music_control_associate_with_music_track(self):
        """Test associating control with music track."""
        control = make_basic_music_control()
        control.associate_with_music_track(EntityId(88))
        assert control.music_track_id.value == 88
        assert control.version.value == 2
    
    def test_music_control_associate_with_music_theme(self):
        """Test associating control with music theme."""
        control = make_basic_music_control()
        control.associate_with_music_theme(EntityId(99))
        assert control.music_theme_id.value == 99
        assert control.version.value == 2


# Integration Tests
class TestMusicSystemIntegration:
    def test_theme_track_relationship(self):
        """Test relationship between theme and track."""
        theme = make_basic_music_theme()
        track = make_basic_music_track()
        
        # Simulate theme having ID after save
        theme_id = EntityId(100)
        object.__setattr__(theme, 'id', theme_id)
        
        # Associate track with theme
        track.associate_with_theme(theme_id)
        assert track.music_theme_id == theme_id
    
    def test_state_control_relationship(self):
        """Test relationship between state and control."""
        state = make_basic_music_state()
        control = make_basic_music_control()
        
        # Simulate state having ID after save
        state_id = EntityId(200)
        object.__setattr__(state, 'id', state_id)
        
        # Associate control with state
        control.associate_with_music_state(state_id)
        assert control.music_state_id == state_id
    
    def test_theme_character_association(self):
        """Test theme can be associated with character."""
        theme = MusicTheme.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Hero Theme",
            description=Description("The hero's personal theme"),
            theme_type=MusicThemeType.CHARACTER_THEME,
            character_id=EntityId(42),
        )
        assert theme.character_id.value == 42
        assert theme.theme_type == MusicThemeType.CHARACTER_THEME
    
    def test_control_with_full_context(self):
        """Test control with complete lore context."""
        control = MusicControl.create(
            tenant_id=TenantId(1),
            world_id=EntityId(1),
            name="Climactic Battle Control",
            description=Description("Control for the final boss battle"),
            lore_state="final_battle",
            narrative_phase=NarrativePhase.CLIMAX,
            emotional_tone=EmotionalTone.EPIC,
            player_context=PlayerContext.COMBAT,
            priority=20,
            fade_in_duration_seconds=0.5,
            fade_out_duration_seconds=2.0,
            allow_interrupt=False,
            can_interrupt_others=True,
            interrupt_priority_threshold=15,
        )
        assert control.lore_state == "final_battle"
        assert control.narrative_phase == NarrativePhase.CLIMAX
        assert control.emotional_tone == EmotionalTone.EPIC
        assert control.can_interrupt_others is True
