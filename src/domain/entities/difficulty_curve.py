"""DifficultyCurve Entity

A DifficultyCurve defines how game difficulty scales
through progression. Critical for player retention, balancing
learning curves, and difficulty settings.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class DifficultyCurve:
    """Difficulty progression curve for player experience scaling."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str  # "Linear", "Exponential", "Logarithmic"
    description: Description
    curve_type: str  # "linear", "exponential", "logarithmic", "sigmoid"
    base_level: int = 1  # Starting level
    max_level: int = 100  # Level cap
    level_xp_requirement: List[int]  # XP needed per level
    scaling_factor: float = 1.0  # Multiplier for overall difficulty
    level_time_minutes: List[int]  # Estimated time per level
    player_count_tiers: Dict[int, int] = field(default_factory=dict)  # Level -> player count
    is_adaptive: bool = False  # Whether curve adapts to player
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Difficulty curve name cannot be empty")
        
        if self.curve_type not in ["linear", "exponential", "logarithmic", "sigmoid"]:
            raise InvariantViolation("Invalid curve type")
        
        if len(self.level_xp_requirement) != self.max_level:
            raise InvariantViolation("XP requirement list must match max_level")
        
        if self.base_level < 1:
            raise InvariantViolation("Base level must be >= 1")
        
        if self.scaling_factor <= 0:
            raise InvariantViolation("Scaling factor must be positive")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: str,
        curve_type: str = "linear",
        base_level: int = 1,
        max_level: int = 100,
        xp_multiplier: float = 1.0,
        is_adaptive: bool = False,
    ) -> "DifficultyCurve":
        """Factory method to create a new DifficultyCurve."""
        # Generate level XP requirements based on curve type
        xp_reqs = []
        if curve_type == "linear":
            base_xp = 100
            for level in range(1, max_level + 1):
                xp = int(base_xp * level * xp_multiplier)
                xp_reqs.append(xp)
        elif curve_type == "exponential":
            base_xp = 100
            for level in range(1, max_level + 1):
                xp = int(base_xp * (1.1 ** level) * xp_multiplier)
                xp_reqs.append(xp)
        elif curve_type == "logarithmic":
            base_xp = 10000
            for level in range(1, max_level + 1):
                xp = int(base_xp * (1 / (level + 1)) * xp_multiplier)
                xp_reqs.append(xp)
        elif curve_type == "sigmoid":
            base_xp = 10000
            for level in range(1, max_level + 1):
                xp = int(base_xp / (1 + (level / 10) ** 2) * xp_multiplier)
                xp_reqs.append(xp)
        else:
            # Default to linear
            xp_reqs = [int(100 * l * xp_multiplier) for l in range(1, max_level + 1)]
        
        # Generate level time estimates
        base_time = 30  # 30 minutes for level 1
        time_estimates = []
        for level in range(1, max_level + 1):
            time = int(base_time * (1 + (level * 0.1) * xp_multiplier))
            time_estimates.append(time)
        
        now = Timestamp.now()
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            description=Description(description),
            curve_type=curve_type,
            base_level=base_level,
            max_level=max_level,
            level_xp_requirement=xp_reqs,
            scaling_factor=1.0,
            level_time_minutes=time_estimates,
            player_count_tiers={},
            is_adaptive=is_adaptive,
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def get_xp_for_level(self, level: int) -> int:
        """Get XP required for a specific level."""
        if level < 1 or level > self.max_level:
            raise InvariantViolation(f"Level must be between 1 and {self.max_level}")
        return self.level_xp_requirement[level - 1]
    
    def get_time_for_level(self, level: int) -> int:
        """Get estimated time (minutes) for a specific level."""
        if level < 1 or level > self.max_level:
            raise InvariantViolation(f"Level must be between 1 and {self.max_level}")
        return self.level_time_minutes[level - 1]
    
    def adjust_difficulty(self, multiplier: float) -> "DifficultyCurve":
        """Adjust difficulty curve by multiplier."""
        if multiplier <= 0:
            raise InvariantViolation("Multiplier must be positive")
        
        old_xp = self.level_xp_requirement[:]
        new_xp = [int(xp * multiplier) for xp in old_xp]
        self.level_xp_requirement = new_xp
        self.scaling_factor *= multiplier
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_minor()
        return self
    
    def add_level_tier(self, level: int, player_count: int) -> None:
        """Add a player count tier for a specific level."""
        if level < 1 or level > self.max_level:
            raise InvariantViolation(f"Level must be between 1 and {self.max_level}")
        self.player_count_tiers[level] = player_count
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_patch()
    
    def get_difficulty_at_level(self, level: int) -> float:
        """Get numeric difficulty rating at a specific level."""
        if level < 1 or level > self.max_level:
            raise InvariantViolation(f"Level must be between 1 and {self.max_level}")
        return (level / self.max_level) * self.scaling_factor
    
    def __str__(self) -> str:
        return f"DifficultyCurve({self.name}, type={self.curve_type}, levels=1-{self.max_level})"
    
    def __repr__(self) -> str:
        return f"<DifficultyCurve {self.name}: {self.curve_type} curve, {self.base_level}-{self.max_level} levels>"
