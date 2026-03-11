"""War entity for military conflicts."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..exceptions import InvariantViolation
from ..value_objects.common import EntityId, TenantId, Timestamp, Version


VALID_WAR_TYPES = {"civil", "interstate", "colonial", "religious", "ideological", "territorial", "total"}


@dataclass
class War:
    """Represents a war or armed conflict between two named forces."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: str
    war_type: str
    aggressor_name: str
    defender_name: str
    conflict_region_name: str
    start_date: Timestamp
    end_date: Timestamp | None
    total_casualties: int = 0
    battles_fought: int = 0
    territorial_change_names: list[str] = field(default_factory=list)
    is_active: bool = True
    victor_name: str | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("War name cannot be empty")
        if not self.aggressor_name or not self.aggressor_name.strip():
            raise InvariantViolation("War aggressor_name cannot be empty")
        if not self.defender_name or not self.defender_name.strip():
            raise InvariantViolation("War defender_name cannot be empty")
        if not self.conflict_region_name or not self.conflict_region_name.strip():
            raise InvariantViolation("War conflict_region_name cannot be empty")
        if self.war_type not in VALID_WAR_TYPES:
            raise InvariantViolation(f"War war_type must be one of {sorted(VALID_WAR_TYPES)}")
        if self.total_casualties < 0:
            raise InvariantViolation("War total_casualties cannot be negative")
        if self.battles_fought < 0:
            raise InvariantViolation("War battles_fought cannot be negative")
        if self.end_date is not None and self.end_date.value < self.start_date.value:
            raise InvariantViolation("War end_date cannot be before start_date")
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("War updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        war_type: str,
        aggressor_name: str,
        defender_name: str,
        conflict_region_name: str,
        start_date: Timestamp | None = None,
        end_date: Timestamp | None = None,
        total_casualties: int = 0,
        battles_fought: int = 0,
        territorial_change_names: list[str] | None = None,
        is_active: bool = True,
        victor_name: str | None = None,
    ) -> "War":
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=description.strip(),
            war_type=war_type,
            aggressor_name=aggressor_name.strip(),
            defender_name=defender_name.strip(),
            conflict_region_name=conflict_region_name.strip(),
            start_date=start_date or now,
            end_date=end_date,
            total_casualties=total_casualties,
            battles_fought=battles_fought,
            territorial_change_names=list(territorial_change_names or []),
            is_active=is_active,
            victor_name=victor_name.strip() if victor_name else None,
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

    def record_battle(self, casualties: int = 0) -> None:
        self.battles_fought += 1
        self.total_casualties += max(0, casualties)
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def add_casualties(self, count: int) -> None:
        self.total_casualties += max(0, count)
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def add_territorial_change(self, location_name: str) -> None:
        normalized = location_name.strip()
        if normalized and normalized not in self.territorial_change_names:
            self.territorial_change_names.append(normalized)
            self.updated_at = Timestamp.now()
            self.version = self.version.increment()

    def end_war(self, victor_name: str | None = None) -> None:
        self.is_active = False
        self.end_date = self.end_date or Timestamp.now()
        if victor_name:
            self.victor_name = victor_name.strip()
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def __repr__(self) -> str:
        status = "active" if self.is_active else "ended"
        return f"<War {self.name}: {status}, {self.battles_fought} battles, {self.total_casualties} casualties>"
