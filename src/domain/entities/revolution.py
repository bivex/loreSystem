"""Revolution entity for political uprisings."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Revolution:
    """Represents a revolution or uprising against an existing government."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        revolution_type: str,
        target_government_id: UUID,
        rebel_faction_id: UUID,
        affected_region_id: UUID,
        support_level: float,
        government_response: str,
        start_date: datetime,
        end_date: Optional[datetime],
        casualties: int,
        is_successful: Optional[bool],
        is_active: bool = True,
        new_government_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.revolution_type = revolution_type
        self.target_government_id = target_government_id
        self.rebel_faction_id = rebel_faction_id
        self.affected_region_id = affected_region_id
        self.support_level = support_level
        self.government_response = government_response
        self.start_date = start_date
        self.end_date = end_date
        self.casualties = casualties
        self.is_successful = is_successful
        self.is_active = is_active
        self.new_government_id = new_government_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        revolution_type: str,
        target_government_id: UUID,
        rebel_faction_id: UUID,
        affected_region_id: UUID,
        government_response: str = "negotiation",
        initial_support: float = 10.0,
    ) -> "Revolution":
        """Factory method to create a new revolution."""
        if not name or not name.strip():
            raise ValueError("Revolution name is required")
        if revolution_type not in ["political", "social", "economic", "religious", "nationalist", "technological"]:
            raise ValueError("Invalid revolution type")
        if government_response not in ["negotiation", "suppression", "reform", "military", "concession"]:
            raise ValueError("Invalid government response")
        if not 0.0 <= initial_support <= 100.0:
            raise ValueError("Support level must be between 0.0 and 100.0")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            revolution_type=revolution_type,
            target_government_id=target_government_id,
            rebel_faction_id=rebel_faction_id,
            affected_region_id=affected_region_id,
            support_level=initial_support,
            government_response=government_response,
            start_date=datetime.utcnow(),
            end_date=None,
            casualties=0,
            is_successful=None,
            is_active=True,
            new_government_id=None,
        )

    def validate(self) -> bool:
        """Validate revolution data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.revolution_type in ["political", "social", "economic", "religious", "nationalist", "technological"]
            and self.government_response in ["negotiation", "suppression", "reform", "military", "concession"]
            and 0.0 <= self.support_level <= 100.0
            and isinstance(self.start_date, datetime)
            and isinstance(self.casualties, int) and self.casualties >= 0
        )

    def increase_support(self, amount: float) -> None:
        """Increase popular support for the revolution."""
        self.support_level = min(100.0, self.support_level + amount)
        self.updated_at = datetime.utcnow()

    def decrease_support(self, amount: float) -> None:
        """Decrease popular support for the revolution."""
        self.support_level = max(0.0, self.support_level - amount)
        self.updated_at = datetime.utcnow()

    def add_casualties(self, count: int) -> None:
        """Add casualties from the revolution."""
        self.casualties += max(0, count)
        self.updated_at = datetime.utcnow()

    def set_government_response(self, response: str) -> None:
        """Change the government's response to the revolution."""
        if response in ["negotiation", "suppression", "reform", "military", "concession"]:
            self.government_response = response
            self.updated_at = datetime.utcnow()

    def end_revolution(self, successful: bool, new_government_id: Optional[UUID] = None) -> None:
        """End the revolution with an outcome."""
        self.is_active = False
        self.is_successful = successful
        self.end_date = self.end_date or datetime.utcnow()
        if successful and new_government_id is not None:
            self.new_government_id = new_government_id
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        status = "active" if self.is_active else ("successful" if self.is_successful else "failed")
        return f"<Revolution {self.name}: {status}, support={self.support_level}%>"
