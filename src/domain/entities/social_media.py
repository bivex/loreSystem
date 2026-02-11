"""
SocialMedia Entity

A SocialMedia represents a platform for social networking,
content sharing, and user interaction.
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
class SocialMedia:
    """
    SocialMedia entity for social networking platforms.
    
    Invariants:
    - Name must not be empty
    - Version increases monotonically
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    name: str
    description: Description
    world_id: Optional[EntityId]
    platform_type: str  # e.g., "Microblog", "Photo", "Video", "Professional"
    founder_name: Optional[str]
    follower_count: Optional[int]
    hashtag_count: Optional[int]
    monetization_enabled: bool
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
            raise ValueError("SocialMedia name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("SocialMedia name must be <= 255 characters")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        name: str,
        description: Description,
        platform_type: str,
        is_active: bool = True,
        monetization_enabled: bool = False,
        world_id: Optional[EntityId] = None,
        founder_name: Optional[str] = None,
    ) -> 'SocialMedia':
        """Factory method for creating a new SocialMedia platform."""
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            name=name,
            description=description,
            world_id=world_id,
            platform_type=platform_type,
            founder_name=founder_name,
            follower_count=0,
            hashtag_count=0,
            monetization_enabled=monetization_enabled,
            is_active=is_active,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update platform description."""
        if str(self.description) == str(new_description):
            return
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_monetization(self, enabled: bool) -> None:
        """Set monetization status."""
        if self.monetization_enabled == enabled:
            return
        object.__setattr__(self, 'monetization_enabled', enabled)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
