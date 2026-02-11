"""Oath entity - Sacred vow/promise."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Oath:
    """Represents a sacred oath or vow."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    oath_name: str = ""
    oath_type: str = ""  # fealty, silence, vengeance, protection, service
    terms: list[str] = field(default_factory=list)
    restrictions: list[str] = field(default_factory=list)
    benefits: list[str] = field(default_factory=list)
    witness_id: str = ""  # Character who witnessed the oath
    broken: bool = False
    break_penalty: str = ""

    @classmethod
    def create(
        cls,
        tenant_id: str,
        character_id: str,
        oath_name: str,
        oath_type: str,
    ) -> Self:
        """Factory method to create a new Oath."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not character_id:
            raise ValueError("character_id is required")
        if not oath_name:
            raise ValueError("oath_name is required")
        if not oath_type:
            raise ValueError("oath_type is required")

        valid_types = ["fealty", "silence", "vengeance", "protection", "service"]
        if oath_type not in valid_types:
            raise ValueError(f"oath_type must be one of {valid_types}")

        return cls(
            tenant_id=tenant_id,
            character_id=character_id,
            oath_name=oath_name,
            oath_type=oath_type,
        )

    def add_term(self, term: str) -> None:
        """Add a term."""
        if term and term not in self.terms:
            self.terms.append(term)
            self.updated_at = datetime.utcnow()

    def add_restriction(self, restriction: str) -> None:
        """Add a restriction."""
        if restriction and restriction not in self.restrictions:
            self.restrictions.append(restriction)
            self.updated_at = datetime.utcnow()

    def add_benefit(self, benefit: str) -> None:
        """Add a benefit."""
        if benefit and benefit not in self.benefits:
            self.benefits.append(benefit)
            self.updated_at = datetime.utcnow()

    def set_witness(self, witness_id: str) -> None:
        """Set oath witness."""
        self.witness_id = witness_id
        self.updated_at = datetime.utcnow()

    def set_penalty(self, penalty: str) -> None:
        """Set break penalty."""
        self.break_penalty = penalty
        self.updated_at = datetime.utcnow()

    def break_oath(self) -> None:
        """Mark oath as broken."""
        self.broken = True
        self.updated_at = datetime.utcnow()

    def is_broken(self) -> bool:
        """Check if oath is broken."""
        return self.broken

    def is_active(self) -> bool:
        """Check if oath is active (not broken)."""
        return not self.broken

    def has_witness(self) -> bool:
        """Check if oath has a witness."""
        return bool(self.witness_id)
