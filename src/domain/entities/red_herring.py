"""RedHerring entity for misleading narrative clues."""

from dataclasses import dataclass
from typing import Optional

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


@dataclass
class RedHerring:
    """Narrative clue that intentionally misdirects player expectations."""

    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: Optional[EntityId]
    name: str
    description: Optional[Description]
    source_scene_id: Optional[EntityId]
    misdirects_from_id: Optional[EntityId]
    is_revealed_false: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version

    def __post_init__(self):
        self._validate_invariants()

    def _validate_invariants(self):
        if not self.name or not self.name.strip():
            raise InvariantViolation("RedHerring name cannot be empty")
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Optional[Description] = None,
        world_id: Optional[EntityId] = None,
        source_scene_id: Optional[EntityId] = None,
        misdirects_from_id: Optional[EntityId] = None,
        is_revealed_false: bool = False,
    ) -> "RedHerring":
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            source_scene_id=source_scene_id,
            misdirects_from_id=misdirects_from_id,
            is_revealed_false=is_revealed_false,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def reveal_false_lead(self) -> None:
        if self.is_revealed_false:
            return
        self.is_revealed_false = True
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()

    def update_details(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[Description] = None,
        source_scene_id: Optional[EntityId] = None,
        misdirects_from_id: Optional[EntityId] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if source_scene_id is not None:
            self.source_scene_id = source_scene_id
        if misdirects_from_id is not None:
            self.misdirects_from_id = misdirects_from_id
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()
        self._validate_invariants()

