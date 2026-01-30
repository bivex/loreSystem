"""Ceremony entity for formal rituals."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Ceremony:
    """Represents a formal ceremony or ritual."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        ceremony_type: str,
        location_id: UUID,
        presider_id: Optional[UUID],
        participants: list[UUID],
        steps: list[dict],
        requirements: dict,
        outcomes: dict,
        is_sacred: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.ceremony_type = ceremony_type
        self.location_id = location_id
        self.presider_id = presider_id
        self.participants = participants
        self.steps = steps
        self.requirements = requirements
        self.outcomes = outcomes
        self.is_sacred = is_sacred
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        ceremony_type: str,
        location_id: UUID,
        presider_id: Optional[UUID] = None,
        is_sacred: bool = False,
    ) -> "Ceremony":
        """Factory method to create a new ceremony."""
        if not name or not name.strip():
            raise ValueError("Ceremony name is required")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            ceremony_type=ceremony_type,
            location_id=location_id,
            presider_id=presider_id,
            participants=[],
            steps=[],
            requirements={},
            outcomes={},
            is_sacred=is_sacred,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate ceremony data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.steps, list)
            and isinstance(self.participants, list)
        )

    def __repr__(self) -> str:
        return f"<Ceremony {self.name}: {self.ceremony_type}, sacred={self.is_sacred}>"
