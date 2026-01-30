"""Tournament entity for structured competitions."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Tournament:
    """Represents a tournament competition."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        tournament_type: str,
        organizer_id: UUID,
        location_id: UUID,
        participants: list[UUID],
        bracket_structure: dict,
        current_round: int,
        total_rounds: int,
        matches: list[UUID],
        rewards: dict,
        start_date: datetime,
        end_date: datetime,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.tournament_type = tournament_type
        self.organizer_id = organizer_id
        self.location_id = location_id
        self.participants = participants
        self.bracket_structure = bracket_structure
        self.current_round = current_round
        self.total_rounds = total_rounds
        self.matches = matches
        self.rewards = rewards
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        tournament_type: str,
        organizer_id: UUID,
        location_id: UUID,
        start_date: datetime,
        end_date: datetime,
        total_rounds: int = 4,
    ) -> "Tournament":
        """Factory method to create a new tournament."""
        if not name or not name.strip():
            raise ValueError("Tournament name is required")
        if end_date < start_date:
            raise ValueError("End date must be after start date")
        if total_rounds < 1:
            raise ValueError("Total rounds must be at least 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            tournament_type=tournament_type,
            organizer_id=organizer_id,
            location_id=location_id,
            participants=[],
            bracket_structure={},
            current_round=1,
            total_rounds=total_rounds,
            matches=[],
            rewards={},
            start_date=start_date,
            end_date=end_date,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate tournament data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.start_date <= self.end_date
            and isinstance(self.current_round, int) and 1 <= self.current_round <= self.total_rounds
        )

    def __repr__(self) -> str:
        return f"<Tournament {self.name}: round {self.current_round}/{self.total_rounds}>"
