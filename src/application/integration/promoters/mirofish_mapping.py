"""Promote approved MiroFish candidate deltas into canonical lore records."""

from __future__ import annotations

from dataclasses import is_dataclass, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.domain.entities.character import Character, CharacterElement, CharacterRole
from src.domain.entities.character_relationship import CharacterRelationship, RelationshipType
from src.domain.entities.event import Event
from src.domain.entities.faction import Faction, FactionAlignment, FactionType
from src.domain.entities.location import Location
from src.domain.entities.rumor import Rumor
from src.domain.value_objects.common import (
    Backstory,
    CharacterName,
    CharacterStatus,
    DateRange,
    Description,
    EntityId,
    EventOutcome,
    LocationType,
    Rarity,
    TenantId,
    Timestamp,
    Version,
)
from src.infrastructure.mirofish_writeback_store import MiroFishWriteBackStore


from .mirofish_mapping import MiroFishMappingMixin
from .mirofish_validation import MiroFishValidationMixin
from .mirofish_lookup import MiroFishLookupMixin
from .mirofish_resolution import MiroFishResolutionMixin
from .mirofish_utils import MiroFishUtilsMixin


class MiroFishCandidatePromoter(
    MiroFishMappingMixin,
    MiroFishValidationMixin,
    MiroFishLookupMixin,
    MiroFishResolutionMixin,
    MiroFishUtilsMixin,
class MiroFishMappingMixin:
                candidate_id,
                canonical_type=canonical_entity["canonical_type"],
                canonical_id=canonical_entity["canonical_id"],
            )
        return {
            "candidate_id": candidate_id,
            "canonical_entity": canonical_entity,
            "run_link": run_link,
            "candidate": updated_candidate,
        }

