"""Evidence entity for legal proof."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Evidence:
    """Represents evidence in legal proceedings."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        evidence_type: str,
        case_id: UUID,
        description: str,
        source_id: UUID,
        collection_date: datetime,
        is_admissible: bool,
        authenticity_score: float,
        chain_of_custody: list[dict],
        is_tampered: bool,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.evidence_type = evidence_type
        self.case_id = case_id
        self.description = description
        self.source_id = source_id
        self.collection_date = collection_date
        self.is_admissible = is_admissible
        self.authenticity_score = authenticity_score
        self.chain_of_custody = chain_of_custody
        self.is_tampered = is_tampered
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        evidence_type: str,
        case_id: UUID,
        source_id: UUID,
        description: str = "",
        authenticity_score: float = 1.0,
    ) -> "Evidence":
        """Factory method to create new evidence."""
        if not name or not name.strip():
            raise ValueError("Evidence name is required")
        if evidence_type not in ["physical", "documentary", "testimony", "digital", "forensic"]:
            raise ValueError("Invalid evidence type")
        if not 0.0 <= authenticity_score <= 1.0:
            raise ValueError("Authenticity score must be between 0.0 and 1.0")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            evidence_type=evidence_type,
            case_id=case_id,
            description=description,
            source_id=source_id,
            collection_date=datetime.utcnow(),
            is_admissible=True,
            authenticity_score=authenticity_score,
            chain_of_custody=[],
            is_tampered=False,
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate evidence data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and self.evidence_type in ["physical", "documentary", "testimony", "digital", "forensic"]
            and isinstance(self.authenticity_score, (int, float)) and 0.0 <= self.authenticity_score <= 1.0
        )

    def __repr__(self) -> str:
        return f"<Evidence {self.name}: {self.evidence_type}, admissible={self.is_admissible}>"
