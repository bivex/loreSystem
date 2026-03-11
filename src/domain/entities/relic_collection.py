"""RelicCollection entity - Collections of ancient relics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


VALID_RELIC_COLLECTION_TYPES = {"historical", "mythological", "divine", "cursed", "forbidden", "ancient"}
VALID_RELIC_COLLECTION_RARITIES = {"rare", "epic", "legendary", "mythical", "divine", "unique"}


@dataclass
class RelicCollection:
    """Bridge-compatible relic collection aggregate used by CAMEL.Bridge."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    collection_type: str
    total_relics: int
    rarity: str = "legendary"
    collection_power: int = 0
    completion_reward: str = ""
    collected_relic_ids: list[str] = field(default_factory=list)
    relic_names: list[str] = field(default_factory=list)
    relic_descriptions: dict[str, str] = field(default_factory=dict)
    relic_origins: dict[str, str] = field(default_factory=dict)
    relic_eras: dict[str, str] = field(default_factory=dict)
    lore_power: int = 0
    historical_significance: str = ""
    main_lore: str = ""
    hidden_lore: str = ""
    bonuses: list[str] = field(default_factory=list)
    unlock_level: int = 0
    unlock_conditions: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    prophecies: list[str] = field(default_factory=list)
    powers_granted: list[str] = field(default_factory=list)
    restrictions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    is_complete: bool = False
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("RelicCollection name cannot be empty")
        if not self.collection_type or not self.collection_type.strip():
            raise InvariantViolation("RelicCollection collection_type cannot be empty")
        if self.collection_type not in VALID_RELIC_COLLECTION_TYPES:
            raise InvariantViolation(
                f"RelicCollection collection_type must be one of {sorted(VALID_RELIC_COLLECTION_TYPES)}"
            )
        if self.total_relics < 1:
            raise InvariantViolation("RelicCollection total_relics must be at least 1")
        if self.collection_power < 0 or self.lore_power < 0:
            raise InvariantViolation("RelicCollection powers must be non-negative")
        if self.rarity not in VALID_RELIC_COLLECTION_RARITIES:
            raise InvariantViolation(
                f"RelicCollection rarity must be one of {sorted(VALID_RELIC_COLLECTION_RARITIES)}"
            )
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("RelicCollection updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        collection_type: str,
        total_relics: int,
        rarity: str = "legendary",
        collection_power: int = 0,
        completion_reward: str = "",
    ) -> "RelicCollection":
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=Description(description.strip()),
            collection_type=collection_type.strip().lower(),
            total_relics=total_relics,
            rarity=rarity.strip().lower() or "legendary",
            collection_power=max(0, collection_power),
            completion_reward=completion_reward.strip(),
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
    def collection_name(self) -> str:
        return self.name

    @property
    def tier(self) -> str:
        return self.rarity

    def add_relic(
        self,
        relic_id: str,
        relic_name: str,
        description: str = "",
        origin: str = "",
        era: str = ""
    ) -> None:
        """Add a relic to the collection."""
        if not relic_id:
            raise InvariantViolation("relic_id is required")
        if not relic_name:
            raise InvariantViolation("relic_name is required")

        if relic_id not in self.collected_relic_ids:
            self.collected_relic_ids.append(relic_id)
        if relic_name not in self.relic_names:
            self.relic_names.append(relic_name)

        if description:
            self.relic_descriptions[relic_name] = description
        if origin:
            self.relic_origins[relic_name] = origin
        if era:
            self.relic_eras[relic_name] = era

        self.update_completion_status()
        self.updated_at = Timestamp.now()

    def remove_relic(self, relic_id: str) -> None:
        """Remove a relic from the collection."""
        if relic_id in self.collected_relic_ids:
            self.collected_relic_ids.remove(relic_id)
            self.update_completion_status()
            self.updated_at = Timestamp.now()

    def add_bonus(self, bonus: str) -> None:
        """Add a collection bonus."""
        if bonus and bonus not in self.bonuses:
            self.bonuses.append(bonus)
            self.updated_at = Timestamp.now()

    def add_secret(self, secret: str) -> None:
        """Add a secret revealed by the collection."""
        if secret and secret not in self.secrets:
            self.secrets.append(secret)
            self.updated_at = Timestamp.now()

    def add_prophecy(self, prophecy: str) -> None:
        """Add a prophecy tied to the collection."""
        if prophecy and prophecy not in self.prophecies:
            self.prophecies.append(prophecy)
            self.updated_at = Timestamp.now()

    def add_power_granted(self, power: str) -> None:
        """Add a power granted by the collection."""
        if power and power not in self.powers_granted:
            self.powers_granted.append(power)
            self.updated_at = Timestamp.now()

    def add_restriction(self, restriction: str) -> None:
        """Add a restriction."""
        if restriction and restriction not in self.restrictions:
            self.restrictions.append(restriction)
            self.updated_at = Timestamp.now()

    def add_warning(self, warning: str) -> None:
        """Add a warning."""
        if warning and warning not in self.warnings:
            self.warnings.append(warning)
            self.updated_at = Timestamp.now()

    def add_unlock_condition(self, condition: str) -> None:
        """Add an unlock condition."""
        if condition and condition not in self.unlock_conditions:
            self.unlock_conditions.append(condition)
            self.updated_at = Timestamp.now()

    def increase_collection_power(self, amount: int) -> None:
        """Increase collection power."""
        if amount < 0:
            raise InvariantViolation("amount must be positive")
        self.collection_power += amount
        self.updated_at = Timestamp.now()

    def increase_lore_power(self, amount: int) -> None:
        """Increase lore power."""
        if amount < 0:
            raise InvariantViolation("amount must be positive")
        self.lore_power += amount
        self.updated_at = Timestamp.now()

    def update_completion_status(self) -> None:
        """Update completion status."""
        previous_status = self.is_complete
        self.is_complete = len(self.collected_relic_ids) >= self.total_relics

        # Reveal hidden lore when completed
        if self.is_complete and not previous_status:
            # Trigger completion rewards
            pass

        self.updated_at = Timestamp.now()

    def set_completion_reward(self, reward: str) -> None:
        """Set the reward for completing the collection."""
        self.completion_reward = reward
        self.updated_at = Timestamp.now()

    def get_completion_percentage(self) -> float:
        """Get collection completion percentage."""
        if self.total_relics == 0:
            return 0.0
        return (len(self.collected_relic_ids) / self.total_relics) * 100

    def get_total_power(self) -> int:
        """Calculate total power."""
        return self.collection_power + self.lore_power

    def has_relic(self, relic_id: str) -> bool:
        """Check if collection contains specific relic."""
        return relic_id in self.collected_relic_ids

    def has_relic_name(self, relic_name: str) -> bool:
        """Check if collection has relic by name."""
        return relic_name in self.relic_names

    def get_relic_origin(self, relic_name: str) -> Optional[str]:
        """Get origin of a relic."""
        return self.relic_origins.get(relic_name)

    def get_relic_era(self, relic_name: str) -> Optional[str]:
        """Get era of a relic."""
        return self.relic_eras.get(relic_name)

    def get_relic_description(self, relic_name: str) -> Optional[str]:
        """Get description of a relic."""
        return self.relic_descriptions.get(relic_name)

    def is_dangerous(self) -> bool:
        """Check if collection is dangerous."""
        return self.collection_type in ["cursed", "forbidden"] or len(self.warnings) > 0

    def can_reveal_hidden_lore(self) -> bool:
        """Check if hidden lore can be revealed."""
        return self.is_complete

    def get_hidden_lore(self) -> str:
        """Get hidden lore (only if complete)."""
        if self.is_complete:
            return self.hidden_lore
        return "Collection must be complete to reveal hidden lore."

    def get_relic_count(self) -> int:
        """Get number of collected relics."""
        return len(self.collected_relic_ids)

    def get_missing_relic_count(self) -> int:
        """Get number of missing relics."""
        return max(0, self.total_relics - len(self.collected_relic_ids))

    def has_secret(self, secret: str) -> bool:
        """Check for specific secret."""
        return secret in self.secrets

    def has_prophecy(self, prophecy: str) -> bool:
        """Check for specific prophecy."""
        return prophecy in self.prophecies

    def has_restriction(self, restriction: str) -> bool:
        """Check for specific restriction."""
        return restriction in self.restrictions
