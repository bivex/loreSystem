"""Judge entity for legal authority."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Judge:
    """Represents a judge in the legal system."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        title: str,
        court_id: UUID,
        years_experience: int,
        bias_level: float,
        rulings: dict,
        reputation: float,
        specialty: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.title = title
        self.court_id = court_id
        self.years_experience = years_experience
        self.bias_level = bias_level
        self.rulings = rulings
        self.reputation = reputation
        self.specialty = specialty
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        title: str,
        court_id: UUID,
        years_experience: int = 10,
        bias_level: float = 0.0,
        specialty: str = "general",
    ) -> "Judge":
        """Factory method to create a new judge."""
        if not name or not name.strip():
            raise ValueError("Judge name is required")
        if not title or not title.strip():
            raise ValueError("Judge title is required")
        if years_experience < 0:
            raise ValueError("Years experience cannot be negative")
        if not -1.0 <= bias_level <= 1.0:
            raise ValueError("Bias level must be between -1.0 and 1.0")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            title=title.strip(),
            court_id=court_id,
            years_experience=years_experience,
            bias_level=bias_level,
            rulings={},
            reputation=0.5,
            specialty=specialty,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate judge data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.years_experience, int) and self.years_experience >= 0
            and isinstance(self.bias_level, (int, float)) and -1.0 <= self.bias_level <= 1.0
        )

    def __repr__(self) -> str:
        return f"<Judge {self.name}: {self.title}, {self.years_experience} years exp>"
