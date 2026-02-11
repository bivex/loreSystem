"""ArtifactSet entity - Collections of legendary artifacts."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class ArtifactSet:
    """Represents a set of artifacts that provide bonuses when collected."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    set_name: str = ""
    set_type: str = ""  # armor, weapons, accessories, mixed
    tier: str = "legendary"  # epic, legendary, mythical, divine
    rarity: str = "legendary"  # epic, legendary, mythical, divine
    total_pieces: int = 0
    collected_pieces: list[str] = field(default_factory=list)
    piece_names: list[str] = field(default_factory=list)  # Names of all pieces
    piece_descriptions: dict[str, str] = field(default_factory=dict)  # piece_name: description
    set_bonus_2: str = ""  # Bonus for 2 pieces
    set_bonus_3: str = ""  # Bonus for 3 pieces
    set_bonus_4: str = ""  # Bonus for 4 pieces
    set_bonus_5: str = ""  # Bonus for 5 pieces
    set_bonus_full: str = ""  # Bonus for full set
    passive_bonuses: list[str] = field(default_factory=list)
    active_abilities: list[str] = field(default_factory=list)
    unlock_level: int = 0
    lore: str = ""
    origin_story: str = ""
    creator: str = ""
    creation_era: str = ""
    set_effects: dict[str, list[str]] = field(default_factory=dict)  # piece_count: [effects]
    synergies: list[str] = field(default_factory=list)  # Synergies with other sets
    hidden_effects: list[str] = field(default_factory=list)  # Effects that only reveal at full set
    unlock_conditions: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        set_name: str,
        set_type: str,
        total_pieces: int,
    ) -> Self:
        """Factory method to create a new ArtifactSet."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not set_name:
            raise ValueError("set_name is required")
        if not set_type:
            raise ValueError("set_type is required")
        if total_pieces < 2 or total_pieces > 6:
            raise ValueError("total_pieces must be between 2 and 6")

        valid_types = ["armor", "weapons", "accessories", "mixed"]
        if set_type not in valid_types:
            raise ValueError(f"set_type must be one of {valid_types}")

        valid_tiers = ["epic", "legendary", "mythical", "divine"]
        if tier not in valid_tiers:
            raise ValueError(f"tier must be one of {valid_tiers}")

        valid_rarity = ["epic", "legendary", "mythical", "divine"]
        if rarity not in valid_rarity:
            raise ValueError(f"rarity must be one of {valid_rarity}")

        return cls(
            tenant_id=tenant_id,
            set_name=set_name,
            set_type=set_type,
            total_pieces=total_pieces,
        )

    def add_piece(self, piece_id: str, piece_name: str, description: str = "") -> None:
        """Add a piece to the set."""
        if not piece_id:
            raise ValueError("piece_id is required")
        if not piece_name:
            raise ValueError("piece_name is required")
        if len(self.piece_names) >= self.total_pieces:
            raise ValueError("Set is already complete")

        if piece_id not in self.collected_pieces:
            self.collected_pieces.append(piece_id)
        if piece_name not in self.piece_names:
            self.piece_names.append(piece_name)
        if description:
            self.piece_descriptions[piece_name] = description
        self.updated_at = datetime.utcnow()

    def remove_piece(self, piece_id: str) -> None:
        """Remove a piece from the set."""
        if piece_id in self.collected_pieces:
            self.collected_pieces.remove(piece_id)
            self.updated_at = datetime.utcnow()

    def set_bonus(self, piece_count: int, bonus: str) -> None:
        """Set bonus for specific piece count."""
        if piece_count < 2 or piece_count > self.total_pieces:
            raise ValueError(f"piece_count must be between 2 and {self.total_pieces}")

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

        self.updated_at = datetime.utcnow()

    def add_set_effect(self, piece_count: int, effect: str) -> None:
        """Add an effect for specific piece count."""
        if piece_count < 2 or piece_count > self.total_pieces:
            raise ValueError(f"piece_count must be between 2 and {self.total_pieces}")

        key = str(piece_count)
        if key not in self.set_effects:
            self.set_effects[key] = []
        if effect and effect not in self.set_effects[key]:
            self.set_effects[key].append(effect)
        self.updated_at = datetime.utcnow()

    def add_passive_bonus(self, bonus: str) -> None:
        """Add a passive bonus."""
        if bonus and bonus not in self.passive_bonuses:
            self.passive_bonuses.append(bonus)
            self.updated_at = datetime.utcnow()

    def add_active_ability(self, ability: str) -> None:
        """Add an active ability."""
        if ability and ability not in self.active_abilities:
            self.active_abilities.append(ability)
            self.updated_at = datetime.utcnow()

    def add_synergy(self, synergy: str) -> None:
        """Add a synergy with another set."""
        if synergy and synergy not in self.synergies:
            self.synergies.append(synergy)
            self.updated_at = datetime.utcnow()

    def add_hidden_effect(self, effect: str) -> None:
        """Add a hidden effect (revealed only at full set)."""
        if effect and effect not in self.hidden_effects:
            self.hidden_effects.append(effect)
            self.updated_at = datetime.utcnow()

    def add_unlock_condition(self, condition: str) -> None:
        """Add an unlock condition."""
        if condition and condition not in self.unlock_conditions:
            self.unlock_conditions.append(condition)
            self.updated_at = datetime.utcnow()

    def get_completion_percentage(self) -> float:
        """Get set completion percentage."""
        if self.total_pieces == 0:
            return 0.0
        return (len(self.collected_pieces) / self.total_pieces) * 100

    def get_current_bonus(self) -> str:
        """Get the bonus for current pieces."""
        count = len(self.collected_pieces)
        if count >= self.total_pieces:
            return self.set_bonus_full
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
