"""
Candidate Promoter for MiroFish Merge-Side Auto-Merge

Provides explicit policies for detecting and handling duplicate entities
when merging external data into the canonical lore system.
"""
from dataclasses import dataclass
from typing import Optional, List, Literal
from enum import Enum


class PromotionStatus(str, Enum):
    """Status of a promotion attempt."""
    PENDING = "pending"
    NO_MATCH = "no_match"
    AMBIGUOUS_MATCH = "ambiguous_match"
    GATE_FAILURE = "gate_failure"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class DuplicateMatchResult:
    """Result of a duplicate detection query."""
    status: Literal["no_match", "single_match", "ambiguous_match"]
    matched_entity_id: Optional[int]
    matched_entity_name: Optional[str]
    all_match_ids: List[int]
    reason: str


@dataclass
class PromotionResult:
    """Result of a promotion attempt."""
    status: PromotionStatus
    message: str
    promoted_entity_id: Optional[int] = None
    matched_against_id: Optional[int] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class CandidatePromoter:
    """
    Base promoter for merge-side auto-merge candidates.

    Promoters evaluate candidate entities for merging into the canonical
    lore system using explicit deterministic matching rules.
    """

    def __init__(self, repository):
        """
        Initialize the promoter with a repository.

        Args:
            repository: Repository for querying existing entities
        """
        self._repository = repository

    def find_duplicate(self, candidate) -> DuplicateMatchResult:
        """
        Find duplicate entities for a candidate.

        Subclasses implement specific matching logic.

        Args:
            candidate: Candidate entity to match

        Returns:
            DuplicateMatchResult with match status and details
        """
        raise NotImplementedError("Subclasses must implement find_duplicate")

    def can_promote(self, candidate, match_result: DuplicateMatchResult) -> tuple[bool, str]:
        """
        Check if a candidate can be promoted.

        Args:
            candidate: Candidate entity
            match_result: Result from find_duplicate

        Returns:
            Tuple of (can_promote: bool, reason: str)
        """
        if match_result.status == "no_match":
            return True, "No existing duplicate found - candidate can be promoted as new entity"
        if match_result.status == "single_match":
            return True, f"Exact duplicate found: {match_result.matched_entity_name} (ID: {match_result.matched_entity_id})"
        return False, f"Ambiguous match - found {len(match_result.all_match_ids)} potential duplicates"

    def preview(self, candidate) -> PromotionResult:
        """
        Preview promotion of a candidate without executing.

        Args:
            candidate: Candidate entity to preview

        Returns:
            PromotionResult with preview information
        """
        match_result = self.find_duplicate(candidate)
        can_promote, reason = self.can_promote(candidate, match_result)

        if match_result.status == "no_match":
            return PromotionResult(
                status=PromotionStatus.NO_MATCH,
                message=reason,
            )
        elif match_result.status == "single_match":
            return PromotionResult(
                status=PromotionStatus.APPROVED,
                message=reason,
                matched_against_id=match_result.matched_entity_id,
            )
        else:  # ambiguous_match
            return PromotionResult(
                status=PromotionStatus.AMBIGUOUS_MATCH,
                message=reason,
            )

    def execute(self, candidate) -> PromotionResult:
        """
        Execute promotion of a candidate.

        Args:
            candidate: Candidate entity to promote

        Returns:
            PromotionResult with execution result
        """
        preview_result = self.preview(candidate)

        if preview_result.status == PromotionStatus.AMBIGUOUS_MATCH:
            return PromotionResult(
                status=PromotionStatus.GATE_FAILURE,
                message="Cannot promote candidate with ambiguous matches",
                errors=[preview_result.message],
            )

        if preview_result.status == PromotionStatus.APPROVED:
            # Candidate matches an existing entity - return the matched entity ID
            return PromotionResult(
                status=PromotionStatus.APPROVED,
                message=preview_result.message,
                promoted_entity_id=preview_result.matched_against_id,
                matched_against_id=preview_result.matched_against_id,
            )

        # No match - candidate would be promoted as new entity
        return PromotionResult(
            status=PromotionStatus.NO_MATCH,
            message=preview_result.message,
        )
