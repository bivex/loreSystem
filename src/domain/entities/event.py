"""
Event Entity

An Event represents a significant occurrence in the world timeline.
"""
from dataclasses import dataclass
from typing import Optional, List, Set

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    DateRange,
    EventOutcome,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class Event:
    """
    Event entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Must have at least one participant (Character)
    - Date range must be valid (start <= end)
    - Version increases monotonically
    - Can optionally occur at a specific Location
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    date_range: DateRange
    outcome: EventOutcome
    participant_ids: List[EntityId]
    location_id: Optional[EntityId]  # Location where this event occurs
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
        
        if not self.participant_ids:
            raise InvariantViolation(
                "Event must have at least one participant"
            )
        
        # Check for duplicate participants
        if len(self.participant_ids) != len(set(self.participant_ids)):
            raise InvariantViolation(
                "Event cannot have duplicate participants"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        start_date: Timestamp,
        participant_ids: List[EntityId],
        end_date: Optional[Timestamp] = None,
        outcome: EventOutcome = EventOutcome.ONGOING,
        location_id: Optional[EntityId] = None,
    ) -> 'Event':
        """
        Factory method for creating a new Event.
        
        Args:
            tenant_id: Tenant this event belongs to
            world_id: World this event occurs in
            name: Event name (unique within world)
            description: Detailed description
            start_date: When event begins
            participant_ids: IDs of participating characters (>= 1)
            end_date: When event ends (None if ongoing)
            outcome: Result of the event
            location_id: Location where event occurs (optional)
        
        Raises:
            ValueError: If name is empty
            InvariantViolation: If no participants
        """
        if not name or len(name.strip()) == 0:
            raise ValueError("Event name cannot be empty")
        if len(name) > 255:
            raise ValueError("Event name must be <= 255 characters")
        
        if not participant_ids:
            raise InvariantViolation("Event must have at least one participant")
        
        now = Timestamp.now()
        date_range = DateRange(start_date, end_date)
        
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            date_range=date_range,
            outcome=outcome,
            participant_ids=participant_ids.copy(),
            location_id=location_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_participant(self, character_id: EntityId) -> None:
        """
        Add a participant to the event.
        
        Raises:
            InvariantViolation: If character already participating
        """
        if character_id in self.participant_ids:
            raise InvariantViolation(
                f"Character {character_id} already participating in event"
            )
        
        self.participant_ids.append(character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_participant(self, character_id: EntityId) -> None:
        """
        Remove a participant from the event.
        
        Raises:
            InvalidState: If character not participating
            InvariantViolation: If removing last participant
        """
        if character_id not in self.participant_ids:
            raise InvalidState(
                f"Character {character_id} not participating in event"
            )
        
        if len(self.participant_ids) == 1:
            raise InvariantViolation(
                "Cannot remove last participant from event"
            )
        
        self.participant_ids.remove(character_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(
        self,
        end_date: Timestamp,
        outcome: EventOutcome,
    ) -> None:
        """
        Mark event as completed with an outcome.
        
        Raises:
            InvalidState: If event already completed
            ValueError: If end_date < start_date
        """
        if not self.date_range.is_ongoing():
            raise InvalidState("Event is already completed")
        
        if outcome == EventOutcome.ONGOING:
            raise ValueError("Cannot complete event with ONGOING outcome")
        
        new_date_range = DateRange(self.date_range.start_date, end_date)
        object.__setattr__(self, 'date_range', new_date_range)
        object.__setattr__(self, 'outcome', outcome)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_description(self, new_description: Description) -> None:
        """Update event description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def move_to_location(self, location_id: Optional[EntityId]) -> None:
        """Move event to a different location."""
        if self.location_id == location_id:
            return
        
        object.__setattr__(self, 'location_id', location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_ongoing(self) -> bool:
        """Check if event is still ongoing."""
        return self.date_range.is_ongoing()
    
    def participant_count(self) -> int:
        """Get number of participants."""
        return len(self.participant_ids)
    
    def has_participant(self, character_id: EntityId) -> bool:
        """Check if character is participating."""
        return character_id in self.participant_ids
    
    def __str__(self) -> str:
        status = "ongoing" if self.is_ongoing() else "completed"
        return f"Event({self.name}, {status}, {self.participant_count()} participants)"
    
    def __repr__(self) -> str:
        return (
            f"Event(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', outcome={self.outcome})"
        )
