"""
QuestPrerequisite Entity

A QuestPrerequisite represents conditions that must be met before a quest can be started.
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    PrerequisiteType,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class QuestPrerequisite:
    """
    QuestPrerequisite entity for quest requirements.
    
    Invariants:
    - Must have a valid prerequisite type
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    prerequisite_type: PrerequisiteType
    description: Description
    required_quest_ids: List[EntityId]  # Quests that must be completed
    required_level: Optional[int]  # Minimum level required
    required_item_ids: List[EntityId]  # Items that must be possessed
    required_skill_ids: List[EntityId]  # Skills that must be learned
    required_attribute_values: dict  # Attribute name -> minimum value
    is_flexible: bool  # Can multiple prerequisites satisfy this?
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
        
        if self.required_level is not None and self.required_level < 1:
            raise InvariantViolation("Required level must be >= 1")
        
        # Validate attribute values are positive
        for attr_name, value in self.required_attribute_values.items():
            if not isinstance(value, (int, float)) or value < 0:
                raise InvariantViolation(
                    f"Attribute '{attr_name}' must have non-negative value"
                )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        prerequisite_type: PrerequisiteType,
        description: Description,
        required_quest_ids: Optional[List[EntityId]] = None,
        required_level: Optional[int] = None,
        required_item_ids: Optional[List[EntityId]] = None,
        required_skill_ids: Optional[List[EntityId]] = None,
        required_attribute_values: Optional[dict] = None,
        is_flexible: bool = False,
    ) -> 'QuestPrerequisite':
        """
        Factory method for creating a new QuestPrerequisite.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            prerequisite_type=prerequisite_type,
            description=description,
            required_quest_ids=required_quest_ids or [],
            required_level=required_level,
            required_item_ids=required_item_ids or [],
            required_skill_ids=required_skill_ids or [],
            required_attribute_values=required_attribute_values or {},
            is_flexible=is_flexible,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_required_quest(self, quest_id: EntityId) -> None:
        """Add a quest that must be completed."""
        if quest_id in self.required_quest_ids:
            return
        
        self.required_quest_ids.append(quest_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_required_item(self, item_id: EntityId) -> None:
        """Add an item that must be possessed."""
        if item_id in self.required_item_ids:
            return
        
        self.required_item_ids.append(item_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_required_skill(self, skill_id: EntityId) -> None:
        """Add a skill that must be learned."""
        if skill_id in self.required_skill_ids:
            return
        
        self.required_skill_ids.append(skill_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_required_attribute(self, attribute_name: str, value: float) -> None:
        """Set a required attribute value."""
        if not isinstance(value, (int, float)) or value < 0:
            raise InvariantViolation("Attribute value must be non-negative")
        
        self.required_attribute_values[attribute_name] = value
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_required_attribute(self, attribute_name: str) -> None:
        """Remove a required attribute."""
        if attribute_name not in self.required_attribute_values:
            raise InvalidState(f"Attribute '{attribute_name}' not found in prerequisites")
        
        del self.required_attribute_values[attribute_name]
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def has_requirements(self) -> bool:
        """Check if this prerequisite has any requirements set."""
        return (
            bool(self.required_quest_ids)
            or bool(self.required_item_ids)
            or bool(self.required_skill_ids)
            or bool(self.required_attribute_values)
            or self.required_level is not None
        )
    
    def __str__(self) -> str:
        return f"QuestPrerequisite({self.prerequisite_type})"
    
    def __repr__(self) -> str:
        return (
            f"QuestPrerequisite(id={self.id}, world_id={self.world_id}, "
            f"type={self.prerequisite_type})"
        )
