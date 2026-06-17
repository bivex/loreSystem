"""Canonical-persistence layer for the rumor bridge pipeline.

Aggregates the generic persist engine/primitives, the per-entity persist
policies, and the repository (``Store``) Protocol interfaces. Extracted
from the monolithic ``rumor_agents.py``.

Public surface (re-exported here, also re-exported by ``rumor_agents``):
``CanonicalPersistContext``, ``CanonicalPersistEngine``,
``CanonicalPersistRegistry``, plus the persist policies and the ``*Store``
protocols.
"""

from __future__ import annotations

from src.application.integration.camel_bridge.persistence.canonical import (  # noqa: F401
    CanonicalPersistContext,
    CanonicalPersistEngine,
    CanonicalPersistPolicy,
    CanonicalPersistRegistry,
    SemanticCandidateLookup,
    TCanonical,
)
from src.application.integration.camel_bridge.persistence.policies import (  # noqa: F401
    EventCanonicalPersistPolicy,
    RelationshipCanonicalPersistPolicy,
    RumorCanonicalPersistPolicy,
)
from src.application.integration.camel_bridge.persistence.stores import *  # noqa: F401,F403

__all__ = [
    "CanonicalPersistContext",
    "CanonicalPersistEngine",
    "CanonicalPersistPolicy",
    "CanonicalPersistRegistry",
    "EventCanonicalPersistPolicy",
    "RelationshipCanonicalPersistPolicy",
    "RumorCanonicalPersistPolicy",
    "SemanticCandidateLookup",
    "TCanonical",
]
