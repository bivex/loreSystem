"""FactionIdeology entity - Faction belief system."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class FactionIdeology:
    """Represents a faction's ideology/belief system."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    faction_id: str = ""
    core_beliefs: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    taboos: list[str] = field(default_factory=list)
    alignment: str = ""  # good, evil, lawful, chaotic, neutral
    strictness: int = 0  # 0-100 how strictly enforced

    @classmethod
    def create(
        cls,
        tenant_id: str,
        faction_id: str,
        core_beliefs: list[str] | None = None,
    ) -> Self:
        """Factory method to create a new FactionIdeology."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not faction_id:
            raise ValueError("faction_id is required")

        return cls(
            tenant_id=tenant_id,
            faction_id=faction_id,
            core_beliefs=core_beliefs or [],
        )

    def add_belief(self, belief: str) -> None:
        """Add a core belief."""
        if belief and belief not in self.core_beliefs:
            self.core_beliefs.append(belief)
            self.updated_at = datetime.utcnow()

    def add_value(self, value: str) -> None:
        """Add a value."""
        if value and value not in self.values:
            self.values.append(value)
            self.updated_at = datetime.utcnow()

    def add_goal(self, goal: str) -> None:
        """Add a goal."""
        if goal and goal not in self.goals:
            self.goals.append(goal)
            self.updated_at = datetime.utcnow()

    def add_taboo(self, taboo: str) -> None:
        """Add a taboo."""
        if taboo and taboo not in self.taboos:
            self.taboos.append(taboo)
            self.updated_at = datetime.utcnow()

    def set_alignment(self, alignment: str) -> None:
        """Set ideological alignment."""
        valid_alignments = ["good", "evil", "lawful", "chaotic", "neutral"]
        if alignment not in valid_alignments:
            raise ValueError(f"alignment must be one of {valid_alignments}")
        self.alignment = alignment
        self.updated_at = datetime.utcnow()

    def set_strictness(self, strictness: int) -> None:
        """Set ideology enforcement strictness."""
        self.strictness = max(0, min(100, strictness))
        self.updated_at = datetime.utcnow()

    def violates_taboo(self, action: str) -> bool:
        """Check if action violates any taboo."""
        return any(taboo.lower() in action.lower() for taboo in self.taboos)

    def supports_goal(self, action: str) -> bool:
        """Check if action supports any goal."""
        return any(goal.lower() in action.lower() for goal in self.goals)
