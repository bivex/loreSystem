"""ArtifactSet entity - Collections of legendary artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


VALID_ARTIFACT_SET_TYPES = {"armor", "weapons", "accessories", "mixed"}
VALID_ARTIFACT_SET_RARITIES = {"epic", "legendary", "mythical", "divine"}


@dataclass
class ArtifactSet:
    """Bridge-compatible artifact set aggregate used by CAMEL.Bridge."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    set_type: str
    total_pieces: int
    rarity: str = "legendary"
    set_bonus: str = ""
    collected_pieces: list[str] = field(default_factory=list)
    piece_names: list[str] = field(default_factory=list)
    piece_descriptions: dict[str, str] = field(default_factory=dict)
    set_bonus_2: str = ""
    set_bonus_3: str = ""
    set_bonus_4: str = ""
    set_bonus_5: str = ""
    set_bonus_full: str = ""
    passive_bonuses: list[str] = field(default_factory=list)
    active_abilities: list[str] = field(default_factory=list)
    unlock_level: int = 0
    lore: str = ""
    origin_story: str = ""
    creator: str = ""
    creation_era: str = ""
    set_effects: dict[str, list[str]] = field(default_factory=dict)
    synergies: list[str] = field(default_factory=list)
    hidden_effects: list[str] = field(default_factory=list)
    unlock_conditions: list[str] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    id: EntityId | None = None
    version: Version = field(default_factory=Version)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvariantViolation("ArtifactSet name cannot be empty")
        if not self.set_type or not self.set_type.strip():
            raise InvariantViolation("ArtifactSet set_type cannot be empty")
        if self.set_type not in VALID_ARTIFACT_SET_TYPES:
            raise InvariantViolation(
                f"ArtifactSet set_type must be one of {sorted(VALID_ARTIFACT_SET_TYPES)}"
            )
        if self.total_pieces < 2 or self.total_pieces > 6:
            raise InvariantViolation("ArtifactSet total_pieces must be between 2 and 6")
        if self.rarity not in VALID_ARTIFACT_SET_RARITIES:
            raise InvariantViolation(
                f"ArtifactSet rarity must be one of {sorted(VALID_ARTIFACT_SET_RARITIES)}"
            )
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("ArtifactSet updated_at cannot be before created_at")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
        set_type: str,
        total_pieces: int,
        rarity: str = "legendary",
        set_bonus: str = "",
    ) -> "ArtifactSet":
        now = Timestamp.now()
        normalized_rarity = rarity.strip().lower() or "legendary"
        normalized_bonus = set_bonus.strip()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=Description(description.strip()),
            set_type=set_type.strip().lower(),
            total_pieces=total_pieces,
            rarity=normalized_rarity,
            set_bonus=normalized_bonus,
            set_bonus_full=normalized_bonus,
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
    def set_name(self) -> str:
        return self.name

    @property
    def tier(self) -> str:
        return self.rarity

    def add_piece(self, piece_id: str, piece_name: str, description: str = "") -> None:
        """Add a piece to the set."""
        if not piece_id:
            raise InvariantViolation("piece_id is required")
        if not piece_name:
            raise InvariantViolation("piece_name is required")
        if len(self.piece_names) >= self.total_pieces:
            raise InvariantViolation("Set is already complete")

        if piece_id not in self.collected_pieces:
            self.collected_pieces.append(piece_id)
        if piece_name not in self.piece_names:
            self.piece_names.append(piece_name)
        if description:
            self.piece_descriptions[piece_name] = description
        self.updated_at = Timestamp.now()

    def remove_piece(self, piece_id: str) -> None:
        """Remove a piece from the set."""
        if piece_id in self.collected_pieces:
            self.collected_pieces.remove(piece_id)
            self.updated_at = Timestamp.now()

    def set_piece_bonus(self, piece_count: int, bonus: str) -> None:
        """Set bonus for specific piece count."""
        if piece_count < 2 or piece_count > self.total_pieces:
            raise InvariantViolation(f"piece_count must be between 2 and {self.total_pieces}")

        if piece_count == self.total_pieces:
            self.set_bonus_full = bonus
        elif piece_count == 2:
            self.set_bonus_2 = bonus
        elif piece_count == 3:
            self.set_bonus_3 = bonus
        elif piece_count == 4:
            self.set_bonus_4 = bonus
        elif piece_count == 5:
            self.set_bonus_5 = bonus

        self.updated_at = Timestamp.now()

    def add_set_effect(self, piece_count: int, effect: str) -> None:
        """Add an effect for specific piece count."""
        if piece_count < 2 or piece_count > self.total_pieces:
            raise InvariantViolation(f"piece_count must be between 2 and {self.total_pieces}")

        key = str(piece_count)
        if key not in self.set_effects:
            self.set_effects[key] = []
        if effect and effect not in self.set_effects[key]:
            self.set_effects[key].append(effect)
        self.updated_at = Timestamp.now()

    def add_passive_bonus(self, bonus: str) -> None:
        """Add a passive bonus."""
        if bonus and bonus not in self.passive_bonuses:
            self.passive_bonuses.append(bonus)
            self.updated_at = Timestamp.now()

    def add_active_ability(self, ability: str) -> None:
        """Add an active ability."""
        if ability and ability not in self.active_abilities:
            self.active_abilities.append(ability)
            self.updated_at = Timestamp.now()

    def add_synergy(self, synergy: str) -> None:
        """Add a synergy with another set."""
        if synergy and synergy not in self.synergies:
            self.synergies.append(synergy)
            self.updated_at = Timestamp.now()

    def add_hidden_effect(self, effect: str) -> None:
        """Add a hidden effect (revealed only at full set)."""
        if effect and effect not in self.hidden_effects:
            self.hidden_effects.append(effect)
            self.updated_at = Timestamp.now()

    def add_unlock_condition(self, condition: str) -> None:
        """Add an unlock condition."""
        if condition and condition not in self.unlock_conditions:
            self.unlock_conditions.append(condition)
            self.updated_at = Timestamp.now()

    def get_completion_percentage(self) -> float:
        """Get set completion percentage."""
        if self.total_pieces == 0:
            return 0.0
        return (len(self.collected_pieces) / self.total_pieces) * 100

    def get_current_bonus(self) -> str:
        """Get the bonus for current pieces."""
        count = len(self.collected_pieces)
        if count >= self.total_pieces:
            return self.set_bonus_full or self.set_bonus
        elif count >= 5:
            return self.set_bonus_5
        elif count >= 4:
            return self.set_bonus_4
        elif count >= 3:
            return self.set_bonus_3
        elif count >= 2:
            return self.set_bonus_2
        return ""

    def get_current_effects(self) -> list[str]:
        """Get effects for current piece count."""
        count = len(self.collected_pieces)
        effects = self.passive_bonuses.copy()

        # Add set effects based on piece count
        if count >= 2:
            effects.extend(self.set_effects.get("2", []))
        if count >= 3:
            effects.extend(self.set_effects.get("3", []))
        if count >= 4:
            effects.extend(self.set_effects.get("4", []))
        if count >= 5:
            effects.extend(self.set_effects.get("5", []))
        if count >= self.total_pieces:
            effects.extend(self.set_effects.get(str(self.total_pieces), []))
            # Reveal hidden effects at full set
            effects.extend(self.hidden_effects)

        return list(set(effects))  # Remove duplicates

    def has_piece(self, piece_id: str) -> bool:
        """Check if set contains specific piece."""
        return piece_id in self.collected_pieces

    def is_complete(self) -> bool:
        """Check if set is complete."""
        return len(self.collected_pieces) >= self.total_pieces

    def can_reveal_hidden_effects(self) -> bool:
        """Check if hidden effects can be revealed."""
        return self.is_complete()

    def has_synergy(self, synergy: str) -> bool:
        """Check for specific synergy."""
        return synergy in self.synergies

    def get_piece_count(self) -> int:
        """Get number of collected pieces."""
        return len(self.collected_pieces)

    def get_missing_pieces(self) -> list[str]:
        """Get names of missing pieces."""
        return [name for name in self.piece_names if name not in self.collected_pieces]
