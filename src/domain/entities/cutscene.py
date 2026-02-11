"""
Cutscene entity for game cinematic sequences.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class Cutscene:
    """
    Represents a cinematic cutscene in a game.
    Cutscenes are non-interactive sequences that advance the story.
    """

    id: str
    tenant_id: str
    name: str
    duration_ms: int
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    trigger_event: Optional[str] = None
    priority: int = 0
    skippable: bool = True
    auto_start: bool = False
    camera_id: Optional[str] = None
    cinematic_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        duration_ms: int,
        description: Optional[str] = None,
        trigger_event: Optional[str] = None,
        priority: int = 0,
        skippable: bool = True,
        auto_start: bool = False,
        camera_id: Optional[str] = None,
        cinematic_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "Cutscene":
        """
        Factory method to create a new Cutscene.

        Args:
            tenant_id: Tenant identifier
            name: Cutscene name
            duration_ms: Duration in milliseconds
            description: Optional description
            trigger_event: Event that triggers this cutscene
            priority: Priority for concurrent cutscenes
            skippable: Whether player can skip
            auto_start: Whether cutscene starts automatically
            camera_id: Associated camera ID
            cinematic_id: Associated cinematic ID
            metadata: Additional metadata

        Returns:
            New Cutscene instance

        Raises:
            ValueError: If validation fails
        """
        now = datetime.utcnow()

        # Validation
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        if not name or not name.strip():
            raise ValueError("name cannot be empty")

        if duration_ms <= 0:
            raise ValueError("duration_ms must be positive")

        if priority < 0:
            raise ValueError("priority cannot be negative")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            name=name.strip(),
            duration_ms=duration_ms,
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            trigger_event=trigger_event.strip() if trigger_event else None,
            priority=priority,
            skippable=skippable,
            auto_start=auto_start,
            camera_id=camera_id.strip() if camera_id else None,
            cinematic_id=cinematic_id.strip() if cinematic_id else None,
            metadata=metadata or {},
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        trigger_event: Optional[str] = None,
        priority: Optional[int] = None,
        skippable: Optional[bool] = None,
        auto_start: Optional[bool] = None,
        camera_id: Optional[str] = None,
        cinematic_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update cutscene properties.

        Args:
            name: New name
            description: New description
            trigger_event: New trigger event
            priority: New priority
            skippable: New skippable flag
            auto_start: New auto_start flag
            camera_id: New camera ID
            cinematic_id: New cinematic ID
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

        if priority is not None:
            if priority < 0:
                raise ValueError("priority cannot be negative")
            self.priority = priority

        if skippable is not None:
            self.skippable = skippable

        if auto_start is not None:
            self.auto_start = auto_start

        if camera_id is not None:
            self.camera_id = camera_id.strip() if camera_id else None

        if cinematic_id is not None:
            self.cinematic_id = cinematic_id.strip() if cinematic_id else None

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()
