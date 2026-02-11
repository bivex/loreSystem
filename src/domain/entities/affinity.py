"""Affinity entity - Personal affinity relationships."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Affinity:
    """Represents personal affinity/liking between entities."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    source_id: str = ""  # Character who has the affinity
    target_id: str = ""  # Character toward whom affinity exists
    value: float = 0.0  # -1.0 to 1.0 range
    category: str = ""  # "friendship", "romance", "mentorship", etc.
    flags: list[str] = field(default_factory=list)  # "locked", "declining", "growing", etc.

    @classmethod
    def create(
        cls,
        tenant_id: str,
        source_id: str,
        target_id: str,
        category: str,
        value: float = 0.0,
    ) -> Self:
        """Factory method to create a new Affinity."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not source_id:
            raise ValueError("source_id is required")
        if not target_id:
            raise ValueError("target_id is required")
        if not category:
            raise ValueError("category is required")
        if not -1.0 <= value <= 1.0:
            raise ValueError("value must be between -1.0 and 1.0")

        return cls(
            tenant_id=tenant_id,
            source_id=source_id,
            target_id=target_id,
            category=category,
            value=value,
        )

    def modify(self, delta: float) -> None:
        """Modify affinity value."""
        self.value = max(-1.0, min(1.0, self.value + delta))
        self.updated_at = datetime.utcnow()

    def is_maxed(self) -> bool:
        """Check if affinity is at maximum."""
        return abs(self.value) >= 1.0

    def is_positive(self) -> bool:
        """Check if affinity is positive."""
        return self.value > 0

    def add_flag(self, flag: str) -> None:
        """Add a flag to the affinity."""
        if flag not in self.flags:
            self.flags.append(flag)
            self.updated_at = datetime.utcnow()

    def remove_flag(self, flag: str) -> None:
        """Remove a flag from the affinity."""
        if flag in self.flags:
            self.flags.remove(flag)
            self.updated_at = datetime.utcnow()
