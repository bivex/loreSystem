"""DivineItem entity - Holy items with godly properties."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class DivineItem:
    """Represents a divine item with holy properties."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    item_name: str = ""
    item_type: str = ""  # artifact, relic, sacrament, symbol, icon, talisman
    deity_id: str = ""  # The deity this item is associated with
    pantheon: str = ""  # The pantheon the deity belongs to
    tier: str = "divine"  # legendary, mythical, divine
    rarity: str = "divine"  # common, rare, epic, legendary, mythic, divine
    power: int = 0
    divine_power: int = 0  # Special divine ability power
    divine_ability: str = ""
    ability_description: str = ""
    domain: str = ""  # The domain of power (war, love, death, wisdom, etc.)
    blessing_type: str = ""  # passive, active, passive+active
    effects: list[str] = field(default_factory=list)
    miracles: list[str] = field(default_factory=list)  # Divine miracles this item can perform
    faith_requirement: int = 0  # Minimum faith level required
    alignment: str = ""  # lawful, neutral, chaotic, good, evil, neutral
    unlock_level: int = 0
    lore: str = ""
    history: str = ""  # Historical significance
    curses: list[str] = field(default_factory=list)  # Potential drawbacks
    restrictions: list[str] = field(default_factory=list)
    soulbound: bool = True  # Divine items are typically soulbound
    worship_bonus: int = 0  # Bonus to worship
    prayer_power: int = 0  # Power of prayers with this item
    blessing_duration: str = "permanent"  # temporary, permanent, conditional

    @classmethod
    def create(
        cls,
        tenant_id: str,
        item_name: str,
        item_type: str,
        deity_id: str,
        divine_power: int,
        divine_ability: str,
    ) -> Self:
        """Factory method to create a new DivineItem."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not item_name:
            raise ValueError("item_name is required")
        if not item_type:
            raise ValueError("item_type is required")
        if not deity_id:
            raise ValueError("deity_id is required")
        if divine_power < 0:
            raise ValueError("divine_power must be non-negative")
        if not divine_ability:
            raise ValueError("divine_ability is required")

        valid_types = ["artifact", "relic", "sacrament", "symbol", "icon", "talisman", "holy_weapon"]
        if item_type not in valid_types:
            raise ValueError(f"item_type must be one of {valid_types}")

        valid_tiers = ["legendary", "mythical", "divine"]
        if tier not in valid_tiers:
            raise ValueError(f"tier must be one of {valid_tiers}")

        valid_rarity = ["common", "rare", "epic", "legendary", "mythic", "divine"]
        if rarity not in valid_rarity:
            raise ValueError(f"rarity must be one of {valid_rarity}")

        valid_domains = [
            "war", "love", "death", "wisdom", "nature", "magic", "sun",
            "moon", "justice", "chaos", "order", "fate", "time", "creation", "destruction"
        ]
        if domain and domain not in valid_domains:
            raise ValueError(f"domain must be one of {valid_domains}")

        valid_blessing = ["passive", "active", "passive+active"]
        if blessing_type and blessing_type not in valid_blessing:
            raise ValueError(f"blessing_type must be one of {valid_blessing}")

        valid_alignment = ["lawful", "neutral", "chaotic", "good", "evil", "neutral"]
        if alignment and alignment not in valid_alignment:
            raise ValueError(f"alignment must be one of {valid_alignment}")

        valid_duration = ["temporary", "permanent", "conditional"]
        if blessing_duration not in valid_duration:
            raise ValueError(f"blessing_duration must be one of {valid_duration}")

        return cls(
            tenant_id=tenant_id,
            item_name=item_name,
            item_type=item_type,
            deity_id=deity_id,
            divine_power=divine_power,
            divine_ability=divine_ability,
        )

    def equip(self, character_id: str) -> None:
        """Equip divine item to character."""
        if not character_id:
            raise ValueError("character_id is required")
        self.character_id = character_id
        self.updated_at = datetime.utcnow()

    def unequip(self) -> None:
        """Unequip divine item."""
        self.character_id = ""
        self.updated_at = datetime.utcnow()

    def add_effect(self, effect: str) -> None:
        """Add an effect."""
        if effect and effect not in self.effects:
            self.effects.append(effect)
            self.updated_at = datetime.utcnow()

    def add_miracle(self, miracle: str) -> None:
        """Add a miracle."""
        if miracle and miracle not in self.miracles:
            self.miracles.append(miracle)
            self.updated_at = datetime.utcnow()

    def add_curse(self, curse: str) -> None:
        """Add a curse/drawback."""
        if curse and curse not in self.curses:
            self.curses.append(curse)
            self.updated_at = datetime.utcnow()

    def add_restriction(self, restriction: str) -> None:
        """Add a restriction."""
        if restriction and restriction not in self.restrictions:
            self.restrictions.append(restriction)
            self.updated_at = datetime.utcnow()

    def perform_miracle(self, miracle_name: str) -> bool:
        """Attempt to perform a miracle."""
        if miracle_name not in self.miracles:
            return False
        # Additional logic for miracle performance would go here
        return True

    def increase_divine_power(self, amount: int) -> None:
        """Increase divine power."""
        if amount < 0:
            raise ValueError("amount must be positive")
        self.divine_power += amount
        self.power = self.divine_power  # Sync
        self.updated_at = datetime.utcnow()

    def is_equipped(self) -> bool:
        """Check if item is equipped."""
        return bool(self.character_id)

    def is_soulbound(self) -> bool:
        """Check if item is soulbound."""
        return self.soulbound

    def meets_faith_requirement(self, faith_level: int) -> bool:
        """Check if faith level meets requirement."""
        return faith_level >= self.faith_requirement

    def is_aligned(self, character_alignment: str) -> bool:
        """Check if character alignment matches item."""
        if not self.alignment:
            return True
        return self.alignment.lower() in character_alignment.lower()

    def can_perform_miracle(self, miracle_name: str) -> bool:
        """Check if a miracle can be performed."""
        return miracle_name in self.miracles

    def has_curse(self) -> bool:
        """Check if item has curses."""
        return len(self.curses) > 0

    def has_restriction(self, restriction: str) -> bool:
        """Check if item has specific restriction."""
        return restriction in self.restrictions

    def get_total_power(self) -> int:
        """Calculate total power."""
        return self.power + self.divine_power

    def get_deity_info(self) -> tuple[str, str]:
        """Get deity and pantheon info."""
        return (self.deity_id, self.pantheon)
