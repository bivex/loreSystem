"""CAMEL rumor bridge helpers."""

from .backend import CamelChatBackend
from .env import load_env_file
from .memory import (
    HashingTextEmbedder,
    LocalNgramTextEmbedder,
    LoreMemoryService,
    QdrantMemoryIndex,
    SQLiteLoreMemoryReader,
    build_memory_service_from_env,
)
from .rumor_agents import (
    CanonicalPersistContext,
    CanonicalPersistEngine,
    CanonicalPersistRegistry,
    DeterministicRumorBackend,
    RumorChainResult,
    CharacterRelationshipDraft,
    EventDraft,
    RumorBridgeService,
    RumorDraft,
    RumorGenerationRequest,
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
