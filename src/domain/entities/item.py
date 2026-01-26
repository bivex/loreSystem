"""
Item Entity

An Item represents a tangible object in the lore world.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    ItemType,
    Rarity,
)


@dataclass
class Item:
    """
    Item entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Version increases monotonically
    - Can optionally be located in a specific Location
    - Level and enhancement stats must be non-negative
    - Can optionally have 3D model and textures for visualization
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    item_type: ItemType
    rarity: Optional[Rarity]
    location_id: Optional[EntityId]  # Location where this item is found
    
    # Item stats (for equipment/weapons)
    level: Optional[int]  # Item level (1-100)
    enhancement: Optional[int]  # Enhancement level (0-20)
    max_enhancement: Optional[int]  # Maximum enhancement level
    base_atk: Optional[int]  # Attack bonus
    base_hp: Optional[int]  # HP bonus
    base_def: Optional[int]  # Defense bonus
    special_stat: Optional[str]  # Special stat name (e.g., "crit_rate")
    special_stat_value: Optional[float]  # Special stat value
    
    # 3D Visualization
    model_3d_id: Optional[EntityId]  # Reference to 3D model for rendering
    texture_ids: Optional[List[EntityId]]  # List of texture IDs for the model
    
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
            raise ValueError("Item name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Item name must be <= 255 characters")
        
        # Validate item stats
        if self.level is not None and (self.level < 1 or self.level > 100):
            raise ValueError("Item level must be between 1-100")
        
        if self.enhancement is not None and self.enhancement < 0:
            raise ValueError("Enhancement cannot be negative")
        
        if self.max_enhancement is not None and self.max_enhancement < 0:
            raise ValueError("Max enhancement cannot be negative")
        
        if self.base_atk is not None and self.base_atk < 0:
            raise ValueError("Base ATK cannot be negative")
        
        if self.base_hp is not None and self.base_hp < 0:
            raise ValueError("Base HP cannot be negative")
        
        if self.base_def is not None and self.base_def < 0:
            raise ValueError("Base DEF cannot be negative")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        item_type: ItemType,
        rarity: Optional[Rarity] = None,
        location_id: Optional[EntityId] = None,
        level: Optional[int] = None,
        enhancement: Optional[int] = None,
        max_enhancement: Optional[int] = None,
        base_atk: Optional[int] = None,
        base_hp: Optional[int] = None,
        base_def: Optional[int] = None,
        special_stat: Optional[str] = None,
        special_stat_value: Optional[float] = None,
        model_3d_id: Optional[EntityId] = None,
        texture_ids: Optional[List[EntityId]] = None,
    ) -> 'Item':
        """
        Factory method for creating a new Item.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            item_type=item_type,
            rarity=rarity,
            location_id=location_id,
            level=level,
            enhancement=enhancement,
            max_enhancement=max_enhancement,
            base_atk=base_atk,
            base_hp=base_hp,
            base_def=base_def,
            special_stat=special_stat,
            special_stat_value=special_stat_value,
            model_3d_id=model_3d_id,
            texture_ids=texture_ids,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update item description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def rename(self, new_name: str) -> None:
        """Rename the item."""
        if self.name == new_name:
            return
        
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Item name cannot be empty")
        
        if len(new_name) > 255:
            raise ValueError("Item name must be <= 255 characters")
        
        object.__setattr__(self, 'name', new_name)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_type(self, new_type: ItemType) -> None:
        """Change item type."""
        if self.item_type == new_type:
            return
        
        object.__setattr__(self, 'item_type', new_type)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_rarity(self, rarity: Optional[Rarity]) -> None:
        """Set item rarity."""
        if self.rarity == rarity:
            return
        
        object.__setattr__(self, 'rarity', rarity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def move_to_location(self, location_id: Optional[EntityId]) -> None:
        """Move item to a different location."""
        if self.location_id == location_id:
            return
        
        object.__setattr__(self, 'location_id', location_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def enhance(self) -> None:
        """
        Enhance the item (increase enhancement level).
        
        Raises:
            InvariantViolation: If item is already at max enhancement or has no enhancement system
        """
        if self.enhancement is None:
            raise InvariantViolation("Item has no enhancement system")
        
        if self.max_enhancement and self.enhancement >= self.max_enhancement:
            raise InvariantViolation("Item is already at max enhancement")
        
        object.__setattr__(self, 'enhancement', self.enhancement + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_level(self, new_level: int) -> None:
        """
        Set item level.
        
        Raises:
            InvariantViolation: If level is invalid
        """
        if new_level < 1 or new_level > 100:
            raise InvariantViolation("Item level must be between 1-100")
        
        if self.level == new_level:
            return
        
        object.__setattr__(self, 'level', new_level)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        rarity_str = f" ({self.rarity.value})" if self.rarity else ""
        level_str = f" Lv{self.level}" if self.level else ""
        enhance_str = f" +{self.enhancement}" if self.enhancement is not None else ""
        return f"Item({self.name}{rarity_str}{level_str}{enhance_str}, {self.item_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Item(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.item_type})"
        )