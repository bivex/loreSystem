"""Lawyer entity for legal representation."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Lawyer:
    """Represents a lawyer or attorney."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        specialization: str,
        bar_number: str,
        law_firm_id: Optional[UUID],
        years_experience: int,
        win_rate: float,
        hourly_rate: int,
        clients: list[UUID],
        cases: list[UUID],
        reputation: float,
        is_available: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.specialization = specialization
        self.bar_number = bar_number
        self.law_firm_id = law_firm_id
        self.years_experience = years_experience
        self.win_rate = win_rate
        self.hourly_rate = hourly_rate
        self.clients = clients
        self.cases = cases
        self.reputation = reputation
        self.is_available = is_available
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        specialization: str,
        bar_number: str,
        years_experience: int = 5,
        win_rate: float = 0.5,
        hourly_rate: int = 100,
    ) -> "Lawyer":
        """Factory method to create a new lawyer."""
        if not name or not name.strip():
            raise ValueError("Lawyer name is required")
        if not specialization or not specialization.strip():
            raise ValueError("Specialization is required")
        if not bar_number or not bar_number.strip():
            raise ValueError("Bar number is required")
        if years_experience < 0:
            raise ValueError("Years experience cannot be negative")
        if not 0.0 <= win_rate <= 1.0:
            raise ValueError("Win rate must be between 0.0 and 1.0")
        if hourly_rate < 0:
            raise ValueError("Hourly rate cannot be negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            specialization=specialization.strip(),
            bar_number=bar_number.strip(),
            law_firm_id=None,
            years_experience=years_experience,
            win_rate=win_rate,
            hourly_rate=hourly_rate,
            clients=[],
            cases=[],
            reputation=0.5,
            is_available=True,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate lawyer data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.years_experience, int) and self.years_experience >= 0
            and isinstance(self.win_rate, (int, float)) and 0.0 <= self.win_rate <= 1.0
        )

    def __repr__(self) -> str:
        return f"<Lawyer {self.name}: {self.specialization}, {self.win_rate*100:.0f}% win rate>"
