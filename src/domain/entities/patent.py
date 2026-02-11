"""
Patent Entity

Patent represents intellectual property protection for inventions and blueprints.
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)


class PatentStatus(str, Enum):
    """Status of patent application."""
    PENDING = "pending"
    GRANTED = "granted"
    EXPIRED = "expired"
    REVOKED = "revoked"
    REJECTED = "rejected"


@dataclass
class Patent:
    """
    Patent entity for tracking intellectual property.
    
    Invariants:
    - Name cannot be empty
    - Status must be set
    - Must belong to a world
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    name: str
    description: Description
    status: PatentStatus
    
    # Protected entities
    invention_id: Optional[EntityId]
    blueprint_id: Optional[EntityId]
    
    # Owner information
    owner_id: EntityId  # Character, faction, or organization
    owner_type: str  # "character", "faction", "organization"
    
    # Dates
    filed_date: Optional[Timestamp]
    granted_date: Optional[Timestamp]
    expiration_date: Optional[Timestamp]
    
    # Patent details
    patent_number: Optional[str]
    jurisdiction_id: Optional[EntityId]  # Where patent is valid
    
    # Rights and exclusivity
    is_exclusive: bool
    license_allowed: bool
    license_fee_percentage: float  # Percentage of sales as licensing fee
    
    # Restrictions
    transferable: bool  # Can patent be sold/transfered
    expiry_years: int  # Years until expiration from grant
    
    # Documentation
    claims: List[str]  # Patent claims
    prior_art_ids: List[EntityId]  # References to prior inventions
    
    # Enforcement
    infringer_ids: List[EntityId]  # Entities infringing this patent
    
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
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Patent name cannot be empty")
        
        if len(self.name) > 255:
            raise ValueError("Patent name must be <= 255 characters")
        
        if self.license_fee_percentage < 0.0 or self.license_fee_percentage > 100.0:
            raise ValueError("License fee percentage must be between 0-100")
        
        if self.expiry_years < 1:
            raise ValueError("Expiry years must be at least 1")
        
        if self.status == PatentStatus.GRANTED and self.granted_date is None:
            raise ValueError("Granted patent must have granted_date")
        
        if self.status == PatentStatus.EXPIRED and self.expiration_date is None:
            raise ValueError("Expired patent must have expiration_date")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        owner_id: EntityId,
        owner_type: str,
        invention_id: Optional[EntityId] = None,
        blueprint_id: Optional[EntityId] = None,
        is_exclusive: bool = True,
        license_allowed: bool = False,
        license_fee_percentage: float = 0.0,
        transferable: bool = True,
        expiry_years: int = 20,
        jurisdiction_id: Optional[EntityId] = None,
    ) -> 'Patent':
        """
        Factory method for creating a new Patent.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            status=PatentStatus.PENDING,
            invention_id=invention_id,
            blueprint_id=blueprint_id,
            owner_id=owner_id,
            owner_type=owner_type,
            filed_date=now,
            granted_date=None,
            expiration_date=None,
            patent_number=None,
            jurisdiction_id=jurisdiction_id,
            is_exclusive=is_exclusive,
            license_allowed=license_allowed,
            license_fee_percentage=license_fee_percentage,
            transferable=transferable,
            expiry_years=expiry_years,
            claims=[],
            prior_art_ids=[],
            infringer_ids=[],
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    @property
    def is_pending(self) -> bool:
        """Check if patent is pending approval."""
        return self.status == PatentStatus.PENDING
    
    @property
    def is_active(self) -> bool:
        """Check if patent is active (granted and not expired)."""
        return self.status == PatentStatus.GRANTED
    
    @property
    def is_expired(self) -> bool:
        """Check if patent has expired."""
        return self.status == PatentStatus.EXPIRED
    
    def grant(self) -> None:
        """Grant the patent."""
        if self.status != PatentStatus.PENDING:
            raise ValueError("Can only grant pending patents")
        
        now = Timestamp.now()
        object.__setattr__(self, 'status', PatentStatus.GRANTED)
        object.__setattr__(self, 'granted_date', now)
        object.__setattr__(self, 'updated_at', now)
        object.__setattr__(self, 'version', self.version.increment())
    
    def expire(self) -> None:
        """Expire the patent."""
        if self.status != PatentStatus.GRANTED:
            raise ValueError("Can only expire granted patents")
        
        now = Timestamp.now()
        object.__setattr__(self, 'status', PatentStatus.EXPIRED)
        object.__setattr__(self, 'expiration_date', now)
        object.__setattr__(self, 'updated_at', now)
        object.__setattr__(self, 'version', self.version.increment())
    
    def revoke(self) -> None:
        """Revoke the patent."""
        if self.status == PatentStatus.REVOKED:
            return
        
        object.__setattr__(self, 'status', PatentStatus.REVOKED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def reject(self) -> None:
        """Reject the patent application."""
        if self.status != PatentStatus.PENDING:
            raise ValueError("Can only reject pending patents")
        
        object.__setattr__(self, 'status', PatentStatus.REJECTED)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_claim(self, claim: str) -> None:
        """Add a patent claim."""
        if not claim or len(claim.strip()) == 0:
            raise ValueError("Claim cannot be empty")
        
        self.claims.append(claim)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_prior_art(self, art_id: EntityId) -> None:
        """Add prior art reference."""
        if art_id not in self.prior_art_ids:
            self.prior_art_ids.append(art_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def set_patent_number(self, number: str) -> None:
        """Set the patent number."""
        if not number or len(number.strip()) == 0:
            raise ValueError("Patent number cannot be empty")
        
        object.__setattr__(self, 'patent_number', number)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def transfer_ownership(self, new_owner_id: EntityId, new_owner_type: str) -> None:
        """Transfer patent ownership."""
        if not self.transferable:
            raise ValueError("Patent is not transferable")
        
        if not new_owner_id or not new_owner_type:
            raise ValueError("New owner ID and type must be provided")
        
        object.__setattr__(self, 'owner_id', new_owner_id)
        object.__setattr__(self, 'owner_type', new_owner_type)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_infringer(self, entity_id: EntityId) -> None:
        """Add an infringing entity."""
        if entity_id not in self.infringer_ids:
            self.infringer_ids.append(entity_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
    
    def remove_infringer(self, entity_id: EntityId) -> bool:
        """Remove an infringing entity."""
        if entity_id in self.infringer_ids:
            self.infringer_ids.remove(entity_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
            object.__setattr__(self, 'version', self.version.increment())
            return True
        return False
    
    def __str__(self) -> str:
        number_str = f" #{self.patent_number}" if self.patent_number else ""
        return f"Patent({self.name}{number_str}, {self.status.value})"
    
    def __repr__(self) -> str:
        return (
            f"Patent(id={self.id}, world_id={self.world_id}, "
            f"name='{self.name}', status={self.status}, owner={self.owner_id})"
        )
