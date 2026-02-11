"""
Transition entity for scene transitions.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class Transition:
    """
    Represents a visual transition between scenes or states.
    Transitions include fades, wipes, dissolves, and other effects.
    """

    id: str
    tenant_id: str
    name: str
    transition_type: str
    duration_ms: int
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    from_scene_id: Optional[str] = None
    to_scene_id: Optional[str] = None
    color: Optional[str] = None  # For fades, color transitions
    easing: str = "linear"
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        transition_type: str,
        duration_ms: int,
        description: Optional[str] = None,
        from_scene_id: Optional[str] = None,
        to_scene_id: Optional[str] = None,
        color: Optional[str] = None,
        easing: str = "linear",
        metadata: Optional[dict] = None,
    ) -> "Transition":
        """
        Factory method to create a new Transition.

        Args:
            tenant_id: Tenant identifier
            name: Transition name
            transition_type: Type of transition (fade, wipe, dissolve, etc.)
            duration_ms: Duration in milliseconds
            description: Optional description
            from_scene_id: Source scene ID
            to_scene_id: Destination scene ID
            color: Color for color-based transitions (hex format)
            easing: Easing function
            metadata: Additional metadata

        Returns:
            New Transition instance

        Raises:
            ValueError: If validation fails
        """
        now = datetime.utcnow()

        # Validation
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        if not name or not name.strip():
            raise ValueError("name cannot be empty")

        valid_types = [
            "fade", "fade-in", "fade-out", "crossfade",
            "wipe-left", "wipe-right", "wipe-up", "wipe-down",
            "dissolve", "iris-in", "iris-out", "slide"
        ]
        if transition_type not in valid_types:
            raise ValueError(f"transition_type must be one of: {', '.join(valid_types)}")

        if duration_ms <= 0:
            raise ValueError("duration_ms must be positive")

        valid_easings = [
            "linear", "ease-in", "ease-out", "ease-in-out",
            "smoothstep", "quad", "cubic", "quart", "quint"
        ]
        if easing not in valid_easings:
            raise ValueError(f"easing must be one of: {', '.join(valid_easings)}")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            name=name.strip(),
            transition_type=transition_type,
            duration_ms=duration_ms,
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            from_scene_id=from_scene_id.strip() if from_scene_id else None,
            to_scene_id=to_scene_id.strip() if to_scene_id else None,
            color=color.strip() if color else None,
            easing=easing,
            metadata=metadata or {},
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        transition_type: Optional[str] = None,
        duration_ms: Optional[int] = None,
        from_scene_id: Optional[str] = None,
        to_scene_id: Optional[str] = None,
        color: Optional[str] = None,
        easing: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update transition properties.

        Args:
            name: New name
            description: New description
            transition_type: New transition type
            duration_ms: New duration
            from_scene_id: New source scene ID
            to_scene_id: New destination scene ID
            color: New color
            easing: New easing function
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

        if transition_type is not None:
            valid_types = [
                "fade", "fade-in", "fade-out", "crossfade",
                "wipe-left", "wipe-right", "wipe-up", "wipe-down",
                "dissolve", "iris-in", "iris-out", "slide"
            ]
            if transition_type not in valid_types:
                raise ValueError(f"transition_type must be one of: {', '.join(valid_types)}")
            self.transition_type = transition_type

        if duration_ms is not None:
            if duration_ms <= 0:
                raise ValueError("duration_ms must be positive")
            self.duration_ms = duration_ms

        if from_scene_id is not None:
            self.from_scene_id = from_scene_id.strip() if from_scene_id else None

        if to_scene_id is not None:
            self.to_scene_id = to_scene_id.strip() if to_scene_id else None

        if color is not None:
            self.color = color.strip() if color else None

        if easing is not None:
            valid_easings = [
                "linear", "ease-in", "ease-out", "ease-in-out",
                "smoothstep", "quad", "cubic", "quart", "quint"
            ]
            if easing not in valid_easings:
                raise ValueError(f"easing must be one of: {', '.join(valid_easings)}")
            self.easing = easing

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()
