"""
QuestObjective Entity

A QuestObjective represents a specific goal within a quest that must be achieved.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    ObjectiveType,
    ObjectiveStatus,
)
from ..exceptions import InvariantViolation, InvalidState


@dataclass
class QuestObjective:
    """
    QuestObjective entity representing a single quest goal.
    
    Invariants:
    - Must have a valid objective type
    - Target quantity must be positive if set
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    quest_node_id: EntityId
    objective_type: ObjectiveType
    description: Description
    target_type: Optional[str]  # Type of target (entity, item, location, etc.)
    target_id: Optional[EntityId]  # Specific target entity ID
    target_quantity: int  # How many of the target are needed
    current_progress: int  # Current progress towards goal
    status: ObjectiveStatus
    is_optional: bool  # Is this objective optional?
    is_hidden: bool  # Is this objective hidden from the player?
    order_index: int  # Display order in quest log
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.target_quantity <= 0:
            raise InvariantViolation("Target quantity must be positive")
        
        if self.current_progress < 0:
            raise InvariantViolation("Current progress cannot be negative")
        
        if self.current_progress > self.target_quantity:
            raise InvariantViolation("Current progress cannot exceed target quantity")
        
        if self.order_index < 0:
            raise InvariantViolation("Order index cannot be negative")
        
        if self.version.value < 1:
            raise InvalidState("Version must be >= 1")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        quest_node_id: EntityId,
        objective_type: ObjectiveType,
        description: Description,
        target_type: Optional[str] = None,
        target_id: Optional[EntityId] = None,
        target_quantity: int = 1,
        is_optional: bool = False,
        is_hidden: bool = False,
        order_index: int = 0,
    ) -> 'QuestObjective':
        """
        Factory method for creating a new QuestObjective.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            quest_node_id=quest_node_id,
            objective_type=objective_type,
            description=description,
            target_type=target_type,
            target_id=target_id,
            target_quantity=target_quantity,
            current_progress=0,
            status=ObjectiveStatus.INCOMPLETE,
            is_optional=is_optional,
            is_hidden=is_hidden,
            order_index=order_index,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_progress(self, amount: int = 1) -> None:
        """
        Update the progress towards completing this objective.
        
        Args:
            amount: Amount to increment progress by (default: 1)
        """
        if amount < 0:
            raise InvariantViolation("Progress increment cannot be negative")
        
        new_progress = self.current_progress + amount
        
        if new_progress > self.target_quantity:
            new_progress = self.target_quantity
        
        object.__setattr__(self, 'current_progress', new_progress)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        
        # Check if objective is complete
        if self.current_progress >= self.target_quantity:
            if self.status == ObjectiveStatus.INCOMPLETE:
                object.__setattr__(self, 'status', ObjectiveStatus.COMPLETED)
    
    def complete(self) -> 'QuestObjective':
        """Mark this objective as completed."""
        object.__setattr__(self, 'current_progress', self.target_quantity)
        return QuestObjective(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            quest_node_id=self.quest_node_id,
            objective_type=self.objective_type,
            description=self.description,
            target_type=self.target_type,
            target_id=self.target_id,
            target_quantity=self.target_quantity,
            current_progress=self.target_quantity,
            status=ObjectiveStatus.COMPLETED,
            is_optional=self.is_optional,
            is_hidden=self.is_hidden,
            order_index=self.order_index,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment(),
        )
    
    def reset(self) -> 'QuestObjective':
        """Reset this objective's progress."""
        return QuestObjective(
            id=self.id,
            tenant_id=self.tenant_id,
            world_id=self.world_id,
            quest_node_id=self.quest_node_id,
            objective_type=self.objective_type,
            description=self.description,
            target_type=self.target_type,
            target_id=self.target_id,
            target_quantity=self.target_quantity,
            current_progress=0,
            status=ObjectiveStatus.INCOMPLETE,
            is_optional=self.is_optional,
            is_hidden=self.is_hidden,
            order_index=self.order_index,
            created_at=self.created_at,
            updated_at=Timestamp.now(),
            version=self.version.increment(),
        )
    
    def is_complete(self) -> bool:
        """Check if objective is complete."""
        return self.current_progress >= self.target_quantity
    
    def progress_percentage(self) -> float:
        """Get progress as a percentage (0-100)."""
        if self.target_quantity == 0:
            return 100.0
        return (self.current_progress / self.target_quantity) * 100
    
    def remaining(self) -> int:
        """Get remaining amount to complete."""
        return max(0, self.target_quantity - self.current_progress)
    
    def __str__(self) -> str:
        return f"QuestObjective({self.objective_type}: {self.current_progress}/{self.target_quantity})"
    
    def __repr__(self) -> str:
        return (
            f"QuestObjective(id={self.id}, quest_node_id={self.quest_node_id}, "
            f"type={self.objective_type}, status={self.status})"
        )
