"""
Flashback entity for narrative flashback sequences.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
import uuid


@dataclass
class Flashback:
    """
    Represents a flashback sequence in a game story.
    Flashbacks are narrative devices that show past events.
    """

    id: str
    tenant_id: str
    name: str
    scene_id: str
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    trigger_event: Optional[str] = None
    flashback_time: Optional[datetime] = None  # In-game time the flashback represents
    duration_ms: Optional[int] = None
    characters: List[str] = field(default_factory=list)  # Character IDs present in flashback
    is_skippable: bool = True
    filter_effect: str = "grayscale"  # Visual filter to distinguish flashback
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        scene_id: str,
        description: Optional[str] = None,
        trigger_event: Optional[str] = None,
        flashback_time: Optional[datetime] = None,
        duration_ms: Optional[int] = None,
        characters: Optional[List[str]] = None,
        is_skippable: bool = True,
        filter_effect: str = "grayscale",
        metadata: Optional[dict] = None,
    ) -> "Flashback":
        """
        Factory method to create a new Flashback.

        Args:
            tenant_id: Tenant identifier
            name: Flashback name
            scene_id: Scene ID for the flashback
            description: Optional description
            trigger_event: Event that triggers this flashback
            flashback_time: In-game time the flashback represents
            duration_ms: Duration in milliseconds
            characters: List of character IDs present
            is_skippable: Whether player can skip
            filter_effect: Visual filter (grayscale, sepia, desaturated, etc.)
            metadata: Additional metadata

        Returns:
            New Flashback instance

        Raises:
            ValueError: If validation fails
        """
        now = datetime.utcnow()

        # Validation
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        if not name or not name.strip():
            raise ValueError("name cannot be empty")

        if not scene_id or not scene_id.strip():
            raise ValueError("scene_id cannot be empty")

        valid_filters = [
            "none", "grayscale", "sepia", "desaturated",
            "vignette", "blur", "dream", "nightmare"
        ]
        if filter_effect not in valid_filters:
            raise ValueError(f"filter_effect must be one of: {', '.join(valid_filters)}")

        if duration_ms is not None and duration_ms <= 0:
            raise ValueError("duration_ms must be positive")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            name=name.strip(),
            scene_id=scene_id.strip(),
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            trigger_event=trigger_event.strip() if trigger_event else None,
            flashback_time=flashback_time,
            duration_ms=duration_ms,
            characters=characters or [],
            is_skippable=is_skippable,
            filter_effect=filter_effect,
            metadata=metadata or {},
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        trigger_event: Optional[str] = None,
        flashback_time: Optional[datetime] = None,
        duration_ms: Optional[int] = None,
        characters: Optional[List[str]] = None,
        is_skippable: Optional[bool] = None,
        filter_effect: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update flashback properties.

        Args:
            name: New name
            description: New description
            trigger_event: New trigger event
            flashback_time: New flashback time
            duration_ms: New duration
            characters: New list of characters
            is_skippable: New skippable flag
            filter_effect: New visual filter
            metadata: New metadata

        Raises:
            ValueError: If validation fails
        """
        if name is not None:
            if not name or not name.strip():
                raise ValueError("name cannot be empty")
            self.name = name.strip()

        if description is not None:
            self.description = description.strip() if description else None

        if trigger_event is not None:
            self.trigger_event = trigger_event.strip() if trigger_event else None

        if flashback_time is not None:
            self.flashback_time = flashback_time

        if duration_ms is not None:
            if duration_ms <= 0:
                raise ValueError("duration_ms must be positive")
            self.duration_ms = duration_ms

        if characters is not None:
            self.characters = characters

        if is_skippable is not None:
            self.is_skippable = is_skippable

        if filter_effect is not None:
            valid_filters = [
                "none", "grayscale", "sepia", "desaturated",
                "vignette", "blur", "dream", "nightmare"
            ]
            if filter_effect not in valid_filters:
                raise ValueError(f"filter_effect must be one of: {', '.join(valid_filters)}")
            self.filter_effect = filter_effect

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()

    def add_character(self, character_id: str) -> None:
        """Add a character to the flashback."""
        if character_id and character_id.strip() and character_id not in self.characters:
            self.characters.append(character_id.strip())
            self.updated_at = datetime.utcnow()

    def remove_character(self, character_id: str) -> None:
        """Remove a character from the flashback."""
        if character_id and character_id.strip() in self.characters:
            self.characters.remove(character_id.strip())
            self.updated_at = datetime.utcnow()
