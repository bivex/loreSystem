"""Title Entity

A Title represents an honorific or profile label
that can be granted within a world.
"""

from dataclasses import dataclass, field
from typing import Optional

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


@dataclass
class Title:
    """A profile or honorific title available in a world."""

    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    created_at: Timestamp
    updated_at: Timestamp
    id: Optional[EntityId] = None
    version: Version = field(default_factory=Version)

    def __post_init__(self):
        self._validate_invariants()

    def _validate_invariants(self):
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Title name cannot be empty")

        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: str,
    ) -> "Title":
        """Factory method to create a new Title."""
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            world_id=world_id,
            name=name.strip(),
            description=Description(description),
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def __str__(self) -> str:
        return f"Title({self.name})"

    def __repr__(self) -> str:
        return f"<Title {self.name}>"