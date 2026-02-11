"""
Prototype Entity

Prototype represents early versions, experimental builds, or test versions of items, weapons, or technologies.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    Rarity,
)


class PrototypeStatus(str, Enum):
    """Status of prototype development."""
    DESIGN = "design"
    CONSTRUCTION = "construction"
    TESTING = "testing"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCRAPPED = "scrapped"


class PrototypeCategory(str, Enum):
    """Categories of prototypes."""
    WEAPON = "weapon"
    ARMOR = "armor"
    VEHICLE = "vehicle"
    MACHINE = "machine"
    DEVICE = "device"
    STRUCTURE = "structure"
    MATERIAL = "material"
    OTHER = "other"


@dataclass
class Prototype:
    """
    Prototype entity for tracking experimental builds and test versions.
    
    Invariants:
    - Name cannot be empty
    - Category must be set
    - Must belong to a world
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    category: PrototypeCategory
    status: PrototypeStatus
    rarity: Rarity
    
    # Base reference
    base_item_id: Optional[EntityId]  # The final item this is a prototype of
    final_product_name: Optional[str]
    
    # Creator
    creator_id: Optional[EntityId]  # Character who created prototype
    laboratory_id: Optional[EntityId]  # Where it was created
    
    # Development progress
    progress: float  # 0.0 - 1.0
    build_cost_gold: int
    build_cost_resources: dict  # Resource ID -> quantity
    
    # Testing
    test_count: int
    success_count: int
    failure_count: int
    
    # Performance metrics (relative to base item)
    damage_modifier: float  # 1.0 = same as base
    durability_modifier: float
    efficiency_modifier: float
    cost_modifier: float  # Higher = more expensive to produce
    
    # Known issues
    known_issues: List[str]
    failure_modes: List[str]
    
    # Iteration
    iteration_number: int  # Which version this is
    parent_prototype_id: Optional[EntityId]  # Previous iteration
    
    # Features and improvements
    new_features: List[str]
    removed_features: List[str]
    
    # Approval process
    reviewer_ids: List[EntityId]  # Characters who reviewed it
    approval_notes: List[str]
    approved_by_id: Optional[EntityId]
    
    # Visuals
    icon_id: Optional[EntityId]
    model_id: Optional[EntityId]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Prototype name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Prototype name must be <= 255 characters")
        
        if self.progress < 0.0 or self.progress > 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        if self.build_cost_gold < 0:
            raise ValueError("Build cost gold cannot be negative")
        
        if self.test_count < 0:
            raise ValueError("Test count cannot be negative")
        
        if self.success_count < 0:
            raise ValueError("Success count cannot be negative")
        
        if self.failure_count < 0:
            raise ValueError("Failure count cannot be negative")
        
        if self.damage_modifier < 0:
            raise ValueError("Damage modifier cannot be negative")
        
        if self.durability_modifier < 0:
            raise ValueError("Durability modifier cannot be negative")
        
        if self.efficiency_modifier < 0:
            raise ValueError("Efficiency modifier cannot be negative")
        
        if self.cost_modifier < 0:
            raise ValueError("Cost modifier cannot be negative")
        
        if self.iteration_number < 1:
            raise ValueError("Iteration number must be >= 1")
        
        if self.status == PrototypeStatus.APPROVED and self.approved_by_id is None:
            raise ValueError("Approved prototype must have approved_by_id")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        category: PrototypeCategory,
        rarity: Rarity,
        base_item_id: Optional[EntityId] = None,
        creator_id: Optional[EntityId] = None,
        laboratory_id: Optional[EntityId] = None,
        build_cost_gold: int = 0,
        build_cost_resources: Optional[dict] = None,
        damage_modifier: float = 1.0,
        durability_modifier: float = 1.0,
        efficiency_modifier: float = 1.0,
        cost_modifier: float = 1.0,
        iteration_number: int = 1,
        parent_prototype_id: Optional[EntityId] = None,
        icon_id: Optional[EntityId] = None,
        model_id: Optional[EntityId] = None,
    ) -> 'Prototype':
        """
        Factory method for creating a new Prototype.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            category=category,
            status=PrototypeStatus.DESIGN,
            rarity=rarity,
            base_item_id=base_item_id,
            final_product_name=None,
            creator_id=creator_id,
            laboratory_id=laboratory_id,
            progress=0.0,
            build_cost_gold=build_cost_gold,
            build_cost_resources=build_cost_resources or {},
            test_count=0,
            success_count=0,
            failure_count=0,
            damage_modifier=damage_modifier,
            durability_modifier=durability_modifier,
            efficiency_modifier=efficiency_modifier,
            cost_modifier=cost_modifier,
            known_issues=[],
            failure_modes=[],
            iteration_number=iteration_number,
            parent_prototype_id=parent_prototype_id,
            new_features=[],
            removed_features=[],
            reviewer_ids=[],
            approval_notes=[],
            approved_by_id=None,
            icon_id=icon_id,
            model_id=model_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if prototype is complete (progress >= 1.0)."""
        return self.progress >= 1.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of tests."""
        if self.test_count == 0:
            return 0.0
        return self.success_count / self.test_count
    
    def start_construction(self) -> None:
        """Begin prototype construction."""
        if self.status != PrototypeStatus.DESIGN:
            raise ValueError("Can only start construction from design status")
        
        object.__setattr__(self, 'status', PrototypeStatus.CONSTRUCTION)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def begin_testing(self) -> None:
        """Begin prototype testing phase."""
        if self.status != PrototypeStatus.CONSTRUCTION:
            raise ValueError("Can only begin testing from construction status")
        
        object.__setattr__(self, 'status', PrototypeStatus.TESTING)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def record_test(self, success: bool, notes: Optional[str] = None) -> None:
        """Record a test result."""
        if self.status != PrototypeStatus.TESTING:
            raise ValueError("Can only record tests during testing phase")
        
        object.__setattr__(self, 'test_count', self.test_count + 1)
        
        if success:
            object.__setattr__(self, 'success_count', self.success_count + 1)
        else:
            object.__setattr__(self, 'failure_count', self.failure_count + 1)
            if notes:
                self.failure_modes.append(notes)
        
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def approve(self, reviewer_id: EntityId, notes: Optional[str] = None) -> None:
        """Approve the prototype."""
        if self.status != PrototypeStatus.TESTING:
            raise ValueError("Can only approve prototypes in testing phase")
        
        if reviewer_id not in self.reviewer_ids:
            self.reviewer_ids.append(reviewer_id)
        
        if notes:
            self.approval_notes.append(notes)
        
        object.__setattr__(self, 'status', PrototypeStatus.APPROVED)
        object.__setattr__(self, 'approved_by_id', reviewer_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def reject(self, reviewer_id: EntityId, reason: Optional[str] = None) -> None:
        """Reject the prototype."""
        if self.status == PrototypeStatus.REJECTED:
            return
        
        if reviewer_id not in self.reviewer_ids:
            self.reviewer_ids.append(reviewer_id)
        
        if reason:
            self.approval_notes.append(reason)
        
        object.__setattr__(self, 'status', PrototypeStatus.REJECTED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def scrap(self) -> None:
        """Scrap the prototype."""
        if self.status == PrototypeStatus.SCRAPPED:
            return
        
        object.__setattr__(self, 'status', PrototypeStatus.SCRAPPED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_progress(self, amount: float) -> None:
        """Update construction progress."""
        if self.status != PrototypeStatus.CONSTRUCTION:
            raise ValueError("Can only update progress during construction")
        
        new_progress = self.progress + amount
        new_progress = max(0.0, min(1.0, new_progress))
        
        object.__setattr__(self, 'progress', new_progress)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_known_issue(self, issue: str) -> None:
        """Add a known issue."""
        if issue and len(issue.strip()) > 0:
            self.known_issues.append(issue)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def add_feature(self, feature: str) -> None:
        """Add a new feature."""
        if feature and len(feature.strip()) > 0:
            self.new_features.append(feature)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def add_removed_feature(self, feature: str) -> None:
        """Add a removed feature."""
        if feature and len(feature.strip()) > 0:
            self.removed_features.append(feature)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def set_final_product_name(self, name: str) -> None:
        """Set the name of the final product."""
        if not name or len(name.strip()) == 0:
            raise ValueError("Final product name cannot be empty")
        
        object.__setattr__(self, 'final_product_name', name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Prototype({self.name}, iteration {self.iteration_number}, {self.status.value})"
    
    def __repr__(self) -> str:
        return (
            f"Prototype(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', category={self.category}, status={self.status})"
        )
