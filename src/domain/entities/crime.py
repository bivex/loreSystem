"""Crime entity for unlawful acts."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Crime:
    """Represents a crime committed."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        crime_type: str,
        description: str,
        perpetrator_id: UUID,
        victim_id: Optional[UUID],
        location_id: UUID,
        date_committed: datetime,
        severity: int,
        evidence_ids: list[UUID],
        witness_ids: list[UUID],
        is_reported: bool,
        is_solved: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.crime_type = crime_type
        self.description = description
        self.perpetrator_id = perpetrator_id
        self.victim_id = victim_id
        self.location_id = location_id
        self.date_committed = date_committed
        self.severity = severity
        self.evidence_ids = evidence_ids
        self.witness_ids = witness_ids
        self.is_reported = is_reported
        self.is_solved = is_solved
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        crime_type: str,
        perpetrator_id: UUID,
        location_id: UUID,
        description: str = "",
        severity: int = 1,
        victim_id: Optional[UUID] = None,
    ) -> "Crime":
        """Factory method to create a new crime record."""
        if not name or not name.strip():
            raise ValueError("Crime name is required")
        if not 1 <= severity <= 10:
            raise ValueError("Severity must be between 1 and 10")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            crime_type=crime_type,
            description=description,
            perpetrator_id=perpetrator_id,
            victim_id=victim_id,
            location_id=location_id,
            date_committed=datetime.utcnow(),
            severity=severity,
            evidence_ids=[],
            witness_ids=[],
            is_reported=False,
            is_solved=False,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate crime data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.severity, int) and 1 <= self.severity <= 10
        )

    def __repr__(self) -> str:
        return f"<Crime {self.name}: severity {self.severity}, solved={self.is_solved}>"
