"""HolySite entity - Religious location."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Self


@dataclass
class HolySite:
    """Represents a holy site or sacred location."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain fields
    name: str = ""
    location_id: str = ""
    religion_id: str = ""
    deity_id: str = ""
    site_type: str = ""  # temple, shrine, altar, monument, pilgrimage
    sanctity_level: int = 50  # 0-100
    visitors_count: int = 0
    blessings_offered: list[str] = field(default_factory=list)
    rituals_performed: list[str] = field(default_factory=list)
    guardian_id: str = ""

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        location_id: str,
        religion_id: str,
        site_type: str,
    ) -> Self:
        """Factory method to create a new HolySite."""
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not name:
            raise ValueError("name is required")
        if not location_id:
            raise ValueError("location_id is required")
        if not religion_id:
            raise ValueError("religion_id is required")
        if not site_type:
            raise ValueError("site_type is required")

        valid_types = ["temple", "shrine", "altar", "monument", "pilgrimage"]
        if site_type not in valid_types:
            raise ValueError(f"site_type must be one of {valid_types}")

        return cls(
            tenant_id=tenant_id,
            name=name,
            location_id=location_id,
            religion_id=religion_id,
            site_type=site_type,
        )

    def set_deity(self, deity_id: str) -> None:
        """Set associated deity."""
        self.deity_id = deity_id
        self.updated_at = datetime.utcnow()

    def set_sanctity(self, level: int) -> None:
        """Set sanctity level."""
        self.sanctity_level = max(0, min(100, level))
        self.updated_at = datetime.utcnow()

    def add_blessing(self, blessing: str) -> None:
        """Add a blessing offered."""
        if blessing and blessing not in self.blessings_offered:
            self.blessings_offered.append(blessing)
            self.updated_at = datetime.utcnow()

    def add_ritual(self, ritual: str) -> None:
        """Add a ritual performed."""
        if ritual and ritual not in self.rituals_performed:
            self.rituals_performed.append(ritual)
            self.updated_at = datetime.utcnow()

    def set_guardian(self, guardian_id: str) -> None:
        """Set guardian NPC."""
        self.guardian_id = guardian_id
        self.updated_at = datetime.utcnow()

    def add_visitor(self) -> None:
        """Record a visitor."""
        self.visitors_count += 1
        self.updated_at = datetime.utcnow()

    def is_sanctified(self) -> bool:
        """Check if site is highly sanctified."""
        return self.sanctity_level >= 80

    def is_desecrated(self) -> bool:
        """Check if site is desecrated (low sanctity)."""
        return self.sanctity_level <= 20
