"""Honor entity - Character honor standing."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Honor:
    """Represents character's honor standing."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    points: int = 0  # 0 to 1000 range
    rank: str = "dishonorable"  # dishonorable, common, respected, honorable, legendary
    stain_count: int = 0  # Number of honor stains/shame marks
    reputation: str = ""  # Public reputation

    @classmethod
    def create(
        cls,
        tenant_id: str,
        character_id: str,
        points: int = 0,
        reputation: str = "",
    ) -> Self:
        """Factory method to create a new Honor."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not character_id:
            raise ValueError("character_id is required")
        if not 0 <= points <= 1000:
            raise ValueError("points must be between 0 and 1000")

        rank = cls._calculate_rank(points)

        return cls(
            tenant_id=tenant_id,
            character_id=character_id,
            points=points,
            rank=rank,
            reputation=reputation,
        )

    def award(self, points: int) -> None:
        """Award honor points."""
        self.points = max(0, min(1000, self.points + points))
        self.rank = self._calculate_rank(self.points)
        self.updated_at = datetime.utcnow()

    def penalize(self, points: int) -> None:
        """Penalize honor points."""
        self.points = max(0, min(1000, self.points - points))
        self.rank = self._calculate_rank(self.points)
        self.stain_count += 1
        self.updated_at = datetime.utcnow()

    @staticmethod
    def _calculate_rank(points: int) -> str:
        """Calculate honor rank from points."""
        if points >= 900:
            return "legendary"
        elif points >= 700:
            return "honorable"
        elif points >= 400:
            return "respected"
        elif points >= 100:
            return "common"
        else:
            return "dishonorable"

    def is_honorable(self) -> bool:
        """Check if character is honorable."""
        return self.rank in ["honorable", "legendary"]

    def is_dishonorable(self) -> bool:
        """Check if character is dishonorable."""
        return self.rank == "dishonorable"

    def has_stains(self) -> bool:
        """Check if character has honor stains."""
        return self.stain_count > 0
