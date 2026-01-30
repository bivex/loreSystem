"""
Inventory Entity

An Inventory represents a player's or container's item storage.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)


@dataclass
class InventorySlot:
    """Represents a single slot in an inventory."""
    item_id: Optional[EntityId]
    quantity: int
    slot_index: int
    
    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if self.slot_index < 0:
            raise ValueError("Slot index cannot be negative")


@dataclass
class Inventory:
    """
    Inventory entity for storing items.
    
    Invariants:
    - Capacity must be positive (0 for unlimited)
    - Quantities must be non-negative
    - Each item occupies a specific slot
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    owner_id: EntityId  # Character or player who owns this inventory
    capacity: int  # Maximum slots (0 = unlimited)
    slots: Dict[int, InventorySlot]  # slot_index -> InventorySlot
    gold: int  # Currency amount
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
        
        if self.capacity < 0:
            raise ValueError("Capacity cannot be negative")
        
        if self.gold < 0:
            raise ValueError("Gold cannot be negative")
        
        # Validate slots don't exceed capacity (if capacity is set)
        if self.capacity > 0 and len(self.slots) > self.capacity:
            raise ValueError(
                f"Inventory has {len(self.slots)} slots but capacity is {self.capacity}"
            )
        
        # Validate slot indices
        for slot_index, slot in self.slots.items():
            if slot.slot_index != slot_index:
                raise ValueError(f"Slot index mismatch: {slot.slot_index} vs {slot_index}")
            
            if self.capacity > 0 and slot_index >= self.capacity:
                raise ValueError(f"Slot index {slot_index} exceeds capacity {self.capacity}")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        owner_id: EntityId,
        capacity: int = 20,
        gold: int = 0,
    ) -> 'Inventory':
        """
        Factory method for creating a new Inventory.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            owner_id=owner_id,
            capacity=capacity,
            slots={},
            gold=gold,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def used_slots(self) -> int:
        """Return number of occupied slots."""
        return len(self.slots)
    
    @property
    def free_slots(self) -> int:
        """Return number of free slots (0 for unlimited)."""
        if self.capacity == 0:
            return 999999  # Effectively unlimited
        return self.capacity - self.used_slots
    
    @property
    def is_full(self) -> bool:
        """Check if inventory is full."""
        if self.capacity == 0:
            return False  # Unlimited capacity
        return self.used_slots >= self.capacity
    
    def add_item(self, item_id: EntityId, quantity: int = 1) -> int:
        """
        Add an item to the inventory.
        
        Returns:
            The slot index where the item was placed.
        
        Raises:
            ValueError: If inventory is full or quantity is invalid.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check if item already exists (stackable items)
        for slot_index, slot in self.slots.items():
            if slot.item_id == item_id:
                # Stack with existing
                object.__setattr__(slot, 'quantity', slot.quantity + quantity)
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return slot_index
        
        # Find first empty slot
        if self.capacity > 0:
            for i in range(self.capacity):
                if i not in self.slots:
                    new_slot = InventorySlot(
                        item_id=item_id,
                        quantity=quantity,
                        slot_index=i
                    )
                    self.slots[i] = new_slot
                    object.__setattr__(self, 'updated_at', Timestamp.now())
                    object.__setattr__(self, 'version', self.version.increment())
                    return i
        else:
            # Unlimited capacity - use next available index
            slot_index = len(self.slots)
            new_slot = InventorySlot(
                item_id=item_id,
                quantity=quantity,
                slot_index=slot_index
            )
            self.slots[slot_index] = new_slot
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
            return slot_index
        
        raise ValueError("Inventory is full")
    
    def remove_item(self, item_id: EntityId, quantity: int = 1) -> bool:
        """
        Remove an item from the inventory.
        
        Returns:
            True if item was removed, False if not found or insufficient quantity.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        for slot_index, slot in list(self.slots.items()):
            if slot.item_id == item_id:
                if slot.quantity < quantity:
                    return False  # Not enough items
                
                new_quantity = slot.quantity - quantity
                if new_quantity == 0:
                    # Remove slot entirely
                    del self.slots[slot_index]
                else:
                    object.__setattr__(slot, 'quantity', new_quantity)
                
                object.__setattr__(self, 'updated_at', Timestamp.now())
                object.__setattr__(self, 'version', self.version.increment())
                return True
        
        return False  # Item not found
    
    def get_item_quantity(self, item_id: EntityId) -> int:
        """Get total quantity of an item in the inventory."""
        total = 0
        for slot in self.slots.values():
            if slot.item_id == item_id:
                total += slot.quantity
        return total
    
    def has_item(self, item_id: EntityId, quantity: int = 1) -> bool:
        """Check if inventory has at least the specified quantity of an item."""
        return self.get_item_quantity(item_id) >= quantity
    
    def add_gold(self, amount: int) -> None:
        """Add gold to the inventory."""
        if amount < 0:
            raise ValueError("Amount must be positive (use remove_gold to subtract)")
        
        object.__setattr__(self, 'gold', self.gold + amount)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_gold(self, amount: int) -> bool:
        """
        Remove gold from the inventory.
        
        Returns:
            True if gold was removed, False if insufficient gold.
        """
        if amount < 0:
            raise ValueError("Amount must be positive (use add_gold to add)")
        
        if self.gold < amount:
            return False
        
        object.__setattr__(self, 'gold', self.gold - amount)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        return True
    
    def set_capacity(self, new_capacity: int) -> None:
        """
        Set new inventory capacity.
        
        Raises:
            ValueError: If new capacity is less than current used slots.
        """
        if new_capacity < 0:
            raise ValueError("Capacity cannot be negative")
        
        if new_capacity > 0 and self.used_slots > new_capacity:
            raise ValueError(
                f"Cannot set capacity to {new_capacity}: {self.used_slots} slots in use"
            )
        
        # Remove slots beyond new capacity
        if new_capacity > 0:
            for slot_index in list(self.slots.keys()):
                if slot_index >= new_capacity:
                    del self.slots[slot_index]
        
        object.__setattr__(self, 'capacity', new_capacity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Inventory({self.used_slots}/{self.capacity if self.capacity > 0 else '∞'} slots, {self.gold} gold)"
    
    def __repr__(self) -> str:
        return (
            f"Inventory(id={self.id}, owner_id={self.owner_id}, "
            f"capacity={self.capacity}, gold={self.gold})"
        )
