"""Jury entity for legal proceedings."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Jury:
    """Represents a jury in legal proceedings."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        court_id: UUID,
        case_id: UUID,
        jurors: list[UUID],
        foreperson_id: Optional[UUID],
        selection_date: datetime,
        deliberation_start: Optional[datetime],
        verdict: Optional[str],
        verdict_date: Optional[datetime],
        deliberation_hours: int,
        is_unanimous: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.court_id = court_id
        self.case_id = case_id
        self.jurors = jurors
        self.foreperson_id = foreperson_id
        self.selection_date = selection_date
        self.deliberation_start = deliberation_start
        self.verdict = verdict
        self.verdict_date = verdict_date
        self.deliberation_hours = deliberation_hours
        self.is_unanimous = is_unanimous
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        court_id: UUID,
        case_id: UUID,
        jurors: list[UUID],
    ) -> "Jury":
        """Factory method to create a new jury."""
        if len(jurors) < 1:
            raise ValueError("At least one juror is required")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            court_id=court_id,
            case_id=case_id,
            jurors=jurors,
            foreperson_id=None,
            selection_date=datetime.utcnow(),
            deliberation_start=None,
            verdict=None,
            verdict_date=None,
            deliberation_hours=0,
            is_unanimous=False,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate jury data."""
        return (
            isinstance(self.jurors, list) and len(self.jurors) > 0
            and isinstance(self.deliberation_hours, int) and self.deliberation_hours >= 0
        )

    def __repr__(self) -> str:
        return f"<Jury {len(self.jurors)} members, verdict={self.verdict}>"
