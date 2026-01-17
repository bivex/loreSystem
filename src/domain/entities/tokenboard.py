"""
Tokenboard Entity

A Tokenboard represents the GM's dashboard with counters, sticky notes, shortcuts, and tools.
Part of the World aggregate.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from ..value_objects.common import (
    TenantId,
    EntityId,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Tokenboard:
    """
    Tokenboard entity within a World.
    
    Invariants:
    - Must belong to exactly one World
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Optional[str]
    counters: Dict[str, int]  # Named counters (e.g., {"initiative": 5, "round": 1})
    sticky_notes: List[str]  # Sticky notes content
    shortcuts: Dict[str, str]  # Keyboard shortcuts to actions/commands
    timers: Dict[str, int]  # Named timers in seconds
    is_active: bool  # Whether this is the currently active tokenboard
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Optional[str] = None,
        counters: Optional[Dict[str, int]] = None,
        sticky_notes: Optional[List[str]] = None,
        shortcuts: Optional[Dict[str, str]] = None,
        timers: Optional[Dict[str, int]] = None,
        is_active: bool = False,
    ) -> 'Tokenboard':
        """
        Factory method for creating a new Tokenboard.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            counters=counters or {},
            sticky_notes=sticky_notes or [],
            shortcuts=shortcuts or {},
            timers=timers or {},
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def increment_counter(self, name: str, amount: int = 1) -> None:
        """Increment a counter by the given amount."""
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += amount
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def decrement_counter(self, name: str, amount: int = 1) -> None:
        """Decrement a counter by the given amount."""
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] -= amount
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_counter(self, name: str, value: int) -> None:
        """Set a counter to a specific value."""
        self.counters[name] = value
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_sticky_note(self, note: str) -> None:
        """Add a sticky note."""
        self.sticky_notes.append(note)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_sticky_note(self, index: int) -> None:
        """Remove a sticky note by index."""
        if 0 <= index < len(self.sticky_notes):
            self.sticky_notes.pop(index)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def add_shortcut(self, key: str, action: str) -> None:
        """Add a keyboard shortcut."""
        self.shortcuts[key] = action
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def remove_shortcut(self, key: str) -> None:
        """Remove a keyboard shortcut."""
        if key in self.shortcuts:
            del self.shortcuts[key]
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def start_timer(self, name: str, duration_seconds: int) -> None:
        """Start or set a timer."""
        self.timers[name] = duration_seconds
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def stop_timer(self, name: str) -> None:
        """Stop a timer."""
        if name in self.timers:
            del self.timers[name]
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def activate(self) -> None:
        """Make this the active tokenboard."""
        if self.is_active:
            return
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def deactivate(self) -> None:
        """Deactivate this tokenboard."""
        if not self.is_active:
            return
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def __str__(self) -> str:
        return f"Tokenboard({self.name}, active={self.is_active})"
    
    def __repr__(self) -> str:
        return (
            f"Tokenboard(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', active={self.is_active}, version={self.version})"
        )