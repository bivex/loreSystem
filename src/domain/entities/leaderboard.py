"""Leaderboard Entity

A Leaderboard represents a ranked list of players
or entities sorted by a specific criterion (score, level, etc.).
Often used for competitive gameplay, leaderboards, and tournaments.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Leaderboard:
    """A ranked list of players or entities."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    board_type: str  # "global", "faction", "event", "weekly", "seasonal"
    sort_criterion: str  # "score", "level", "wins", "time"
    size_limit: int = 100  # Max entries on leaderboard
    entries: List[str]  # IDs of top players/entities
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Leaderboard name cannot be empty")
        
        if self.size_limit <= 0:
            raise InvariantViolation("Size limit must be positive")
        
        if self.sort_criterion not in ["score", "level", "wins", "time"]:
            raise InvariantViolation("Invalid sort criterion")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: str,
        board_type: str = "global",
        sort_criterion: str = "score",
        size_limit: int = 100,
    ) -> "Leaderboard":
        """Factory method to create a new Leaderboard."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            description=Description(description),
            board_type=board_type,
            sort_criterion=sort_criterion,
            size_limit=size_limit,
            entries=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_entry(self, entry_id: str) -> "Leaderboard":
        """Add an entry to the leaderboard."""
        if entry_id not in self.entries:
            self.entries.append(entry_id)
            # Sort entries based on sort_criterion
            self.entries = sorted(self.entries, reverse=True)
            # Trim to size_limit
            self.entries = self.entries[:self.size_limit]
            self.updated_at = Timestamp.now()
            self.version = self.version.bump_minor()
        return self
    
    def update_entries(self, new_entries: List[str]) -> "Leaderboard":
        """Bulk update leaderboard entries."""
        self.entries = new_entries[:self.size_limit]
        self.updated_at = Timestamp.now()
        self.version = self.version.bump_minor()
        return self
    
    def clear_entries(self) -> "Leaderboard":
        """Clear all entries."""
        self.entries = []
        self.updated_at = Timestamp.now()
        self.version = self.version.bump_minor()
        return self
    
    def get_top_players(self, limit: Optional[int] = None) -> List[str]:
        """Get top N players."""
        limit = limit or min(len(self.entries), 10)
        return self.entries[:limit]
    
    def __str__(self) -> str:
        return f"Leaderboard({self.name}, {len(self.entries)} entries, type={self.board_type})"
    
    def __repr__(self) -> str:
        return (
            f"<Leaderboard id={self.id}, name='{self.name}', "
            f"type={self.board_type}, criterion={self.sort_criterion}>"
        )
