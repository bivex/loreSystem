"""Scripture entity - Religious text."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Scripture:
    """Represents a religious scripture or text."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    title: str = ""
    religion_id: str = ""
    author_id: str = ""
    language: str = ""
    chapters: int = 0
    verses_count: int = 0
    key_teachings: list[str] = field(default_factory=list)
    prophecies: list[str] = field(default_factory=list)
    forbidden_knowledge: bool = False
    rarity: str = "common"  # common, rare, legendary, lost

    @classmethod
    def create(
        cls,
        tenant_id: str,
        title: str,
        religion_id: str,
    ) -> Self:
        """Factory method to create a new Scripture."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not title:
            raise ValueError("title is required")
        if not religion_id:
            raise ValueError("religion_id is required")

        return cls(
            tenant_id=tenant_id,
            title=title,
            religion_id=religion_id,
        )

    def set_author(self, author_id: str) -> None:
        """Set author."""
        self.author_id = author_id
        self.updated_at = datetime.utcnow()

    def set_language(self, language: str) -> None:
        """Set language."""
        self.language = language
        self.updated_at = datetime.utcnow()

    def set_structure(self, chapters: int, verses: int) -> None:
        """Set scripture structure."""
        self.chapters = max(0, chapters)
        self.verses_count = max(0, verses)
        self.updated_at = datetime.utcnow()

    def add_teaching(self, teaching: str) -> None:
        """Add a key teaching."""
        if teaching and teaching not in self.key_teachings:
            self.key_teachings.append(teaching)
            self.updated_at = datetime.utcnow()

    def add_prophecy(self, prophecy: str) -> None:
        """Add a prophecy."""
        if prophecy and prophecy not in self.prophecies:
            self.prophecies.append(prophecy)
            self.updated_at = datetime.utcnow()

    def set_forbidden(self, forbidden: bool) -> None:
        """Set as forbidden knowledge."""
        self.forbidden_knowledge = forbidden
        self.updated_at = datetime.utcnow()

    def set_rarity(self, rarity: str) -> None:
        """Set rarity."""
        valid_rarities = ["common", "rare", "legendary", "lost"]
        if rarity not in valid_rarities:
            raise ValueError(f"rarity must be one of {valid_rarities}")
        self.rarity = rarity
        self.updated_at = datetime.utcnow()

    def is_forbidden(self) -> bool:
        """Check if scripture is forbidden."""
        return self.forbidden_knowledge

    def is_lost(self) -> bool:
        """Check if scripture is lost."""
        return self.rarity == "lost"

    def is_legendary(self) -> bool:
        """Check if scripture is legendary."""
        return self.rarity == "legendary"
