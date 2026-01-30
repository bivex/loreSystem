"""Witness entity for testimony."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Witness:
    """Represents a witness in legal proceedings."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        witness_type: str,
        case_id: UUID,
        character_id: UUID,
        testimony: str,
        credibility: float,
        is_hostile: bool,
        has_testified: bool,
        cross_examined: bool,
        deposition_date: Optional[datetime],
        testimony_date: Optional[datetime],
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.witness_type = witness_type
        self.case_id = case_id
        self.character_id = character_id
        self.testimony = testimony
        self.credibility = credibility
        self.is_hostile = is_hostile
        self.has_testified = has_testified
        self.cross_examined = cross_examined
        self.deposition_date = deposition_date
        self.testimony_date = testimony_date
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        witness_type: str,
        case_id: UUID,
        character_id: UUID,
        testimony: str = "",
        credibility: float = 0.5,
        is_hostile: bool = False,
    ) -> "Witness":
        """Factory method to create a new witness."""
        if not name or not name.strip():
            raise ValueError("Witness name is required")
        if witness_type not in ["eyewitness", "expert", "character", "hearsay"]:
            raise ValueError("Invalid witness type")
        if not 0.0 <= credibility <= 1.0:
            raise ValueError("Credibility must be between 0.0 and 1.0")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            witness_type=witness_type,
            case_id=case_id,
            character_id=character_id,
            testimony=testimony,
            credibility=credibility,
            is_hostile=is_hostile,
            has_testified=False,
            cross_examined=False,
            deposition_date=None,
            testimony_date=None,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate witness data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.witness_type in ["eyewitness", "expert", "character", "hearsay"]
            and isinstance(self.credibility, (int, float)) and 0.0 <= self.credibility <= 1.0
        )

    def __repr__(self) -> str:
        return f"<Witness {self.name}: {self.witness_type}, credibility={self.credibility}>"
