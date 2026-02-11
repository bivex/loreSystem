"""SessionData Entity

A SessionData represents aggregated data about gaming sessions.
Used for analytics, capacity planning, and operational insights.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timedelta

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class SessionData:
    """Aggregated data about gaming sessions."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    world_id: EntityId
    date: datetime  # Date of sessions (not timestamp)
    total_sessions: int
    total_playtime_minutes: int
    peak_concurrent_players: int
    average_session_duration: timedelta
    unique_players: int
    new_players: int
    returning_players: int
    crash_rate: float  # Percentage of sessions that ended unexpectedly
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.total_sessions < 0:
            raise InvariantViolation("Total sessions cannot be negative")
        
        if self.total_playtime_minutes < 0:
            raise InvariantViolation("Total playtime cannot be negative")
        
        if self.peak_concurrent_players < 0:
            raise InvariantViolation("Peak concurrent players must be positive")
        
        if self.crash_rate < 0 or self.crash_rate > 1:
            raise InvariantViolation("Crash rate must be between 0 and 1")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        date: datetime,
        total_sessions: int = 0,
        total_playtime_minutes: int = 0,
        peak_concurrent_players: int = 0,
        average_session_duration: timedelta = timedelta(minutes=30),
        unique_players: int = 0,
        new_players: int = 0,
        returning_players: int = 0,
        crash_rate: float = 0.0,
    ) -> "SessionData":
        """Factory method to create new SessionData."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            id=None,
            world_id=world_id,
            date=date,
            total_sessions=total_sessions,
            total_playtime_minutes=total_playtime_minutes,
            peak_concurrent_players=peak_concurrent_players,
            average_session_duration=average_session_duration,
            unique_players=unique_players,
            new_players=new_players,
            returning_players=returning_players,
            crash_rate=crash_rate,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def calculate_crash_rate(self, unexpected_terminations: int) -> None:
        """Calculate crash rate based on unexpected session endings."""
        if self.total_sessions > 0:
            self.crash_rate = unexpected_terminations / self.total_sessions
            self.updated_at = Timestamp.now()
    
    def __str__(self) -> str:
        return f"SessionData({self.date}: {self.total_sessions} sessions, {self.peak_concurrent_players} peak)"
    
    def __repr__(self) -> str:
        return (
            f"<SessionData id={self.id}, date={self.date}, "
            f"sessions={self.total_sessions}, playtime={self.total_playtime_minutes}m>"
        )
