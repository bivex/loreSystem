"""DivineItem entity - Holy items with godly properties."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


VALID_DIVINE_RARITIES = {"epic", "legendary", "mythic", "divine"}


@dataclass
class DivineItem:
    """Bridge-compatible divine item aggregate used by CAMEL.Bridge."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    item_type: str
    power: int
    rarity: str = "divine"
    deity_name: str = ""
    domain: str = ""
    divine_ability: str = ""
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("DivineItem name cannot be empty")
        if not self.item_type or not self.item_type.strip():
            raise InvariantViolation("DivineItem item_type cannot be empty")
        if self.power < 0:
            raise InvariantViolation("DivineItem power must be non-negative")
        if self.rarity not in VALID_DIVINE_RARITIES:
            raise InvariantViolation(
                f"DivineItem rarity must be one of {sorted(VALID_DIVINE_RARITIES)}"
            )
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("DivineItem updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        item_type: str,
        power: int,
        rarity: str = "divine",
        deity_name: str = "",
        domain: str = "",
        divine_ability: str = "",
    ) -> "DivineItem":
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=Description(description.strip()),
            item_type=item_type.strip(),
            power=max(0, power),
            rarity=rarity.strip().lower() or "divine",
            deity_name=deity_name.strip(),
            domain=domain.strip(),
            divine_ability=divine_ability.strip(),
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
    def item_name(self) -> str:
        return self.name

    @property
    def divine_power(self) -> int:
        return self.power

    def get_total_power(self) -> int:
        return self.power
