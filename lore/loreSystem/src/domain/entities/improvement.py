"""
Improvement Entity

Represents a proposed enhancement to the lore that must be validated
against requirements before being applied.
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.common import (
    TenantId,
    EntityId,
    EntityType,
    ImprovementStatus,
    Timestamp,
    GitCommitHash,
)
from ..exceptions import InvalidState


@dataclass
class Improvement:
    """
    Improvement aggregate root.
    
    Represents a proposed change to lore that must be validated.
    Linked to a specific entity (World, Character, or Event) and
    tracked through Git for traceability.
    
    Invariants:
    - Must reference exactly one entity
    - Status transitions must be valid
    - Approved improvements must have been validated
    """
    
    id: Optional[EntityId]
    tenant_id: TenantId
    entity_type: EntityType
    entity_id: EntityId
    suggestion: str
    status: ImprovementStatus
    git_commit_hash: GitCommitHash
    created_at: Timestamp
    
    def __post_init__(self):
        """Validate invariants after construction."""
        if not self.suggestion or len(self.suggestion.strip()) == 0:
            raise ValueError("Suggestion cannot be empty")
    
    @classmethod
    def propose(
        cls,
        tenant_id: TenantId,
        entity_type: EntityType,
        entity_id: EntityId,
        suggestion: str,
        git_commit_hash: GitCommitHash,
    ) -> 'Improvement':
        """
        Factory method for proposing a new improvement.
        
        Initial status is always PROPOSED.
        """
        return cls(
            id=None,
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            suggestion=suggestion,
            status=ImprovementStatus.PROPOSED,
            git_commit_hash=git_commit_hash,
            created_at=Timestamp.now(),
        )
    
    def approve(self) -> None:
        """
        Approve the improvement.
        
        Raises:
            InvalidState: If not in PROPOSED state
        """
        if self.status != ImprovementStatus.PROPOSED:
            raise InvalidState(
                f"Cannot approve improvement in {self.status} state"
            )
        
        object.__setattr__(self, 'status', ImprovementStatus.APPROVED)
    
    def apply(self) -> None:
        """
        Mark improvement as applied to the lore.
        
        Raises:
            InvalidState: If not in APPROVED state
        """
        if self.status != ImprovementStatus.APPROVED:
            raise InvalidState(
                f"Cannot apply improvement in {self.status} state. "
                "Must be approved first."
            )
        
        object.__setattr__(self, 'status', ImprovementStatus.APPLIED)
    
    def reject(self, reason: Optional[str] = None) -> None:
        """
        Reject the improvement.
        
        Can be rejected from PROPOSED or APPROVED states.
        
        Args:
            reason: Optional explanation for rejection
        """
        if self.status == ImprovementStatus.REJECTED:
            return  # Already rejected
        
        if self.status == ImprovementStatus.APPLIED:
            raise InvalidState("Cannot reject an already applied improvement")
        
        object.__setattr__(self, 'status', ImprovementStatus.REJECTED)
        # Note: reason could be stored in a separate field if needed
    
    def is_proposed(self) -> bool:
        """Check if improvement is in proposed state."""
        return self.status == ImprovementStatus.PROPOSED
    
    def is_approved(self) -> bool:
        """Check if improvement has been approved."""
        return self.status == ImprovementStatus.APPROVED
    
    def is_applied(self) -> bool:
        """Check if improvement has been applied."""
        return self.status == ImprovementStatus.APPLIED
    
    def is_rejected(self) -> bool:
        """Check if improvement has been rejected."""
        return self.status == ImprovementStatus.REJECTED
    
    def can_be_applied(self) -> bool:
        """Check if improvement is ready to be applied."""
        return self.status == ImprovementStatus.APPROVED
    
    def __str__(self) -> str:
        return (
            f"Improvement({self.entity_type}:{self.entity_id}, "
            f"{self.status}, commit={self.git_commit_hash.short()})"
        )
    
    def __repr__(self) -> str:
        return (
            f"Improvement(id={self.id}, entity_type={self.entity_type}, "
            f"entity_id={self.entity_id}, status={self.status})"
        )
