"""LegendaryWeapon entity - Rare and powerful weapons."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


VALID_WEAPON_RARITIES = {"rare", "epic", "legendary", "mythic", "divine"}


@dataclass
class LegendaryWeapon:
    """Bridge-compatible legendary weapon aggregate used by CAMEL.Bridge."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    weapon_type: str
    damage: int
    rarity: str = "legendary"
    special_ability: str = ""
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("LegendaryWeapon name cannot be empty")
        if not self.weapon_type or not self.weapon_type.strip():
            raise InvariantViolation("LegendaryWeapon weapon_type cannot be empty")
        if self.damage < 0:
            raise InvariantViolation("LegendaryWeapon damage must be non-negative")
        if self.rarity not in VALID_WEAPON_RARITIES:
            raise InvariantViolation(
                f"LegendaryWeapon rarity must be one of {sorted(VALID_WEAPON_RARITIES)}"
            )
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("LegendaryWeapon updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        weapon_type: str,
        damage: int,
        rarity: str = "legendary",
        special_ability: str = "",
    ) -> "LegendaryWeapon":
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=Description(description.strip()),
            weapon_type=weapon_type.strip(),
            damage=max(0, damage),
            rarity=rarity.strip().lower() or "legendary",
            special_ability=special_ability.strip(),
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
    def weapon_name(self) -> str:
        return self.name

    @property
    def attack_power(self) -> int:
        return self.damage

    def get_total_power(self) -> int:
        return self.damage
