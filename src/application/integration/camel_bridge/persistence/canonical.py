"""Canonical-persistence engine primitives for the rumor bridge pipeline.

Extracted from ``rumor_agents.py``. Provides the generic
``CanonicalPersistEngine`` / ``CanonicalPersistRegistry`` machinery plus
the canonical-text similarity helpers used by the persist policies and
the save/merge layer. These are pure primitives with no dependency on
the concrete repository implementations.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Generic, Protocol, TypeVar

from src.application.integration.camel_bridge.drafts import NoveltyDecision
from src.domain.value_objects.common import EntityId, EventOutcome, TenantId, Timestamp


# --- Auto-extracted bodies (lines 319-491 of original rumor_agents.py) ---
TCanonical = TypeVar("TCanonical")


@dataclass(frozen=True)
class CanonicalPersistContext:
    tenant_id: TenantId
    world_id: EntityId
    theme: str = ""
    context: str = ""


class CanonicalPersistPolicy(Protocol[TCanonical]):
    def find_existing(
        self, candidate: TCanonical, context: CanonicalPersistContext
    ) -> TCanonical | None: ...

    def decide(
        self, existing: TCanonical, candidate: TCanonical
    ) -> NoveltyDecision: ...

    def merge(self, existing: TCanonical, candidate: TCanonical) -> TCanonical: ...


class CanonicalPersistEngine(Generic[TCanonical]):
    def __init__(
        self,
        *,
        policy: CanonicalPersistPolicy[TCanonical],
        save: Callable[[TCanonical, CanonicalPersistContext], TCanonical],
    ):
        self._policy = policy
        self._save = save

    def persist(
        self, candidate: TCanonical, context: CanonicalPersistContext
    ) -> TCanonical:
        existing = self._policy.find_existing(candidate, context)
        if existing is None:
            return self._save(candidate, context)
        decision = self._policy.decide(existing, candidate)
        if decision.action == "skip_duplicate":
            return existing
        merged = self._policy.merge(existing, candidate)
        return self._save(merged, context)


class CanonicalPersistRegistry:
    def __init__(self):
        self._engines: dict[str, CanonicalPersistEngine[Any]] = {}

    def register(self, key: str, engine: CanonicalPersistEngine[Any]) -> None:
        self._engines[key] = engine

    def get(self, key: str) -> CanonicalPersistEngine[Any]:
        return self._engines[key]


SemanticCandidateLookup = Callable[[str, str, CanonicalPersistContext], set[int]]


def _coerce_canonical_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_canonical_text(value: object) -> str:
    text = (_coerce_canonical_text(value) or "").lower().strip()
    # Preserve alphanumeric characters from any language, and spaces.
    # \w in Python 3 with re.UNICODE (default) includes unicode letters.
    # We want to remove punctuation but keep letters and numbers.
    text = re.sub(r"[^\w\s]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _canonical_set_similarity(
    left: set[int] | set[str], right: set[int] | set[str]
) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    union = len(left | right)
    if union == 0:
        return 0.0
    return intersection / union


def _canonical_text_similarity(left: str, right: str) -> float:
    return _canonical_set_similarity(set(left.split()), set(right.split()))


def _canonical_anchor_tokens(value: object) -> set[str]:
    text = _normalize_canonical_text(value)
    if not text:
        return set()
    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "into",
        "over",
        "under",
        "this",
        "that",
        "main",
        "side",
        "story",
        "storyline",
        "line",
        "arc",
        "chapter",
        "episode",
        "act",
        "part",
        "path",
        "quest",
        "chain",
        "run",
        "tale",
    }
    return {
        token for token in text.split() if len(token) >= 4 and token not in stop_words
    }


def _canonical_anchor_overlap(left: object, right: object) -> int:
    return len(_canonical_anchor_tokens(left) & _canonical_anchor_tokens(right))


def _contains_cyrillic_text(value: object) -> bool:
    text = _coerce_canonical_text(value) or ""
    return bool(re.search(r"[А-Яа-яЁёІіЇїЄєҐґ]", text))


def _row_payload_json(row: Any) -> dict[str, object]:
    try:
        payload_text = str(row["payload_json"] or "").strip()
    except Exception:
        return {}
    if not payload_text:
        return {}
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _row_json_int_ids(row: Any, field: str) -> list[int]:
    raw = row[field] if field in row.keys() else None
    try:
        return [int(item) for item in json.loads(raw or "[]")]
    except Exception:
        return []


def _row_timestamp_value(row: Any, field: str) -> Timestamp | None:
    raw = row[field] if field in row.keys() else None
    text = _coerce_canonical_text(raw)
    if not text:
        return None
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return Timestamp(dt)


def _spread_speed_rank(value: str) -> int:
    return {"Slow": 0, "Moderate": 1, "Rapid": 2, "Explosive": 3}.get(value, 0)


def _event_outcome_value(value: EventOutcome | str) -> str:
    return value.value if hasattr(value, "value") else str(value)
