"""Quarter entity for urban sections."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Quarter:
    """Represents a quarter within a city."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        ward_id: UUID,
        quarter_type: str,
        description: str,
        landmarks: list,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.ward_id = ward_id
        self.quarter_type = quarter_type
        self.description = description
        self.landmarks = landmarks
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        ward_id: UUID,
        quarter_type: str = "general",
        description: str = "",
        landmarks: Optional[list] = None,
    ) -> "Quarter":
        """Factory method to create a new quarter."""
        if not name or not name.strip():
            raise ValueError("Quarter name is required")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            ward_id=ward_id,
            quarter_type=quarter_type,
            description=description,
            landmarks=landmarks or [],
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate quarter data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.landmarks, list)
        )

    def __repr__(self) -> str:
        return f"<Quarter {self.name}: {self.quarter_type}>"
