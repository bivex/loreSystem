"""LootTableWeight Entity

A LootTableWeight defines the probability distribution
of items from loot tables. Essential for rewarding players,
balance economy, and creating rare item excitement.
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
class LootTableWeight:
    """Loot table probability distribution for item drops."""
    
    tenant_id: TenantId
    id: Optional[EntityId] = None
    name: str
    description: Description
    loot_table_id: EntityId  # Reference to parent LootTable
    item_type: str  # "weapon", "armor", "currency", "material"
    rarity: str  # "common", "uncommon", "rare", "epic", "legendary"
    weight: float  # 0.0 to 1.0 (normalized probability)
    min_level: int = 1  # Minimum level required to get this item
    is_unique: bool = False  # Whether this item appears only once per table roll
    conditions: List[str] = field(default_factory=list)  # Special conditions
    created_at: Timestamp
    updated_at: Timestamp
    version: Version = field(default_factory=Version)
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("LootTableWeight name cannot be empty")
        
        if not (0.0 <= self.weight <= 1.0):
            raise InvariantViolation("Weight must be between 0.0 and 1.0")
        
        if self.min_level < 1:
            raise InvariantViolation("Min level must be >= 1")
        
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        loot_table_id: EntityId,
        item_type: str,
        rarity: str,
        weight: float,
        min_level: int = 1,
        is_unique: bool = False,
        conditions: Optional[List[str]] = None,
    ) -> "LootTableWeight":
        """Factory method to create a new LootTableWeight."""
        now = Timestamp.now()
        
        return cls(
            tenant_id=tenant_id,
            name=name.strip(),
            description=Description(f"Weight for {rarity} {item_type} in loot table"),
            loot_table_id=loot_table_id,
            item_type=item_type,
            rarity=rarity,
            weight=weight,
            min_level=min_level,
            is_unique=is_unique,
            conditions=conditions or [],
            created_at=now,
            updated_at=now,
            version=Version(1, 0, 0),
        )
    
    def adjust_weight(self, new_weight: float) -> "LootTableWeight":
        """Adjust item weight."""
        if not (0.0 <= new_weight <= 1.0):
            raise InvariantViolation("Weight must be between 0.0 and 1.0")
        
        self.weight = new_weight
        self.updated_at = Timestamp.now()
        self.version = self.version.increment_minor()
        return self
    
    def check_condition(self, condition: str, context: Dict) -> bool:
        """Check if condition is met based on context."""
        # Simplified condition checking
        for c in self.conditions:
            # Simple string match (in real implementation, would parse condition)
            if condition.lower() in str(context).lower():
                return True
        return False
    
    def __str__(self) -> str:
        return f"LootTableWeight({self.name}, {self.rarity}, weight={self.weight:.2f})"
    
    def __repr__(self) -> str:
        return (
            f"<LootTableWeight id={self.id}, name='{self.name}', "
            f"type={self.item_type}, rarity={self.rarity}, weight={self.weight:.2f}>"
        )
