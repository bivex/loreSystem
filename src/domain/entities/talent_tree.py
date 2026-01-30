"""
TalentTree Entity

A TalentTree represents a branching progression system of talents/skills.
Characters unlock nodes by spending talent points.
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
)
from ..exceptions import InvariantViolation, InvalidState


class TalentNodeType(str, Enum):
    """Type of talent node."""
    PASSIVE = "passive"  # Permanent passive effect
    ACTIVE = "active"  # Active ability
    BOOST = "boost"  # Stat boost
    TRIGGER = "trigger"  # Triggered effect
    ULTIMATE = "ultimate"  # Ultimate ability (capstone)


class TalentTreeType(str, Enum):
    """Type of talent tree."""
    CLASS = "class"  # Class-specific tree
    SPECIALIZATION = "specialization"  # Specialization tree
    RACIAL = "racial"  # Racial tree
    UNIVERSAL = "universal"  # Universal tree for all
    CUSTOM = "custom"  # Custom tree


@dataclass
class TalentNode:
    """A single node in a talent tree."""
    id: str
    name: str
    description: Description
    node_type: TalentNodeType
    tier: int  # Row/level in tree (1-indexed)
    column: int  # Column position in tree
    point_cost: int  # Points required to unlock
    prerequisite_node_ids: List[str]  # IDs of prerequisite nodes
    effects: Optional[dict]  # Effects granted by this node
    icon_id: Optional[str]
    is_unlocked: bool = False


@dataclass
class TalentTree:
    """
    TalentTree entity representing a progression tree.
    
    Invariants:
    - Points spent cannot exceed total points
    - Points spent cannot be negative
    - Version increases monotonically
    - Cannot have empty name
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    character_id: Optional[EntityId]  # None = base template
    name: str
    description: Description
    talent_tree_type: TalentTreeType
    
    # Points
    total_points: int  # Total points available
    points_spent: int  # Points currently spent
    points_available: int  # Points available to spend (computed)
    
    # Nodes
    nodes: List[TalentNode]  # All nodes in the tree
    unlocked_node_ids: List[str]  # IDs of unlocked nodes
    
    # Progression
    max_tier: int  # Maximum tier (row) unlocked
    progress_percentage: float  # Progress percentage (0-100)
    
    # Metadata
    icon_id: Optional[str]
    required_level: int  # Minimum character level to use
    tags: Optional[List[str]]
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
        self._calculate_progress()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Talent tree name cannot be empty")
        
        if self.points_spent < 0:
            raise InvariantViolation("Points spent cannot be negative")
        
        if self.points_spent > self.total_points:
            raise InvariantViolation(
                f"Points spent ({self.points_spent}) cannot exceed total points ({self.total_points})"
            )
        
        if self.max_tier < 0:
            raise InvariantViolation("Max tier cannot be negative")
        
        if self.required_level < 1:
            raise InvariantViolation("Required level must be at least 1")
    
    def _calculate_progress(self) -> None:
        """Calculate progress statistics."""
        object.__setattr__(self, 'points_available', self.total_points - self.points_spent)
        
        if not self.nodes:
            object.__setattr__(self, 'progress_percentage', 0.0)
            return
        
        unlocked_count = sum(1 for node in self.nodes if node.is_unlocked)
        object.__setattr__(self, 'progress_percentage', (unlocked_count / len(self.nodes)) * 100.0)
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        talent_tree_type: TalentTreeType,
        character_id: Optional[EntityId] = None,
        total_points: int = 50,
        points_spent: int = 0,
        nodes: Optional[List[TalentNode]] = None,
        unlocked_node_ids: Optional[List[str]] = None,
        icon_id: Optional[str] = None,
        required_level: int = 1,
        tags: Optional[List[str]] = None,
    ) -> 'TalentTree':
        """
        Factory method for creating a new TalentTree.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            character_id=character_id,
            name=name,
            description=description,
            talent_tree_type=talent_tree_type,
            total_points=total_points,
            points_spent=points_spent,
            points_available=total_points - points_spent,
            nodes=nodes or [],
            unlocked_node_ids=unlocked_node_ids or [],
            max_tier=0,
            progress_percentage=0.0,
            icon_id=icon_id,
            required_level=required_level,
            tags=tags,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def unlock_node(self, node_id: str) -> None:
        """
        Unlock a talent node.
        
        Raises:
            InvalidState: If node doesn't exist or prerequisites not met
            InvariantViolation: If insufficient points
        """
        node = self._find_node(node_id)
        if not node:
            raise InvalidState(f"Node '{node_id}' not found in tree")
        
        if node.is_unlocked:
            return  # Already unlocked
        
        if node.point_cost > self.points_available:
            raise InvariantViolation(
                f"Insufficient points: need {node.point_cost}, have {self.points_available}"
            )
        
        # Check prerequisites
        for prereq_id in node.prerequisite_node_ids:
            if prereq_id not in self.unlocked_node_ids:
                raise InvalidState(
                    f"Prerequisite node '{prereq_id}' not unlocked"
                )
        
        # Unlock the node
        node.is_unlocked = True
        self.unlocked_node_ids.append(node_id)
        object.__setattr__(self, 'points_spent', self.points_spent + node.point_cost)
        
        # Update max tier
        if node.tier > self.max_tier:
            object.__setattr__(self, 'max_tier', node.tier)
        
        self._calculate_progress()
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def lock_node(self, node_id: str) -> None:
        """
        Lock a talent node (refund points).
        
        Raises:
            InvalidState: If node doesn't exist or can't be locked
        """
        node = self._find_node(node_id)
        if not node:
            raise InvalidState(f"Node '{node_id}' not found in tree")
        
        if not node.is_unlocked:
            return  # Already locked
        
        # Check if any dependent nodes are unlocked
        for other_node in self.nodes:
            if node_id in other_node.prerequisite_node_ids and other_node.is_unlocked:
                raise InvalidState(
                    f"Cannot lock node '{node_id}': dependent node '{other_node.id}' is unlocked"
                )
        
        # Lock the node and refund points
        node.is_unlocked = False
        if node_id in self.unlocked_node_ids:
            self.unlocked_node_ids.remove(node_id)
        
        object.__setattr__(self, 'points_spent', self.points_spent - node.point_cost)
        
        # Recalculate max tier
        self._recalculate_max_tier()
        
        self._calculate_progress()
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_total_points(self, amount: int) -> None:
        """Add points to the total pool."""
        if amount <= 0:
            raise InvariantViolation("Points amount must be positive")
        
        object.__setattr__(self, 'total_points', self.total_points + amount)
        self._calculate_progress()
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def _find_node(self, node_id: str) -> Optional[TalentNode]:
        """Find a node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def _recalculate_max_tier(self) -> None:
        """Recalculate maximum unlocked tier."""
        max_tier = 0
        for node in self.nodes:
            if node.is_unlocked and node.tier > max_tier:
                max_tier = node.tier
        object.__setattr__(self, 'max_tier', max_tier)
    
    def can_unlock_node(self, node_id: str) -> bool:
        """Check if a node can be unlocked."""
        node = self._find_node(node_id)
        if not node or node.is_unlocked:
            return False
        
        if node.point_cost > self.points_available:
            return False
        
        for prereq_id in node.prerequisite_node_ids:
            if prereq_id not in self.unlocked_node_ids:
                return False
        
        return True
    
    def get_unlocked_nodes(self) -> List[TalentNode]:
        """Get all unlocked nodes."""
        return [node for node in self.nodes if node.is_unlocked]
    
    def get_unlockable_nodes(self) -> List[TalentNode]:
        """Get nodes that can be unlocked (prereqs met, enough points)."""
        return [node for node in self.nodes if self.can_unlock_node(node.id)]
    
    def is_complete(self) -> bool:
        """Check if all nodes are unlocked."""
        return self.progress_percentage >= 100.0
    
    def __str__(self) -> str:
        return f"TalentTree({self.name}: {self.points_spent}/{self.total_points} pts, {self.progress_percentage:.1f}%)"
    
    def __repr__(self) -> str:
        return (
            f"TalentTree(id={self.id}, name='{self.name}', "
            f"type={self.talent_tree_type.value}, nodes={len(self.nodes)})"
        )
