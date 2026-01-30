"""Court entity for legal proceedings."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Court:
    """Represents a court for legal proceedings."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        court_type: str,
        location_id: UUID,
        jurisdiction: str,
        judge_id: UUID,
        cases: list[UUID],
        prosecutors: list[UUID],
        defense_attorneys: list[UUID],
        juries: list[UUID],
        session_schedule: dict,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.court_type = court_type
        self.location_id = location_id
        self.jurisdiction = jurisdiction
        self.judge_id = judge_id
        self.cases = cases
        self.prosecutors = prosecutors
        self.defense_attorneys = defense_attorneys
        self.juries = juries
        self.session_schedule = session_schedule
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        court_type: str,
        location_id: UUID,
        judge_id: UUID,
        jurisdiction: str = "local",
    ) -> "Court":
        """Factory method to create a new court."""
        if not name or not name.strip():
            raise ValueError("Court name is required")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            court_type=court_type,
            location_id=location_id,
            jurisdiction=jurisdiction,
            judge_id=judge_id,
            cases=[],
            prosecutors=[],
            defense_attorneys=[],
            juries=[],
            session_schedule={},
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate court data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.cases, list)
            and isinstance(self.juries, list)
        )

    def __repr__(self) -> str:
        return f"<Court {self.name}: {self.court_type}, jurisdiction={self.jurisdiction}>"
