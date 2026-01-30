"""Invasion entity for hostile force invasions."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Invasion:
    """Represents an invasion by hostile forces into a territory."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        invader_faction_id: UUID,
        target_region_id: UUID,
        invasion_type: str,
        force_size: int,
        start_date: datetime,
        end_date: Optional[datetime],
        casualties: int,
        conquest_progress: float,
        is_successful: Optional[bool],
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.invader_faction_id = invader_faction_id
        self.target_region_id = target_region_id
        self.invasion_type = invasion_type
        self.force_size = force_size
        self.start_date = start_date
        self.end_date = end_date
        self.casualties = casualties
        self.conquest_progress = conquest_progress
        self.is_successful = is_successful
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        invader_faction_id: UUID,
        target_region_id: UUID,
        invasion_type: str = "military",
        force_size: int = 1000,
    ) -> "Invasion":
        """Factory method to create a new invasion."""
        if not name or not name.strip():
            raise ValueError("Invasion name is required")
        if force_size < 1:
            raise ValueError("Force size must be at least 1")
        if invasion_type not in ["military", "magical", "demonic", "extradimensional", "naval", "aerial"]:
            raise ValueError("Invalid invasion type")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            invader_faction_id=invader_faction_id,
            target_region_id=target_region_id,
            invasion_type=invasion_type,
            force_size=force_size,
            start_date=datetime.utcnow(),
            end_date=None,
            casualties=0,
            conquest_progress=0.0,
            is_successful=None,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate invasion data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.force_size, int) and self.force_size > 0
            and self.invasion_type in ["military", "magical", "demonic", "extradimensional", "naval", "aerial"]
            and isinstance(self.start_date, datetime)
            and 0.0 <= self.conquest_progress <= 100.0
            and isinstance(self.casualties, int) and self.casualties >= 0
        )

    def advance_conquest(self, progress: float) -> None:
        """Advance the conquest progress."""
        self.conquest_progress = max(0.0, min(100.0, self.conquest_progress + progress))
        if self.conquest_progress >= 100.0:
            self.is_successful = True
            self.end_invasion()
        self.updated_at = datetime.utcnow()

    def add_casualties(self, count: int) -> None:
        """Add casualties to the invasion."""
        self.casualties += max(0, count)
        self.updated_at = datetime.utcnow()

    def end_invasion(self, successful: Optional[bool] = None) -> None:
        """End the invasion."""
        self.is_active = False
        self.end_date = self.end_date or datetime.utcnow()
        if successful is not None:
            self.is_successful = successful
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Invasion {self.name}: {self.invasion_type}, progress={self.conquest_progress}%>"
