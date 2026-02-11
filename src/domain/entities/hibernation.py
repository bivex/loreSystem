"""Hibernation entity for biological dormancy."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Hibernation:
    """Represents hibernation or dormancy patterns."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        species_id: str,
        hibernation_type: str,
        start_month: int,
        end_month: int,
        temperature_threshold: float,
        energy_reserve_rate: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.species_id = species_id
        self.hibernation_type = hibernation_type
        self.start_month = start_month
        self.end_month = end_month
        self.temperature_threshold = temperature_threshold
        self.energy_reserve_rate = energy_reserve_rate
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        species_id: str,
        hibernation_type: str = "winter",
        start_month: int = 11,
        end_month: int = 3,
        temperature_threshold: float = 5.0,
        energy_reserve_rate: float = 0.3,
    ) -> "Hibernation":
        """Factory method to create hibernation pattern."""
        if not species_id or not species_id.strip():
            raise ValueError("Species ID is required")
        if not (1 <= start_month <= 12) or not (1 <= end_month <= 12):
            raise ValueError("Months must be between 1 and 12")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            species_id=species_id.strip(),
            hibernation_type=hibernation_type,
            start_month=start_month,
            end_month=end_month,
            temperature_threshold=temperature_threshold,
            energy_reserve_rate=energy_reserve_rate,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate hibernation data."""
        return (
            isinstance(self.species_id, str) and len(self.species_id) > 0
            and 1 <= self.start_month <= 12
            and 1 <= self.end_month <= 12
            and 0 <= self.energy_reserve_rate <= 1
        )

    def __repr__(self) -> str:
        return f"<Hibernation {self.species_id}: month {self.start_month}-{self.end_month}>"
