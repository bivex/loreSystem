"""SocialMobility entity - Social class movement tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class SocialMobility:
    """Represents character's social mobility over time."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    starting_class: str = ""
    current_class: str = ""
    highest_class: str = ""
    moves_made: int = 0  # Number of class changes
    direction: str = "static"  # upward, downward, static
    locked: bool = False  # Cannot change further

    @classmethod
    def create(
        cls,
        tenant_id: str,
        character_id: str,
        starting_class: str,
    ) -> Self:
        """Factory method to create a new SocialMobility."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not character_id:
            raise ValueError("character_id is required")
        if not starting_class:
            raise ValueError("starting_class is required")

        return cls(
            tenant_id=tenant_id,
            character_id=character_id,
            starting_class=starting_class,
            current_class=starting_class,
            highest_class=starting_class,
        )

    def move_class(self, new_class: str) -> None:
        """Record a class change."""
        if self.locked:
            raise ValueError("social mobility is locked")

        self.direction = self._calculate_direction(self.current_class, new_class)
        self.current_class = new_class
        self.moves_made += 1

        # Update highest class achieved
        if self._is_higher_class(new_class, self.highest_class):
            self.highest_class = new_class

        self.updated_at = datetime.utcnow()

    def lock(self) -> None:
        """Lock social mobility."""
        self.locked = True
        self.updated_at = datetime.utcnow()

    def unlock(self) -> None:
        """Unlock social mobility."""
        self.locked = False
        self.updated_at = datetime.utcnow()

    @staticmethod
    def _calculate_direction(from_class: str, to_class: str) -> str:
        """Calculate mobility direction."""
        class_hierarchy = ["peasant", "commoner", "merchant", "noble", "aristocrat", "royalty"]

        try:
            from_idx = class_hierarchy.index(from_class)
            to_idx = class_hierarchy.index(to_class)

            if to_idx > from_idx:
                return "upward"
            elif to_idx < from_idx:
                return "downward"
            else:
                return "static"
        except ValueError:
            return "static"

    @staticmethod
    def _is_higher_class(class1: str, class2: str) -> bool:
        """Check if class1 is higher than class2."""
        class_hierarchy = ["peasant", "commoner", "merchant", "noble", "aristocrat", "royalty"]

        try:
            idx1 = class_hierarchy.index(class1)
            idx2 = class_hierarchy.index(class2)
            return idx1 > idx2
        except ValueError:
            return False

    def has_advanced(self) -> bool:
        """Check if character has advanced socially."""
        return self.direction == "upward" and self.current_class != self.starting_class

    def total_rise(self) -> int:
        """Calculate total rise in class levels."""
        class_hierarchy = ["peasant", "commoner", "merchant", "noble", "aristocrat", "royalty"]

        try:
            start_idx = class_hierarchy.index(self.starting_class)
            current_idx = class_hierarchy.index(self.current_class)
            return max(0, current_idx - start_idx)
        except ValueError:
            return 0
