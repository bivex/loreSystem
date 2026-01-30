"""Disposition entity - General attitude toward entities."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Disposition:
    """Represents general disposition/attitude toward entities."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    entity_id: str = ""  # Character/NPC with this disposition
    target_type: str = ""  # "race", "class", "faction", etc.
    target_value: str = ""  # "human", "elf", "warrior", etc.
    attitude: str = "neutral"  # hostile, unfriendly, neutral, friendly, helpful
    intensity: int = 0  # 0-100 strength of attitude

    @classmethod
    def create(
        cls,
        tenant_id: str,
        entity_id: str,
        target_type: str,
        target_value: str,
        attitude: str = "neutral",
        intensity: int = 0,
    ) -> Self:
        """Factory method to create a new Disposition."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not entity_id:
            raise ValueError("entity_id is required")
        if not target_type:
            raise ValueError("target_type is required")
        if not target_value:
            raise ValueError("target_value is required")

        valid_attitudes = ["hostile", "unfriendly", "neutral", "friendly", "helpful"]
        if attitude not in valid_attitudes:
            raise ValueError(f"attitude must be one of {valid_attitudes}")

        if not 0 <= intensity <= 100:
            raise ValueError("intensity must be between 0 and 100")

        return cls(
            tenant_id=tenant_id,
            entity_id=entity_id,
            target_type=target_type,
            target_value=target_value,
            attitude=attitude,
            intensity=intensity,
        )

    def change_attitude(self, new_attitude: str) -> None:
        """Change the disposition attitude."""
        valid_attitudes = ["hostile", "unfriendly", "neutral", "friendly", "helpful"]
        if new_attitude not in valid_attitudes:
            raise ValueError(f"attitude must be one of {valid_attitudes}")
        self.attitude = new_attitude
        self.updated_at = datetime.utcnow()

    def set_intensity(self, intensity: int) -> None:
        """Set the intensity of disposition."""
        self.intensity = max(0, min(100, intensity))
        self.updated_at = datetime.utcnow()

    def is_hostile(self) -> bool:
        """Check if disposition is hostile."""
        return self.attitude in ["hostile", "unfriendly"]

    def is_friendly(self) -> bool:
        """Check if disposition is friendly."""
        return self.attitude in ["friendly", "helpful"]
