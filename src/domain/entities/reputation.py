"""Reputation entity - NPC/player reputation tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Reputation:
    """Represents reputation standing with entities/groups."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    target_id: str = ""  # Character, faction, or entity ID
    target_type: str = ""  # "character", "faction", "location", etc.
    score: int = 0  # -100 to 100 range
    level: str = "neutral"  # hated, hostile, unfriendly, neutral, friendly, honored, revered
    visible: bool = True
    locked: bool = False

    @classmethod
    def create(
        cls,
        tenant_id: str,
        target_id: str,
        target_type: str,
        score: int = 0,
        visible: bool = True,
    ) -> Self:
        """Factory method to create a new Reputation."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not target_id:
            raise ValueError("target_id is required")
        if not target_type:
            raise ValueError("target_type is required")
        if not -100 <= score <= 100:
            raise ValueError("score must be between -100 and 100")

        level = cls._calculate_level(score)

        return cls(
            tenant_id=tenant_id,
            target_id=target_id,
            target_type=target_type,
            score=score,
            level=level,
            visible=visible,
        )

    def update_score(self, delta: int) -> None:
        """Update reputation score and recalculate level."""
        self.score = max(-100, min(100, self.score + delta))
        self.level = self._calculate_level(self.score)
        self.updated_at = datetime.utcnow()

    @staticmethod
    def _calculate_level(score: int) -> str:
        """Calculate reputation level from score."""
        if score >= 90:
            return "revered"
        elif score >= 70:
            return "honored"
        elif score >= 40:
            return "friendly"
        elif score >= -10:
            return "neutral"
        elif score >= -40:
            return "unfriendly"
        elif score >= -70:
            return "hostile"
        else:
            return "hated"

    def can_access(self, required_level: str) -> bool:
        """Check if reputation meets required level."""
        levels = [
            "hated",
            "hostile",
            "unfriendly",
            "neutral",
            "friendly",
            "honored",
            "revered",
        ]
        try:
            return levels.index(self.level) >= levels.index(required_level)
        except ValueError:
            return False
