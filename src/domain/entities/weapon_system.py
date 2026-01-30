"""WeaponSystem entity for military equipment."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class WeaponSystem:
    """Represents a weapon system or armament."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        weapon_type: str,
        damage: float,
        range_value: float,
        accuracy: float,
        fire_rate: float,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.weapon_type = weapon_type
        self.damage = damage
        self.range_value = range_value
        self.accuracy = accuracy
        self.fire_rate = fire_rate
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        weapon_type: str,
        damage: float,
        range_value: float,
        accuracy: float = 0.8,
        fire_rate: float = 1.0,
    ) -> "WeaponSystem":
        """Factory method to create a new weapon system."""
        if not name or not name.strip():
            raise ValueError("Weapon name is required")
        if damage < 0 or range_value < 0:
            raise ValueError("Damage and range must be non-negative")
        if not (0 <= accuracy <= 1):
            raise ValueError("Accuracy must be between 0 and 1")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            weapon_type=weapon_type,
            damage=damage,
            range_value=range_value,
            accuracy=accuracy,
            fire_rate=fire_rate,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate weapon system data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.damage, (int, float)) and self.damage >= 0
            and isinstance(self.range_value, (int, float)) and self.range_value >= 0
            and 0 <= self.accuracy <= 1
        )

    def __repr__(self) -> str:
        return f"<WeaponSystem {self.name}: {self.damage} dmg, range {self.range_value}>"
