"""
Integration Layer

This module contains integration logic for merging external data
into the canonical lore system, including duplicate detection policies.
"""
from .promoter import (
    CandidatePromoter,
    DuplicateMatchResult,
    PromotionResult,
    PromotionStatus,
)
from .policies import SafeExistingCharacterDuplicateOnlyPolicy

__all__ = [
    "CandidatePromoter",
    "DuplicateMatchResult",
    "PromotionResult",
    "PromotionStatus",
    "SafeExistingCharacterDuplicateOnlyPolicy",
]
