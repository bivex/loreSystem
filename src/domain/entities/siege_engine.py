"""SiegeEngine entity for military equipment."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class SiegeEngine:
    """Represents a siege engine or catapult."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        engine_type: str,
        damage: float,
        range_value: float,
        reload_time: float,
        mobility: float,
        required_operators: int,
        is_deployed: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.engine_type = engine_type
        self.damage = damage
        self.range_value = range_value
        self.reload_time = reload_time
        self.mobility = mobility
        self.required_operators = required_operators
        self.is_deployed = is_deployed
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        engine_type: str,
        damage: float,
        range_value: float,
        reload_time: float = 5.0,
        mobility: float = 0.2,
        required_operators: int = 4,
    ) -> "SiegeEngine":
        """Factory method to create a new siege engine."""
        if not name or not name.strip():
            raise ValueError("Siege engine name is required")
        if damage < 0 or range_value < 0:
            raise ValueError("Damage and range must be non-negative")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            engine_type=engine_type,
            damage=damage,
            range_value=range_value,
            reload_time=reload_time,
            mobility=mobility,
            required_operators=required_operators,
            is_deployed=False,
        )

    def validate(self) -> bool:
        """Validate siege engine data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.damage, (int, float)) and self.damage >= 0
            and isinstance(self.range_value, (int, float)) and self.range_value >= 0
            and isinstance(self.required_operators, int) and self.required_operators > 0
        )

    def __repr__(self) -> str:
        return f"<SiegeEngine {self.name}: {self.damage} dmg, range {self.range_value}>"
