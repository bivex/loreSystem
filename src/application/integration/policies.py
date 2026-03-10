"""
Explicit Duplicate-Only Policies for MiroFish Merge-Side Auto-Merge

Each policy implements exact deterministic duplicate matching for a specific
entity type. No fuzzy matching, no generic engine - explicit rules only.
"""
from typing import Optional, List

from .promoter import CandidatePromoter, DuplicateMatchResult
from src.domain.entities.character import Character
from src.domain.value_objects.common import TenantId, EntityId, CharacterName


class SafeExistingCharacterDuplicateOnlyPolicy(CandidatePromoter):
    """
    Explicit policy for exact duplicate Character detection.

    This policy implements deterministic exact duplicate matching against
    an existing staged canonical Character in the same world.

    Matching Rules:
    - Characters are duplicates if they have the EXACT same name
    - Must be in the same world (world_id must match)
    - No fuzzy matching - exact string comparison only

    The "safe" in the name means:
    - Only matches against existing canonical characters
    - Does not create new entities automatically
    - Requires explicit confirmation for ambiguous cases
    """

    def find_duplicate(self, candidate: Character) -> DuplicateMatchResult:
        """
        Find exact duplicate characters for a candidate.

        Args:
            candidate: Character candidate to match

        Returns:
            DuplicateMatchResult with exact match status:
            - no_match: No character with this name exists in the world
            - single_match: Exactly one character with this name exists
            - ambiguous_match: Multiple characters with this name exist (should not happen with unique constraint)
        """
        # Query repository for characters with same name in same world
        matches = self._repository.find_by_name(
            tenant_id=candidate.tenant_id,
            world_id=candidate.world_id,
            name=candidate.name,
        )

        if matches is None:
            # No exact match found
            return DuplicateMatchResult(
                status="no_match",
                matched_entity_id=None,
                matched_entity_name=None,
                all_match_ids=[],
                reason=f"No character with name '{candidate.name}' exists in world {candidate.world_id}",
            )
        else:
            # Exact match found
            return DuplicateMatchResult(
                status="single_match",
                matched_entity_id=matches.id,
                matched_entity_name=str(matches.name),
                all_match_ids=[matches.id],
                reason=f"Exact duplicate found: '{matches.name}' (ID: {matches.id}) in world {candidate.world_id}",
            )

    def can_promote(self, candidate: Character, match_result: DuplicateMatchResult) -> tuple[bool, str]:
        """
        Check if a character candidate can be promoted.

        Promotion rules:
        - no_match: Cannot auto-promote (requires manual review to create as new)
        - single_match: Can promote to existing matched entity
        - ambiguous_match: Cannot promote (gate failure - requires manual resolution)

        Args:
            candidate: Character candidate
            match_result: Result from find_duplicate

        Returns:
            Tuple of (can_promote: bool, reason: str)
        """
        if match_result.status == "no_match":
            return False, f"No existing duplicate - candidate '{candidate.name}' requires manual review to create as new entity"
        if match_result.status == "single_match":
            return True, f"Exact duplicate confirmed: {match_result.matched_entity_name} (ID: {match_result.matched_entity_id})"
        return False, f"Gate failure: ambiguous match found {len(match_result.all_match_ids)} potential duplicates"


# Future policies (following the same explicit pattern):
#
# - SafeExistingLocationDuplicateOnlyPolicy
# - SafeExistingEventDuplicateOnlyPolicy
# - SafeExistingRumorDuplicateOnlyPolicy
# - SafeExistingCharacterRelationshipDuplicateOnlyPolicy
# - SafeExistingFactionDuplicateOnlyPolicy
#
# Each policy should:
# 1. Inherit from CandidatePromoter
# 2. Implement find_duplicate() with exact deterministic matching
# 3. Implement can_promote() with explicit rules for that entity type
# 4. Use only the repository to query for matches
