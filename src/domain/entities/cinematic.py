"""
Cinematic entity for game cinematic sequences.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
import uuid


@dataclass
class Cinematic:
    """
    Represents a complete cinematic sequence in a game.
    Cinematics are collections of camera movements, animations, and effects.
    """

    id: str
    tenant_id: str
    name: str
    duration_ms: int
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    scene_id: Optional[str] = None
    camera_path_id: Optional[str] = None
    transitions: List[str] = field(default_factory=list)
    fades: List[str] = field(default_factory=list)
    priority: int = 0
    is_looping: bool = False
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        duration_ms: int,
        description: Optional[str] = None,
        scene_id: Optional[str] = None,
        camera_path_id: Optional[str] = None,
        transitions: Optional[List[str]] = None,
        fades: Optional[List[str]] = None,
        priority: int = 0,
        is_looping: bool = False,
        metadata: Optional[dict] = None,
    ) -> "Cinematic":
        """
        Factory method to create a new Cinematic.

        Args:
            tenant_id: Tenant identifier
            name: Cinematic name
            duration_ms: Duration in milliseconds
            description: Optional description
            scene_id: Associated scene ID
            camera_path_id: Associated camera path ID
            transitions: List of transition IDs
            fades: List of fade IDs
            priority: Priority for concurrent cinematics
            is_looping: Whether cinematic loops
            metadata: Additional metadata

        Returns:
            New Cinematic instance

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
            scene_id=scene_id.strip() if scene_id else None,
            camera_path_id=camera_path_id.strip() if camera_path_id else None,
            transitions=transitions or [],
            fades=fades or [],
            priority=priority,
            is_looping=is_looping,
            metadata=metadata or {},
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scene_id: Optional[str] = None,
        camera_path_id: Optional[str] = None,
        transitions: Optional[List[str]] = None,
        fades: Optional[List[str]] = None,
        priority: Optional[int] = None,
        is_looping: Optional[bool] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update cinematic properties.

        Args:
            name: New name
            description: New description
            scene_id: New scene ID
            camera_path_id: New camera path ID
            transitions: New list of transition IDs
            fades: New list of fade IDs
            priority: New priority
            is_looping: New looping flag
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

        if scene_id is not None:
            self.scene_id = scene_id.strip() if scene_id else None

        if camera_path_id is not None:
            self.camera_path_id = camera_path_id.strip() if camera_path_id else None

        if transitions is not None:
            self.transitions = transitions

        if fades is not None:
            self.fades = fades

        if priority is not None:
            if priority < 0:
                raise ValueError("priority cannot be negative")
            self.priority = priority

        if is_looping is not None:
            self.is_looping = is_looping

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()

    def add_transition(self, transition_id: str) -> None:
        """Add a transition to the cinematic."""
        if transition_id and transition_id.strip():
            self.transitions.append(transition_id.strip())
            self.updated_at = datetime.utcnow()

    def add_fade(self, fade_id: str) -> None:
        """Add a fade to the cinematic."""
        if fade_id and fade_id.strip():
            self.fades.append(fade_id.strip())
            self.updated_at = datetime.utcnow()
