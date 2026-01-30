"""Famine entity for food shortage crises."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Famine:
    """Represents a famine or food shortage crisis affecting regions."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        affected_region_id: UUID,
        severity: str,
        cause: str,
        food_shortage_percentage: float,
        starvation_deaths: int,
        start_date: datetime,
        end_date: Optional[datetime],
        relief_aid_received: int,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.affected_region_id = affected_region_id
        self.severity = severity
        self.cause = cause
        self.food_shortage_percentage = food_shortage_percentage
        self.starvation_deaths = starvation_deaths
        self.start_date = start_date
        self.end_date = end_date
        self.relief_aid_received = relief_aid_received
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        affected_region_id: UUID,
        severity: str = "moderate",
        cause: str = "drought",
        initial_shortage: float = 50.0,
    ) -> "Famine":
        """Factory method to create a new famine."""
        if not name or not name.strip():
            raise ValueError("Famine name is required")
        if severity not in ["mild", "moderate", "severe", "extreme"]:
            raise ValueError("Severity must be one of: mild, moderate, severe, extreme")
        if not 0.0 <= initial_shortage <= 100.0:
            raise ValueError("Food shortage percentage must be between 0.0 and 100.0")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            affected_region_id=affected_region_id,
            severity=severity,
            cause=cause.strip(),
            food_shortage_percentage=initial_shortage,
            starvation_deaths=0,
            start_date=datetime.utcnow(),
            end_date=None,
            relief_aid_received=0,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate famine data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.severity in ["mild", "moderate", "severe", "extreme"]
            and isinstance(self.cause, str) and len(self.cause) > 0
            and 0.0 <= self.food_shortage_percentage <= 100.0
            and isinstance(self.starvation_deaths, int) and self.starvation_deaths >= 0
            and isinstance(self.relief_aid_received, int) and self.relief_aid_received >= 0
        )

    def worsen(self, increase_percentage: float) -> None:
        """Increase the food shortage percentage."""
        self.food_shortage_percentage = min(100.0, self.food_shortage_percentage + increase_percentage)
        self.updated_at = datetime.utcnow()

    def add_deaths(self, count: int) -> None:
        """Add starvation deaths."""
        self.starvation_deaths += max(0, count)
        self.updated_at = datetime.utcnow()

    def receive_relief(self, aid_amount: int) -> None:
        """Record relief aid received."""
        self.relief_aid_received += max(0, aid_amount)
        reduction = min(self.food_shortage_percentage, aid_amount * 0.1)
        self.food_shortage_percentage -= reduction
        self.updated_at = datetime.utcnow()

    def end_famine(self) -> None:
        """End the famine."""
        self.is_active = False
        self.end_date = self.end_date or datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Famine {self.name}: {self.food_shortage_percentage}% shortage, {self.starvation_deaths} deaths>"
