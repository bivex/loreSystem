"""MythicalArmor entity - Extraordinary protective equipment."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class MythicalArmor:
    """Represents mythical armor with extraordinary defensive capabilities."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    armor_name: str = ""
    armor_type: str = ""  # chestplate, helmet, boots, gauntlets, shield, full_set
    tier: str = "mythical"  # legendary, mythical, divine
    rarity: str = "mythical"  # common, rare, epic, legendary, mythic
    defense_power: int = 0
    special_protection: str = ""
    protection_description: str = ""
    damage_resistance: dict[str, int] = field(default_factory=dict)  # damage_type: resistance %
    elemental_immune: list[str] = field(default_factory=list)  # immune elements
    durability: int = 100
    max_durability: int = 100
    unlock_level: int = 0
    required_class: str = ""
    lore: str = ""
    enchantments: list[str] = field(default_factory=list)
    passive_effects: list[str] = field(default_factory=list)
    set_bonus: str = ""  # name of set this belongs to
    weight: int = 0  # affects movement speed
    mobility_penalty: int = 0  # 0-100, reduces mobility
    magical_defense: int = 0
    physical_defense: int = 0
    soulbound: bool = False
    upgrade_level: int = 0
    max_upgrade_level: int = 10
    previous_owners: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        armor_name: str,
        armor_type: str,
        defense_power: int,
        special_protection: str,
    ) -> Self:
        """Factory method to create a new MythicalArmor."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not armor_name:
            raise ValueError("armor_name is required")
        if not armor_type:
            raise ValueError("armor_type is required")
        if defense_power < 0:
            raise ValueError("defense_power must be non-negative")
        if not special_protection:
            raise ValueError("special_protection is required")

        valid_types = [
            "chestplate", "helmet", "boots", "gauntlets",
            "shield", "full_set", "shoulders", "leggings"
        ]
        if armor_type not in valid_types:
            raise ValueError(f"armor_type must be one of {valid_types}")

        valid_tiers = ["legendary", "mythical", "divine"]
        if tier not in valid_tiers:
            raise ValueError(f"tier must be one of {valid_tiers}")

        valid_rarity = ["common", "rare", "epic", "legendary", "mythic"]
        if rarity not in valid_rarity:
            raise ValueError(f"rarity must be one of {valid_rarity}")

        valid_elements = ["fire", "ice", "lightning", "poison", "holy", "dark", "void"]
        for element in elemental_immune:
            if element not in valid_elements:
                raise ValueError(f"elemental_immune must contain only {valid_elements}")

        return cls(
            tenant_id=tenant_id,
            armor_name=armor_name,
            armor_type=armor_type,
            defense_power=defense_power,
            special_protection=special_protection,
        )

    def equip(self, character_id: str) -> None:
        """Equip armor to character."""
        if not character_id:
            raise ValueError("character_id is required")
        self.character_id = character_id
        self.updated_at = datetime.utcnow()

    def unequip(self) -> None:
        """Unequip armor."""
        self.character_id = ""
        self.updated_at = datetime.utcnow()

    def upgrade(self) -> None:
        """Upgrade armor."""
        if self.upgrade_level >= self.max_upgrade_level:
            raise ValueError("Armor is at max upgrade level")
        self.upgrade_level += 1
        self.defense_power = int(self.defense_power * 1.1)
        self.magical_defense = int(self.magical_defense * 1.1)
        self.physical_defense = int(self.physical_defense * 1.1)
        self.updated_at = datetime.utcnow()

    def repair(self) -> None:
        """Repair armor to max durability."""
        self.durability = self.max_durability
        self.updated_at = datetime.utcnow()

    def take_damage(self, amount: int) -> None:
        """Reduce durability."""
        self.durability = max(0, self.durability - amount)
        self.updated_at = datetime.utcnow()

    def set_resistance(self, damage_type: str, resistance: int) -> None:
        """Set damage resistance."""
        if resistance < 0 or resistance > 100:
            raise ValueError("resistance must be between 0 and 100")
        self.damage_resistance[damage_type] = resistance
        self.updated_at = datetime.utcnow()

    def add_elemental_immunity(self, element: str) -> None:
        """Add elemental immunity."""
        valid_elements = ["fire", "ice", "lightning", "poison", "holy", "dark", "void"]
        if element not in valid_elements:
            raise ValueError(f"element must be one of {valid_elements}")
        if element not in self.elemental_immune:
            self.elemental_immune.append(element)
            self.updated_at = datetime.utcnow()

    def add_enchantment(self, enchantment: str) -> None:
        """Add an enchantment."""
        if enchantment and enchantment not in self.enchantments:
            self.enchantments.append(enchantment)
            self.updated_at = datetime.utcnow()

    def add_passive_effect(self, effect: str) -> None:
        """Add a passive effect."""
        if effect and effect not in self.passive_effects:
            self.passive_effects.append(effect)
            self.updated_at = datetime.utcnow()

    def bind_soul(self, character_id: str) -> None:
        """Bind armor to character's soul."""
        if not character_id:
            raise ValueError("character_id is required")
        self.soulbound = True
        self.character_id = character_id
        self.updated_at = datetime.utcnow()

    def add_previous_owner(self, owner_name: str) -> None:
        """Add a previous owner to lore."""
        if owner_name and owner_name not in self.previous_owners:
            self.previous_owners.append(owner_name)
            self.updated_at = datetime.utcnow()

    def get_resistance(self, damage_type: str) -> int:
        """Get resistance for damage type."""
        return self.damage_resistance.get(damage_type, 0)

    def is_immune_to(self, element: str) -> bool:
        """Check if immune to element."""
        return element in self.elemental_immune

    def is_equipped(self) -> bool:
        """Check if armor is equipped."""
        return bool(self.character_id)

    def is_broken(self) -> bool:
        """Check if armor is broken."""
        return self.durability <= 0

    def is_soulbound(self) -> bool:
        """Check if armor is soulbound."""
        return self.soulbound

    def is_max_upgrade(self) -> bool:
        """Check if armor is at max upgrade level."""
        return self.upgrade_level >= self.max_upgrade_level

    def get_total_defense(self) -> int:
        """Calculate total defense including upgrades."""
        multiplier = 1 + (self.upgrade_level * 0.1)
        return int(self.defense_power * multiplier)

    def has_enchantment(self, enchantment: str) -> bool:
        """Check if armor has specific enchantment."""
        return enchantment in self.enchantments
