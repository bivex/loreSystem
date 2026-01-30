"""
Fade entity for visual fade effects.
Part of AAA game development domain entities.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class Fade:
    """
    Represents a fade effect in a game.
    Fades control the opacity of a color overlay.
    """

    id: str
    tenant_id: str
    name: str
    fade_type: str
    duration_ms: int
    created_at: datetime
    updated_at: datetime

    # Optional fields
    description: Optional[str] = None
    color: str = "#000000"  # Hex color, default black
    from_opacity: float = 0.0
    to_opacity: float = 1.0
    easing: str = "linear"
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        fade_type: str,
        duration_ms: int,
        description: Optional[str] = None,
        color: str = "#000000",
        from_opacity: float = 0.0,
        to_opacity: float = 1.0,
        easing: str = "linear",
        metadata: Optional[dict] = None,
    ) -> "Fade":
        """
        Factory method to create a new Fade.

        Args:
            tenant_id: Tenant identifier
            name: Fade name
            fade_type: Type of fade (in, out, in-out)
            duration_ms: Duration in milliseconds
            description: Optional description
            color: Fade color in hex format
            from_opacity: Starting opacity (0.0 to 1.0)
            to_opacity: Ending opacity (0.0 to 1.0)
            easing: Easing function
            metadata: Additional metadata

        Returns:
            New Fade instance

        Raises:
            ValueError: If validation fails
        """
        now = datetime.utcnow()

        # Validation
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        if not name or not name.strip():
            raise ValueError("name cannot be empty")

        valid_types = ["in", "out", "in-out", "out-in"]
        if fade_type not in valid_types:
            raise ValueError(f"fade_type must be one of: {', '.join(valid_types)}")

        if duration_ms <= 0:
            raise ValueError("duration_ms must be positive")

        if not color or not color.strip():
            raise ValueError("color cannot be empty")
        if not color.startswith("#") or len(color) != 7:
            raise ValueError("color must be in hex format (#RRGGBB)")

        if not 0.0 <= from_opacity <= 1.0:
            raise ValueError("from_opacity must be between 0.0 and 1.0")

        if not 0.0 <= to_opacity <= 1.0:
            raise ValueError("to_opacity must be between 0.0 and 1.0")

        valid_easings = [
            "linear", "ease-in", "ease-out", "ease-in-out",
            "smoothstep", "quad", "cubic"
        ]
        if easing not in valid_easings:
            raise ValueError(f"easing must be one of: {', '.join(valid_easings)}")

        return cls(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id.strip(),
            name=name.strip(),
            fade_type=fade_type,
            duration_ms=duration_ms,
            created_at=now,
            updated_at=now,
            description=description.strip() if description else None,
            color=color.strip(),
            from_opacity=from_opacity,
            to_opacity=to_opacity,
            easing=easing,
            metadata=metadata or {},
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        fade_type: Optional[str] = None,
        duration_ms: Optional[int] = None,
        color: Optional[str] = None,
        from_opacity: Optional[float] = None,
        to_opacity: Optional[float] = None,
        easing: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Update fade properties.

        Args:
            name: New name
            description: New description
            fade_type: New fade type
            duration_ms: New duration
            color: New color
            from_opacity: New starting opacity
            to_opacity: New ending opacity
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

        if fade_type is not None:
            valid_types = ["in", "out", "in-out", "out-in"]
            if fade_type not in valid_types:
                raise ValueError(f"fade_type must be one of: {', '.join(valid_types)}")
            self.fade_type = fade_type

        if duration_ms is not None:
            if duration_ms <= 0:
                raise ValueError("duration_ms must be positive")
            self.duration_ms = duration_ms

        if color is not None:
            if not color or not color.strip():
                raise ValueError("color cannot be empty")
            if not color.startswith("#") or len(color) != 7:
                raise ValueError("color must be in hex format (#RRGGBB)")
            self.color = color.strip()

        if from_opacity is not None:
            if not 0.0 <= from_opacity <= 1.0:
                raise ValueError("from_opacity must be between 0.0 and 1.0")
            self.from_opacity = from_opacity

        if to_opacity is not None:
            if not 0.0 <= to_opacity <= 1.0:
                raise ValueError("to_opacity must be between 0.0 and 1.0")
            self.to_opacity = to_opacity

        if easing is not None:
            valid_easings = [
                "linear", "ease-in", "ease-out", "ease-in-out",
                "smoothstep", "quad", "cubic"
            ]
            if easing not in valid_easings:
                raise ValueError(f"easing must be one of: {', '.join(valid_easings)}")
            self.easing = easing

        if metadata is not None:
            self.metadata = metadata

        self.updated_at = datetime.utcnow()
