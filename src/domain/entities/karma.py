"""Karma entity - Player karma/moral alignment."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Karma:
    """Represents player's karma/moral alignment."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    player_id: str = ""
    score: int = 0  # -1000 to 1000 range
    alignment: str = "neutral"  # evil, chaotic, neutral, lawful, good
    tier: int = 0  # Progression tier (0-10)
    visible: bool = True

    @classmethod
    def create(
        cls,
        tenant_id: str,
        player_id: str,
        score: int = 0,
        visible: bool = True,
    ) -> Self:
        """Factory method to create a new Karma."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not player_id:
            raise ValueError("player_id is required")
        if not -1000 <= score <= 1000:
            raise ValueError("score must be between -1000 and 1000")

        alignment = cls._calculate_alignment(score)
        tier = cls._calculate_tier(score)

        return cls(
            tenant_id=tenant_id,
            player_id=player_id,
            score=score,
            alignment=alignment,
            tier=tier,
            visible=visible,
        )

    def add(self, amount: int) -> None:
        """Add karma points."""
        self.score = max(-1000, min(1000, self.score + amount))
        self.alignment = self._calculate_alignment(self.score)
        self.tier = self._calculate_tier(self.score)
        self.updated_at = datetime.utcnow()

    def subtract(self, amount: int) -> None:
        """Subtract karma points."""
        self.add(-amount)

    @staticmethod
    def _calculate_alignment(score: int) -> str:
        """Calculate alignment from score."""
        if score <= -800:
            return "evil"
        elif score <= -400:
            return "chaotic"
        elif score < 400:
            return "neutral"
        elif score < 800:
            return "lawful"
        else:
            return "good"

    @staticmethod
    def _calculate_tier(score: int) -> int:
        """Calculate progression tier from score."""
        tier = abs(score) // 100
        return min(10, tier)

    def is_good(self) -> bool:
        """Check if alignment is good."""
        return self.alignment in ["good", "lawful"]

    def is_evil(self) -> bool:
        """Check if alignment is evil."""
        return self.alignment in ["evil", "chaotic"]

    def is_neutral(self) -> bool:
        """Check if alignment is neutral."""
        return self.alignment == "neutral"
