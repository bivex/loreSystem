"""
Propaganda Entity

A Propaganda represents organized communication intended to influence
attitudes, beliefs, and actions of a population.
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
class Propaganda:
    """
    Propaganda entity for influence campaigns.
    
    Invariants:
    - Message must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    faction_id: Optional[EntityId]
    originator_name: Optional[str]
    campaign_type: str  # e.g., "Political", "Military", "Religious", "Economic"
    distribution_medium: str  # e.g., "Posters", "Radio", "Television", "Internet"
    target_audience: str
    effectiveness_score: Optional[int]  # 1-10 scale
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
            raise ValueError("Propaganda name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Propaganda name must be <= 255 characters")
        
        if self.effectiveness_score is not None and (self.effectiveness_score < 1 or self.effectiveness_score > 10):
            raise ValueError("Effectiveness score must be between 1 and 10")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        campaign_type: str,
        distribution_medium: str,
        target_audience: str,
        is_active: bool = True,
        world_id: Optional[EntityId] = None,
        faction_id: Optional[EntityId] = None,
        originator_name: Optional[str] = None,
    ) -> 'Propaganda':
        """Factory method for creating a new Propaganda."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            faction_id=faction_id,
            originator_name=originator_name,
            campaign_type=campaign_type,
            distribution_medium=distribution_medium,
            target_audience=target_audience,
            effectiveness_score=None,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update propaganda description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_effectiveness(self, new_score: int) -> None:
        """Update the effectiveness score."""
        if new_score < 1 or new_score > 10:
            raise ValueError("Effectiveness score must be between 1 and 10")
        if self.effectiveness_score == new_score:
            return
        object.__setattr__(self, 'effectiveness_score', new_score)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
