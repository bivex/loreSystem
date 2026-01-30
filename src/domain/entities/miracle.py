"""Miracle entity for divine or supernatural events."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Miracle:
    """Represents a miracle or divine intervention."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        miracle_type: str,
        power_level: int,
        deity_id: Optional[UUID],
        location_id: UUID,
        beneficiaries: list[UUID],
        effects: dict,
        rarity: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.miracle_type = miracle_type
        self.power_level = power_level
        self.deity_id = deity_id
        self.location_id = location_id
        self.beneficiaries = beneficiaries
        self.effects = effects
        self.rarity = rarity
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        miracle_type: str,
        power_level: int,
        location_id: UUID,
        deity_id: Optional[UUID] = None,
        rarity: str = "common",
    ) -> "Miracle":
        """Factory method to create a new miracle."""
        if not name or not name.strip():
            raise ValueError("Miracle name is required")
        if power_level < 1 or power_level > 100:
            raise ValueError("Power level must be between 1 and 100")
        if rarity not in ["common", "uncommon", "rare", "epic", "legendary", "divine"]:
            raise ValueError("Invalid rarity")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            miracle_type=miracle_type,
            power_level=power_level,
            deity_id=deity_id,
            location_id=location_id,
            beneficiaries=[],
            effects={},
            rarity=rarity,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate miracle data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.power_level, int) and 1 <= self.power_level <= 100
            and self.rarity in ["common", "uncommon", "rare", "epic", "legendary", "divine"]
        )

    def __repr__(self) -> str:
        return f"<Miracle {self.name}: {self.miracle_type}, power={self.power_level}>"
