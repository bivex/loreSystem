"""Migration entity for biological movement."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Migration:
    """Represents migration patterns."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        species_id: str,
        migration_type: str,
        start_location_id: UUID,
        end_location_id: UUID,
        distance: float,
        duration_days: int,
        trigger_conditions: list,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.species_id = species_id
        self.migration_type = migration_type
        self.start_location_id = start_location_id
        self.end_location_id = end_location_id
        self.distance = distance
        self.duration_days = duration_days
        self.trigger_conditions = trigger_conditions
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        species_id: str,
        migration_type: str,
        start_location_id: UUID,
        end_location_id: UUID,
        distance: float = 0.0,
        duration_days: int = 30,
        trigger_conditions: Optional[list] = None,
    ) -> "Migration":
        """Factory method to create a new migration pattern."""
        if not species_id or not species_id.strip():
            raise ValueError("Species ID is required")
        if distance < 0 or duration_days <= 0:
            raise ValueError("Distance cannot be negative and duration must be positive")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            species_id=species_id.strip(),
            migration_type=migration_type,
            start_location_id=start_location_id,
            end_location_id=end_location_id,
            distance=distance,
            duration_days=duration_days,
            trigger_conditions=trigger_conditions or [],
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate migration data."""
        return (
            isinstance(self.species_id, str) and len(self.species_id) > 0
            and isinstance(self.distance, (int, float)) and self.distance >= 0
            and isinstance(self.duration_days, int) and self.duration_days > 0
        )

    def __repr__(self) -> str:
        return f"<Migration {self.species_id}: {self.distance}km over {self.duration_days} days>"
