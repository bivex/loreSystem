"""FlashForward entity for narrative glimpses of future events."""

from dataclasses import dataclass
from typing import Optional

from ..exceptions import InvariantViolation
from ..value_objects.common import Description, EntityId, TenantId, Timestamp, Version


@dataclass
class FlashForward:
    """Narrative device representing a brief glimpse of a possible future."""

    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Optional[Description]
    hinted_event_id: Optional[EntityId]
    trigger_scene_id: Optional[EntityId]
    clarity_level: str
    is_prophetic: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version

    def __post_init__(self):
        self._validate_invariants()

    def _validate_invariants(self):
        if not self.name or not self.name.strip():
            raise InvariantViolation("FlashForward name cannot be empty")
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation("Updated timestamp must be >= created timestamp")
        if not self.clarity_level or not self.clarity_level.strip():
            raise InvariantViolation("Clarity level cannot be empty")

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Optional[Description] = None,
        hinted_event_id: Optional[EntityId] = None,
        trigger_scene_id: Optional[EntityId] = None,
        clarity_level: str = "symbolic",
        is_prophetic: bool = True,
    ) -> "FlashForward":
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            hinted_event_id=hinted_event_id,
            trigger_scene_id=trigger_scene_id,
            clarity_level=clarity_level,
            is_prophetic=is_prophetic,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )

    def update_details(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[Description] = None,
        hinted_event_id: Optional[EntityId] = None,
        trigger_scene_id: Optional[EntityId] = None,
        clarity_level: Optional[str] = None,
        is_prophetic: Optional[bool] = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if hinted_event_id is not None:
            self.hinted_event_id = hinted_event_id
        if trigger_scene_id is not None:
            self.trigger_scene_id = trigger_scene_id
        if clarity_level is not None:
            self.clarity_level = clarity_level
        if is_prophetic is not None:
            self.is_prophetic = is_prophetic
        self.updated_at = Timestamp.now()
        self.version = self.version.increment()
        self._validate_invariants()

