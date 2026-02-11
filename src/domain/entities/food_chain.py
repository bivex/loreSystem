"""FoodChain entity for biological systems."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class FoodChain:
    """Represents a food chain or ecosystem."""

    def __init__(
        self,
        id: UUID,
        tenant_id: UUID,
        name: str,
        ecosystem_id: UUID,
        trophic_levels: list,
        producers: list,
        consumers: list,
        decomposers: list,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.name = name
        self.ecosystem_id = ecosystem_id
        self.trophic_levels = trophic_levels
        self.producers = producers
        self.consumers = consumers
        self.decomposers = decomposers
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        name: str,
        ecosystem_id: UUID,
        producers: Optional[list] = None,
        consumers: Optional[list] = None,
        decomposers: Optional[list] = None,
    ) -> "FoodChain":
        """Factory method to create a new food chain."""
        if not name or not name.strip():
            raise ValueError("Food chain name is required")

        return cls(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name.strip(),
            ecosystem_id=ecosystem_id,
            trophic_levels=[],
            producers=producers or [],
            consumers=consumers or [],
            decomposers=decomposers or [],
            is_active=True,
        )

    def validate(self) -> bool:
        """Validate food chain data."""
        return (
            isinstance(self.name, str) and len(self.name) > 0
            and isinstance(self.producers, list)
            and isinstance(self.consumers, list)
            and isinstance(self.decomposers, list)
        )

    def __repr__(self) -> str:
        return f"<FoodChain {self.name}: {len(self.producers)} producers, {len(self.consumers)} consumers>"
