"""
CameraPath entity for game camera movement.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import uuid


@dataclass
class CameraPath:
    """
    Represents a predefined camera movement path in a game.
    Camera paths control camera position and orientation over time.
    """

    id: str
    tenant_id: str
    name: str
    duration_ms: int
    keyframes: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    easing: str = "linear"
    loop: bool = False
    look_at_target: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        duration_ms: int,
        keyframes: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        easing: str = "linear",
        loop: bool = False,
        look_at_target: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> "CameraPath":
        """
        Factory method to create a new CameraPath.

        Args:
            tenant_id: Tenant identifier
            name: Camera path name
            duration_ms: Duration in milliseconds
            keyframes: List of keyframe dictionaries with position, rotation, time
            description: Optional description
            easing: Easing function (linear, ease-in, ease-out, etc.)
            loop: Whether path loops
            look_at_target: Target to look at during movement
            metadata: Additional metadata

        Returns:
            New CameraPath instance

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

        valid_easings = [
            "linear", "ease-in", "ease-out", "ease-in-out",
            "smoothstep", "catmull-rom", "bezier"
        ]
        if easing not in valid_easings:
            raise ValueError(f"easing must be one of: {', '.join(valid_easings)}")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            name=name.strip(),
            duration_ms=duration_ms,
            keyframes=keyframes or [],
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            easing=easing,
            loop=loop,
            look_at_target=look_at_target.strip() if look_at_target else None,
            metadata=metadata or {},
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        keyframes: Optional[List[Dict[str, Any]]] = None,
        easing: Optional[str] = None,
        loop: Optional[bool] = None,
        look_at_target: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update camera path properties.

        Args:
            name: New name
            description: New description
            keyframes: New keyframes
            easing: New easing function
            loop: New loop flag
            look_at_target: New look-at target
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

        if keyframes is not None:
            self.keyframes = keyframes

        if easing is not None:
            valid_easings = [
                "linear", "ease-in", "ease-out", "ease-in-out",
                "smoothstep", "catmull-rom", "bezier"
            ]
            if easing not in valid_easings:
                raise ValueError(f"easing must be one of: {', '.join(valid_easings)}")
            self.easing = easing

        if loop is not None:
            self.loop = loop

        if look_at_target is not None:
            self.look_at_target = look_at_target.strip() if look_at_target else None

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()

    def add_keyframe(self, keyframe: Dict[str, Any]) -> None:
        """Add a keyframe to the path."""
        if keyframe:
            self.keyframes.append(keyframe)
            self.updated_at = datetime.utcnow()

    def remove_keyframe(self, index: int) -> None:
        """Remove a keyframe by index."""
        if 0 <= index < len(self.keyframes):
            self.keyframes.pop(index)
            self.updated_at = datetime.utcnow()
