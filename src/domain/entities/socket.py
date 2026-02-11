"""
Socket Entity

A Socket represents a slot on an item where runes or gems can be inserted.
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


class SocketType(str, Enum):
    """Types of sockets."""
    SQUARE = "square"  # Red gems
    TRIANGLE = "triangle"  # Green gems
    CIRCLE = "circle"  # Blue gems
    STAR = "star"  # Purple gems
    HEXAGON = "hexagon"  # Yellow gems
    DIAMOND = "diamond"  # White gems
    UNIVERSAL = "universal"  # Any gem
    RUNE = "rune"  # For runes
    GLYPH = "glyph"  # For glyphs
    SPECIAL = "special"  # Special items only


class SocketShape(str, Enum):
    """Visual shapes for sockets."""
    ROUND = "round"
    SQUARE = "square"
    TRIANGULAR = "triangular"
    HEXAGONAL = "hexagonal"
    OCTAGONAL = "octagonal"
    DIAMOND_SHAPED = "diamond_shaped"
    STAR_SHAPED = "star_shaped"
    CROSS = "cross"
    CRYSTAL = "crystal"


@dataclass
class Socket:
    """
    Socket entity for gem and rune slots on items.
    
    Invariants:
    - Socket type must be set
    - Socket shape must be set
    - Slot index must be non-negative
    - Must belong to an item
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    item_id: EntityId  # Item this socket belongs to
    socket_type: SocketType
    socket_shape: SocketShape
    slot_index: int  # Position on item (0-based)
    
    # Socket properties
    rarity: Rarity
    is_unlocked: bool  # False if socket needs to be unlocked
    is_required: bool  # True if socket must be filled for item to function
    
    # Current contents
    rune_id: Optional[EntityId]  # Currently inserted rune
    gem_id: Optional[EntityId]  # Currently inserted gem
    glyph_id: Optional[EntityId]  # Currently inserted glyph
    
    # Unlock requirements
    required_material_ids: List[EntityId]
    required_gold: int
    required_level: Optional[int]
    
    # Visual effects
    is_glowing: bool
    glow_color: Optional[str]  # Hex color code when filled
    
    # Properties affecting inserted items
    stat_bonus_multiplier: float  # Multiplier for item stats (1.0 = no bonus)
    effect_duration_modifier: float  # Modifier for effect durations
    
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
        
        if self.slot_index < 0:
            raise ValueError("Slot index cannot be negative")
        
        if self.required_gold < 0:
            raise ValueError("Required gold cannot be negative")
        
        if self.required_level is not None and self.required_level < 1:
            raise ValueError("Required level must be positive")
        
        if self.stat_bonus_multiplier < 0:
            raise ValueError("Stat bonus multiplier cannot be negative")
        
        if self.effect_duration_modifier < 0:
            raise ValueError("Effect duration modifier cannot be negative")
        
        # Validate that only one item type is inserted
        filled_count = sum([
            1 if self.rune_id else 0,
            1 if self.gem_id else 0,
            1 if self.glyph_id else 0,
        ])
        if filled_count > 1:
            raise ValueError("Socket can only contain one item at a time")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        item_id: EntityId,
        socket_type: SocketType,
        socket_shape: SocketShape,
        slot_index: int = 0,
        rarity: Rarity = Rarity.COMMON,
        is_unlocked: bool = True,
        is_required: bool = False,
        required_material_ids: Optional[List[EntityId]] = None,
        required_gold: int = 0,
        required_level: Optional[int] = None,
        is_glowing: bool = True,
        glow_color: Optional[str] = None,
        stat_bonus_multiplier: float = 1.0,
        effect_duration_modifier: float = 1.0,
    ) -> 'Socket':
        """
        Factory method for creating a new Socket.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            item_id=item_id,
            socket_type=socket_type,
            socket_shape=socket_shape,
            slot_index=slot_index,
            rarity=rarity,
            is_unlocked=is_unlocked,
            is_required=is_required,
            required_material_ids=required_material_ids or [],
            required_gold=required_gold,
            required_level=required_level,
            rune_id=None,
            gem_id=None,
            glyph_id=None,
            is_glowing=is_glowing,
            glow_color=glow_color,
            stat_bonus_multiplier=stat_bonus_multiplier,
            effect_duration_modifier=effect_duration_modifier,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if socket is empty."""
        return self.rune_id is None and self.gem_id is None and self.glyph_id is None
    
    @property
    def is_filled(self) -> bool:
        """Check if socket is filled."""
        return not self.is_empty
    
    def unlock(self) -> None:
        """Unlock the socket."""
        if self.is_unlocked:
            return
        
        object.__setattr__(self, 'is_unlocked', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_rarity(self, new_rarity: Rarity) -> None:
        """Set socket rarity."""
        if self.rarity == new_rarity:
            return
        
        object.__setattr__(self, 'rarity', new_rarity)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_slot_index(self, index: int) -> None:
        """Set the slot index."""
        if index < 0:
            raise ValueError("Slot index cannot be negative")
        
        object.__setattr__(self, 'slot_index', index)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_glow_color(self, color: Optional[str]) -> None:
        """Set the glow color (hex color code)."""
        if color is not None and not color.startswith("#"):
            color = f"#{color}"
        
        object.__setattr__(self, 'glow_color', color)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_stat_bonus_multiplier(self, multiplier: float) -> None:
        """Set the stat bonus multiplier."""
        if multiplier < 0:
            raise ValueError("Stat bonus multiplier cannot be negative")
        
        object.__setattr__(self, 'stat_bonus_multiplier', multiplier)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_effect_duration_modifier(self, modifier: float) -> None:
        """Set the effect duration modifier."""
        if modifier < 0:
            raise ValueError("Effect duration modifier cannot be negative")
        
        object.__setattr__(self, 'effect_duration_modifier', modifier)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def insert_rune(self, rune_id: EntityId) -> None:
        """
        Insert a rune into the socket.
        
        Raises:
            ValueError: If socket is locked, already filled, or wrong type.
        """
        if not self.is_unlocked:
            raise ValueError("Socket is locked")
        
        if not self.is_empty:
            raise ValueError("Socket is already filled")
        
        if self.socket_type != SocketType.RUNE and self.socket_type != SocketType.UNIVERSAL:
            raise ValueError(f"Socket type {self.socket_type} does not accept runes")
        
        object.__setattr__(self, 'rune_id', rune_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def insert_gem(self, gem_id: EntityId) -> None:
        """
        Insert a gem into the socket.
        
        Raises:
            ValueError: If socket is locked, already filled, or wrong type.
        """
        if not self.is_unlocked:
            raise ValueError("Socket is locked")
        
        if not self.is_empty:
            raise ValueError("Socket is already filled")
        
        if self.socket_type == SocketType.RUNE or self.socket_type == SocketType.GLYPH:
            raise ValueError(f"Socket type {self.socket_type} does not accept gems")
        
        object.__setattr__(self, 'gem_id', gem_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def insert_glyph(self, glyph_id: EntityId) -> None:
        """
        Insert a glyph into the socket.
        
        Raises:
            ValueError: If socket is locked, already filled, or wrong type.
        """
        if not self.is_unlocked:
            raise ValueError("Socket is locked")
        
        if not self.is_empty:
            raise ValueError("Socket is already filled")
        
        if self.socket_type != SocketType.GLYPH and self.socket_type != SocketType.UNIVERSAL:
            raise ValueError(f"Socket type {self.socket_type} does not accept glyphs")
        
        object.__setattr__(self, 'glyph_id', glyph_id)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_item(self) -> Optional[EntityId]:
        """
        Remove the item from the socket.
        
        Returns:
            The ID of the removed item, or None if socket was empty.
        """
        if self.is_empty:
            return None
        
        removed_id = self.rune_id or self.gem_id or self.glyph_id
        
        object.__setattr__(self, 'rune_id', None)
        object.__setattr__(self, 'gem_id', None)
        object.__setattr__(self, 'glyph_id', None)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
        
        return removed_id
    
    def get_inserted_item_id(self) -> Optional[EntityId]:
        """Get the ID of the inserted item."""
        return self.rune_id or self.gem_id or self.glyph_id
    
    def get_inserted_item_type(self) -> Optional[str]:
        """Get the type of inserted item."""
        if self.rune_id:
            return "rune"
        if self.gem_id:
            return "gem"
        if self.glyph_id:
            return "glyph"
        return None
    
    def accepts_item_type(self, item_type: str) -> bool:
        """Check if socket accepts a specific item type."""
        if self.socket_type == SocketType.UNIVERSAL:
            return True
        
        type_mapping = {
            "rune": SocketType.RUNE,
            "gem": [SocketType.SQUARE, SocketType.TRIANGLE, SocketType.CIRCLE, 
                    SocketType.STAR, SocketType.HEXAGON, SocketType.DIAMOND],
            "glyph": SocketType.GLYPH,
        }
        
        accepted = type_mapping.get(item_type)
        
        if isinstance(accepted, list):
            return self.socket_type in accepted
        else:
            return self.socket_type == accepted
    
    def __str__(self) -> str:
        locked_str = " [LOCKED]" if not self.is_unlocked else ""
        filled_str = " [FILLED]" if self.is_filled else " [EMPTY]"
        return f"Socket({self.socket_type.value}, {self.slot_index}{locked_str}{filled_str})"
    
    def __repr__(self) -> str:
        return (
            f"Socket(id={self.id}, item_id={self.item_id}, "
            f"type={self.socket_type}, slot={self.slot_index}, "
            f"unlocked={self.is_unlocked}, filled={self.is_filled})"
        )
