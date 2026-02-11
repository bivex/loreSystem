"""SocialClass entity - Character social class/status."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class SocialClass:
    """Represents character's social class in society."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    character_id: str = ""
    class_name: str = ""  # peasant, commoner, merchant, noble, aristocrat, royalty
    tier: int = 0  # 0-10 within class
    title: str = ""  # Formal title (e.g., "Sir", "Lord", "Duke")
    benefits: list[str] = field(default_factory=list)  # Class-specific benefits
    restrictions: list[str] = field(default_factory=list)  # Class-specific restrictions
    hereditary: bool = False  # Can pass to children

    @classmethod
    def create(
        cls,
        tenant_id: str,
        character_id: str,
        class_name: str,
        tier: int = 0,
        title: str = "",
    ) -> Self:
        """Factory method to create a new SocialClass."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not character_id:
            raise ValueError("character_id is required")
        if not class_name:
            raise ValueError("class_name is required")

        valid_classes = ["peasant", "commoner", "merchant", "noble", "aristocrat", "royalty"]
        if class_name not in valid_classes:
            raise ValueError(f"class_name must be one of {valid_classes}")

        if not 0 <= tier <= 10:
            raise ValueError("tier must be between 0 and 10")

        return cls(
            tenant_id=tenant_id,
            character_id=character_id,
            class_name=class_name,
            tier=tier,
            title=title,
        )

    def promote(self, new_tier: int) -> None:
        """Promote to higher tier."""
        self.tier = max(0, min(10, new_tier))
        self._update_class_from_tier()
        self.updated_at = datetime.utcnow()

    def change_class(self, new_class: str) -> None:
        """Change social class."""
        valid_classes = ["peasant", "commoner", "merchant", "noble", "aristocrat", "royalty"]
        if new_class not in valid_classes:
            raise ValueError(f"class_name must be one of {valid_classes}")
        self.class_name = new_class
        self.tier = 0  # Reset tier on class change
        self.updated_at = datetime.utcnow()

    def set_title(self, title: str) -> None:
        """Set formal title."""
        self.title = title
        self.updated_at = datetime.utcnow()

    def add_benefit(self, benefit: str) -> None:
        """Add a class benefit."""
        if benefit not in self.benefits:
            self.benefits.append(benefit)
            self.updated_at = datetime.utcnow()

    def add_restriction(self, restriction: str) -> None:
        """Add a class restriction."""
        if restriction not in self.restrictions:
            self.restrictions.append(restriction)
            self.updated_at = datetime.utcnow()

    def _update_class_from_tier(self) -> None:
        """Automatically update class based on tier threshold."""
        if self.tier >= 10 and self.class_name != "royalty":
            self.class_name = "royalty"
        elif self.tier >= 8 and self.class_name != "aristocrat":
            self.class_name = "aristocrat"
        elif self.tier >= 5 and self.class_name != "noble":
            self.class_name = "noble"

    def is_upper_class(self) -> bool:
        """Check if upper class."""
        return self.class_name in ["noble", "aristocrat", "royalty"]

    def has_title(self) -> bool:
        """Check if has title."""
        return bool(self.title)
