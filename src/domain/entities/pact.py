"""Pact entity - Supernatural agreement."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Pact:
    """Represents a supernatural pact or agreement."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    entity_id: str = ""  # Demon, deity, spirit, etc.
    entity_name: str = ""
    pact_type: str = ""  # power, knowledge, immortality, wealth, vengeance
    terms: list[str] = field(default_factory=list)
    benefits: list[str] = field(default_factory=list)
    costs: list[str] = field(default_factory=list)
    duration: str = "eternal"  # temporary, eternal, until_condition
    condition: str = ""  # End condition if duration is until_condition
    active: bool = True
    breach_consequence: str = ""

    @classmethod
    def create(
        cls,
        tenant_id: str,
        character_id: str,
        entity_id: str,
        entity_name: str,
        pact_type: str,
    ) -> Self:
        """Factory method to create a new Pact."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not character_id:
            raise ValueError("character_id is required")
        if not entity_id:
            raise ValueError("entity_id is required")
        if not entity_name:
            raise ValueError("entity_name is required")
        if not pact_type:
            raise ValueError("pact_type is required")

        valid_types = ["power", "knowledge", "immortality", "wealth", "vengeance"]
        if pact_type not in valid_types:
            raise ValueError(f"pact_type must be one of {valid_types}")

        return cls(
            tenant_id=tenant_id,
            character_id=character_id,
            entity_id=entity_id,
            entity_name=entity_name,
            pact_type=pact_type,
        )

    def add_term(self, term: str) -> None:
        """Add a term."""
        if term and term not in self.terms:
            self.terms.append(term)
            self.updated_at = datetime.utcnow()

    def add_benefit(self, benefit: str) -> None:
        """Add a benefit."""
        if benefit and benefit not in self.benefits:
            self.benefits.append(benefit)
            self.updated_at = datetime.utcnow()

    def add_cost(self, cost: str) -> None:
        """Add a cost."""
        if cost and cost not in self.costs:
            self.costs.append(cost)
            self.updated_at = datetime.utcnow()

    def set_duration(self, duration: str, condition: str = "") -> None:
        """Set pact duration."""
        valid_durations = ["temporary", "eternal", "until_condition"]
        if duration not in valid_durations:
            raise ValueError(f"duration must be one of {valid_durations}")
        self.duration = duration
        if duration == "until_condition":
            self.condition = condition
        self.updated_at = datetime.utcnow()

    def set_consequence(self, consequence: str) -> None:
        """Set breach consequence."""
        self.breach_consequence = consequence
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate pact."""
        self.active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate pact."""
        self.active = False
        self.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        """Check if pact is active."""
        return self.active

    def is_demonic(self) -> bool:
        """Check if pact with demon (heuristic)."""
        return "demon" in self.entity_name.lower() or self.entity_id.startswith("demon")

    def is_eternal(self) -> bool:
        """Check if pact is eternal."""
        return self.duration == "eternal"
