"""CursedItem entity - Powerful but dangerous items."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class CursedItem:
    """Represents a cursed item with powerful but dangerous properties."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    item_name: str = ""
    item_type: str = ""  # weapon, armor, accessory, amulet, ring, trinket
    tier: str = "cursed"  # common, rare, epic, legendary, cursed
    rarity: str = "cursed"  # common, rare, epic, legendary, cursed, forbidden
    power: int = 0
    curse_power: int = 0  # Strength of the curse
    curse_type: str = ""  # soul_bind, life_drain, corruption, possession, madness, etc.
    benefit: str = ""  # The powerful benefit this item provides
    benefit_description: str = ""
    curse_effect: str = ""  # The negative effect
    curse_description: str = ""
    effects: list[str] = field(default_factory=list)  # Positive effects
    curses: list[str] = field(default_factory=list)  # Negative effects
    unlock_level: int = 0
    lore: str = ""
    origin: str = ""  # How the item became cursed
    curse_bearer: str = ""  # Current name of curse entity
    breaking_conditions: list[str] = field(default_factory=list)  # How to break the curse
    ritual_required: str = ""  # Ritual needed to control/remove
    control_level: int = 0  # How well the user controls the curse (0-100)
    risk_level: str = "high"  # low, medium, high, extreme
    soulbound: bool = True  # Cursed items bind themselves
    possession_chance: int = 0  # 0-100 chance of taking control
    corruption_level: int = 0  # 0-100 how corrupted the user is
    time_to_curse_takeover: str = ""  # Time before curse fully takes over
    warning_signs: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        item_name: str,
        item_type: str,
        power: int,
        curse_type: str,
        benefit: str,
        curse_effect: str,
    ) -> Self:
        """Factory method to create a new CursedItem."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not item_name:
            raise ValueError("item_name is required")
        if not item_type:
            raise ValueError("item_type is required")
        if power < 0:
            raise ValueError("power must be non-negative")
        if not curse_type:
            raise ValueError("curse_type is required")
        if not benefit:
            raise ValueError("benefit is required")
        if not curse_effect:
            raise ValueError("curse_effect is required")

        valid_types = ["weapon", "armor", "accessory", "amulet", "ring", "trinket", "tome", "mask"]
        if item_type not in valid_types:
            raise ValueError(f"item_type must be one of {valid_types}")

        valid_tiers = ["common", "rare", "epic", "legendary", "cursed"]
        if tier not in valid_tiers:
            raise ValueError(f"tier must be one of {valid_tiers}")

        valid_rarity = ["common", "rare", "epic", "legendary", "cursed", "forbidden"]
        if rarity not in valid_rarity:
            raise ValueError(f"rarity must be one of {valid_rarity}")

        valid_curses = [
            "soul_bind", "life_drain", "corruption", "possession",
            "madness", "eternal_hunger", "death_curse", "blood_pact",
            "dimensional_anchor", "memory_loss", "fate_sealed"
        ]
        if curse_type not in valid_curses:
            raise ValueError(f"curse_type must be one of {valid_curses}")

        valid_risk = ["low", "medium", "high", "extreme"]
        if risk_level not in valid_risk:
            raise ValueError(f"risk_level must be one of {valid_risk}")

        return cls(
            tenant_id=tenant_id,
            item_name=item_name,
            item_type=item_type,
            power=power,
            curse_type=curse_type,
            benefit=benefit,
            curse_effect=curse_effect,
        )

    def equip(self, character_id: str) -> None:
        """Equip cursed item to character (warning!)."""
        if not character_id:
            raise ValueError("character_id is required")
        self.character_id = character_id
        self.soulbound = True  # Cursed items always soulbind
        self.updated_at = datetime.utcnow()

    def unequip(self) -> None:
        """Unequip cursed item (may not work if soulbound)."""
        if self.soulbound:
            raise ValueError("Cannot unequip soulbound cursed item without ritual")
        self.character_id = ""
        self.updated_at = datetime.utcnow()

    def add_effect(self, effect: str) -> None:
        """Add a positive effect."""
        if effect and effect not in self.effects:
            self.effects.append(effect)
            self.updated_at = datetime.utcnow()

    def add_curse(self, curse: str) -> None:
        """Add a negative curse effect."""
        if curse and curse not in self.curses:
            self.curses.append(curse)
            self.updated_at = datetime.utcnow()

    def add_warning_sign(self, sign: str) -> None:
        """Add a warning sign of the curse."""
        if sign and sign not in self.warning_signs:
            self.warning_signs.append(sign)
            self.updated_at = datetime.utcnow()

    def add_breaking_condition(self, condition: str) -> None:
        """Add a condition to break the curse."""
        if condition and condition not in self.breaking_conditions:
            self.breaking_conditions.append(condition)
            self.updated_at = datetime.utcnow()

    def increase_control(self, amount: int) -> None:
        """Increase control over the curse."""
        self.control_level = min(100, max(0, self.control_level + amount))
        self.updated_at = datetime.utcnow()

    def increase_corruption(self, amount: int) -> None:
        """Increase corruption level."""
        self.corruption_level = min(100, max(0, self.corruption_level + amount))
        self.updated_at = datetime.utcnow()

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
        return max(0, self.power - (self.curse_power * (self.corruption_level / 100)))

    def is_fully_corrupted(self) -> bool:
        """Check if fully corrupted by the curse."""
        return self.corruption_level >= 100

    def is_risky(self, threshold: int = 70) -> bool:
        """Check if risk level is above threshold."""
        return self.corruption_level >= threshold or self.control_level <= (100 - threshold)

    def attempt_possession(self) -> bool:
        """Check if the curse attempts possession."""
        if not self.character_id:
            return False
        import random
        return random.randint(0, 100) < self.possession_chance

    def set_possession_chance(self, chance: int) -> None:
        """Set possession chance."""
        if chance < 0 or chance > 100:
            raise ValueError("possession_chance must be between 0 and 100")
        self.possession_chance = chance
        self.updated_at = datetime.utcnow()
