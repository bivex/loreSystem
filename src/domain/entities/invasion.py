"""Invasion entity for hostile force invasions."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..exceptions import InvariantViolation
from ..value_objects.common import EntityId, TenantId, Timestamp, Version


VALID_INVASION_TYPES = {"military", "magical", "demonic", "extradimensional", "naval", "aerial"}


@dataclass
class Invasion:
    """Represents an invasion by hostile forces into a territory."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    invasion_type: str
    invader_name: str
    target_name: str
    force_size: int
    start_date: Timestamp
    end_date: Timestamp | None
    casualties: int = 0
    conquest_progress: float = 0.0
    is_successful: bool | None = None
    is_active: bool = True
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("Invasion name cannot be empty")
        if not self.invader_name or not self.invader_name.strip():
            raise InvariantViolation("Invasion invader_name cannot be empty")
        if not self.target_name or not self.target_name.strip():
            raise InvariantViolation("Invasion target_name cannot be empty")
        if self.invasion_type not in VALID_INVASION_TYPES:
            raise InvariantViolation(
                f"Invasion invasion_type must be one of {sorted(VALID_INVASION_TYPES)}"
            )
        if self.force_size < 1:
            raise InvariantViolation("Invasion force_size must be at least 1")
        if self.casualties < 0:
            raise InvariantViolation("Invasion casualties cannot be negative")
        if not 0.0 <= self.conquest_progress <= 100.0:
            raise InvariantViolation("Invasion conquest_progress must be between 0 and 100")
        if self.end_date is not None and self.end_date.value < self.start_date.value:
            raise InvariantViolation("Invasion end_date cannot be before start_date")
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Invasion updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        invader_name: str,
        target_name: str,
        invasion_type: str = "military",
        force_size: int = 1000,
        start_date: Timestamp | None = None,
        end_date: Timestamp | None = None,
        casualties: int = 0,
        conquest_progress: float = 0.0,
        is_successful: bool | None = None,
        is_active: bool = True,
    ) -> "Invasion":
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=description.strip(),
            invasion_type=invasion_type,
            invader_name=invader_name.strip(),
            target_name=target_name.strip(),
            force_size=force_size,
            start_date=start_date or now,
            end_date=end_date,
            casualties=casualties,
            conquest_progress=conquest_progress,
            is_successful=is_successful,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def validate(self) -> bool:
        try:
            self.__post_init__()
        except InvariantViolation:
            return False
        return True

    def advance_conquest(self, progress: float) -> None:
        self.conquest_progress = max(0.0, min(100.0, self.conquest_progress + progress))
        if self.conquest_progress >= 100.0:
            self.is_successful = True
            self.end_invasion()
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def add_casualties(self, count: int) -> None:
        self.casualties += max(0, count)
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def end_invasion(self, successful: bool | None = None) -> None:
        self.is_active = False
        self.end_date = self.end_date or Timestamp.now()
        if successful is not None:
            self.is_successful = successful
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def __repr__(self) -> str:
        return f"<Invasion {self.name}: {self.invasion_type}, progress={self.conquest_progress}%>"
