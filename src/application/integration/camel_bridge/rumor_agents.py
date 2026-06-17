"""CAMEL-powered rumor → event → relationship bridge.

This module is a **backward-compatibility facade**. The monolithic
~16,100-line implementation has been split across subpackages:

* :mod:`.drafts`         - dataclass declarations (Draft types, records, request/result).
* :mod:`.persistence`    - canonical persist engine, policies and ``*Store`` protocols.
* :mod:`.backend_mock`   - ``DeterministicRumorBackend`` (test/offline backend).
* :mod:`.mixins`         - five mixin classes (parsers, stabilizer, fallbacks, prompts, persistence).
* :mod:`.service`        - :class:`RumorBridgeService` orchestrator composing the mixins.

Everything historically importable from ``rumor_agents`` is re-exported
here so existing ``from camel_bridge.rumor_agents import X`` sites keep
working without modification.

See ``docs/refactoring_plan_rumor_agents.md`` for the full plan.
"""

from __future__ import annotations

# Re-export symbols sourced from sibling modules (they were imported here in the
# monolith and external code reaches them through ``rumor_agents``).
from src.application.integration.camel_bridge.backend import (  # noqa: F401
    AgentTextBackend,
    CamelChatBackend,
)
from src.application.integration.camel_bridge.backend_mock import (  # noqa: F401
    DeterministicRumorBackend,
)
from src.application.integration.camel_bridge.env import (  # noqa: F401
    _env_flag,
    load_env_file,
)
from src.application.integration.camel_bridge.memory import (  # noqa: F401
    LoreMemoryService,
)
from src.application.integration.camel_bridge.specs import (  # noqa: F401
    ALL_NARRATIVE_BATCH_FIELDS,
    ALL_SYSTEMS_BATCH_FIELDS,
    DEFAULT_EVENT_AGENT_PROMPT,
    DEFAULT_NARRATIVE_AGENT_PROMPT,
    DEFAULT_NARRATIVE_SYSTEMS_AGENT_PROMPT,
    DEFAULT_RELATIONSHIP_AGENT_PROMPT,
    DEFAULT_RUMOR_AGENT_PROMPTS,
    NARRATIVE_BATCH_SPECS,
    NARRATIVE_STRUCTURE_KEYS,
    SYSTEMS_BATCH_SPECS,
    SYSTEMS_SLICE_KEYS,
)

# Re-export all Draft dataclasses, records and request/result types.
from src.application.integration.camel_bridge.drafts import (  # noqa: F401
    AchievementDraft,
    ActDraft,
    AffinityDraft,
    AlternateRealityDraft,
    ArenaDraft,
    ArtifactSetDraft,
    AttributeDraft,
    BadgeDraft,
    BlueprintDraft,
    BlueprintRequirementDraft,
    BranchPointDraft,
    CampaignDraft,
    ChapterDraft,
    CharacterEvolutionDraft,
    CharacterProfileEntryDraft,
    CharacterRelationshipDraft,
    CharacterVariantDraft,
    ChoiceDraft,
    ComponentDraft,
    ConsequenceDraft,
    CraftingRecipeDraft,
    CursedItemDraft,
    DifficultyCurveDraft,
    DifficultyCurveRecord,
    DivineItemDraft,
    DispositionDraft,
    DropRateDraft,
    DropRateRecord,
    DungeonDraft,
    EnchantmentDraft,
    EnchantmentEffectDraft,
    EndingDraft,
    EpisodeDraft,
    EpilogueDraft,
    EventDraft,
    ExperienceDraft,
    FlashForwardDraft,
    FlashbackDraft,
    GlyphDraft,
    GlyphAbilityDraft,
    GlyphModifierDraft,
    InstanceDraft,
    InventoryDraft,
    InventorySlotDraft,
    InvasionDraft,
    ItemDraft,
    LeaderboardDraft,
    LegendaryWeaponDraft,
    LevelUpDraft,
    LootTableWeightDraft,
    LootTableWeightRecord,
    MasteryDraft,
    MasteryBonusDraft,
    MaterialDraft,
    MoralChoiceDraft,
    MoralChoiceOptionDraft,
    MotionCaptureDraft,
    MythicalArmorDraft,
    NarrativeStructureDraft,
    NoveltyDecision,
    OpenWorldZoneDraft,
    PerkDraft,
    PlayerMetricDraft,
    PlayerMetricRecord,
    PlotBranchDraft,
    PrologueDraft,
    ProgressionCharacterStateDraft,
    ProgressionEventDraft,
    ProgressionEventReasonDraft,
    ProgressionStateDraft,
    QuestChainDraft,
    QuestDraft,
    QuestGiverDraft,
    QuestNodeDraft,
    QuestObjectiveDraft,
    QuestPrerequisiteDraft,
    QuestRewardTierDraft,
    QuestTrackerDraft,
    RaidDraft,
    RankDraft,
    RecipeIngredientDraft,
    RelicCollectionDraft,
    RumorChainResult,
    RumorDraft,
    RumorGenerationRequest,
    RuneDraft,
    RuneBonusDraft,
    RuneEffectDraft,
    SeasonalEventDraft,
    SkillDraft,
    SocketDraft,
    StoryDraft,
    StorylineDraft,
    TalentNodeDraft,
    TalentTreeDraft,
    TitleDraft,
    TraitDraft,
    TrophyDraft,
    VoiceActorDraft,
    WarDraft,
    WorldEventDraft,
)

# Re-export canonical persistence primitives.
from src.application.integration.camel_bridge.persistence.canonical import (  # noqa: F401
    CanonicalPersistContext,
    CanonicalPersistEngine,
    CanonicalPersistPolicy,
    CanonicalPersistRegistry,
    SemanticCandidateLookup,
    TCanonical,
    _canonical_anchor_overlap,
    _canonical_anchor_tokens,
    _canonical_set_similarity,
    _canonical_text_similarity,
    _coerce_canonical_text,
    _contains_cyrillic_text,
    _event_outcome_value,
    _normalize_canonical_text,
    _row_json_int_ids,
    _row_payload_json,
    _row_timestamp_value,
    _spread_speed_rank,
)
from src.application.integration.camel_bridge.persistence.policies import (  # noqa: F401
    EventCanonicalPersistPolicy,
    RelationshipCanonicalPersistPolicy,
    RumorCanonicalPersistPolicy,
)
from src.application.integration.camel_bridge.persistence.stores import *  # noqa: F401,F403

# Re-export the orchestrator service.
from src.application.integration.camel_bridge.service import (  # noqa: F401
    RumorBridgeService,
)

__all__ = [
    "AgentTextBackend",
    "CamelChatBackend",
    "CanonicalPersistContext",
    "CanonicalPersistEngine",
    "CanonicalPersistPolicy",
    "CanonicalPersistRegistry",
    "CharacterRelationshipDraft",
    "DeterministicRumorBackend",
    "EventCanonicalPersistPolicy",
    "EventDraft",
    "LoreMemoryService",
    "NarrativeStructureDraft",
    "NoveltyDecision",
    "NARRATIVE_BATCH_SPECS",
    "NARRATIVE_STRUCTURE_KEYS",
    "RumorBridgeService",
    "RumorChainResult",
    "RumorDraft",
    "RumorGenerationRequest",
    "RelationshipCanonicalPersistPolicy",
    "RumorCanonicalPersistPolicy",
    "SYSTEMS_BATCH_SPECS",
    "SYSTEMS_SLICE_KEYS",
    "SemanticCandidateLookup",
    "_env_flag",
    "load_env_file",
]
