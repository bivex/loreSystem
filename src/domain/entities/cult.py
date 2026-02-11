"""Cult entity - Secret religious organization."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Cult:
    """Represents a cult or secret religious group."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""
    deity_id: str = ""
    leader_id: str = ""
    secret_knowledge: list[str] = field(default_factory=list)
    rituals: list[str] = field(default_factory=list)
    membership_count: int = 0
    secrecy_level: int = 0  # 0-100
    alignment: str = ""  # good, evil, neutral
    headquarters_location_id: str = ""

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        deity_id: str,
    ) -> Self:
        """Factory method to create a new Cult."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not deity_id:
            raise ValueError("deity_id is required")

        return cls(
            tenant_id=tenant_id,
            name=name,
            deity_id=deity_id,
        )

    def set_leader(self, leader_id: str) -> None:
        """Set cult leader."""
        self.leader_id = leader_id
        self.updated_at = datetime.utcnow()

    def set_secrecy(self, level: int) -> None:
        """Set secrecy level."""
        self.secrecy_level = max(0, min(100, level))
        self.updated_at = datetime.utcnow()

    def add_knowledge(self, knowledge: str) -> None:
        """Add secret knowledge."""
        if knowledge and knowledge not in self.secret_knowledge:
            self.secret_knowledge.append(knowledge)
            self.updated_at = datetime.utcnow()

    def add_ritual(self, ritual: str) -> None:
        """Add a ritual."""
        if ritual and ritual not in self.rituals:
            self.rituals.append(ritual)
            self.updated_at = datetime.utcnow()

    def add_member(self) -> None:
        """Increment membership count."""
        self.membership_count += 1
        self.updated_at = datetime.utcnow()

    def remove_member(self) -> None:
        """Decrement membership count."""
        self.membership_count = max(0, self.membership_count - 1)
        self.updated_at = datetime.utcnow()

    def set_alignment(self, alignment: str) -> None:
        """Set alignment."""
        valid_alignments = ["good", "evil", "neutral"]
        if alignment not in valid_alignments:
            raise ValueError(f"alignment must be one of {valid_alignments}")
        self.alignment = alignment
        self.updated_at = datetime.utcnow()

    def is_secretive(self) -> bool:
        """Check if cult is secretive (high secrecy level)."""
        return self.secrecy_level >= 70

    def has_knowledge(self, knowledge: str) -> bool:
        """Check if cult possesses specific knowledge."""
        return knowledge in self.secret_knowledge
