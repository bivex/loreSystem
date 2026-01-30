"""LegendaryWeapon entity - Rare and powerful weapons."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class LegendaryWeapon:
    """Represents a legendary weapon with unique powers."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    weapon_name: str = ""
    weapon_type: str = ""  # sword, axe, bow, staff, spear, etc.
    tier: str = "legendary"  # legendary, mythical, divine
    rarity: str = "legendary"  # common, rare, epic, legendary, mythic
    attack_power: int = 0
    special_ability: str = ""
    ability_description: str = ""
    damage_type: str = ""  # physical, fire, ice, lightning, holy, void
    durability: int = 100
    max_durability: int = 100
    unlock_level: int = 0
    required_class: str = ""
    lore: str = ""
    enchantments: list[str] = field(default_factory=list)
    passive_effects: list[str] = field(default_factory=list)
    unique_abilities: list[str] = field(default_factory=list)
    soulbound: bool = False
    upgrade_level: int = 0
    max_upgrade_level: int = 10
    previous_owners: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        weapon_name: str,
        weapon_type: str,
        attack_power: int,
        special_ability: str,
    ) -> Self:
        """Factory method to create a new LegendaryWeapon."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not weapon_name:
            raise ValueError("weapon_name is required")
        if not weapon_type:
            raise ValueError("weapon_type is required")
        if attack_power < 0:
            raise ValueError("attack_power must be non-negative")
        if not special_ability:
            raise ValueError("special_ability is required")

        valid_types = [
            "sword", "axe", "bow", "staff", "spear", "dagger",
            "mace", "hammer", "crossbow", "wand", "fists", "claws"
        ]
        if weapon_type not in valid_types:
            raise ValueError(f"weapon_type must be one of {valid_types}")

        valid_tiers = ["legendary", "mythical", "divine"]
        if tier not in valid_tiers:
            raise ValueError(f"tier must be one of {valid_tiers}")

        valid_rarity = ["common", "rare", "epic", "legendary", "mythic"]
        if rarity not in valid_rarity:
            raise ValueError(f"rarity must be one of {valid_rarity}")

        valid_damage = ["physical", "fire", "ice", "lightning", "holy", "void", "arcane"]
        if damage_type and damage_type not in valid_damage:
            raise ValueError(f"damage_type must be one of {valid_damage}")

        return cls(
            tenant_id=tenant_id,
            weapon_name=weapon_name,
            weapon_type=weapon_type,
            attack_power=attack_power,
            special_ability=special_ability,
        )

    def equip(self, character_id: str) -> None:
        """Equip weapon to character."""
        if not character_id:
            raise ValueError("character_id is required")
        self.character_id = character_id
        self.updated_at = datetime.utcnow()

    def unequip(self) -> None:
        """Unequip weapon."""
        self.character_id = ""
        self.updated_at = datetime.utcnow()

    def upgrade(self) -> None:
        """Upgrade weapon."""
        if self.upgrade_level >= self.max_upgrade_level:
            raise ValueError("Weapon is at max upgrade level")
        self.upgrade_level += 1
        self.attack_power = int(self.attack_power * 1.1)  # 10% increase
        self.updated_at = datetime.utcnow()

    def repair(self) -> None:
        """Repair weapon to max durability."""
        self.durability = self.max_durability
        self.updated_at = datetime.utcnow()

    def take_damage(self, amount: int) -> None:
        """Reduce durability."""
        self.durability = max(0, self.durability - amount)
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

    def add_unique_ability(self, ability: str) -> None:
        """Add a unique ability."""
        if ability and ability not in self.unique_abilities:
            self.unique_abilities.append(ability)
            self.updated_at = datetime.utcnow()

    def bind_soul(self, character_id: str) -> None:
        """Bind weapon to character's soul."""
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

    def is_equipped(self) -> bool:
        """Check if weapon is equipped."""
        return bool(self.character_id)

    def is_broken(self) -> bool:
        """Check if weapon is broken."""
        return self.durability <= 0

    def is_soulbound(self) -> bool:
        """Check if weapon is soulbound."""
        return self.soulbound

    def is_max_upgrade(self) -> bool:
        """Check if weapon is at max upgrade level."""
        return self.upgrade_level >= self.max_upgrade_level

    def get_total_power(self) -> int:
        """Calculate total power including upgrades."""
        multiplier = 1 + (self.upgrade_level * 0.1)
        return int(self.attack_power * multiplier)

    def has_enchantment(self, enchantment: str) -> bool:
        """Check if weapon has specific enchantment."""
        return enchantment in self.enchantments
