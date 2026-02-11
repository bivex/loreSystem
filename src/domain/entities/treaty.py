"""
Treaty Entity - Formal agreement between parties
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
from ..exceptions import InvariantViolation


class TreatyType(str, Enum):
    """Types of treaties."""
    PEACE = "peace"
    TRADE = "trade"
    ALLIANCE = "alliance"
    BORDER = "border"
    EXTRADITION = "extradition"
    NON_AGGRESSION = "non_aggression"
    MUTUAL_DEFENSE = "mutual_defense"
    VASSALAGE = "vassalage"
    CULTURAL_EXCHANGE = "cultural_exchange"
    MAGICAL_COOPERATION = "magical_cooperation"


class TreatyStatus(str, Enum):
    """Status of treaty."""
    DRAFT = "draft"
    PROPOSED = "proposed"
    NEGOTIATING = "negotiating"
    SIGNED = "signed"
    RATIFIED = "ratified"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    VIOLATED = "violated"
    TERMINATED = "terminated"
    EXPIRED = "expired"


@dataclass
class Treaty:
    """
    Treaty represents a formal agreement between nations or factions.
    
    Invariants:
    - Must have at least two signatories
    - Name cannot be empty
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    name: str
    description: Description
    
    # Treaty details
    treaty_type: TreatyType
    status: TreatyStatus
    
    # Parties involved
    signatory_nation_ids: List[EntityId]
    signatory_faction_ids: List[EntityId]
    third_party_ids: List[EntityId]  # Nations/factions affected but not signing
    
    # Negotiation
    negotiation_location_id: Optional[EntityId]
    mediator_ids: List[EntityId]  # Character IDs
    negotiation_event_ids: List[EntityId]
    
    # Terms
    terms: List[str]  # Text descriptions of terms
    obligations: List[str]
    prohibitions: List[str]
    rights_granted: List[str]
    
    # Duration
    signing_date: Optional[str]
    ratification_date: Optional[str]
    effective_date: Optional[str]
    expiration_date: Optional[str]
    is_indefinite: bool
    
    # Territory changes
    territory_transfers: List[dict]  # e.g., [{"from": X, "to": Y, "region": Z}]
    border_adjustments: List[str]
    
    # Resources and trade
    resource_exchanges: List[str]
    trade_concessions: List[str]
    
    # Enforcement
    violation_consequences: List[str]
    dispute_mechanism: Optional[str]  # e.g., "Arbitration", "War"
    
    # Historical
    related_conflict_id: Optional[EntityId]  # War/conflict that led to treaty
    predecessor_treaty_id: Optional[EntityId]
    successor_treaty_id: Optional[EntityId]
    
    # Documents
    treaty_document_id: Optional[EntityId]  # Handout/document ID
    
    created_at: Timestamp
    updated_at: Timestamp
    version: Version
    
    def __post_init__(self):
        """Validate invariants after construction."""
        self._validate_invariants()
    
    def _validate_invariants(self):
        """Check all invariants are satisfied."""
        if self.updated_at.value < self.created_at.value:
            raise InvariantViolation(
                "Updated timestamp must be >= created timestamp"
            )
        
        if not self.name or len(self.name.strip()) == 0:
            raise InvariantViolation("Treaty name cannot be empty")
        
        total_signatories = len(self.signatory_nation_ids) + len(self.signatory_faction_ids)
        if total_signatories < 2:
            raise InvariantViolation(
                "Treaty must have at least two signatories"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        treaty_type: TreatyType = TreatyType.PEACE,
        is_indefinite: bool = False,
    ) -> 'Treaty':
        """
        Factory method for creating a new Treaty.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            name=name,
            description=description,
            treaty_type=treaty_type,
            status=TreatyStatus.DRAFT,
            signatory_nation_ids=[],
            signatory_faction_ids=[],
            third_party_ids=[],
            negotiation_location_id=None,
            mediator_ids=[],
            negotiation_event_ids=[],
            terms=[],
            obligations=[],
            prohibitions=[],
            rights_granted=[],
            signing_date=None,
            ratification_date=None,
            effective_date=None,
            expiration_date=None,
            is_indefinite=is_indefinite,
            territory_transfers=[],
            border_adjustments=[],
            resource_exchanges=[],
            trade_concessions=[],
            violation_consequences=[],
            dispute_mechanism=None,
            related_conflict_id=None,
            predecessor_treaty_id=None,
            successor_treaty_id=None,
            treaty_document_id=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_signatory_nation(self, nation_id: EntityId) -> None:
        """Add a signatory nation."""
        if nation_id not in self.signatory_nation_ids:
            self.signatory_nation_ids.append(nation_id)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def add_term(self, term: str) -> None:
        """Add a term to the treaty."""
        if term not in self.terms:
            self.terms.append(term)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def update_status(self, new_status: TreatyStatus) -> None:
        """Update treaty status."""
        object.__setattr__(self, 'status', new_status)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
