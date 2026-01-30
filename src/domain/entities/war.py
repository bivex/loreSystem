"""War entity for military conflicts."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class War:
    """Represents a war or armed conflict between factions."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        war_type: str,
        aggressor_faction_id: UUID,
        defender_faction_id: UUID,
        conflict_region_id: UUID,
        start_date: datetime,
        end_date: Optional[datetime],
        total_casualties: int,
        battles_fought: int,
        territorial_changes: list[UUID],
        is_active: bool = True,
        victor: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.war_type = war_type
        self.aggressor_faction_id = aggressor_faction_id
        self.defender_faction_id = defender_faction_id
        self.conflict_region_id = conflict_region_id
        self.start_date = start_date
        self.end_date = end_date
        self.total_casualties = total_casualties
        self.battles_fought = battles_fought
        self.territorial_changes = territorial_changes
        self.is_active = is_active
        self.victor = victor
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        war_type: str,
        aggressor_faction_id: UUID,
        defender_faction_id: UUID,
        conflict_region_id: UUID,
    ) -> "War":
        """Factory method to create a new war."""
        if not name or not name.strip():
            raise ValueError("War name is required")
        if war_type not in ["civil", "interstate", "colonial", "religious", "ideological", "territorial", "total"]:
            raise ValueError("Invalid war type")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            war_type=war_type,
            aggressor_faction_id=aggressor_faction_id,
            defender_faction_id=defender_faction_id,
            conflict_region_id=conflict_region_id,
            start_date=datetime.utcnow(),
            end_date=None,
            total_casualties=0,
            battles_fought=0,
            territorial_changes=[],
            is_active=True,
            victor=None,
        )

    def validate(self) -> bool:
        """Validate war data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.war_type in ["civil", "interstate", "colonial", "religious", "ideological", "territorial", "total"]
            and isinstance(self.start_date, datetime)
            and isinstance(self.total_casualties, int) and self.total_casualties >= 0
            and isinstance(self.battles_fought, int) and self.battles_fought >= 0
        )

    def record_battle(self, casualties: int = 0) -> None:
        """Record a battle fought in the war."""
        self.battles_fought += 1
        self.total_casualties += max(0, casualties)
        self.updated_at = datetime.utcnow()

    def add_casualties(self, count: int) -> None:
        """Add casualties to the war toll."""
        self.total_casualties += max(0, count)
        self.updated_at = datetime.utcnow()

    def add_territorial_change(self, location_id: UUID) -> None:
        """Add a territorial change resulting from the war."""
        if location_id not in self.territorial_changes:
            self.territorial_changes.append(location_id)
            self.updated_at = datetime.utcnow()

    def end_war(self, victor_faction_id: Optional[UUID] = None) -> None:
        """End the war and optionally declare a victor."""
        self.is_active = False
        self.end_date = self.end_date or datetime.utcnow()
        if victor_faction_id is not None:
            self.victor = victor_faction_id
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        status = "active" if self.is_active else "ended"
        return f"<War {self.name}: {status}, {self.battles_fought} battles, {self.total_casualties} casualties>"
