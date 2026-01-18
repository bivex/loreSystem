"""
Common Value Objects

Value objects are immutable and have no identity.
They are compared by their attributes, not by reference.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class EntityType(str, Enum):
    """Types of lore entities."""
    WORLD = "world"
    CHARACTER = "character"
    EVENT = "event"
    ITEM = "item"
    QUEST = "quest"
    STORYLINE = "storyline"
    PAGE = "page"
    TEMPLATE = "template"
    TAG = "tag"
    IMAGE = "image"
    STORY = "story"
    CHOICE = "choice"
    FLOWCHART = "flowchart"
    HANDOUT = "handout"
    INSPIRATION = "inspiration"
    MAP = "map"
    NOTE = "note"
    REQUIREMENT = "requirement"
    SESSION = "session"
    TOKENBOARD = "tokenboard"
    LOCATION = "location"
    MUSIC_THEME = "music_theme"
    MUSIC_TRACK = "music_track"
    MUSIC_STATE = "music_state"
    MUSIC_CONTROL = "music_control"


class ItemType(str, Enum):
    """Types of items in the lore."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ARTIFACT = "artifact"
    CONSUMABLE = "consumable"
    TOOL = "tool"
    OTHER = "other"


class Rarity(str, Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class ImprovementStatus(str, Enum):
    """Lifecycle states of an improvement proposal."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"


class EventOutcome(str, Enum):
    """Possible outcomes of story events."""
    SUCCESS = "success"
    FAILURE = "failure"
    ONGOING = "ongoing"


class CharacterStatus(str, Enum):
    """Character availability status."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class QuestStatus(str, Enum):
    """Quest completion status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StorylineType(str, Enum):
    """Types of storylines."""
    MAIN = "main"
    SIDE = "side"
    EPISODE = "episode"


class TemplateType(str, Enum):
    """Types of templates."""
    PAGE = "page"
    RUNE = "rune"  # Template within template


class TagType(str, Enum):
    """Types of visual tags."""
    CATEGORY = "category"
    THEME = "theme"
    STATUS = "status"
    CUSTOM = "custom"


class ImageType(str, Enum):
    """Types of images."""
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    GIF = "gif"
    SVG = "svg"


class StoryType(str, Enum):
    """Types of stories in Tome."""
    LINEAR = "linear"
    NON_LINEAR = "non_linear"
    INTERACTIVE = "interactive"


class ChoiceType(str, Enum):
    """Types of player choices."""
    BRANCH = "branch"
    CONSEQUENCE = "consequence"
    DECISION = "decision"


class SessionStatus(str, Enum):
    """Session lifecycle states."""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class NoteType(str, Enum):
    """Types of notes."""
    GENERAL = "general"
    REMINDER = "reminder"
    SESSION = "session"
    CHARACTER = "character"
    PLOT = "plot"


class HandoutType(str, Enum):
    """Types of handouts."""
    DOCUMENT = "document"
    IMAGE = "image"
    MAP = "map"
    PROP = "prop"


class InspirationCategory(str, Enum):
    """Categories of inspiration."""
    PLOT = "plot"
    CHARACTER = "character"
    SETTING = "setting"
    ITEM = "item"
    ENCOUNTER = "encounter"
    DIALOGUE = "dialogue"
    OTHER = "other"


class LocationType(str, Enum):
    """Types of locations in the world."""
    BUILDING = "building"  # Generic building
    HOUSE = "house"  # Residential house
    BARN = "barn"  # Storage building
    TEMPLE = "temple"  # Religious building
    CASTLE = "castle"  # Fortified structure
    DUNGEON = "dungeon"  # Underground location
    CAVE = "cave"  # Natural cave
    FOREST = "forest"  # Natural forest area
    MOUNTAIN = "mountain"  # Mountain location
    CITY = "city"  # Large settlement
    VILLAGE = "village"  # Small settlement
    SHOP = "shop"  # Commercial building
    TAVERN = "tavern"  # Inn or pub
    RUINS = "ruins"  # Destroyed structure
    LANDMARK = "landmark"  # Notable feature
    OTHER = "other"  # Other location type


class MusicThemeType(str, Enum):
    """Types of music themes in the lore system."""
    MAIN_THEME = "main_theme"
    WORLD_THEME = "world_theme"
    FACTION_THEME = "faction_theme"
    LOCATION_THEME = "location_theme"
    ERA_THEME = "era_theme"
    CHARACTER_THEME = "character_theme"
    CALM_EXPLORATION = "calm_exploration"
    MYSTERY_AMBIENCE = "mystery_ambience"
    TENSION_BUILD = "tension_build"
    CONFLICT = "conflict"
    COMBAT = "combat"
    BOSS_FIGHT = "boss_fight"
    VICTORY = "victory"
    DEFEAT = "defeat"
    LOSS = "loss"
    DISCOVERY = "discovery"
    REVELATION = "revelation"
    LORE_EXPOSITION = "lore_exposition"
    FLASHBACK = "flashback"
    MEMORY = "memory"
    DREAM = "dream"
    PROPHECY = "prophecy"
    TRAVEL = "travel"
    JOURNEY = "journey"
    TRANSITION = "transition"
    DOWNTIME = "downtime"
    SAFE_ZONE = "safe_zone"
    HUB = "hub"
    CRAFTING = "crafting"
    PREPARATION = "preparation"
    DECISION_MOMENT = "decision_moment"
    MORAL_CHOICE = "moral_choice"
    BETRAYAL = "betrayal"
    TRAGEDY = "tragedy"
    SACRIFICE = "sacrifice"
    HOPE = "hope"
    REBIRTH = "rebirth"
    CLIMAX = "climax"
    RESOLUTION = "resolution"
    EPILOGUE = "epilogue"
    CREDITS = "credits"


class MusicSystemType(str, Enum):
    """Types of music system components."""
    AMBIENT_LOOP = "ambient_loop"
    DYNAMIC_LAYER = "dynamic_layer"
    INTENSITY_LEVEL = "intensity_level"
    STINGER = "stinger"
    CUE = "cue"
    LEITMOTIF = "leitmotif"
    ADAPTIVE_STATE = "adaptive_state"
    CROSSFADE_RULE = "crossfade_rule"
    SILENCE_MOMENT = "silence_moment"


class EmotionalTone(str, Enum):
    """Emotional tones for music control."""
    PEACEFUL = "peaceful"
    TENSE = "tense"
    JOYFUL = "joyful"
    MELANCHOLIC = "melancholic"
    MYSTERIOUS = "mysterious"
    EPIC = "epic"
    DRAMATIC = "dramatic"
    SUSPENSEFUL = "suspenseful"
    TRIUMPHANT = "triumphant"
    SOMBER = "somber"
    HOPEFUL = "hopeful"
    FEARFUL = "fearful"
    AGGRESSIVE = "aggressive"
    CALM = "calm"


class NarrativePhase(str, Enum):
    """Narrative phases for music context."""
    INTRODUCTION = "introduction"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"
    EPILOGUE = "epilogue"
    INTERLUDE = "interlude"
    FLASHBACK = "flashback"


class PlayerContext(str, Enum):
    """Player context states for music adaptation."""
    EXPLORATION = "exploration"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    CUTSCENE = "cutscene"
    MENU = "menu"
    INVENTORY = "inventory"
    CRAFTING = "crafting"
    TRADING = "trading"
    RESTING = "resting"
    TRAVELING = "traveling"


@dataclass(frozen=True)
class TenantId:
    """Tenant identifier for multi-tenancy isolation."""
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("TenantId must be positive")

    def __str__(self) -> str:
        return f"Tenant({self.value})"


@dataclass(frozen=True)
class EntityId:
    """Generic entity identifier."""
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("EntityId must be positive")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class WorldName:
    """World name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("World name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("World name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CharacterName:
    """Character name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Character name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Character name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Backstory:
    """
    Character backstory with minimum length requirement.
    
    Invariant: Must be at least 100 characters to ensure narrative depth.
    """
    value: str

    MIN_LENGTH = 100

    def __post_init__(self):
        if not self.value:
            raise ValueError("Backstory cannot be empty")
        if len(self.value) < self.MIN_LENGTH:
            raise ValueError(
                f"Backstory must be at least {self.MIN_LENGTH} characters, "
                f"got {len(self.value)}"
            )

    def __str__(self) -> str:
        return self.value

    def excerpt(self, length: int = 50) -> str:
        """Return shortened version for display."""
        if len(self.value) <= length:
            return self.value
        return self.value[:length] + "..."


@dataclass(frozen=True)
class Description:
    """Generic text description."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Description cannot be empty")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Version:
    """
    Entity version for optimistic concurrency control.
    
    Version numbers must increase monotonically.
    """
    value: int

    def __post_init__(self):
        if self.value < 1:
            raise ValueError("Version must be >= 1")

    def increment(self) -> 'Version':
        """Return next version."""
        return Version(self.value + 1)

    def __str__(self) -> str:
        return f"v{self.value}"


@dataclass(frozen=True)
class GitCommitHash:
    """SHA-1 commit hash for traceability."""
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Commit hash cannot be empty")
        if len(self.value) != 40:
            raise ValueError("Commit hash must be 40 characters (SHA-1)")
        if not all(c in '0123456789abcdef' for c in self.value.lower()):
            raise ValueError("Commit hash must be hexadecimal")

    def short(self) -> str:
        """Return shortened hash (first 7 chars) for display."""
        return self.value[:7]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Timestamp:
    """UTC timestamp for events."""
    value: datetime

    def __post_init__(self):
        if self.value.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware (UTC)")

    def __str__(self) -> str:
        return self.value.isoformat()

    def __le__(self, other: 'Timestamp') -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, Timestamp):
            return NotImplemented
        return self.value <= other.value

    def __lt__(self, other: 'Timestamp') -> bool:
        """Less than comparison."""
        if not isinstance(other, Timestamp):
            return NotImplemented
        return self.value < other.value

    def __ge__(self, other: 'Timestamp') -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, Timestamp):
            return NotImplemented
        return self.value >= other.value

    def __gt__(self, other: 'Timestamp') -> bool:
        """Greater than comparison."""
        if not isinstance(other, Timestamp):
            return NotImplemented
        return self.value > other.value

    @classmethod
    def now(cls) -> 'Timestamp':
        """Create timestamp for current UTC time."""
        from datetime import timezone
        return cls(datetime.now(timezone.utc))


