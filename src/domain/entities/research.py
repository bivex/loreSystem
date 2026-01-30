"""
Research Entity

Research represents scientific or magical studies that unlock new knowledge, technologies, or abilities.
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


class ResearchStatus(str, Enum):
    """Status of research progress."""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchCategory(str, Enum):
    """Categories of research."""
    TECHNOLOGY = "technology"
    MAGIC = "magic"
    ALCHEMY = "alchemy"
    ENGINEERING = "engineering"
    BIOLOGY = "biology"
    ASTRONOMY = "astronomy"
    HISTORY = "history"
    LINGUISTICS = "linguistics"
    MILITARY = "military"
    ECONOMICS = "economics"
    OTHER = "other"


@dataclass
class ResearchPrerequisite:
    """Prerequisite for research."""
    type: str  # "research", "level", "resource", "item"
    id: Optional[EntityId]  # ID of prerequisite entity
    value: str  # Value or name
    quantity: Optional[int]  # If applicable
    
    def __post_init__(self):
        if not self.type or len(self.type.strip()) == 0:
            raise ValueError("Prerequisite type cannot be empty")
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Prerequisite value cannot be empty")


@dataclass
class Research:
    """
    Research entity for tracking studies and discoveries.
    
    Invariants:
    - Name cannot be empty
    - Category must be set
    - Research time must be non-negative
    - Must belong to a world
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    category: ResearchCategory
    status: ResearchStatus
    rarity: Rarity
    
    # Research progress
    research_time: int  # Seconds to complete
    progress: float  # 0.0 - 1.0
    completed_at: Optional[Timestamp]
    
    # Prerequisites
    prerequisites: List[ResearchPrerequisite]
    required_level: Optional[int]
    
    # Rewards and outcomes
    unlocks: List[EntityId]  # Items, blueprints, abilities unlocked
    grants_stat_bonus: Optional[dict]  # Stat name -> bonus amount
    
    # Resource costs
    cost_resources: dict  # Resource ID -> quantity
    cost_gold: int
    
    # Research location and actors
    location_id: Optional[EntityId]  # Where research can be done
    researcher_ids: List[EntityId]  # NPCs or factions that can research
    
    # Dependencies
    parent_research_id: Optional[EntityId]  # Required parent research
    child_research_ids: List[EntityId]  # Researches this unlocks
    
    # Discoverability
    is_hidden: bool
    auto_unlock: bool
    
    # Visual representation
    icon_id: Optional[EntityId]
    
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
            raise ValueError("Research name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Research name must be <= 255 characters")
        
        if self.research_time < 0:
            raise ValueError("Research time cannot be negative")
        
        if self.progress < 0.0 or self.progress > 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        if self.cost_gold < 0:
            raise ValueError("Cost gold cannot be negative")
        
        if self.required_level is not None and self.required_level < 1:
            raise ValueError("Required level must be positive")
        
        if self.status == ResearchStatus.COMPLETED and self.completed_at is None:
            raise ValueError("Completed research must have completed_at timestamp")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        category: ResearchCategory,
        rarity: Rarity,
        research_time: int = 0,
        prerequisites: Optional[List[ResearchPrerequisite]] = None,
        required_level: Optional[int] = None,
        unlocks: Optional[List[EntityId]] = None,
        grants_stat_bonus: Optional[dict] = None,
        cost_resources: Optional[dict] = None,
        cost_gold: int = 0,
        location_id: Optional[EntityId] = None,
        researcher_ids: Optional[List[EntityId]] = None,
        parent_research_id: Optional[EntityId] = None,
        is_hidden: bool = False,
        auto_unlock: bool = False,
        icon_id: Optional[EntityId] = None,
    ) -> 'Research':
        """
        Factory method for creating a new Research.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            category=category,
            status=ResearchStatus.LOCKED,
            rarity=rarity,
            research_time=research_time,
            progress=0.0,
            completed_at=None,
            prerequisites=prerequisites or [],
            required_level=required_level,
            unlocks=unlocks or [],
            grants_stat_bonus=grants_stat_bonus,
            cost_resources=cost_resources or {},
            cost_gold=cost_gold,
            location_id=location_id,
            researcher_ids=researcher_ids or [],
            parent_research_id=parent_research_id,
            child_research_ids=[],
            is_hidden=is_hidden,
            auto_unlock=auto_unlock,
            icon_id=icon_id,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def is_completed(self) -> bool:
        """Check if research is completed."""
        return self.status == ResearchStatus.COMPLETED
    
    @property
    def is_available(self) -> bool:
        """Check if research is available to start."""
        return self.status == ResearchStatus.AVAILABLE
    
    @property
    def in_progress(self) -> bool:
        """Check if research is currently in progress."""
        return self.status == ResearchStatus.IN_PROGRESS
    
    @property
    def has_parent(self) -> bool:
        """Check if research has a parent dependency."""
        return self.parent_research_id is not None
    
    def start_research(self) -> None:
        """Start the research."""
        if self.status != ResearchStatus.AVAILABLE:
            raise ValueError("Can only start available research")
        
        object.__setattr__(self, 'status', ResearchStatus.IN_PROGRESS)
        object.__setattr__(self, 'progress', 0.0)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def complete(self) -> None:
        """Mark research as completed."""
        if self.status != ResearchStatus.IN_PROGRESS:
            raise ValueError("Can only complete in-progress research")
        
        now = Timestamp.now()
        object.__setattr__(self, 'status', ResearchStatus.COMPLETED)
        object.__setattr__(self, 'progress', 1.0)
        object.__setattr__(self, 'completed_at', now)
        object.__setattr__(self, 'updated_at', now)
        object.__setattr__(self, 'version', self.version.increment())
    
    def fail(self) -> None:
        """Mark research as failed."""
        if self.status != ResearchStatus.IN_PROGRESS:
            raise ValueError("Can only fail in-progress research")
        
        object.__setattr__(self, 'status', ResearchStatus.FAILED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def make_available(self) -> None:
        """Make research available to start."""
        if self.status != ResearchStatus.LOCKED:
            raise ValueError("Can only make locked research available")
        
        object.__setattr__(self, 'status', ResearchStatus.AVAILABLE)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_progress(self, amount: float) -> None:
        """Update research progress."""
        if self.status != ResearchStatus.IN_PROGRESS:
            raise ValueError("Can only update progress of in-progress research")
        
        new_progress = self.progress + amount
        new_progress = max(0.0, min(1.0, new_progress))
        
        object.__setattr__(self, 'progress', new_progress)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        
        # Auto-complete if progress reaches 100%
        if new_progress >= 1.0:
            self.complete()
    
    def add_unlock(self, entity_id: EntityId) -> None:
        """Add an entity that this research unlocks."""
        if entity_id not in self.unlocks:
            self.unlocks.append(entity_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def remove_unlock(self, entity_id: EntityId) -> bool:
        """Remove an unlocked entity."""
        if entity_id in self.unlocks:
            self.unlocks.remove(entity_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
            return True
        return False
    
    def add_prerequisite(self, prerequisite: ResearchPrerequisite) -> None:
        """Add a prerequisite."""
        self.prerequisites.append(prerequisite)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def can_research(self, player_level: int, completed_research: set) -> bool:
        """Check if player can start this research."""
        if self.status != ResearchStatus.AVAILABLE:
            return False
        
        if self.required_level is not None and player_level < self.required_level:
            return False
        
        if self.parent_research_id is not None and self.parent_research_id not in completed_research:
            return False
        
        return True
    
    def __str__(self) -> str:
        return f"Research({self.name}, {self.category.value}, {self.status.value})"
    
    def __repr__(self) -> str:
        return (
            f"Research(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', category={self.category}, status={self.status})"
        )
