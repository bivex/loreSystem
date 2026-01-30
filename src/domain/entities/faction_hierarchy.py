"""FactionHierarchy entity - Faction organizational structure."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class FactionHierarchy:
    """Represents a faction's organizational hierarchy."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    faction_id: str = ""
    structure_type: str = ""  # pyramidal, flat, feudal, military, religious
    ranks: list[dict] = field(default_factory=list)  # [{name: "Initiate", tier: 1}, ...]
    leadership_id: str = ""  # Current leader character ID
    succession_rules: str = ""  # hereditary, meritocratic, appointed, elected
    promotion_criteria: str = ""  # Requirements for promotion

    @classmethod
    def create(
        cls,
        tenant_id: str,
        faction_id: str,
        structure_type: str,
    ) -> Self:
        """Factory method to create a new FactionHierarchy."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not faction_id:
            raise ValueError("faction_id is required")
        if not structure_type:
            raise ValueError("structure_type is required")

        valid_structures = ["pyramidal", "flat", "feudal", "military", "religious"]
        if structure_type not in valid_structures:
            raise ValueError(f"structure_type must be one of {valid_structures}")

        return cls(
            tenant_id=tenant_id,
            faction_id=faction_id,
            structure_type=structure_type,
        )

    def add_rank(self, name: str, tier: int, permissions: list[str] | None = None) -> None:
        """Add a rank to the hierarchy."""
        if not name:
            raise ValueError("rank name is required")
        if tier < 0:
            raise ValueError("tier must be non-negative")

        rank_entry = {"name": name, "tier": tier, "permissions": permissions or []}
        self.ranks.append(rank_entry)
        self.ranks.sort(key=lambda x: x["tier"])
        self.updated_at = datetime.utcnow()

    def set_leadership(self, leader_id: str) -> None:
        """Set the faction leader."""
        self.leadership_id = leader_id
        self.updated_at = datetime.utcnow()

    def set_succession_rules(self, rules: str) -> None:
        """Set succession rules."""
        valid_rules = ["hereditary", "meritocratic", "appointed", "elected"]
        if rules and rules not in valid_rules:
            raise ValueError(f"succession_rules must be one of {valid_rules}")
        self.succession_rules = rules
        self.updated_at = datetime.utcnow()

    def set_promotion_criteria(self, criteria: str) -> None:
        """Set promotion criteria."""
        self.promotion_criteria = criteria
        self.updated_at = datetime.utcnow()

    def get_highest_rank(self) -> dict | None:
        """Get the highest rank."""
        if not self.ranks:
            return None
        return max(self.ranks, key=lambda x: x["tier"])

    def get_lowest_rank(self) -> dict | None:
        """Get the lowest rank."""
        if not self.ranks:
            return None
        return min(self.ranks, key=lambda x: x["tier"])

    def get_rank_by_tier(self, tier: int) -> dict | None:
        """Get rank by tier level."""
        for rank in self.ranks:
            if rank["tier"] == tier:
                return rank
        return None