@dataclass(frozen=True)
class DateRange:
    """
    Date range for events with validation.
    
    Invariant: start_date must be <= end_date if end_date exists.
    """
    start_date: Timestamp
    end_date: Optional[Timestamp] = None

    def __post_init__(self):
        if self.end_date and self.end_date.value < self.start_date.value:
            raise ValueError("End date must be >= start date")

    def is_ongoing(self) -> bool:
        """Check if event is still ongoing (no end date)."""
        return self.end_date is None

    def duration_days(self) -> Optional[int]:
        """Calculate duration in days, or None if ongoing."""
        if self.end_date is None:
            return None
        delta = self.end_date.value - self.start_date.value
        return delta.days


@dataclass(frozen=True)
class PageName:
    """Page name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Page name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Page name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TemplateName:
    """Template name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Template name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Template name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TagName:
    """Tag name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Tag name cannot be empty")
        if len(self.value) > 100:
            raise ValueError("Tag name must be <= 100 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ImagePath:
    """Image file path with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Image path cannot be empty")
        if len(self.value) > 500:
            raise ValueError("Image path must be <= 500 characters")
        # Basic validation for file extension
        allowed_ext = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
        if not any(self.value.lower().endswith(ext) for ext in allowed_ext):
            raise ValueError("Image path must have valid extension")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class StoryName:
    """Story name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Story name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Story name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Content:
    """Rich content for pages and stories."""
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Content cannot be empty")

    def __str__(self) -> str:
        return self.value

    def excerpt(self, length: int = 100) -> str:
        """Return shortened version for display."""
        if len(self.value) <= length:
            return self.value
        return self.value[:length] + "..."


@dataclass(frozen=True)
class SessionName:
    """Session name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Session name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Session name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class NoteTitle:
    """Note title with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Note title cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Note title must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MapName:
    """Map name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Map name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Map name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class HandoutName:
    """Handout name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Handout name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Handout name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class InspirationName:
    """Inspiration name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Inspiration name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Inspiration name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TokenboardName:
    """Tokenboard name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Tokenboard name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Tokenboard name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class FlowchartName:
    """Flowchart name with validation."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Flowchart name cannot be empty")
        if len(self.value) > 255:
            raise ValueError("Flowchart name must be <= 255 characters")

    def __str__(self) -> str:
        return self.value
