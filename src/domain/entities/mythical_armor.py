"""MythicalArmor entity - Extraordinary protective equipment."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


VALID_ARMOR_RARITIES = {"rare", "epic", "legendary", "mythic", "divine"}


@dataclass
class MythicalArmor:
    """Bridge-compatible mythical armor aggregate used by CAMEL.Bridge."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    armor_type: str
    defense: int
    rarity: str = "mythic"
    special_protection: str = ""
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("MythicalArmor name cannot be empty")
        if not self.armor_type or not self.armor_type.strip():
            raise InvariantViolation("MythicalArmor armor_type cannot be empty")
        if self.defense < 0:
            raise InvariantViolation("MythicalArmor defense must be non-negative")
        if self.rarity not in VALID_ARMOR_RARITIES:
            raise InvariantViolation(
                f"MythicalArmor rarity must be one of {sorted(VALID_ARMOR_RARITIES)}"
            )
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("MythicalArmor updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        armor_type: str,
        defense: int,
        rarity: str = "mythic",
        special_protection: str = "",
    ) -> "MythicalArmor":
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=Description(description.strip()),
            armor_type=armor_type.strip(),
            defense=max(0, defense),
            rarity=rarity.strip().lower() or "mythic",
            special_protection=special_protection.strip(),
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

    @property
    def armor_name(self) -> str:
        return self.name

    @property
    def defense_power(self) -> int:
        return self.defense

    def get_total_defense(self) -> int:
        return self.defense
