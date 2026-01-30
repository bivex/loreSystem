"""
Constitution Entity - Founding legal document
"""
from dataclasses import dataclass
from typing import Optional, List

from ..value_objects.common import (
    TenantId,
    EntityId,
    Description,
    Version,
    Timestamp,
)
from ..exceptions import InvariantViolation


@dataclass
class Constitution:
    """
    Constitution represents the supreme law of a nation.
    
    Invariants:
    - Must be linked to a nation
    - Must have at least one article
    - Name cannot be empty
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    world_id: EntityId
    
    nation_id: Optional[EntityId]
    
    name: str
    description: Description
    
    # Structure
    preamble: Optional[str]
    articles: List[str]  # Article text contents
    amendments: List[str]  # Amendment text contents
    
    # Rights and principles
    guaranteed_rights: List[str]
    fundamental_principles: List[str]
    
    # Government structure
    branches_of_government: List[str]
    separation_of_powers: Optional[str]
    checks_and_balances: Optional[str]
    
    # Amendment process
    amendment_process: Optional[str]
    amendment_threshold: Optional[str]  # e.g., "2/3 majority", "75%"
    
    # Citizenship
    citizenship_criteria: Optional[str]
    citizen_rights: List[str]
    citizen_duties: List[str]
    
    # Origin and history
    adoption_date: Optional[str]
    ratification_event_id: Optional[EntityId]
    authors: List[EntityId]  # Character IDs
    inspirations: List[EntityId]  # Other constitutions that inspired this
    
    # Documents
    original_document_id: Optional[EntityId]  # Handout ID
    
    # Status
    is_active: bool
    suspension_reason: Optional[str]
    
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
            raise InvariantViolation("Constitution name cannot be empty")
        
        if not self.nation_id:
            raise InvariantViolation("Constitution must be linked to a nation")
    
    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        world_id: EntityId,
        nation_id: EntityId,
        name: str,
        description: Description,
    ) -> 'Constitution':
        """
        Factory method for creating a new Constitution.
        """
        now = Timestamp.now()
        return cls(
            id=None,
            tenant_id=tenant_id,
            world_id=world_id,
            nation_id=nation_id,
            name=name,
            description=description,
            preamble=None,
            articles=[],
            amendments=[],
            guaranteed_rights=[],
            fundamental_principles=[],
            branches_of_government=[],
            separation_of_powers=None,
            checks_and_balances=None,
            amendment_process=None,
            amendment_threshold=None,
            citizenship_criteria=None,
            citizen_rights=[],
            citizen_duties=[],
            adoption_date=None,
            ratification_event_id=None,
            authors=[],
            inspirations=[],
            original_document_id=None,
            is_active=True,
            suspension_reason=None,
            created_at=now,
            updated_at=now,
            version=Version(1),
        )
    
    def add_article(self, article_text: str) -> None:
        """Add an article to the constitution."""
        self.articles.append(article_text)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def add_amendment(self, amendment_text: str) -> None:
        """Add an amendment to the constitution."""
        self.amendments.append(amendment_text)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def suspend(self, reason: str) -> None:
        """Suspend the constitution."""
        object.__setattr__(self, 'is_active', False)
        object.__setattr__(self, 'suspension_reason', reason)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
    
    def reinstate(self) -> None:
        """Reinstate a suspended constitution."""
        object.__setattr__(self, 'is_active', True)
        object.__setattr__(self, 'suspension_reason', None)
        object.__setattr__(self, 'updated_at', Timestamp.now())
        object.__setattr__(self, 'version', self.version.increment())
