"""
ShareCode Entity

A ShareCode represents a shareable code for distributing game content configurations.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
    ShareCodeType,
    ShareCodeStatus,
)


@dataclass
class ShareCode:
    """
    ShareCode entity representing shareable codes for content distribution.
    
    Invariants:
    - Must belong to exactly one tenant
    - Version increases monotonically
    - Code must be non-empty and valid format
    - Usage count must be non-negative
    - Max uses must be positive if set
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    author_id: EntityId
    code: str  # The actual shareable code (e.g., "ABC-123-XYZ")
    name: str
    description: Description
    code_type: ShareCodeType
    status: ShareCodeStatus
    
    # Content reference
    content_type: str  # "mod", "custom_map", "scenario", "build", etc.
    content_id: EntityId  # Reference to the content this code distributes
    content_version: Optional[str]
    
    # Usage limits
    usage_count: int  # Times this code has been redeemed
    max_uses: Optional[int]  # Maximum times this code can be used (None = unlimited)
    expires_at: Optional[Timestamp]  # Code expiration time
    
    # Visibility settings
    is_public: bool
    requires_authentication: bool
    
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
        
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("Share code cannot be empty")
        
        # Validate code format (letters, numbers, hyphens only)
        import re
        if not re.match(r'^[A-Z0-9-]+$', self.code):
            raise ValueError("Share code must contain only uppercase letters, numbers, and hyphens")
        
        if len(self.code) > 50:
            raise ValueError("Share code must be <= 50 characters")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Share code name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Share code name must be <= 255 characters")
        
        if self.usage_count < 0:
            raise ValueError("Usage count cannot be negative")
        
        if self.max_uses is not None and self.max_uses <= 0:
            raise ValueError("Max uses must be positive")
        
        if self.max_uses is not None and self.usage_count > self.max_uses:
            raise ValueError("Usage count cannot exceed max uses")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        author_id: EntityId,
        code: str,
        name: str,
        description: Description,
        code_type: ShareCodeType,
        content_type: str,
        content_id: EntityId,
        content_version: Optional[str] = None,
        status: ShareCodeStatus = ShareCodeStatus.ACTIVE,
        max_uses: Optional[int] = None,
        expires_at: Optional[Timestamp] = None,
        is_public: bool = False,
        requires_authentication: bool = True,
    ) -> 'ShareCode':
        """
        Factory method for creating a new ShareCode.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            author_id=author_id,
            code=code.upper(),  # Normalize to uppercase
            name=name,
            description=description,
            code_type=code_type,
            status=status,
            content_type=content_type,
            content_id=content_id,
            content_version=content_version,
            usage_count=0,
            max_uses=max_uses,
            expires_at=expires_at,
            is_public=is_public,
            requires_authentication=requires_authentication,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def update_description(self, new_description: Description) -> None:
        """Update share code description."""
        if str(self.description) == str(new_description):
            return
        
        object.__setattr__(self, 'description', new_description)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def change_status(self, new_status: ShareCodeStatus) -> None:
        """Change share code status."""
        if self.status == new_status:
            return
        
        object.__setattr__(self, 'status', new_status)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def redeem(self) -> bool:
        """
        Redeem the share code (increment usage count).
        
        Returns:
            True if code was successfully redeemed
        
        Raises:
            ValueError: If code is inactive, expired, or at max uses
        """
        if self.status != ShareCodeStatus.ACTIVE:
            raise ValueError("Cannot redeem inactive share code")
        
        if self.expires_at is not None and self.expires_at.value < Timestamp.now().value:
            raise ValueError("Share code has expired")
        
        if self.max_uses is not None and self.usage_count >= self.max_uses:
            raise ValueError("Share code has reached maximum uses")
        
        object.__setattr__(self, 'usage_count', self.usage_count + 1)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        
        # Auto-disable if max uses reached
        if self.max_uses is not None and self.usage_count >= self.max_uses:
            object.__setattr__(self, 'status', ShareCodeStatus.INACTIVE)
        
        return True
    
    def set_visibility(self, is_public: bool) -> None:
        """Change visibility setting."""
        if self.is_public == is_public:
            return
        
        object.__setattr__(self, 'is_public', is_public)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def set_expiration(self, expires_at: Optional[Timestamp]) -> None:
        """Set or remove expiration time."""
        if self.expires_at == expires_at:
            return
        
        object.__setattr__(self, 'expires_at', expires_at)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def update_content_version(self, new_version: str) -> None:
        """Update the content version this code points to."""
        if self.content_version == new_version:
            return
        
        object.__setattr__(self, 'content_version', new_version)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def is_redeemable(self) -> bool:
        """
        Check if the code is currently redeemable.
        
        Returns:
            True if code can be redeemed
        """
        if self.status != ShareCodeStatus.ACTIVE:
            return False
        
        if self.expires_at is not None and self.expires_at.value < Timestamp.now().value:
            return False
        
        if self.max_uses is not None and self.usage_count >= self.max_uses:
            return False
        
        return True
    
    def __str__(self) -> str:
        status_str = f" [{self.status.value}]" if self.status != ShareCodeStatus.ACTIVE else ""
        uses_str = f" ({self.usage_count}/{self.max_uses or '∞'})" if self.max_uses else f" ({self.usage_count})"
        return f"ShareCode({self.code}: {self.name}{status_str}{uses_str})"
    
    def __repr__(self) -> str:
        return (
            f"ShareCode(id={self.id}, code='{self.code}', "
            f"content_type={self.content_type}, content_id={self.content_id})"
        )
