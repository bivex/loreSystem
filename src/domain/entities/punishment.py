"""Punishment entity for legal penalties."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Punishment:
    """Represents a punishment or penalty."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        punishment_type: str,
        description: str,
        offender_id: UUID,
        crime_id: UUID,
        sentence_length_days: Optional[int],
        fine_amount: int,
        severity: int,
        start_date: datetime,
        end_date: Optional[datetime],
        is_served: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.punishment_type = punishment_type
        self.description = description
        self.offender_id = offender_id
        self.crime_id = crime_id
        self.sentence_length_days = sentence_length_days
        self.fine_amount = fine_amount
        self.severity = severity
        self.start_date = start_date
        self.end_date = end_date
        self.is_served = is_served
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        punishment_type: str,
        offender_id: UUID,
        crime_id: UUID,
        description: str = "",
        severity: int = 1,
        fine_amount: int = 0,
        sentence_length_days: Optional[int] = None,
    ) -> "Punishment":
        """Factory method to create a new punishment."""
        if not name or not name.strip():
            raise ValueError("Punishment name is required")
        if not 1 <= severity <= 10:
            raise ValueError("Severity must be between 1 and 10")
        if fine_amount < 0:
            raise ValueError("Fine amount cannot be negative")
        if sentence_length_days is not None and sentence_length_days < 0:
            raise ValueError("Sentence length cannot be negative")

        start_date = datetime.utcnow()
        end_date = None
        if sentence_length_days:
            from datetime import timedelta
            end_date = start_date + timedelta(days=sentence_length_days)

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            punishment_type=punishment_type,
            description=description,
            offender_id=offender_id,
            crime_id=crime_id,
            sentence_length_days=sentence_length_days,
            fine_amount=fine_amount,
            severity=severity,
            start_date=start_date,
            end_date=end_date,
            is_served=False,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate punishment data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.severity, int) and 1 <= self.severity <= 10
            and isinstance(self.fine_amount, int) and self.fine_amount >= 0
        )

    def __repr__(self) -> str:
        return f"<Punishment {self.name}: {self.punishment_type}, severity {self.severity}>"
