"""FactionLeader entity - Faction leadership tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class FactionLeader:
    """Represents leadership of a faction."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    faction_id: str = ""
    character_id: str = ""
    rank: str = ""  # Leader's official rank title
    started_leading: datetime = field(default_factory=datetime.utcnow)
    approval_rating: int = 50  # 0-100
    mandates: list[str] = field(default_factory=list)
    challenges: int = 0  # Number of leadership challenges faced

    @classmethod
    def create(
        cls,
        tenant_id: str,
        faction_id: str,
        character_id: str,
        rank: str,
    ) -> Self:
        """Factory method to create a new FactionLeader."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not faction_id:
            raise ValueError("faction_id is required")
        if not character_id:
            raise ValueError("character_id is required")
        if not rank:
            raise ValueError("rank is required")

        return cls(
            tenant_id=tenant_id,
            faction_id=faction_id,
            character_id=character_id,
            rank=rank,
            started_leading=datetime.utcnow(),
        )

    def set_approval(self, rating: int) -> None:
        """Set approval rating."""
        self.approval_rating = max(0, min(100, rating))
        self.updated_at = datetime.utcnow()

    def add_mandate(self, mandate: str) -> None:
        """Add a leadership mandate."""
        if mandate and mandate not in self.mandates:
            self.mandates.append(mandate)
            self.updated_at = datetime.utcnow()

    def remove_mandate(self, mandate: str) -> None:
        """Remove a leadership mandate."""
        if mandate in self.mandates:
            self.mandates.remove(mandate)
            self.updated_at = datetime.utcnow()

    def increment_challenges(self) -> None:
        """Record a leadership challenge."""
        self.challenges += 1
        self.updated_at = datetime.utcnow()

    def days_in_power(self) -> int:
        """Calculate days the leader has been in power."""
        delta = datetime.utcnow() - self.started_leading
        return delta.days

    def is_popular(self) -> bool:
        """Check if leader is popular (approval >= 60)."""
        return self.approval_rating >= 60

    def is_unpopular(self) -> bool:
        """Check if leader is unpopular (approval <= 30)."""
        return self.approval_rating <= 30

    def is_under_pressure(self) -> bool:
        """Check if leader is under pressure (unpopular OR many challenges)."""
        return self.is_unpopular() or self.challenges >= 3

    def mandate_active(self, mandate: str) -> bool:
        """Check if a specific mandate is active."""
        return mandate in self.mandates
