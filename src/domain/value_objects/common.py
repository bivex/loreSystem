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
