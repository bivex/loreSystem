"""Dataclass declarations for the rumor bridge pipeline.

Aggregates metric records, narrative drafts, systems drafts and the
top-level request/result types. Extracted from the monolithic
``rumor_agents.py`` to isolate pure data declarations from orchestration.

Importing ``from camel_bridge.drafts import *`` re-exports every draft
and record class, preserving the original flat namespace.
"""

from __future__ import annotations

from src.application.integration.camel_bridge.drafts.narrative import *  # noqa: F401,F403
from src.application.integration.camel_bridge.drafts.records import *  # noqa: F401,F403
from src.application.integration.camel_bridge.drafts.results import *  # noqa: F401,F403
from src.application.integration.camel_bridge.drafts.systems import *  # noqa: F401,F403

# Re-export every public name from the submodules so that
# ``from camel_bridge.drafts import X`` works for any draft/record/result.
from src.application.integration.camel_bridge.drafts.narrative import (  # noqa: F401
    NarrativeStructureDraft,
)
from src.application.integration.camel_bridge.drafts.records import (  # noqa: F401
    DifficultyCurveRecord,
    DropRateRecord,
    LootTableWeightRecord,
    PlayerMetricRecord,
)
from src.application.integration.camel_bridge.drafts.results import (  # noqa: F401
    NoveltyDecision,
    RumorChainResult,
    RumorGenerationRequest,
)

__all__ = [
    "DifficultyCurveRecord",
    "DropRateRecord",
    "LootTableWeightRecord",
    "NarrativeStructureDraft",
    "NoveltyDecision",
    "PlayerMetricRecord",
    "RumorChainResult",
    "RumorGenerationRequest",
]
