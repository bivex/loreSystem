"""CursedItem entity - Powerful but dangerous items."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


VALID_CURSED_ITEM_RARITIES = {"rare", "epic", "legendary", "cursed", "forbidden"}
VALID_CURSED_ITEM_RISKS = {"low", "medium", "high", "extreme"}


@dataclass
class CursedItem:
    """Bridge-compatible cursed item aggregate used by CAMEL.Bridge."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    item_type: str
    power: int
    curse_type: str
    rarity: str = "cursed"
    benefit: str = ""
    curse_effect: str = ""
    curse_power: int = 0
    character_id: str = ""
    benefit_description: str = ""
    curse_description: str = ""
    effects: list[str] = field(default_factory=list)
    curses: list[str] = field(default_factory=list)
    unlock_level: int = 0
    lore: str = ""
    origin: str = ""
    curse_bearer: str = ""
    breaking_conditions: list[str] = field(default_factory=list)
    ritual_required: str = ""
    control_level: int = 0
    risk_level: str = "high"
    soulbound: bool = True
    possession_chance: int = 0
    corruption_level: int = 0
    time_to_curse_takeover: str = ""
    warning_signs: list[str] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("CursedItem name cannot be empty")
        if not self.item_type or not self.item_type.strip():
            raise InvariantViolation("CursedItem item_type cannot be empty")
        if not self.curse_type or not self.curse_type.strip():
            raise InvariantViolation("CursedItem curse_type cannot be empty")
        if self.power < 0:
            raise InvariantViolation("CursedItem power must be non-negative")
        if self.curse_power < 0:
            raise InvariantViolation("CursedItem curse_power must be non-negative")
        if self.rarity not in VALID_CURSED_ITEM_RARITIES:
            raise InvariantViolation(
                f"CursedItem rarity must be one of {sorted(VALID_CURSED_ITEM_RARITIES)}"
            )
        if self.risk_level not in VALID_CURSED_ITEM_RISKS:
            raise InvariantViolation(
                f"CursedItem risk_level must be one of {sorted(VALID_CURSED_ITEM_RISKS)}"
            )
        for field_name, value in {
            "control_level": self.control_level,
            "possession_chance": self.possession_chance,
            "corruption_level": self.corruption_level,
        }.items():
            if not 0 <= value <= 100:
                raise InvariantViolation(f"CursedItem {field_name} must be between 0 and 100")
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("CursedItem updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        item_type: str,
        power: int,
        curse_type: str,
        rarity: str = "cursed",
        benefit: str = "",
        curse_effect: str = "",
        curse_power: int = 0,
        risk_level: str = "high",
    ) -> "CursedItem":
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=Description(description.strip()),
            item_type=item_type.strip(),
            power=max(0, power),
            curse_type=curse_type.strip(),
            rarity=rarity.strip().lower() or "cursed",
            benefit=benefit.strip(),
            curse_effect=curse_effect.strip(),
            curse_power=max(0, curse_power),
            risk_level=risk_level.strip().lower() or "high",
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
    def tier(self) -> str:
        return self.rarity

    def equip(self, character_id: str) -> None:
        """Equip cursed item to character (warning!)."""
        if not character_id:
            raise InvariantViolation("character_id is required")
        self.character_id = character_id
        self.soulbound = True
        self.updated_at = Timestamp.now()

    def unequip(self) -> None:
        """Unequip cursed item (may not work if soulbound)."""
        if self.soulbound:
            raise InvariantViolation("Cannot unequip soulbound cursed item without ritual")
        self.character_id = ""
        self.updated_at = Timestamp.now()

    def add_effect(self, effect: str) -> None:
        """Add a positive effect."""
        if effect and effect not in self.effects:
            self.effects.append(effect)
            self.updated_at = Timestamp.now()

    def add_curse(self, curse: str) -> None:
        """Add a negative curse effect."""
        if curse and curse not in self.curses:
            self.curses.append(curse)
            self.updated_at = Timestamp.now()

    def add_warning_sign(self, sign: str) -> None:
        """Add a warning sign of the curse."""
        if sign and sign not in self.warning_signs:
            self.warning_signs.append(sign)
            self.updated_at = Timestamp.now()

    def add_breaking_condition(self, condition: str) -> None:
        """Add a condition to break the curse."""
        if condition and condition not in self.breaking_conditions:
            self.breaking_conditions.append(condition)
            self.updated_at = Timestamp.now()

    def increase_control(self, amount: int) -> None:
        """Increase control over the curse."""
        self.control_level = min(100, max(0, self.control_level + amount))
        self.updated_at = Timestamp.now()

    def increase_corruption(self, amount: int) -> None:
        """Increase corruption level."""
        self.corruption_level = min(100, max(0, self.corruption_level + amount))
        self.updated_at = Timestamp.now()

    def is_equipped(self) -> bool:
        """Check if item is equipped."""
        return bool(self.character_id)

    def is_soulbound(self) -> bool:
        """Check if item is soulbound."""
        return self.soulbound

    def is_controlled(self) -> bool:
        """Check if the curse is controlled."""
        return self.control_level >= 50

    def is_dangerous(self) -> bool:
        """Check if the curse is dangerous."""
        return self.corruption_level > 50 or self.control_level < 30

    def can_break_curse(self) -> bool:
        """Check if curse can be broken."""
        return len(self.breaking_conditions) > 0

    def has_warning_sign(self, sign: str) -> bool:
        """Check for specific warning sign."""
        return sign in self.warning_signs

    def get_net_power(self) -> int:
        """Calculate net power (power - curse_power)."""
        return max(0, self.power - int(self.curse_power * (self.corruption_level / 100)))

    def is_fully_corrupted(self) -> bool:
        """Check if fully corrupted by the curse."""
        return self.corruption_level >= 100

    def is_risky(self, threshold: int = 70) -> bool:
        """Check if risk level is above threshold."""
        return self.corruption_level >= threshold or self.control_level <= (100 - threshold)

    def attempt_possession(self) -> bool:
        """Deterministically report whether the curse is in possession-risk territory."""
        return bool(self.character_id) and self.possession_chance > 0 and self.corruption_level >= (100 - self.possession_chance)

    def set_possession_chance(self, chance: int) -> None:
        if chance < 0 or chance > 100:
            raise InvariantViolation("possession_chance must be between 0 and 100")
        self.possession_chance = chance
        self.updated_at = Timestamp.now()
