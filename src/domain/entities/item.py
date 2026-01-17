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
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    item_type: ItemType
    rarity: Optional[Rarity]
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
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        item_type: ItemType,
        rarity: Optional[Rarity] = None,
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
    
    def __str__(self) -> str:
        rarity_str = f" ({self.rarity.value})" if self.rarity else ""
        return f"Item({self.name}{rarity_str}, {self.item_type.value})"
    
    def __repr__(self) -> str:
        return (
            f"Item(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', type={self.item_type})"
        )