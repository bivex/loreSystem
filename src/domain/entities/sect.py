"""Sect entity - Religious subdivision/heresy."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class Sect:
    """Represents a religious sect or subdivision."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""
    parent_religion_id: str = ""
    founder_id: str = ""
    doctrines: list[str] = field(default_factory=list)
    practices: list[str] = field(default_factory=list)
    is_heresy: bool = False
    persecution_level: int = 0  # 0-100
    member_count: int = 0
    headquarters: str = ""

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        parent_religion_id: str,
        is_heresy: bool = False,
    ) -> Self:
        """Factory method to create a new Sect."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not parent_religion_id:
            raise ValueError("parent_religion_id is required")

        return cls(
            tenant_id=tenant_id,
            name=name,
            parent_religion_id=parent_religion_id,
            is_heresy=is_heresy,
        )

    def set_founder(self, founder_id: str) -> None:
        """Set sect founder."""
        self.founder_id = founder_id
        self.updated_at = datetime.utcnow()

    def set_persecution(self, level: int) -> None:
        """Set persecution level."""
        self.persecution_level = max(0, min(100, level))
        self.updated_at = datetime.utcnow()

    def add_doctrine(self, doctrine: str) -> None:
        """Add a doctrine."""
        if doctrine and doctrine not in self.doctrines:
            self.doctrines.append(doctrine)
            self.updated_at = datetime.utcnow()

    def add_practice(self, practice: str) -> None:
        """Add a practice."""
        if practice and practice not in self.practices:
            self.practices.append(practice)
            self.updated_at = datetime.utcnow()

    def set_headquarters(self, location: str) -> None:
        """Set headquarters location."""
        self.headquarters = location
        self.updated_at = datetime.utcnow()

    def add_member(self) -> None:
        """Add a member."""
        self.member_count += 1
        self.updated_at = datetime.utcnow()

    def remove_member(self) -> None:
        """Remove a member."""
        self.member_count = max(0, self.member_count - 1)
        self.updated_at = datetime.utcnow()

    def is_persecuted(self) -> bool:
        """Check if sect is persecuted."""
        return self.persecution_level >= 50

    def is_heretical(self) -> bool:
        """Check if sect is considered heresy."""
        return self.is_heresy
