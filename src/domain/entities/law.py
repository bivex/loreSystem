"""
Law Entity - Legal rule or statute
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


class LawType(str, Enum):
    """Types of laws."""
    CRIMINAL = "criminal"
    CIVIL = "civil"
    CONSTITUTIONAL = "constitutional"
    ADMINISTRATIVE = "administrative"
    TAX = "tax"
    TRADE = "trade"
    MAGICAL = "magical"
    MILITARY = "military"
    RELIGIOUS = "religious"
    CUSTOMARY = "customary"


class LawSeverity(str, Enum):
    """Severity of law violations."""
    INFRACTION = "infraction"  # Minor offenses
    MISDEMEANOR = "misdemeanor"  # Moderate offenses
    FELONY = "felony"  # Serious offenses
    CAPITAL = "capital"  # Punishable by death


@dataclass
class Law:
    """
    Law represents a specific legal rule or statute.
    
    Invariants:
    - Must belong to a legal system or nation
    - Name cannot be empty
    - Must specify at least one penalty
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    # Jurisdiction
    legal_system_id: Optional[EntityId]
    nation_id: Optional[EntityId]
    region_id: Optional[EntityId]
    
    name: str
    description: Description
    
    # Classification
    law_type: LawType
    severity: LawSeverity
    
    # Content
    text: str  # Full legal text
    summary: Optional[str]  # Brief summary
    
    # Scope and application
    applies_to: List[str]  # e.g., ["Citizens", "Foreigners", "Nobles"]
    exceptions: List[str]  # Groups exempt from this law
    
    # Penalties
    penalties: List[str]  # Penalties for violation
    minimum_penalty: Optional[str]
    maximum_penalty: Optional[str]
    
    # Enforcement
    enforcement_agency: Optional[str]  # e.g., "Royal Guard", "Magistrates"
    statute_of_limitations: Optional[str]  # e.g., "10 years", "None"
    
    # Legislative history
    enacted_date: Optional[str]
    repealed_date: Optional[str]
    is_active: bool
    
    # Provenance
    enacting_body: Optional[str]  # e.g., "Parliament", "Royal Decree"
    amendment_ids: List[EntityId]  # IDs of related amendments
    related_law_ids: List[EntityId]
    
    # Legal precedents
    precedent_case_ids: List[EntityId]  # IDs of related legal cases
    
    # References
    constitution_article_id: Optional[EntityId]
    treaty_id: Optional[EntityId]
    
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
            raise InvariantViolation("Law name cannot be empty")
        
        if not self.text or len(self.text.strip()) == 0:
            raise InvariantViolation("Law text cannot be empty")
        
        if not any([self.legal_system_id, self.nation_id, self.region_id]):
            raise InvariantViolation(
                "Law must belong to a legal system, nation, or region"
            )
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        name: str,
        description: Description,
        law_type: LawType,
        text: str,
        severity: LawSeverity,
        legal_system_id: Optional[EntityId] = None,
        nation_id: Optional[EntityId] = None,
        region_id: Optional[EntityId] = None,
    ) -> 'Law':
        """
        Factory method for creating a new Law.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            legal_system_id=legal_system_id,
            nation_id=nation_id,
            region_id=region_id,
            name=name,
            description=description,
            law_type=law_type,
            severity=severity,
            text=text,
            summary=None,
            applies_to=[],
            exceptions=[],
            penalties=[],
            minimum_penalty=None,
            maximum_penalty=None,
            enforcement_agency=None,
            statute_of_limitations=None,
            enacted_date=None,
            repealed_date=None,
            is_active=True,
            enacting_body=None,
            amendment_ids=[],
            related_law_ids=[],
            precedent_case_ids=[],
            constitution_article_id=None,
            treaty_id=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_penalty(self, penalty: str) -> None:
        """Add a penalty for this law."""
        if penalty not in self.penalties:
            self.penalties.append(penalty)
            object.__setattr__(self, 'updated_at', Timestamp.now())
    
    def repeal(self, repeal_date: Optional[str] = None) -> None:
        """Repeal the law."""
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'repealed_date', repeal_date)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
