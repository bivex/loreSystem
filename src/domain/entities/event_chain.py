"""
EventChain Entity

Represents a chain of cause-and-effect events.
Allows for branching storylines and consequences.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


class ChainStatus(str, Enum):
    """Status of an event chain."""
    PENDING = "pending"  # Chain not yet started
    ACTIVE = "active"  # Chain is currently progressing
    COMPLETED = "completed"  # Chain completed successfully
    FAILED = "failed"  # Chain failed (bad ending)
    ABANDONED = "abandoned"  # Player abandoned the chain


@dataclass
class EventChain:
    """
    EventChain entity for cause-and-effect event sequences.
    
    Invariants:
    - Must have at least one event in the chain
    - Next event must be valid if status is active
    - Cannot have circular dependencies
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId  # World this chain belongs to
    name: str
    description: Description
    
    # Chain structure
    event_ids: List[EntityId]  # Ordered list of events in chain
    current_event_index: int  # Index of current event (0-based)
    status: ChainStatus
    
    # Branching
    branching_enabled: bool  # Can this chain branch?
    branch_point_indices: List[int]  # Indices where chain can branch
    
    # Conditions
    required_character_ids: List[EntityId]  # Characters required for chain
    required_faction_id: Optional[EntityId]  # Required faction membership
    min_reputation: Optional[int]  # Minimum faction reputation
    
    # Consequences
    success_reward_id: Optional[EntityId]  # Reward for completing chain
    failure_consequence: Optional[str]  # Description of failure consequence
    affects_world_state: bool  # Does this chain affect world state?
    
    # Timeline
    started_at: Optional[Timestamp]
    completed_at: Optional[Timestamp]
    
    # Metadata
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Event chain name cannot be empty")
        
        if len(self.name) > 200:
            raise InvariantViolation("Event chain name must be <= 200 characters")
        
        if len(self.event_ids) == 0:
            raise InvariantViolation("Event chain must have at least one event")
        
        if self.current_event_index < 0:
            raise InvariantViolation("Current event index cannot be negative")
        
        if self.current_event_index >= len(self.event_ids):
            raise InvariantViolation("Current event index out of bounds")
        
        # Validate branch points
        for idx in self.branch_point_indices:
            if idx < 0 or idx >= len(self.event_ids):
                raise InvariantViolation(f"Invalid branch point index: {idx}")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        event_ids: List[EntityId],
        branching_enabled: bool = False,
        required_character_ids: Optional[List[EntityId]] = None,
    ) -> 'EventChain':
        """
        Factory method for creating a new EventChain.
        
        Example:
            chain = EventChain.create(
                tenant_id=TenantId(1),
                world_id=EntityId(1),
                name="The Vampire Purge",
                description=Description("Chain of events leading to vampire war"),
                event_ids=[EntityId(10), EntityId(11), EntityId(12)],
            )
        """
        if not event_ids or len(event_ids) == 0:
            raise InvariantViolation("Event chain must have at least one event")
        
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            event_ids=event_ids,
            current_event_index=0,
            status=ChainStatus.PENDING,
            branching_enabled=branching_enabled,
            branch_point_indices=[],
            required_character_ids=required_character_ids or [],
            required_faction_id=None,
            min_reputation=None,
            success_reward_id=None,
            failure_consequence=None,
            affects_world_state=False,
            started_at=None,
            completed_at=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def start(self) -> None:
        """
        Start the event chain.
        
        Raises:
            InvariantViolation: If chain is not pending
        """
        if self.status != ChainStatus.PENDING:
            raise InvariantViolation(f"Cannot start chain with status {self.status}")
        
        object.__setattr__(self, 'status', ChainStatus.ACTIVE)
        object.__setattr__(self, 'started_at', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def advance_to_next_event(self) -> bool:
        """
        Advance to the next event in the chain.
        
        Returns:
            True if advanced, False if at end of chain
        
        Raises:
            InvariantViolation: If chain is not active
        """
        if self.status != ChainStatus.ACTIVE:
            raise InvariantViolation(f"Cannot advance chain with status {self.status}")
        
        if self.current_event_index >= len(self.event_ids) - 1:
            # End of chain
            return False
        
        object.__setattr__(self, 'current_event_index', self.current_event_index + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        return True
    
    def complete(self) -> None:
        """
        Complete the event chain successfully.
        
        Raises:
            InvariantViolation: If chain is not active
        """
        if self.status != ChainStatus.ACTIVE:
            raise InvariantViolation(f"Cannot complete chain with status {self.status}")
        
        object.__setattr__(self, 'status', ChainStatus.COMPLETED)
        object.__setattr__(self, 'completed_at', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def fail(self) -> None:
        """
        Mark the event chain as failed.
        
        Raises:
            InvariantViolation: If chain is not active
        """
        if self.status != ChainStatus.ACTIVE:
            raise InvariantViolation(f"Cannot fail chain with status {self.status}")
        
        object.__setattr__(self, 'status', ChainStatus.FAILED)
        object.__setattr__(self, 'completed_at', Timestamp.now())
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def abandon(self) -> None:
        """Abandon the event chain."""
        if self.status not in [ChainStatus.PENDING, ChainStatus.ACTIVE]:
            raise InvariantViolation(f"Cannot abandon chain with status {self.status}")
        
        object.__setattr__(self, 'status', ChainStatus.ABANDONED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def get_current_event_id(self) -> EntityId:
        """Get the ID of the current event in the chain."""
        return self.event_ids[self.current_event_index]
    
    def is_at_branch_point(self) -> bool:
        """Check if current event is a branch point."""
        return self.current_event_index in self.branch_point_indices
    
    def get_progress_percentage(self) -> float:
        """Get progress through the chain as a percentage."""
        if len(self.event_ids) == 0:
            return 0.0
        return (self.current_event_index / len(self.event_ids)) * 100.0
    
    def __str__(self) -> str:
        return f"EventChain({self.name}, {self.status.value}, {len(self.event_ids)} events)"
    
    def __repr__(self) -> str:
        return (
            f"EventChain(id={self.id}, name='{self.name}', "
            f"status={self.status}, events={len(self.event_ids)})"
        )
