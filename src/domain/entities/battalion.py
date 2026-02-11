"""Battalion entity for military organization."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Battalion:
    """Represents a military battalion."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        army_id: UUID,
        commander_id: UUID,
        size: int,
        unit_type: str,
        morale: float,
        status: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.army_id = army_id
        self.commander_id = commander_id
        self.size = size
        self.unit_type = unit_type
        self.morale = morale
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        army_id: UUID,
        commander_id: UUID,
        size: int = 100,
        unit_type: str = "infantry",
        morale: float = 1.0,
        status: str = "ready",
    ) -> "Battalion":
        """Factory method to create a new battalion."""
        if not name or not name.strip():
            raise ValueError("Battalion name is required")
        if size <= 0:
            raise ValueError("Battalion size must be positive")
        if not (0 <= morale <= 1):
            raise ValueError("Morale must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            army_id=army_id,
            commander_id=commander_id,
            size=size,
            unit_type=unit_type,
            morale=morale,
            status=status,
        )

    def validate(self) -> bool:
        """Validate battalion data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.size, int) and self.size > 0
            and 0 <= self.morale <= 1
            and self.status in ["ready", "fighting", "retreating", "routed"]
        )

    def __repr__(self) -> str:
        return f"<Battalion {self.name}: {self.size} {self.unit_type}, morale {self.morale}>"
