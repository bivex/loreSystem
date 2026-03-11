"""CAMEL rumor bridge helpers."""

from .rumor_agents import (
    CanonicalPersistContext,
    CanonicalPersistEngine,
    CanonicalPersistRegistry,
    CamelChatBackend,
    DeterministicRumorBackend,
    RumorChainResult,
    CharacterRelationshipDraft,
    EventDraft,
    load_env_file,
    RumorBridgeService,
    RumorDraft,
    RumorGenerationRequest,
)
from .memory import (
    HashingTextEmbedder,
    LocalNgramTextEmbedder,
    LoreMemoryService,
    QdrantMemoryIndex,
    SQLiteLoreMemoryReader,
    build_memory_service_from_env,
)

__all__ = [
    "CanonicalPersistContext",
    "CanonicalPersistEngine",
    "CanonicalPersistRegistry",
    "CamelChatBackend",
    "CharacterRelationshipDraft",
    "DeterministicRumorBackend",
    "EventDraft",
    "HashingTextEmbedder",
    "LocalNgramTextEmbedder",
    "load_env_file",
    "LoreMemoryService",
    "QdrantMemoryIndex",
    "RumorChainResult",
    "RumorBridgeService",
    "RumorDraft",
    "RumorGenerationRequest",
    "SQLiteLoreMemoryReader",
    "build_memory_service_from_env",
]