"""
Rumor Entity

A Rumor represents unverified information or gossip that spreads
through a population, often influencing public opinion.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


@dataclass
class Rumor:
    """
    Rumor entity for unverified information.
    
    Invariants:
    - Content must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    location_id: Optional[EntityId]
    source_name: Optional[str]  # Who started the rumor
    origin_date: Optional[Timestamp]
    truth_level: str  # e.g., "False", "Unverified", "Partially True", "True"
    spread_speed: str  # e.g., "Slow", "Moderate", "Rapid", "Explosive"
    credibility_score: Optional[int]  # 1-10 scale
    is_active: bool
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise ValueError("Updated timestamp must be >= created timestamp")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Rumor name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Rumor name must be <= 255 characters")
        
        if self.credibility_score is not None and (self.credibility_score < 1 or self.credibility_score > 10):
            raise ValueError("Credibility score must be between 1 and 10")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        truth_level: str = "Unverified",
        spread_speed: str = "Moderate",
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        location_id: Optional[EntityId] = None,
        source_name: Optional[str] = None,
    ) -> 'Rumor':
        """Factory method for creating a new Rumor."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            location_id=location_id,
            source_name=source_name,
            origin_date=None,
            truth_level=truth_level,
            spread_speed=spread_speed,
            credibility_score=None,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update rumor description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_truth_level(self, new_level: str) -> None:
        """Update the truth level of the rumor."""
        if self.truth_level == new_level:
            return
        object.__setattr__(self, 'truth_level', new_level)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_credibility(self, new_score: int) -> None:
        """Update the credibility score."""
        if new_score < 1 or new_score > 10:
            raise ValueError("Credibility score must be between 1 and 10")
        if self.credibility_score == new_score:
            return
        object.__setattr__(self, 'credibility_score', new_score)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
